#!/usr/bin/env python3
"""Simple offline search over the curated bank (name, tags, intent).

Does not search the local PATH — that is Nova's discovery side.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load() -> list[dict]:
    items = []
    for path in sorted((ROOT / "commands").glob("*/*.yaml")):
        items.append(yaml.safe_load(path.read_text(encoding="utf-8")))
    return items


def score(entry: dict, query: str, lang: str) -> int:
    q = query.lower().strip()
    if not q:
        return 0
    s = 0
    if entry.get("id", "").lower() == q or entry.get("name", "").lower() == q:
        s += 100
    if q in entry.get("id", "").lower() or q in entry.get("name", "").lower():
        s += 40
    for t in entry.get("tags") or []:
        if q in t:
            s += 15
    for phrase in (entry.get("intent") or {}).get(lang, []):
        pl = phrase.lower()
        if q == pl:
            s += 50
        elif q in pl or pl in q:
            s += 25
    summary = (entry.get("summary") or {}).get(lang, "").lower()
    if q in summary:
        s += 10
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--lang", choices=["tr", "en"], default="tr")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    ranked = []
    for entry in load():
        sc = score(entry, args.query, args.lang)
        if sc:
            ranked.append((sc, entry))
    ranked.sort(key=lambda x: (-x[0], x[1]["id"]))
    if not ranked:
        print("no hits", file=sys.stderr)
        return 1
    for sc, entry in ranked[: args.limit]:
        summary = entry["summary"][args.lang]
        print(f"{sc:3d}  {entry['id']:16s}  [{entry['category']}/{entry['risk']}]  {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
