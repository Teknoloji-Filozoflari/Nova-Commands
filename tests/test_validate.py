"""Tests for Nova-Commands validators and catalog build."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate_catalog.py"
BUILD = ROOT / "scripts" / "build_catalog.py"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_validate_passes_on_repo() -> None:
    proc = run(VALIDATE)
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout


def test_build_catalog_shape() -> None:
    out = ROOT / "metadata" / "catalog.json"
    proc = run(BUILD)
    assert proc.returncode == 0, proc.stderr
    cat = json.loads(out.read_text(encoding="utf-8"))
    assert cat["schema_version"] == 1
    assert cat["kind"] == "nova-commands-bank"
    assert cat["command_count"] == len(cat["commands"])
    assert cat["command_count"] >= 50
    ids = [c["id"] for c in cat["commands"]]
    assert len(ids) == len(set(ids))


def test_categories_match_schema_enum() -> None:
    schema = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    enum = set(schema["properties"]["category"]["enum"])
    cats = yaml.safe_load((ROOT / "metadata" / "categories.yaml").read_text())
    meta = {c["id"] for c in cats["categories"]}
    assert enum == meta


def test_no_verified_without_sources() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        ver = data["verification"]
        if ver["status"] == "verified":
            assert ver.get("sources"), path
            assert ver.get("last_reviewed"), path


def test_draft_flags_not_marked_verified() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data["verification"]["status"] != "draft":
            continue
        for flag in data.get("flags") or []:
            assert flag.get("verified") is not True, path


def test_dual_concept_docs_exist() -> None:
    for name in (
        "dual-concept.md",
        "local-discovery-contract.md",
        "nova-consumption.md",
        "safety.md",
    ):
        assert (ROOT / "docs" / name).is_file()


def test_filename_matches_id() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == path.stem
        assert data["category"] == path.parent.name
