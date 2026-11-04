#!/usr/bin/env python3
"""Soft-validate command schema v2 + stub schemas (Faz 2).

Dual-path policy:
  - Live bank under commands/ continues to validate against command.schema.json (v1)
    via validate_catalog.py until Faz 3 migration.
  - This script soft-checks that v2/task/profile/compatibility schemas load as
    Draft 2020-12 and that fixtures/schema-v2/* YAML conforms.
  - Does NOT migrate commands, demote verified, bump catalog schema_version,
    or require commands/ to pass v2.

Optional cross-ref: when fixtures cite package_refs.manager / operating_systems /
shells, check ids exist in Faz 1 registries (warn-as-error for fixtures only).
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
    "command.schema.v2.json",
    "task.schema.json",
    "profile.schema.json",
    "compatibility.schema.json",
]

# (glob pattern under fixtures/, schema filename)
FIXTURE_MAP: list[tuple[str, str]] = [
    ("command-*.yaml", "command.schema.v2.json"),
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
        # v1 short names (sh/bash/any) are allowed alongside registry ids
        legacy = {
            "any",
            "sh",
            "bash",
            "zsh",
            "fish",
        }
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

    # Dual-path invariant: v1 schema must still exist and differ from v2 $id
    v1 = schema_dir / "command.schema.json"
    v2 = schema_dir / "command.schema.v2.json"
    if not v1.is_file():
        errors.append("missing schema/command.schema.json (v1 dual-path)")
    if v1.is_file() and v2.is_file():
        v1_id = json.loads(v1.read_text(encoding="utf-8")).get("$id")
        v2_id = json.loads(v2.read_text(encoding="utf-8")).get("$id")
        if v1_id == v2_id:
            errors.append("command.schema.json and .v2.json must have distinct $id")

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

                if schema_name == "command.schema.v2.json":
                    check_command_fixture_refs(errors, rel, raw, ids)
                    # Fixtures must stay draft — never fake verified
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
        f"OK: schema v2 soft-validate — {len(SCHEMA_FILES)} schemas, "
        f"{fixture_count} fixtures (bank remains on command.schema.json v1)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
