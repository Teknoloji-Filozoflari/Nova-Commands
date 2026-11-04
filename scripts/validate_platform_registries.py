#!/usr/bin/env python3
"""Soft-validate cross-platform metadata registries (Faz 1).

Checks registry YAML against JSON Schema and internal cross-references:
  OS ← distributions / shells / PMs / execution-envs / server-platforms
  distributions ← PM.distributions, distribution.parent/id_like, server based_on
  package-managers ← distribution.package_managers
  support-levels ← *.support_level

Does NOT require commands/concepts to reference registries yet (Faz 2+).
Does NOT migrate commands or bump catalog schema_version.
Missing optional dirs (tasks/, profiles/) are ignored here; Faz 8+ uses
scripts/validate_tasks_profiles.py when those trees exist.
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
META = ROOT / "metadata"
SCHEMA = ROOT / "schema"

REGISTRIES: list[tuple[str, str, str]] = [
    # (yaml filename, schema filename, list key)
    ("support-levels.yaml", "support-level.schema.json", "support_levels"),
    ("operating-systems.yaml", "operating-system.schema.json", "operating_systems"),
    ("distributions.yaml", "distribution.schema.json", "distributions"),
    ("shells.yaml", "shell.schema.json", "shells"),
    ("package-managers.yaml", "package-manager.schema.json", "package_managers"),
    ("architectures.yaml", "architecture.schema.json", "architectures"),
    ("execution-environments.yaml", "execution-environment.schema.json", "execution_environments"),
    ("server-platforms.yaml", "server-platform.schema.json", "server_platforms"),
    ("cloud-providers.yaml", "cloud-provider.schema.json", "cloud_providers"),
]


def load_schema_validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    resource = Resource.from_contents(schema)
    registry = Registry().with_resource(schema["$id"], resource)
    return Draft202012Validator(schema, registry=registry)


def unique_ids(errors: list[str], rel: str, entries: list[dict], key: str = "id") -> set[str]:
    seen: dict[str, int] = {}
    ids: set[str] = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {key}[{i}] must be a mapping")
            continue
        eid = entry.get("id")
        if not isinstance(eid, str):
            errors.append(f"{rel}: entry[{i}] missing id")
            continue
        if eid in seen:
            errors.append(f"{rel}: duplicate id {eid!r} (indices {seen[eid]} and {i})")
        else:
            seen[eid] = i
            ids.add(eid)
    return ids


def ref_check(
    errors: list[str],
    rel: str,
    entry_id: str,
    field: str,
    value: Any,
    allowed: set[str],
    *,
    multi: bool = False,
) -> None:
    if value is None:
        return
    values = value if multi else [value]
    if not isinstance(values, list):
        errors.append(f"{rel}: {entry_id}.{field} must be a list" if multi else f"{rel}: {entry_id}.{field} invalid")
        return
    for item in values:
        if item not in allowed:
            errors.append(
                f"{rel}: {entry_id}.{field} unknown ref {item!r} "
                f"(not in registry; known={len(allowed)})"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=META,
        help="Override metadata directory",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=SCHEMA,
        help="Override schema directory",
    )
    args = parser.parse_args()
    meta_dir: Path = args.metadata_dir
    schema_dir: Path = args.schema_dir

    errors: list[str] = []
    loaded: dict[str, list[dict]] = {}
    id_sets: dict[str, set[str]] = {}

    for yaml_name, schema_name, list_key in REGISTRIES:
        path = meta_dir / yaml_name
        rel = str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
        schema_path = schema_dir / schema_name
        if not path.is_file():
            errors.append(f"{rel}: missing platform registry (required for Faz 1+)")
            continue
        if not schema_path.is_file():
            errors.append(f"{schema_path}: missing schema for {yaml_name}")
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {exc}")
            continue
        if not isinstance(raw, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue

        validator = load_schema_validator(schema_path)
        for err in sorted(validator.iter_errors(raw), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel}: schema {loc}: {err.message}")

        entries = raw.get(list_key) or []
        if not isinstance(entries, list):
            errors.append(f"{rel}: {list_key} must be a list")
            entries = []
        ids = unique_ids(errors, rel, entries)
        loaded[list_key] = [e for e in entries if isinstance(e, dict)]
        id_sets[list_key] = ids

        # Never invent verified: seed must stay skeleton|draft unless sources+review present.
        for entry in loaded[list_key]:
            status = entry.get("status")
            if status == "verified":
                # support-levels have no status; only entity registries
                errors.append(
                    f"{rel}: {entry.get('id')!r} status=verified is not allowed in "
                    "Faz 1 seed registries without an explicit human-review process "
                    "(use skeleton|draft)"
                )

    os_ids = id_sets.get("operating_systems", set())
    dist_ids = id_sets.get("distributions", set())
    pm_ids = id_sets.get("package_managers", set())
    support_ids = id_sets.get("support_levels", set())

    for entry in loaded.get("distributions", []):
        eid = entry.get("id", "?")
        ref_check(errors, "metadata/distributions.yaml", eid, "operating_system", entry.get("operating_system"), os_ids)
        ref_check(errors, "metadata/distributions.yaml", eid, "parent", entry.get("parent"), dist_ids)
        ref_check(errors, "metadata/distributions.yaml", eid, "id_like", entry.get("id_like"), dist_ids, multi=True)
        ref_check(
            errors,
            "metadata/distributions.yaml",
            eid,
            "package_managers",
            entry.get("package_managers"),
            pm_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/distributions.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("operating_systems", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/operating-systems.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("shells", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/shells.yaml",
            eid,
            "operating_systems",
            entry.get("operating_systems"),
            os_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/shells.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("package_managers", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/package-managers.yaml",
            eid,
            "operating_systems",
            entry.get("operating_systems"),
            os_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/package-managers.yaml",
            eid,
            "distributions",
            entry.get("distributions"),
            dist_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/package-managers.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("architectures", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/architectures.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("execution_environments", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/execution-environments.yaml",
            eid,
            "host_operating_systems",
            entry.get("host_operating_systems"),
            os_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/execution-environments.yaml",
            eid,
            "guest_operating_systems",
            entry.get("guest_operating_systems"),
            os_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/execution-environments.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("server_platforms", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/server-platforms.yaml",
            eid,
            "operating_systems",
            entry.get("operating_systems"),
            os_ids,
            multi=True,
        )
        ref_check(
            errors,
            "metadata/server-platforms.yaml",
            eid,
            "based_on_distribution",
            entry.get("based_on_distribution"),
            dist_ids,
        )
        ref_check(
            errors,
            "metadata/server-platforms.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    for entry in loaded.get("cloud_providers", []):
        eid = entry.get("id", "?")
        ref_check(
            errors,
            "metadata/cloud-providers.yaml",
            eid,
            "support_level",
            entry.get("support_level"),
            support_ids,
        )

    # Dual-concept reminder: registries are bank metadata, not PATH discovery.
    for optional in ("tasks", "profiles"):
        # Soft: absence is OK in Faz 1
        _ = (ROOT / optional).is_dir()

    if errors:
        print(f"FAIL: {len(errors)} platform-registry issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    counts = {k: len(v) for k, v in loaded.items()}
    summary = ", ".join(f"{k}={n}" for k, n in sorted(counts.items()))
    print(f"OK: platform registries validated ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
