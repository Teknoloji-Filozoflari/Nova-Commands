#!/usr/bin/env python3
"""Validate Nova-Commands curated bank + concept articles.

Checks (CI gate):
  - JSON Schema conformance (command.schema.json = live v2, concept.schema.json)
  - Unique command ids; filename stem == id; directory == category
  - schema_version == 2 on every command YAML
  - Category ∈ metadata/categories.yaml
  - package_refs.manager / distributions reference Faz 1 registries when present
  - verification.status rules (verified requires sources + last_reviewed)
  - Flag verified=true only allowed when command verification is reviewed|verified
  - Risk consistency helpers; related must not self-ref
  - learning_level (optional; independent of risk; missing → unspecified at build)
  - examples[].difficulty (optional pedagogy label; not derived from risk)
  - i18n consistency: every localized object has non-empty tr and en
  - nova.concepts / related_topics / concept related_* reference known registry or article ids
  - Concept/topic-guide articles under concepts/; id == filename; related_commands exist
  - Topic-guide structured refs (learning_path, command_table, graded_examples, …) resolve
  - safe_exercises.risk is only safe|caution
  - Soft: platform registries (scripts/validate_platform_registries.py)
  - Soft: stub fixtures task/profile/compatibility (scripts/validate_schema_v2.py)
    (loads both command schema v1 archive + live v2; fixtures fail on missing fields)
  - Hard when present: tasks/ + profiles/ (scripts/validate_tasks_profiles.py)
  - Hard: security / wipe-pattern / related / minisign gates (scripts/validate_security.py)
  - Hard: generated catalog/manifest/search-index (scripts/validate_generated_artifacts.py)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
CONCEPTS_DIR = ROOT / "concepts"
SCHEMA_PATH = ROOT / "schema" / "command.schema.json"
CONCEPT_SCHEMA_PATH = ROOT / "schema" / "concept.schema.json"
CATEGORIES_PATH = ROOT / "metadata" / "categories.yaml"
CONCEPTS_META_PATH = ROOT / "metadata" / "concepts.yaml"
PLATFORM_VALIDATE = ROOT / "scripts" / "validate_platform_registries.py"
SCHEMA_V2_VALIDATE = ROOT / "scripts" / "validate_schema_v2.py"
TASKS_PROFILES_VALIDATE = ROOT / "scripts" / "validate_tasks_profiles.py"
SECURITY_VALIDATE = ROOT / "scripts" / "validate_security.py"
GENERATED_VALIDATE = ROOT / "scripts" / "validate_generated_artifacts.py"
META = ROOT / "metadata"

RISK_RANK = {"safe": 0, "caution": 1, "dangerous": 2, "destructive": 3}
LEARNING_LEVELS = frozenset({"beginner", "intermediate", "advanced", "unspecified"})
EXAMPLE_DIFFICULTIES = frozenset({"beginner", "intermediate", "advanced"})

# Shells allowed by schema enum that are short/legacy names (not all in shells.yaml).
LEGACY_SHELL_NAMES = frozenset({"any", "sh", "bash", "zsh", "fish"})


def load_registry_ids(yaml_name: str, list_key: str) -> set[str]:
    path = META / yaml_name
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get(list_key) or []
    return {e["id"] for e in entries if isinstance(e, dict) and "id" in e}


def load_categories() -> set[str]:
    data = yaml.safe_load(CATEGORIES_PATH.read_text(encoding="utf-8"))
    return {c["id"] for c in data["categories"]}


def load_concept_registry() -> dict[str, dict]:
    data = yaml.safe_load(CONCEPTS_META_PATH.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data.get("concepts") or []}


def load_schema_validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    resource = Resource.from_contents(schema)
    registry = Registry().with_resource(schema["$id"], resource)
    return Draft202012Validator(schema, registry=registry)


def check_localized(
    errors: list[str],
    rel: Path | str,
    prefix: str,
    obj: Any,
    *,
    required: bool = True,
) -> None:
    """Ensure mapping has non-empty tr and en strings."""
    if obj is None:
        if required:
            errors.append(f"{rel}: {prefix} missing")
        return
    if not isinstance(obj, dict):
        errors.append(f"{rel}: {prefix} must be a mapping with tr/en")
        return
    for lang in ("tr", "en"):
        val = obj.get(lang)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{rel}: {prefix}.{lang} missing or empty")


def check_i18n_command(errors: list[str], rel: Path, raw: dict) -> None:
    check_localized(errors, rel, "summary", raw.get("summary"))
    check_localized(errors, rel, "description", raw.get("description"))
    if "install_notes" in raw and raw["install_notes"] is not None:
        check_localized(errors, rel, "install_notes", raw.get("install_notes"))

    intent = raw.get("intent")
    if not isinstance(intent, dict):
        errors.append(f"{rel}: intent must be mapping with tr/en arrays")
    else:
        for lang in ("tr", "en"):
            arr = intent.get(lang)
            if not isinstance(arr, list) or not arr:
                errors.append(f"{rel}: intent.{lang} must be a non-empty array")
            elif any(not isinstance(x, str) or not x.strip() for x in arr):
                errors.append(f"{rel}: intent.{lang} contains empty phrase")

    for i, flag in enumerate(raw.get("flags") or []):
        if not isinstance(flag, dict):
            continue
        check_localized(errors, rel, f"flags[{i}].meaning", flag.get("meaning"))

    for i, ex in enumerate(raw.get("examples") or []):
        if not isinstance(ex, dict):
            continue
        check_localized(errors, rel, f"examples[{i}].title", ex.get("title"))
        check_localized(
            errors, rel, f"examples[{i}].explanation", ex.get("explanation")
        )

    for optional in ("when_to_use", "expected_effect", "purpose"):
        if optional in raw and raw[optional] is not None:
            check_localized(errors, rel, optional, raw.get(optional), required=False)

    for i, mistake in enumerate(raw.get("common_mistakes") or []):
        check_localized(errors, rel, f"common_mistakes[{i}]", mistake)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commands-dir",
        type=Path,
        default=COMMANDS_DIR,
        help="Override commands directory",
    )
    parser.add_argument(
        "--concepts-dir",
        type=Path,
        default=CONCEPTS_DIR,
        help="Override concepts directory",
    )
    args = parser.parse_args()
    commands_dir: Path = args.commands_dir
    concepts_dir: Path = args.concepts_dir

    errors: list[str] = []
    categories = load_categories()
    concept_registry = load_concept_registry()
    known_concept_ids = set(concept_registry)
    validator = load_schema_validator(SCHEMA_PATH)
    concept_validator = load_schema_validator(CONCEPT_SCHEMA_PATH)
    seen_ids: dict[str, Path] = {}
    pm_ids = load_registry_ids("package-managers.yaml", "package_managers")
    distro_ids = load_registry_ids("distributions.yaml", "distributions")
    os_ids = load_registry_ids("operating-systems.yaml", "operating_systems")
    shell_ids = load_registry_ids("shells.yaml", "shells")

    files = sorted(commands_dir.glob("*/*.yaml")) if commands_dir.is_dir() else []
    if not files:
        errors.append(f"no command YAML files under {commands_dir}")

    for path in files:
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {exc}")
            continue

        if not isinstance(raw, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue

        if raw.get("schema_version") != 2:
            errors.append(
                f"{rel}: schema_version must be 2 (got {raw.get('schema_version')!r})"
            )

        for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel}: schema {loc}: {err.message}")

        check_i18n_command(errors, rel, raw)

        cid = raw.get("id")
        category = raw.get("category")
        stem = path.stem
        parent = path.parent.name

        if cid != stem:
            errors.append(f"{rel}: id {cid!r} must equal filename stem {stem!r}")
        if category != parent:
            errors.append(
                f"{rel}: category {category!r} must equal directory name {parent!r}"
            )
        if category not in categories:
            errors.append(f"{rel}: unknown category {category!r}")

        if isinstance(cid, str):
            if cid in seen_ids:
                errors.append(
                    f"{rel}: duplicate id {cid!r} (also {seen_ids[cid]})"
                )
            else:
                seen_ids[cid] = rel

        for os_id in raw.get("operating_systems") or []:
            if os_ids and os_id not in os_ids:
                errors.append(f"{rel}: operating_systems unknown id {os_id!r}")

        for sh in raw.get("shells") or []:
            if shell_ids and sh not in shell_ids and sh not in LEGACY_SHELL_NAMES:
                errors.append(f"{rel}: shells unknown id {sh!r}")

        for i, pref in enumerate(raw.get("package_refs") or []):
            if not isinstance(pref, dict):
                continue
            mgr = pref.get("manager")
            if pm_ids and mgr not in pm_ids:
                errors.append(
                    f"{rel}: package_refs[{i}].manager unknown id {mgr!r}"
                )
            for dist in pref.get("distributions") or []:
                if distro_ids and dist not in distro_ids:
                    errors.append(
                        f"{rel}: package_refs[{i}].distributions unknown id {dist!r}"
                    )

        ver = raw.get("verification") or {}
        status = ver.get("status")
        if status == "verified":
            sources = ver.get("sources") or []
            if not sources:
                errors.append(f"{rel}: verified entries require verification.sources")
            if not ver.get("last_reviewed"):
                errors.append(
                    f"{rel}: verified entries require verification.last_reviewed"
                )

        if status == "draft":
            for i, flag in enumerate(raw.get("flags") or []):
                if flag.get("verified") is True:
                    errors.append(
                        f"{rel}: flags[{i}].verified cannot be true while "
                        "verification.status is draft"
                    )

        cmd_risk = raw.get("risk")
        cmd_rank = RISK_RANK.get(cmd_risk, 0)
        for i, ex in enumerate(raw.get("examples") or []):
            if not isinstance(ex, dict):
                continue
            ex_risk = ex.get("risk")
            ex_rank = RISK_RANK.get(ex_risk, 0)
            if cmd_rank == 0 and ex_rank >= 3:
                errors.append(
                    f"{rel}: examples[{i}].risk is destructive but command risk is safe "
                    "(raise command.risk or lower example risk)"
                )
            ex_diff = ex.get("difficulty")
            if ex_diff is not None and ex_diff not in EXAMPLE_DIFFICULTIES:
                errors.append(
                    f"{rel}: examples[{i}].difficulty invalid {ex_diff!r} "
                    "(expected beginner|intermediate|advanced; do not use risk labels)"
                )

        # learning_level is optional; missing means unspecified at catalog build.
        # Never derive from risk — only validate explicit values here.
        learning = raw.get("learning_level")
        if learning is not None and learning not in LEARNING_LEVELS:
            errors.append(
                f"{rel}: learning_level invalid {learning!r} "
                "(expected beginner|intermediate|advanced|unspecified; "
                "independent of risk)"
            )

        for rid in raw.get("related") or []:
            if rid == cid:
                errors.append(f"{rel}: related must not include self")

        nova = raw.get("nova") or {}
        for concept in nova.get("concepts") or []:
            if concept not in known_concept_ids:
                errors.append(
                    f"{rel}: nova.concepts unknown id {concept!r} "
                    "(add to metadata/concepts.yaml)"
                )
        for topic in raw.get("related_topics") or []:
            if topic not in known_concept_ids:
                errors.append(
                    f"{rel}: related_topics unknown id {topic!r} "
                    "(add to metadata/concepts.yaml)"
                )

    # --- concepts articles ---
    concept_files = (
        sorted(concepts_dir.glob("*.yaml")) if concepts_dir.is_dir() else []
    )
    if not concept_files:
        errors.append(f"no concept YAML files under {concepts_dir}")

    seen_concept_articles: dict[str, Path] = {}
    for path in concept_files:
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {exc}")
            continue
        if not isinstance(raw, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue

        for err in sorted(
            concept_validator.iter_errors(raw), key=lambda e: list(e.path)
        ):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel}: schema {loc}: {err.message}")

        check_localized(errors, rel, "title", raw.get("title"))
        check_localized(errors, rel, "summary", raw.get("summary"))
        check_localized(errors, rel, "body", raw.get("body"))
        if raw.get("intro") is not None:
            check_localized(errors, rel, "intro", raw.get("intro"), required=False)

        cid = raw.get("id")
        if cid != path.stem:
            errors.append(f"{rel}: id {cid!r} must equal filename stem {path.stem!r}")
        if isinstance(cid, str):
            if cid in seen_concept_articles:
                errors.append(f"{rel}: duplicate concept id {cid!r}")
            else:
                seen_concept_articles[cid] = rel
            if cid not in known_concept_ids:
                errors.append(
                    f"{rel}: concept id {cid!r} missing from metadata/concepts.yaml"
                )

        ver = raw.get("verification") or {}
        if ver.get("status") == "verified":
            if not (ver.get("sources") or []):
                errors.append(f"{rel}: verified concepts require sources")
            if not ver.get("last_reviewed"):
                errors.append(f"{rel}: verified concepts require last_reviewed")

        for rid in raw.get("related_commands") or []:
            if rid not in seen_ids:
                errors.append(
                    f"{rel}: related_commands unknown command id {rid!r}"
                )
        for xid in raw.get("related_concepts") or []:
            if xid not in known_concept_ids and xid not in seen_concept_articles:
                # allow forward refs within articles after loop — check registry only
                if xid not in known_concept_ids:
                    errors.append(
                        f"{rel}: related_concepts unknown id {xid!r}"
                    )

        # Topic-guide structured sections (all optional; omit empty).
        for i, step in enumerate(raw.get("learning_path") or []):
            if not isinstance(step, dict):
                continue
            ref = step.get("ref")
            kind = step.get("kind")
            if kind == "command" and ref not in seen_ids:
                errors.append(
                    f"{rel}: learning_path[{i}].ref unknown command id {ref!r}"
                )
            if kind == "concept" and ref not in known_concept_ids:
                errors.append(
                    f"{rel}: learning_path[{i}].ref unknown concept id {ref!r}"
                )
            if step.get("note") is not None:
                check_localized(
                    errors, rel, f"learning_path[{i}].note", step.get("note")
                )

        for i, sub in enumerate(raw.get("subtopics") or []):
            if not isinstance(sub, dict):
                continue
            check_localized(errors, rel, f"subtopics[{i}].title", sub.get("title"))
            check_localized(
                errors, rel, f"subtopics[{i}].summary", sub.get("summary")
            )
            for rid in sub.get("related_commands") or []:
                if rid not in seen_ids:
                    errors.append(
                        f"{rel}: subtopics[{i}].related_commands unknown "
                        f"command id {rid!r}"
                    )

        for i, row in enumerate(raw.get("command_table") or []):
            if not isinstance(row, dict):
                continue
            rid = row.get("id")
            if rid not in seen_ids:
                errors.append(
                    f"{rel}: command_table[{i}].id unknown command id {rid!r}"
                )
            check_localized(
                errors, rel, f"command_table[{i}].purpose", row.get("purpose")
            )

        for i, ex in enumerate(raw.get("graded_examples") or []):
            if not isinstance(ex, dict):
                continue
            check_localized(
                errors, rel, f"graded_examples[{i}].title", ex.get("title")
            )
            check_localized(
                errors,
                rel,
                f"graded_examples[{i}].explanation",
                ex.get("explanation"),
            )
            for rid in ex.get("related_commands") or []:
                if rid not in seen_ids:
                    errors.append(
                        f"{rel}: graded_examples[{i}].related_commands "
                        f"unknown command id {rid!r}"
                    )

        for i, callout in enumerate(raw.get("callouts") or []):
            if not isinstance(callout, dict):
                continue
            check_localized(
                errors, rel, f"callouts[{i}].text", callout.get("text")
            )

        for i, exer in enumerate(raw.get("safe_exercises") or []):
            if not isinstance(exer, dict):
                continue
            check_localized(
                errors, rel, f"safe_exercises[{i}].title", exer.get("title")
            )
            check_localized(
                errors, rel, f"safe_exercises[{i}].prompt", exer.get("prompt")
            )
            risk = exer.get("risk")
            if risk not in (None, "safe", "caution"):
                errors.append(
                    f"{rel}: safe_exercises[{i}].risk must be safe|caution "
                    f"(got {risk!r})"
                )
            for rid in exer.get("related_commands") or []:
                if rid not in seen_ids:
                    errors.append(
                        f"{rel}: safe_exercises[{i}].related_commands "
                        f"unknown command id {rid!r}"
                    )

        for i, step in enumerate(raw.get("next_steps") or []):
            if not isinstance(step, dict):
                continue
            nid = step.get("id")
            if nid not in known_concept_ids:
                errors.append(
                    f"{rel}: next_steps[{i}].id unknown concept id {nid!r}"
                )
            if step.get("note") is not None:
                check_localized(
                    errors, rel, f"next_steps[{i}].note", step.get("note")
                )

        for dist in raw.get("distributions") or []:
            if distro_ids and dist not in distro_ids:
                errors.append(f"{rel}: distributions unknown id {dist!r}")

    # Registry articles field must point at existing files when set
    for cid, meta in concept_registry.items():
        article = meta.get("article")
        if article and article not in seen_concept_articles:
            errors.append(
                f"metadata/concepts.yaml: concept {cid!r} article {article!r} "
                "has no concepts/<id>.yaml"
            )

    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    # Soft platform-registry gate (additive; does not alter command bank).
    if PLATFORM_VALIDATE.is_file():
        proc = subprocess.run(
            [sys.executable, str(PLATFORM_VALIDATE)],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            return proc.returncode

    # Soft stub-schema gate (task/profile/compatibility fixtures; bank is live v2).
    if SCHEMA_V2_VALIDATE.is_file():
        proc = subprocess.run(
            [sys.executable, str(SCHEMA_V2_VALIDATE)],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            return proc.returncode

    # Faz 8+: validate tasks/ + profiles/ when present (not in catalog hash yet).
    if TASKS_PROFILES_VALIDATE.is_file():
        tp_args = [sys.executable, str(TASKS_PROFILES_VALIDATE)]
        if (ROOT / "tasks").is_dir() or (ROOT / "profiles").is_dir():
            tp_args.append("--require")
        proc = subprocess.run(tp_args, cwd=ROOT, check=False)
        if proc.returncode != 0:
            return proc.returncode

    # Faz 10: security / compatibility / signing-material gates (static only).
    if SECURITY_VALIDATE.is_file():
        proc = subprocess.run(
            [sys.executable, str(SECURITY_VALIDATE), "--commands-dir", str(commands_dir)],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            return proc.returncode

    # Generated catalog artifacts (schema + matching content_sha256).
    if GENERATED_VALIDATE.is_file():
        proc = subprocess.run(
            [sys.executable, str(GENERATED_VALIDATE)],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            return proc.returncode

    print(
        f"OK: {len(seen_ids)} commands (schema v2), "
        f"{len(seen_concept_articles)} concepts validated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
