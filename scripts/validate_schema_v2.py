#!/usr/bin/env python3
"""Validate live command schema v2 load + stub schema fixtures (Faz 3).

Live bank under commands/ validates against command.schema.json (v2) via
validate_catalog.py. This script:

  - Confirms command.schema.json (live v2) and archived command.schema.v1.json load
  - Soft-checks task/profile/compatibility schemas + fixtures/schema-v2/*
  - Optionally re-checks command-* fixtures against live command.schema.json

Does NOT demote verification statuses or invent platform claims.
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
SCHEMA = ROOT / "schema"
FIXTURES = ROOT / "fixtures" / "schema-v2"
META = ROOT / "metadata"

SCHEMA_FILES = [
    "command.schema.json",  # live v2
    "command.schema.v2.json",  # twin ($id differs)
    "task.schema.json",
    "profile.schema.json",
    "compatibility.schema.json",
]

# (glob pattern under fixtures/, schema filename)
FIXTURE_MAP: list[tuple[str, str]] = [
    ("command-*.yaml", "command.schema.json"),
    ("task-*.yaml", "task.schema.json"),
    ("profile-*.yaml", "profile.schema.json"),
    ("compatibility-*.yaml", "compatibility.schema.json"),
]


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


def check_command_fixture_refs(
    errors: list[str], rel: str, raw: dict[str, Any], ids: dict[str, set[str]]
) -> None:
    for os_id in raw.get("operating_systems") or []:
        if ids["os"] and os_id not in ids["os"]:
            errors.append(f"{rel}: operating_systems unknown id {os_id!r}")
    for sh in raw.get("shells") or []:
        legacy = {"any", "sh", "bash", "zsh", "fish"}
        if ids["shells"] and sh not in ids["shells"] and sh not in legacy:
            errors.append(f"{rel}: shells unknown id {sh!r}")
    for pref in raw.get("package_refs") or []:
        if not isinstance(pref, dict):
            continue
        mgr = pref.get("manager")
        if ids["pm"] and mgr not in ids["pm"]:
            errors.append(f"{rel}: package_refs.manager unknown id {mgr!r}")
        for dist in pref.get("distributions") or []:
            if ids["distros"] and dist not in ids["distros"]:
                errors.append(
                    f"{rel}: package_refs.distributions unknown id {dist!r}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=FIXTURES,
        help="Override fixtures directory",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=SCHEMA,
        help="Override schema directory",
    )
    args = parser.parse_args()
    fixtures_dir: Path = args.fixtures_dir
    schema_dir: Path = args.schema_dir

    errors: list[str] = []
    validators: dict[str, Draft202012Validator] = {}

    for name in SCHEMA_FILES:
        path = schema_dir / name
        rel = str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
        if not path.is_file():
            errors.append(f"missing schema {rel}")
            continue
        try:
            validators[name] = load_schema_validator(path)
        except Exception as exc:  # noqa: BLE001 — surface schema errors
            errors.append(f"{rel}: invalid JSON Schema: {exc}")

    live = schema_dir / "command.schema.json"
    v2_twin = schema_dir / "command.schema.v2.json"
    v1_arch = schema_dir / "command.schema.v1.json"
    if not v1_arch.is_file():
        errors.append("missing schema/command.schema.v1.json (archived v1)")
    if live.is_file() and v2_twin.is_file():
        live_doc = json.loads(live.read_text(encoding="utf-8"))
        twin_doc = json.loads(v2_twin.read_text(encoding="utf-8"))
        if live_doc.get("$id") == twin_doc.get("$id"):
            errors.append(
                "command.schema.json and command.schema.v2.json must have distinct $id"
            )
        if "windows" not in live_doc["properties"]["platforms"]["items"]["enum"]:
            errors.append("live command.schema.json must include platforms windows")
        if "package_refs" not in live_doc["properties"]:
            errors.append("live command.schema.json must include package_refs")
        # Core property sets must match (ignore $id/title/description drift).
        if set(live_doc.get("properties", {})) != set(twin_doc.get("properties", {})):
            errors.append(
                "command.schema.json and .v2.json property keys drifted — keep in sync"
            )

    if v1_arch.is_file():
        v1_doc = json.loads(v1_arch.read_text(encoding="utf-8"))
        if "windows" in v1_doc["properties"]["platforms"]["items"]["enum"]:
            errors.append("archived v1 must not list windows (historical)")
        if "package_refs" in v1_doc["properties"]:
            errors.append("archived v1 must not define package_refs")

    ids = {
        "os": load_registry_ids("operating-systems.yaml", "operating_systems"),
        "distros": load_registry_ids("distributions.yaml", "distributions"),
        "shells": load_registry_ids("shells.yaml", "shells"),
        "pm": load_registry_ids("package-managers.yaml", "package_managers"),
    }

    fixture_count = 0
    if not fixtures_dir.is_dir():
        errors.append(f"missing fixtures dir {fixtures_dir}")
    else:
        for pattern, schema_name in FIXTURE_MAP:
            validator = validators.get(schema_name)
            for path in sorted(fixtures_dir.glob(pattern)):
                fixture_count += 1
                rel = str(
                    path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                )
                try:
                    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                except yaml.YAMLError as exc:
                    errors.append(f"{rel}: YAML parse error: {exc}")
                    continue
                if not isinstance(raw, dict):
                    errors.append(f"{rel}: root must be a mapping")
                    continue
                if validator is None:
                    errors.append(f"{rel}: no validator for {schema_name}")
                    continue
                for err in sorted(
                    validator.iter_errors(raw), key=lambda e: list(e.path)
                ):
                    loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
                    errors.append(f"{rel}: schema {loc}: {err.message}")

                if schema_name == "command.schema.json":
                    check_command_fixture_refs(errors, rel, raw, ids)
                    status = (raw.get("verification") or {}).get("status")
                    if status == "verified":
                        errors.append(
                            f"{rel}: fixtures must not use verification.status=verified"
                        )

    if errors:
        print(f"FAIL: {len(errors)} schema-v2 issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK: schema v2 live + stubs — {len(SCHEMA_FILES)} schemas, "
        f"{fixture_count} fixtures (bank on command.schema.json v2)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
