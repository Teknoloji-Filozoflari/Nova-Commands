#!/usr/bin/env python3
"""Build catalog.json, search-index.json, and manifest.json (deterministic SHA)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
CONCEPTS_DIR = ROOT / "concepts"
TASKS_DIR = ROOT / "tasks"
PROFILES_DIR = ROOT / "profiles"
META = ROOT / "metadata"
OUT_CATALOG = META / "catalog.json"
OUT_SEARCH = META / "search-index.json"
OUT_MANIFEST = META / "manifest.json"

CATALOG_SCHEMA_VERSION = 2

# Pedagogical level — independent of risk. Missing source → explicit unspecified.
LEARNING_LEVELS = frozenset({"beginner", "intermediate", "advanced", "unspecified"})
EXAMPLE_DIFFICULTIES = frozenset({"beginner", "intermediate", "advanced"})


def normalize_learning_level(command: dict) -> dict:
    """Ensure learning_level is explicit; never derive from risk."""
    level = command.get("learning_level")
    if level is None or level == "":
        command["learning_level"] = "unspecified"
    elif level not in LEARNING_LEVELS:
        raise SystemExit(
            f"command {command.get('id')!r}: invalid learning_level {level!r}"
        )
    # Example difficulty stays optional; do not invent from example risk.
    for i, ex in enumerate(command.get("examples") or []):
        if not isinstance(ex, dict):
            continue
        diff = ex.get("difficulty")
        if diff is None or diff == "":
            continue
        if diff not in EXAMPLE_DIFFICULTIES:
            raise SystemExit(
                f"command {command.get('id')!r}: examples[{i}].difficulty "
                f"invalid {diff!r}"
            )
    return command


def load_yaml_dir_commands(commands_dir: Path) -> list[dict]:
    items: list[dict] = []
    for path in sorted(commands_dir.glob("*/*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: root must be mapping")
        items.append(normalize_learning_level(data))
    items.sort(key=lambda c: c.get("id", ""))
    return items


def load_yaml_flat(directory: Path) -> list[dict]:
    items: list[dict] = []
    if not directory.is_dir():
        return items
    for path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: root must be mapping")
        items.append(data)
    items.sort(key=lambda c: c.get("id", ""))
    return items


def load_concepts(concepts_dir: Path) -> list[dict]:
    return load_yaml_flat(concepts_dir)


def load_tasks(tasks_dir: Path) -> list[dict]:
    return load_yaml_flat(tasks_dir)


def load_profiles(profiles_dir: Path) -> list[dict]:
    return load_yaml_flat(profiles_dir)


def registry_count(yaml_name: str, list_key: str) -> int:
    path = META / yaml_name
    if not path.is_file():
        return 0
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get(list_key) or []
    return len(entries) if isinstance(entries, list) else 0


def canonical_bytes(obj: Any) -> bytes:
    """Stable JSON encoding for hashing (sorted keys, no timestamp)."""
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def content_sha256(
    commands: list[dict],
    concepts: list[dict],
    tasks: list[dict],
    profiles: list[dict],
) -> str:
    payload = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-bank",
        "commands": commands,
        "concepts": concepts,
        "tasks": tasks,
        "profiles": profiles,
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _uniq_sorted(values: list[str]) -> list[str]:
    return sorted({v for v in values if isinstance(v, str) and v})


def task_platforms(task: dict) -> list[str]:
    out: list[str] = []
    for impl in task.get("implementations") or []:
        if not isinstance(impl, dict):
            continue
        for key in ("platforms", "operating_systems"):
            for item in impl.get(key) or []:
                if isinstance(item, str):
                    out.append(item)
    return _uniq_sorted(out)


def task_command_ids(task: dict) -> list[str]:
    out: list[str] = []
    for impl in task.get("implementations") or []:
        if not isinstance(impl, dict):
            continue
        for cmd in impl.get("commands") or []:
            if isinstance(cmd, str):
                out.append(cmd)
    return _uniq_sorted(out)


def build_search_index(
    commands: list[dict],
    concepts: list[dict],
    tasks: list[dict],
    profiles: list[dict],
) -> dict:
    entries = []
    for c in commands:
        entries.append(
            {
                "type": "command",
                "id": c["id"],
                "name": c.get("name"),
                "category": c.get("category"),
                "kind": c.get("kind"),
                "risk": c.get("risk"),
                "learning_level": c.get("learning_level", "unspecified"),
                "platforms": c.get("platforms") or [],
                "verification": (c.get("verification") or {}).get("status"),
                "tags": c.get("tags") or [],
                "summary": c.get("summary") or {},
                "intent": c.get("intent") or {},
                "concepts": (c.get("nova") or {}).get("concepts") or [],
            }
        )
    for concept in concepts:
        entries.append(
            {
                "type": "concept",
                "id": concept["id"],
                "difficulty": concept.get("difficulty"),
                "tags": concept.get("tags") or [],
                "title": concept.get("title") or {},
                "summary": concept.get("summary") or {},
                "related_commands": concept.get("related_commands") or [],
            }
        )
    for task in tasks:
        entries.append(
            {
                "type": "task",
                "id": task["id"],
                "name": task.get("name") or {},
                "category": task.get("category"),
                "platforms": task_platforms(task),
                "verification": (task.get("verification") or {}).get("status"),
                "tags": task.get("tags") or [],
                "summary": task.get("summary") or {},
                "intent": task.get("intent") or {},
                "related_commands": task_command_ids(task),
            }
        )
    for profile in profiles:
        entries.append(
            {
                "type": "profile",
                "id": profile["id"],
                "name": profile.get("name") or {},
                "operating_systems": profile.get("operating_systems") or [],
                "distributions": profile.get("distributions") or [],
                "server_platforms": profile.get("server_platforms") or [],
                "verification": (profile.get("verification") or {}).get("status"),
                "tags": profile.get("tags") or [],
                "summary": profile.get("summary") or {},
                "related_commands": profile.get("related_commands") or [],
                "related_tasks": profile.get("related_tasks") or [],
            }
        )
    entries.sort(key=lambda e: (e["type"], e["id"]))
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-search-index",
        "entry_count": len(entries),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_CATALOG)
    parser.add_argument("--search-out", type=Path, default=OUT_SEARCH)
    parser.add_argument("--manifest-out", type=Path, default=OUT_MANIFEST)
    parser.add_argument("--commands-dir", type=Path, default=COMMANDS_DIR)
    parser.add_argument("--concepts-dir", type=Path, default=CONCEPTS_DIR)
    parser.add_argument("--tasks-dir", type=Path, default=TASKS_DIR)
    parser.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)
    args = parser.parse_args()

    commands = load_yaml_dir_commands(args.commands_dir)
    concepts = load_concepts(args.concepts_dir)
    tasks = load_tasks(args.tasks_dir)
    profiles = load_profiles(args.profiles_dir)
    digest = content_sha256(commands, concepts, tasks, profiles)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    os_count = registry_count("operating-systems.yaml", "operating_systems")
    pm_count = registry_count("package-managers.yaml", "package_managers")

    catalog = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-bank",
        "generated_at": generated_at,
        "content_sha256": digest,
        "command_count": len(commands),
        "concept_count": len(concepts),
        "task_count": len(tasks),
        "profile_count": len(profiles),
        "commands": commands,
        "concepts": concepts,
        "tasks": tasks,
        "profiles": profiles,
    }

    search_index = build_search_index(commands, concepts, tasks, profiles)
    search_index["content_sha256"] = digest
    search_index["generated_at"] = generated_at
    search_index["command_count"] = len(commands)
    search_index["concept_count"] = len(concepts)
    search_index["task_count"] = len(tasks)
    search_index["profile_count"] = len(profiles)

    manifest = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-manifest",
        "generated_at": generated_at,
        "content_sha256": digest,
        "command_count": len(commands),
        "concept_count": len(concepts),
        "task_count": len(tasks),
        "profile_count": len(profiles),
        "operating_system_count": os_count,
        "package_manager_count": pm_count,
        "artifacts": {
            "catalog": "metadata/catalog.json",
            "search_index": "metadata/search-index.json",
        },
    }

    for path, obj in (
        (args.out, catalog),
        (args.search_out, search_index),
        (args.manifest_out, manifest),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(
        f"wrote {args.out} ({len(commands)} commands, {len(concepts)} concepts, "
        f"{len(tasks)} tasks, {len(profiles)} profiles); "
        f"sha256={digest[:12]}…"
    )
    print(f"wrote {args.search_out}")
    print(f"wrote {args.manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
