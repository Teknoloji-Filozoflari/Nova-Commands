#!/usr/bin/env python3
"""Build metadata/catalog.json from commands/**/*.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
OUT_PATH = ROOT / "metadata" / "catalog.json"


def load_commands(commands_dir: Path) -> list[dict]:
    items: list[dict] = []
    for path in sorted(commands_dir.glob("*/*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: root must be mapping")
        items.append(data)
    items.sort(key=lambda c: c.get("id", ""))
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    parser.add_argument("--commands-dir", type=Path, default=COMMANDS_DIR)
    args = parser.parse_args()

    commands = load_commands(args.commands_dir)
    catalog = {
        "schema_version": 1,
        "kind": "nova-commands-bank",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command_count": len(commands),
        "commands": commands,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.out} ({len(commands)} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
