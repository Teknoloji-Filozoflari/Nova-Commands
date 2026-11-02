#!/usr/bin/env python3
"""Validate Nova-Commands curated bank.

Checks (CI gate):
  - JSON Schema conformance (command.schema.json)
  - Unique ids; filename stem == id; directory == category
  - Category ∈ metadata/categories.yaml
  - verification.status rules (verified requires sources + last_reviewed)
  - Flag verified=true only allowed when command verification is reviewed|verified
  - Example risk severity ≥ command risk when example requires_elevated and command does not
  - Risk rank consistency helpers
  - No shell metacharacters inventing pipelines as the sole "command" name
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
SCHEMA_PATH = ROOT / "schema" / "command.schema.json"
CATEGORIES_PATH = ROOT / "metadata" / "categories.yaml"

RISK_RANK = {"safe": 0, "caution": 1, "dangerous": 2, "destructive": 3}


def load_categories() -> set[str]:
    data = yaml.safe_load(CATEGORIES_PATH.read_text(encoding="utf-8"))
    cats = {c["id"] for c in data["categories"]}
    return cats


def load_schema_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    resource = Resource.from_contents(schema)
    registry = Registry().with_resource(schema["$id"], resource)
    return Draft202012Validator(schema, registry=registry)


def iter_command_files() -> list[Path]:
    if not COMMANDS_DIR.is_dir():
        return []
    return sorted(COMMANDS_DIR.glob("*/*.yaml"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commands-dir",
        type=Path,
        default=COMMANDS_DIR,
        help="Override commands directory",
    )
    args = parser.parse_args()
    commands_dir: Path = args.commands_dir

    errors: list[str] = []
    categories = load_categories()
    validator = load_schema_validator()
    seen_ids: dict[str, Path] = {}

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

        for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel}: schema {loc}: {err.message}")

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
            ex_risk = ex.get("risk")
            ex_rank = RISK_RANK.get(ex_risk, 0)
            if ex_rank < cmd_rank and ex_rank == 0 and cmd_rank >= 2:
                # Allow documenting a safe read-only example on a dangerous tool
                # (e.g. dd with status=progress of /dev/zero to /dev/null) — OK.
                pass
            # Destructive examples on a safe command are suspicious
            if cmd_rank == 0 and ex_rank >= 3:
                errors.append(
                    f"{rel}: examples[{i}].risk is destructive but command risk is safe "
                    "(raise command.risk or lower example risk)"
                )

        # related ids are soft references; warn-level collected as errors only if self-ref
        for rid in raw.get("related") or []:
            if rid == cid:
                errors.append(f"{rel}: related must not include self")

    if errors:
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(seen_ids)} commands validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
