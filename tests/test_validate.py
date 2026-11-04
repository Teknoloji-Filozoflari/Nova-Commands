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
        "DATA_SCHEMA.md",
        "PLATFORM_SUPPORT.md",
    ):
        assert (ROOT / "docs" / name).is_file()


def test_community_and_ci_files_exist() -> None:
    required = [
        ROOT / "SECURITY.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
        ROOT / ".github" / "dependabot.yml",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "new-command.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "category.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "translation.yml",
    ]
    for path in required:
        assert path.is_file(), path


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


PLATFORM_VALIDATE = ROOT / "scripts" / "validate_platform_registries.py"

PLATFORM_FILES = [
    ("operating-systems.yaml", "operating_systems", "operating-system.schema.json"),
    ("distributions.yaml", "distributions", "distribution.schema.json"),
    ("shells.yaml", "shells", "shell.schema.json"),
    ("package-managers.yaml", "package_managers", "package-manager.schema.json"),
    ("architectures.yaml", "architectures", "architecture.schema.json"),
    ("execution-environments.yaml", "execution_environments", "execution-environment.schema.json"),
    ("server-platforms.yaml", "server_platforms", "server-platform.schema.json"),
    ("cloud-providers.yaml", "cloud_providers", "cloud-provider.schema.json"),
    ("support-levels.yaml", "support_levels", "support-level.schema.json"),
]


def test_platform_registries_validate() -> None:
    proc = run(PLATFORM_VALIDATE)
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout


def test_platform_registry_files_and_schemas_exist() -> None:
    for yaml_name, _key, schema_name in PLATFORM_FILES:
        assert (ROOT / "metadata" / yaml_name).is_file(), yaml_name
        assert (ROOT / "schema" / schema_name).is_file(), schema_name


def test_platform_registry_ids_unique_and_draft_status() -> None:
    for yaml_name, list_key, _schema in PLATFORM_FILES:
        data = yaml.safe_load(
            (ROOT / "metadata" / yaml_name).read_text(encoding="utf-8")
        )
        entries = data[list_key]
        ids = [e["id"] for e in entries]
        assert len(ids) == len(set(ids)), yaml_name
        assert entries, yaml_name
        for entry in entries:
            status = entry.get("status")
            if status is not None:
                assert status in ("skeleton", "draft", "reviewed"), (
                    yaml_name,
                    entry["id"],
                    status,
                )
                assert status != "verified", entry["id"]


def test_arch_pacman_first_class_in_registries() -> None:
    distros = yaml.safe_load(
        (ROOT / "metadata" / "distributions.yaml").read_text(encoding="utf-8")
    )
    pms = yaml.safe_load(
        (ROOT / "metadata" / "package-managers.yaml").read_text(encoding="utf-8")
    )
    dist_ids = {d["id"] for d in distros["distributions"]}
    pm_ids = {p["id"] for p in pms["package_managers"]}
    assert "arch" in dist_ids
    assert "pacman" in pm_ids
    pacman = next(p for p in pms["package_managers"] if p["id"] == "pacman")
    assert "arch" in pacman.get("distributions", [])


def test_platform_support_doc_exists() -> None:
    assert (ROOT / "docs" / "PLATFORM_SUPPORT.md").is_file()


def test_catalog_schema_version_unchanged() -> None:
    cat = json.loads((ROOT / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    assert cat["schema_version"] == 1
    assert cat["kind"] == "nova-commands-bank"


SCHEMA_V2_VALIDATE = ROOT / "scripts" / "validate_schema_v2.py"

SCHEMA_V2_FILES = [
    "command.schema.v2.json",
    "task.schema.json",
    "profile.schema.json",
    "compatibility.schema.json",
]


def test_schema_v2_soft_validate() -> None:
    proc = run(SCHEMA_V2_VALIDATE)
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout


def test_schema_v2_files_and_fixtures_exist() -> None:
    for name in SCHEMA_V2_FILES:
        assert (ROOT / "schema" / name).is_file(), name
    fixtures = ROOT / "fixtures" / "schema-v2"
    assert fixtures.is_dir()
    assert (fixtures / "README.md").is_file()
    assert list(fixtures.glob("command-*.yaml"))
    assert list(fixtures.glob("task-*.yaml"))
    assert list(fixtures.glob("profile-*.yaml"))
    assert list(fixtures.glob("compatibility-*.yaml"))


def test_schema_v2_distinct_from_v1() -> None:
    v1 = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    v2 = json.loads((ROOT / "schema" / "command.schema.v2.json").read_text())
    assert v1["$id"] != v2["$id"]
    assert "windows" in v2["properties"]["platforms"]["items"]["enum"]
    assert "windows" not in v1["properties"]["platforms"]["items"]["enum"]
    assert "package_refs" in v2["properties"]
    assert "package_refs" not in v1["properties"]
    assert "powershell" in v2["properties"]["shells"]["items"]["enum"]
    assert "cmd" in v2["properties"]["shells"]["items"]["enum"]


def test_live_bank_still_v1_only() -> None:
    """commands/ must not carry schema_version: 2 until Faz 3 migrate."""
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("schema_version") in (None, 1), path


def test_data_schema_doc_exists() -> None:
    assert (ROOT / "docs" / "DATA_SCHEMA.md").is_file()
