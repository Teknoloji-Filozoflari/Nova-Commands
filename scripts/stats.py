#!/usr/bin/env python3
"""Print bank statistics (category counts, verification mix, risk mix, concepts)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    files = sorted((ROOT / "commands").glob("*/*.yaml"))
    cats: Counter[str] = Counter()
    ver: Counter[str] = Counter()
    risk: Counter[str] = Counter()
    with_concepts = 0
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cats[data["category"]] += 1
        ver[data["verification"]["status"]] += 1
        risk[data["risk"]] += 1
        if (data.get("nova") or {}).get("concepts"):
            with_concepts += 1
    concept_files = sorted((ROOT / "concepts").glob("*.yaml"))
    task_files = sorted((ROOT / "tasks").glob("*.yaml")) if (ROOT / "tasks").is_dir() else []
    profile_files = (
        sorted((ROOT / "profiles").glob("*.yaml")) if (ROOT / "profiles").is_dir() else []
    )
    print(f"commands: {len(files)}")
    print(f"commands with nova.concepts: {with_concepts}")
    print(f"concept articles: {len(concept_files)}")
    for path in concept_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        print(f"  - {data['id']} [{data['verification']['status']}/{data['difficulty']}]")
    print(f"tasks: {len(task_files)}")
    for path in task_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        print(f"  - {data['id']} [{data['verification']['status']}/{data.get('category')}]")
    print(f"profiles: {len(profile_files)}")
    for path in profile_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        print(f"  - {data['id']} [{data['verification']['status']}]")
    print("by category:")
    for k, v in sorted(cats.items()):
        print(f"  {k}: {v}")
    print("by verification:")
    for k, v in sorted(ver.items()):
        print(f"  {k}: {v}")
    print("by risk:")
    for k, v in sorted(risk.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
