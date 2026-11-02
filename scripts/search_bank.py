#!/usr/bin/env python3
"""Simple offline search over the curated bank (commands + concepts).

Prefer metadata/search-index.json when present; else scan YAML.
Does not search the local PATH — that is Nova's discovery side.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "metadata" / "search-index.json"


def load_entries() -> list[dict]:
    if INDEX_PATH.is_file():
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        return list(data.get("entries") or [])
    entries: list[dict] = []
    for path in sorted((ROOT / "commands").glob("*/*.yaml")):
        c = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries.append(
            {
                "type": "command",
                "id": c["id"],
                "name": c.get("name"),
                "category": c.get("category"),
                "risk": c.get("risk"),
                "tags": c.get("tags") or [],
                "summary": c.get("summary") or {},
                "intent": c.get("intent") or {},
                "concepts": (c.get("nova") or {}).get("concepts") or [],
            }
        )
    for path in sorted((ROOT / "concepts").glob("*.yaml")):
        c = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries.append(
            {
                "type": "concept",
                "id": c["id"],
                "tags": c.get("tags") or [],
                "title": c.get("title") or {},
                "summary": c.get("summary") or {},
            }
        )
    return entries


def score(entry: dict, query: str, lang: str) -> int:
    q = query.lower().strip()
    if not q:
        return 0
    s = 0
    eid = entry.get("id", "").lower()
    name = (entry.get("name") or entry.get("id") or "").lower()
    if eid == q or name == q:
        s += 100
    if q in eid or q in name:
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
    title = (entry.get("title") or {}).get(lang, "").lower()
    if q in title:
        s += 20
    for concept in entry.get("concepts") or []:
        if q in concept:
            s += 8
    if entry.get("type") == "concept":
        s += 1  # slight boost so concepts surface for topical queries
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--lang", choices=["tr", "en"], default="tr")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--type",
        choices=["all", "command", "concept"],
        default="all",
    )
    args = parser.parse_args()

    ranked = []
    for entry in load_entries():
        if args.type != "all" and entry.get("type") != args.type:
            continue
        sc = score(entry, args.query, args.lang)
        if sc:
            ranked.append((sc, entry))
    ranked.sort(key=lambda x: (-x[0], x[1].get("type", ""), x[1]["id"]))
    if not ranked:
        print("no hits", file=sys.stderr)
        return 1
    for sc, entry in ranked[: args.limit]:
        et = entry.get("type", "?")
        if et == "command":
            summary = (entry.get("summary") or {}).get(args.lang, "")
            print(
                f"{sc:3d}  cmd  {entry['id']:24s}  "
                f"[{entry.get('category')}/{entry.get('risk')}]  {summary}"
            )
        else:
            title = (entry.get("title") or entry.get("summary") or {}).get(
                args.lang, ""
            )
            print(f"{sc:3d}  concept  {entry['id']:20s}  {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
