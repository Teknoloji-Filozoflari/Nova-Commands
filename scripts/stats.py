#!/usr/bin/env python3
"""Print bank statistics (category counts, verification mix, risk mix)."""

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
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cats[data["category"]] += 1
        ver[data["verification"]["status"]] += 1
        risk[data["risk"]] += 1
    print(f"commands: {len(files)}")
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
