#!/usr/bin/env python3
"""Simple offline search over the curated bank (commands + concepts + tasks + profiles).

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

ENTRY_TYPES = ("command", "concept", "task", "profile")


def _task_platforms(task: dict) -> list[str]:
    out: list[str] = []
    for impl in task.get("implementations") or []:
        if not isinstance(impl, dict):
            continue
        for key in ("platforms", "operating_systems"):
            for item in impl.get(key) or []:
                if isinstance(item, str):
                    out.append(item)
    return sorted(set(out))


def _task_commands(task: dict) -> list[str]:
    out: list[str] = []
    for impl in task.get("implementations") or []:
        if not isinstance(impl, dict):
            continue
        for cmd in impl.get("commands") or []:
            if isinstance(cmd, str):
                out.append(cmd)
    return sorted(set(out))


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
    tasks_dir = ROOT / "tasks"
    if tasks_dir.is_dir():
        for path in sorted(tasks_dir.glob("*.yaml")):
            t = yaml.safe_load(path.read_text(encoding="utf-8"))
            entries.append(
                {
                    "type": "task",
                    "id": t["id"],
                    "name": t.get("name") or {},
                    "category": t.get("category"),
                    "platforms": _task_platforms(t),
                    "tags": t.get("tags") or [],
                    "summary": t.get("summary") or {},
                    "intent": t.get("intent") or {},
                    "related_commands": _task_commands(t),
                }
            )
    profiles_dir = ROOT / "profiles"
    if profiles_dir.is_dir():
        for path in sorted(profiles_dir.glob("*.yaml")):
            p = yaml.safe_load(path.read_text(encoding="utf-8"))
            entries.append(
                {
                    "type": "profile",
                    "id": p["id"],
                    "name": p.get("name") or {},
                    "tags": p.get("tags") or [],
                    "summary": p.get("summary") or {},
                    "operating_systems": p.get("operating_systems") or [],
                    "related_commands": p.get("related_commands") or [],
                    "related_tasks": p.get("related_tasks") or [],
                }
            )
    return entries


def score(entry: dict, query: str, lang: str, prefer_os: str | None) -> int:
    q = query.lower().strip()
    if not q:
        return 0
    s = 0
    eid = entry.get("id", "").lower()
    name_field = entry.get("name")
    if isinstance(name_field, dict):
        name = (name_field.get(lang) or name_field.get("en") or eid).lower()
    else:
        name = (name_field or eid).lower()
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
    for related in entry.get("related_commands") or []:
        if q in related.lower():
            s += 6
    for related in entry.get("related_tasks") or []:
        if q in related.lower():
            s += 6
    et = entry.get("type")
    if et == "concept":
        s += 1  # slight boost so concepts surface for topical queries
    elif et == "task":
        s += 2  # intent records should rank for natural-language goals
    elif et == "profile":
        s += 1
    if prefer_os:
        platforms = {
            *(entry.get("platforms") or []),
            *(entry.get("operating_systems") or []),
        }
        if prefer_os in platforms:
            s += 20
    return s


def _display_label(entry: dict, lang: str) -> str:
    et = entry.get("type", "?")
    if et == "command":
        summary = (entry.get("summary") or {}).get(lang, "")
        return (
            f"cmd  {entry['id']:24s}  "
            f"[{entry.get('category')}/{entry.get('risk')}]  {summary}"
        )
    if et == "task":
        name = (entry.get("name") or {}).get(lang, "")
        summary = (entry.get("summary") or {}).get(lang, "")
        return f"task  {entry['id']:24s}  [{entry.get('category')}]  {name or summary}"
    if et == "profile":
        name = (entry.get("name") or {}).get(lang, "")
        summary = (entry.get("summary") or {}).get(lang, "")
        return f"profile  {entry['id']:20s}  {name or summary}"
    title = (entry.get("title") or entry.get("summary") or {}).get(lang, "")
    return f"concept  {entry['id']:20s}  {title}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--lang", choices=["tr", "en"], default="tr")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--type",
        choices=["all", *ENTRY_TYPES],
        default="all",
    )
    parser.add_argument(
        "--os",
        dest="prefer_os",
        default=None,
        help="Boost entries matching this operating_system / platform id "
        "(e.g. linux, windows, macos, freebsd)",
    )
    args = parser.parse_args()

    ranked = []
    for entry in load_entries():
        if args.type != "all" and entry.get("type") != args.type:
            continue
        sc = score(entry, args.query, args.lang, args.prefer_os)
        if sc:
            ranked.append((sc, entry))
    ranked.sort(key=lambda x: (-x[0], x[1].get("type", ""), x[1]["id"]))
    if not ranked:
        print("no hits", file=sys.stderr)
        return 1
    for sc, entry in ranked[: args.limit]:
        print(f"{sc:3d}  {_display_label(entry, args.lang)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
