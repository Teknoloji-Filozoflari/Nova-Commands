#!/usr/bin/env python3
"""CI helper: assert rebuild matches committed content_sha256 + catalog shape."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"


def main() -> int:
    committed = (Path.home() / "committed_sha.txt").read_text(encoding="utf-8").strip()
    cat = json.loads((META / "catalog.json").read_text(encoding="utf-8"))
    man = json.loads((META / "manifest.json").read_text(encoding="utf-8"))
    idx = json.loads((META / "search-index.json").read_text(encoding="utf-8"))

    assert cat["schema_version"] == 2
    assert cat["kind"] == "nova-commands-bank"
    assert cat["commands"], "catalog must contain commands"
    assert cat["concepts"], "catalog must contain concepts"
    ids = [c["id"] for c in cat["commands"]]
    assert len(ids) == len(set(ids))
    assert cat["command_count"] == len(ids)
    assert cat["concept_count"] == len(cat["concepts"])
    assert cat.get("task_count", 0) == len(cat.get("tasks") or [])
    assert cat.get("profile_count", 0) == len(cat.get("profiles") or [])
    assert man.get("task_count", 0) == cat.get("task_count", 0)
    assert man.get("profile_count", 0) == cat.get("profile_count", 0)
    assert idx.get("task_count", 0) == cat.get("task_count", 0)
    assert idx.get("profile_count", 0) == cat.get("profile_count", 0)
    entry_types = {e.get("type") for e in idx.get("entries") or []}
    if cat.get("task_count"):
        assert "task" in entry_types
    if cat.get("profile_count"):
        assert "profile" in entry_types
    assert len(cat["content_sha256"]) == 64
    assert man["content_sha256"] == cat["content_sha256"] == idx["content_sha256"]
    assert cat["content_sha256"] == committed, (
        "rebuild content_sha256 differs from committed artifacts; "
        "run scripts/build_catalog.py and commit metadata/"
    )
    verified_cmds = sum(
        1
        for c in cat["commands"]
        if c.get("verification", {}).get("status") == "verified"
    )
    verified_concepts = sum(
        1
        for c in cat["concepts"]
        if c.get("verification", {}).get("status") == "verified"
    )
    print(
        f"catalog ok: {len(ids)} commands, {cat['concept_count']} concepts, "
        f"{cat.get('task_count', 0)} tasks, {cat.get('profile_count', 0)} profiles, "
        f"sha={cat['content_sha256'][:12]}… "
        f"(verified commands={verified_cmds}, concepts={verified_concepts})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
