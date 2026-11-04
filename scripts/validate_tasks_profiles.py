#!/usr/bin/env python3
"""Validate live tasks/ and profiles/ trees (Faz 8).

Hard gate when the directories exist (Faz 8+). Checks:
  - JSON Schema (task.schema.json / profile.schema.json)
  - id == filename stem; unique ids within kind
  - task ids do not collide with command ids
  - related_commands / implementation.commands reference known command ids
  - related_tasks reference known task ids (when both present)
  - operating_systems / distributions / shells / server_platforms registry refs
  - verification.status rules (verified requires sources + last_reviewed)
  - i18n: name/summary(+description/intent) non-empty tr/en
  - no silent verified promotions expected for agent drafts

Catalog indexing / content_sha256 inclusion is handled by scripts/build_catalog.py (Faz 9).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
PROFILES_DIR = ROOT / "profiles"
COMMANDS_DIR = ROOT / "commands"
SCHEMA_TASK = ROOT / "schema" / "task.schema.json"
SCHEMA_PROFILE = ROOT / "schema" / "profile.schema.json"
META = ROOT / "metadata"


def load_schema_validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    resource = Resource.from_contents(schema)
    registry = Registry().with_resource(schema["$id"], resource)
    return Draft202012Validator(schema, registry=registry)


def load_registry_ids(yaml_name: str, list_key: str) -> set[str]:
    path = META / yaml_name
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get(list_key) or []
    return {e["id"] for e in entries if isinstance(e, dict) and "id" in e}


def load_command_ids(commands_dir: Path) -> set[str]:
    ids: set[str] = set()
    if not commands_dir.is_dir():
        return ids
    for path in commands_dir.rglob("*.yaml"):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "id" in raw:
            ids.add(raw["id"])
    return ids


def check_localized(
    errors: list[str],
    rel: str,
    prefix: str,
    obj: Any,
    *,
    required: bool = True,
) -> None:
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


def check_verification(errors: list[str], rel: str, ver: Any) -> None:
    if not isinstance(ver, dict):
        errors.append(f"{rel}: verification missing or not a mapping")
        return
    status = ver.get("status")
    if status not in ("draft", "reviewed", "verified"):
        errors.append(f"{rel}: verification.status invalid: {status!r}")
    if status == "verified":
        if not ver.get("sources"):
            errors.append(f"{rel}: verified requires sources")
        if not ver.get("last_reviewed"):
            errors.append(f"{rel}: verified requires last_reviewed")


def check_refs(
    errors: list[str],
    rel: str,
    raw: dict[str, Any],
    *,
    command_ids: set[str],
    task_ids: set[str],
    registries: dict[str, set[str]],
    kind: str,
) -> None:
    for cid in raw.get("related_commands") or []:
        if command_ids and cid not in command_ids:
            errors.append(f"{rel}: related_commands unknown command id {cid!r}")

    for tid in raw.get("related_tasks") or []:
        if task_ids and tid not in task_ids:
            errors.append(f"{rel}: related_tasks unknown task id {tid!r}")

    for field, key in (
        ("operating_systems", "os"),
        ("distributions", "distros"),
        ("server_platforms", "servers"),
    ):
        known = registries.get(key) or set()
        for rid in raw.get(field) or []:
            if known and rid not in known:
                errors.append(f"{rel}: {field} unknown id {rid!r}")

    if kind == "task":
        for i, impl in enumerate(raw.get("implementations") or []):
            if not isinstance(impl, dict):
                continue
            prefix = f"{rel}: implementations[{i}]"
            for cid in impl.get("commands") or []:
                if command_ids and cid not in command_ids:
                    errors.append(f"{prefix}: commands unknown id {cid!r}")
            for rid in impl.get("operating_systems") or []:
                if registries["os"] and rid not in registries["os"]:
                    errors.append(f"{prefix}: operating_systems unknown id {rid!r}")
            for rid in impl.get("distributions") or []:
                if registries["distros"] and rid not in registries["distros"]:
                    errors.append(f"{prefix}: distributions unknown id {rid!r}")
            for rid in impl.get("shells") or []:
                if registries["shells"] and rid not in registries["shells"]:
                    errors.append(f"{prefix}: shells unknown id {rid!r}")


def validate_tree(
    errors: list[str],
    directory: Path,
    *,
    kind: str,
    validator: Draft202012Validator,
    command_ids: set[str],
    task_ids: set[str],
    registries: dict[str, set[str]],
) -> list[dict[str, Any]]:
    if not directory.is_dir():
        return []

    seen: dict[str, str] = {}
    loaded: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        rel = str(path.relative_to(ROOT))
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {exc}")
            continue
        if not isinstance(raw, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue

        for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel}: schema {loc}: {err.message}")

        cid = raw.get("id")
        if not isinstance(cid, str):
            errors.append(f"{rel}: id missing")
            continue
        if cid != path.stem:
            errors.append(f"{rel}: id {cid!r} != filename stem {path.stem!r}")
        if cid in seen:
            errors.append(f"{rel}: duplicate id {cid!r} (also {seen[cid]})")
        else:
            seen[cid] = rel

        if raw.get("schema_version") not in (None, 2):
            errors.append(
                f"{rel}: schema_version must be 2 (got {raw.get('schema_version')!r})"
            )
        if raw.get("kind") not in (None, kind):
            errors.append(f"{rel}: kind must be {kind!r} (got {raw.get('kind')!r})")

        check_localized(errors, rel, "name", raw.get("name"))
        check_localized(errors, rel, "summary", raw.get("summary"))
        check_localized(errors, rel, "description", raw.get("description"), required=False)
        if kind == "task":
            intent = raw.get("intent")
            if not isinstance(intent, dict):
                errors.append(f"{rel}: intent missing")
            else:
                for lang in ("tr", "en"):
                    vals = intent.get(lang)
                    if not isinstance(vals, list) or not vals:
                        errors.append(f"{rel}: intent.{lang} missing or empty")

        check_verification(errors, rel, raw.get("verification"))
        check_refs(
            errors,
            rel,
            raw,
            command_ids=command_ids,
            task_ids=task_ids,
            registries=registries,
            kind=kind,
        )

        if kind == "task" and command_ids and cid in command_ids:
            errors.append(f"{rel}: task id {cid!r} collides with a command id")

        loaded.append(raw)

    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=TASKS_DIR)
    parser.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)
    parser.add_argument("--commands-dir", type=Path, default=COMMANDS_DIR)
    parser.add_argument(
        "--require",
        action="store_true",
        help="Fail if tasks/ or profiles/ directories are missing",
    )
    args = parser.parse_args()

    errors: list[str] = []
    tasks_dir: Path = args.tasks_dir
    profiles_dir: Path = args.profiles_dir

    if args.require:
        if not tasks_dir.is_dir():
            errors.append(f"missing required directory {tasks_dir}")
        if not profiles_dir.is_dir():
            errors.append(f"missing required directory {profiles_dir}")

    if not tasks_dir.is_dir() and not profiles_dir.is_dir():
        if errors:
            print(f"FAIL: {len(errors)} tasks/profiles issue(s)", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        print("OK: tasks/profiles absent (optional pre-Faz 8)")
        return 0

    for path, label in ((SCHEMA_TASK, "task"), (SCHEMA_PROFILE, "profile")):
        if not path.is_file():
            errors.append(f"missing schema/{label}.schema.json")

    if errors and (not SCHEMA_TASK.is_file() or not SCHEMA_PROFILE.is_file()):
        print(f"FAIL: {len(errors)} tasks/profiles issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    task_validator = load_schema_validator(SCHEMA_TASK)
    profile_validator = load_schema_validator(SCHEMA_PROFILE)
    command_ids = load_command_ids(args.commands_dir)
    registries = {
        "os": load_registry_ids("operating-systems.yaml", "operating_systems"),
        "distros": load_registry_ids("distributions.yaml", "distributions"),
        "shells": load_registry_ids("shells.yaml", "shells"),
        "servers": load_registry_ids("server-platforms.yaml", "server_platforms"),
    }

    # First pass: collect task ids for cross-refs
    pending_task_ids: set[str] = set()
    if tasks_dir.is_dir():
        for path in tasks_dir.glob("*.yaml"):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if isinstance(raw, dict) and isinstance(raw.get("id"), str):
                pending_task_ids.add(raw["id"])

    tasks = validate_tree(
        errors,
        tasks_dir,
        kind="task",
        validator=task_validator,
        command_ids=command_ids,
        task_ids=pending_task_ids,
        registries=registries,
    )
    profiles = validate_tree(
        errors,
        profiles_dir,
        kind="profile",
        validator=profile_validator,
        command_ids=command_ids,
        task_ids=pending_task_ids,
        registries=registries,
    )

    if tasks_dir.is_dir() and not tasks and not any("YAML parse" in e or "schema" in e for e in errors):
        # empty dir with no yaml is suspicious post-Faz 8
        if args.require:
            errors.append(f"{tasks_dir}: no task YAML files")
    if profiles_dir.is_dir() and not profiles and args.require:
        errors.append(f"{profiles_dir}: no profile YAML files")

    if errors:
        print(f"FAIL: {len(errors)} tasks/profiles issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(tasks)} tasks, {len(profiles)} profiles validated "
        f"(catalog index via build_catalog.py)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
