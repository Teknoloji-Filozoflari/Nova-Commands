#!/usr/bin/env python3
"""CI helper: assert committed catalog/manifest/search-index digests match."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"


def main() -> int:
    cat = json.loads((META / "catalog.json").read_text(encoding="utf-8"))
    man = json.loads((META / "manifest.json").read_text(encoding="utf-8"))
    idx = json.loads((META / "search-index.json").read_text(encoding="utf-8"))
    sha = cat["content_sha256"]
    if not (sha == man["content_sha256"] == idx["content_sha256"]):
        print(
            "committed catalog/manifest/search-index content_sha256 mismatch",
            file=sys.stderr,
        )
        return 1
    out = Path.home() / "committed_sha.txt"
    out.write_text(sha, encoding="utf-8")
    print(f"committed_sha={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
