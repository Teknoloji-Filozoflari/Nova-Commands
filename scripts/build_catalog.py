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
META = ROOT / "metadata"
OUT_CATALOG = META / "catalog.json"
OUT_SEARCH = META / "search-index.json"
OUT_MANIFEST = META / "manifest.json"


def load_yaml_dir_commands(commands_dir: Path) -> list[dict]:
    items: list[dict] = []
    for path in sorted(commands_dir.glob("*/*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: root must be mapping")
        items.append(data)
    items.sort(key=lambda c: c.get("id", ""))
    return items


def load_concepts(concepts_dir: Path) -> list[dict]:
    items: list[dict] = []
    if not concepts_dir.is_dir():
        return items
    for path in sorted(concepts_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: root must be mapping")
        items.append(data)
    items.sort(key=lambda c: c.get("id", ""))
    return items


def canonical_bytes(obj: Any) -> bytes:
    """Stable JSON encoding for hashing (sorted keys, no timestamp)."""
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


CATALOG_SCHEMA_VERSION = 2


def content_sha256(commands: list[dict], concepts: list[dict]) -> str:
    payload = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-bank",
        "commands": commands,
        "concepts": concepts,
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def build_search_index(commands: list[dict], concepts: list[dict]) -> dict:
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
    args = parser.parse_args()

    commands = load_yaml_dir_commands(args.commands_dir)
    concepts = load_concepts(args.concepts_dir)
    digest = content_sha256(commands, concepts)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-bank",
        "generated_at": generated_at,
        "content_sha256": digest,
        "command_count": len(commands),
        "concept_count": len(concepts),
        "commands": commands,
        "concepts": concepts,
    }

    search_index = build_search_index(commands, concepts)
    search_index["content_sha256"] = digest
    search_index["generated_at"] = generated_at

    manifest = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "kind": "nova-commands-manifest",
        "generated_at": generated_at,
        "content_sha256": digest,
        "command_count": len(commands),
        "concept_count": len(concepts),
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
        f"wrote {args.out} ({len(commands)} commands, {len(concepts)} concepts); "
        f"sha256={digest[:12]}…"
    )
    print(f"wrote {args.search_out}")
    print(f"wrote {args.manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
