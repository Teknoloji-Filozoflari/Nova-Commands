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


def test_build_catalog_shape_and_sha() -> None:
    out = ROOT / "metadata" / "catalog.json"
    search = ROOT / "metadata" / "search-index.json"
    manifest = ROOT / "metadata" / "manifest.json"
    proc = run(BUILD)
    assert proc.returncode == 0, proc.stderr
    cat = json.loads(out.read_text(encoding="utf-8"))
    assert cat["schema_version"] == 1
    assert cat["kind"] == "nova-commands-bank"
    assert cat["command_count"] == len(cat["commands"])
    assert cat["concept_count"] == len(cat["concepts"])
    assert cat["command_count"] >= 50
    assert cat["concept_count"] >= 7
    assert len(cat["content_sha256"]) == 64
    ids = [c["id"] for c in cat["commands"]]
    assert len(ids) == len(set(ids))

    man = json.loads(manifest.read_text(encoding="utf-8"))
    idx = json.loads(search.read_text(encoding="utf-8"))
    assert man["kind"] == "nova-commands-manifest"
    assert idx["kind"] == "nova-commands-search-index"
    assert man["content_sha256"] == cat["content_sha256"] == idx["content_sha256"]


def test_content_sha_is_deterministic() -> None:
    run(BUILD)
    sha1 = json.loads((ROOT / "metadata" / "manifest.json").read_text())[
        "content_sha256"
    ]
    run(BUILD)
    sha2 = json.loads((ROOT / "metadata" / "manifest.json").read_text())[
        "content_sha256"
    ]
    assert sha1 == sha2


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
    for path in (ROOT / "concepts").glob("*.yaml"):
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
        "NOVA_INTEGRATION.md",
        "safety.md",
    ):
        assert (ROOT / "docs" / name).is_file()


def test_filename_matches_id() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == path.stem
        assert data["category"] == path.parent.name


def test_concept_articles_match_registry() -> None:
    registry = yaml.safe_load(
        (ROOT / "metadata" / "concepts.yaml").read_text(encoding="utf-8")
    )
    reg_ids = {c["id"] for c in registry["concepts"]}
    for path in (ROOT / "concepts").glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == path.stem
        assert data["kind"] == "nova-commands-concept"
        assert data["id"] in reg_ids
        assert data["title"]["tr"].strip() and data["title"]["en"].strip()
        assert data["body"]["tr"].strip() and data["body"]["en"].strip()


def test_i18n_summary_description_present() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for field in ("summary", "description"):
            for lang in ("tr", "en"):
                assert data[field][lang].strip(), path
        for lang in ("tr", "en"):
            assert data["intent"][lang], path
