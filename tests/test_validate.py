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
GENERATED_VALIDATE = ROOT / "scripts" / "validate_generated_artifacts.py"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    # Always launch validators with the active test interpreter (venv), never
    # a hardcoded /usr/bin/python3 that may lack project deps.
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
    assert cat["schema_version"] == 2
    assert cat["kind"] == "nova-commands-bank"
    assert cat["command_count"] == len(cat["commands"])
    assert cat["concept_count"] == len(cat["concepts"])
    assert cat["task_count"] == len(cat["tasks"])
    assert cat["profile_count"] == len(cat["profiles"])
    assert cat["command_count"] >= 50
    assert cat["concept_count"] >= 7
    assert cat["task_count"] >= 10
    assert cat["profile_count"] >= 8
    assert len(cat["content_sha256"]) == 64
    ids = [c["id"] for c in cat["commands"]]
    assert len(ids) == len(set(ids))
    task_ids = [t["id"] for t in cat["tasks"]]
    assert len(task_ids) == len(set(task_ids))
    assert not (set(task_ids) & set(ids))
    # Live bank is schema v2
    for cmd in cat["commands"]:
        assert cmd.get("schema_version") == 2
        assert cmd.get("kind") in {
            "executable",
            "shell_builtin",
            "shell_keyword",
            "powershell_cmdlet",
            "command_interpreter",
            "package_manager",
            "subcommand",
            "script",
            "administrative_tool",
            "remote_cli",
            "vendor_cli",
        }

    man = json.loads(manifest.read_text(encoding="utf-8"))
    idx = json.loads(search.read_text(encoding="utf-8"))
    assert man["schema_version"] == 2
    assert man["kind"] == "nova-commands-manifest"
    assert man["task_count"] == cat["task_count"]
    assert man["profile_count"] == cat["profile_count"]
    assert man["operating_system_count"] >= 1
    assert man["package_manager_count"] >= 1
    assert idx["schema_version"] == 2
    assert idx["kind"] == "nova-commands-search-index"
    assert idx["task_count"] == cat["task_count"]
    assert idx["profile_count"] == cat["profile_count"]
    types = {e["type"] for e in idx["entries"]}
    assert {"command", "concept", "task", "profile"} <= types
    assert idx["entry_count"] == len(idx["entries"])
    assert man["content_sha256"] == cat["content_sha256"] == idx["content_sha256"]
    gen = run(GENERATED_VALIDATE)
    assert gen.returncode == 0, gen.stderr + gen.stdout
    assert "OK:" in gen.stdout


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


def test_topic_guides_have_structured_sections() -> None:
    """NV-123: topic-guide format exposes learning structure for Nova TUI."""
    guides = []
    for path in (ROOT / "concepts").glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("format") != "topic-guide":
            continue
        guides.append(data)
        assert data.get("intro") or data.get("body")
        # At least one navigational section beyond freeform body
        structured = any(
            data.get(key)
            for key in (
                "learning_path",
                "subtopics",
                "command_table",
                "graded_examples",
                "callouts",
                "safe_exercises",
                "next_steps",
            )
        )
        assert structured, path
        for ex in data.get("safe_exercises") or []:
            assert ex.get("risk") in ("safe", "caution"), path
    assert len(guides) >= 20


def test_teachable_command_fields_schema_and_seed() -> None:
    """Optional when/syntax/mistakes/topics are additive on schema v2."""
    live = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    v2 = json.loads((ROOT / "schema" / "command.schema.v2.json").read_text())
    for schema in (live, v2):
        props = schema["properties"]
        for key in (
            "when_to_use",
            "syntax",
            "expected_effect",
            "common_mistakes",
            "related_topics",
        ):
            assert key in props
    concept = json.loads((ROOT / "schema" / "concept.schema.json").read_text())
    for key in (
        "format",
        "intro",
        "learning_path",
        "subtopics",
        "command_table",
        "graded_examples",
        "callouts",
        "safe_exercises",
        "next_steps",
    ):
        assert key in concept["properties"]

    seeded = 0
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("when_to_use") or data.get("syntax") or data.get("common_mistakes"):
            seeded += 1
            # learning_level must not be used as an excuse to skip explanation
            if data.get("learning_level") == "beginner":
                assert data.get("summary", {}).get("en")
    assert seeded >= 15


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


def test_catalog_schema_version_is_v2() -> None:
    cat = json.loads((ROOT / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    assert cat["schema_version"] == 2
    assert cat["kind"] == "nova-commands-bank"


SCHEMA_V2_VALIDATE = ROOT / "scripts" / "validate_schema_v2.py"
MIGRATE = ROOT / "scripts" / "migrate_v1_to_v2.py"

SCHEMA_V2_FILES = [
    "command.schema.json",
    "command.schema.v2.json",
    "command.schema.v1.json",
    "catalog.schema.json",
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
    assert MIGRATE.is_file()


def test_live_schema_is_v2_with_archived_v1() -> None:
    live = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    twin = json.loads((ROOT / "schema" / "command.schema.v2.json").read_text())
    v1 = json.loads((ROOT / "schema" / "command.schema.v1.json").read_text())
    assert live["$id"] != twin["$id"]
    assert live["$id"] != v1["$id"]
    assert "windows" in live["properties"]["platforms"]["items"]["enum"]
    assert "windows" not in v1["properties"]["platforms"]["items"]["enum"]
    assert "package_refs" in live["properties"]
    assert "package_refs" not in v1["properties"]
    assert "powershell" in live["properties"]["shells"]["items"]["enum"]
    assert "cmd" in live["properties"]["shells"]["items"]["enum"]


def test_live_bank_is_schema_v2() -> None:
    """All commands/ YAML must carry schema_version: 2 after Faz 3 migrate."""
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data.get("schema_version") == 2, path
        assert data.get("kind"), path


def test_migrate_check_passes() -> None:
    proc = run(MIGRATE, "--check")
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout


def test_package_refs_prefer_pacman_when_arch() -> None:
    """Arch-first: when packages.arch exists, package_refs should lead with pacman."""
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        packages = data.get("packages") or {}
        refs = data.get("package_refs") or []
        if "arch" in packages and refs:
            assert refs[0]["manager"] == "pacman", path


def test_verification_statuses_not_silently_demoted() -> None:
    """Sanity: bank still has verified + reviewed after migrate (not all draft)."""
    statuses = {}
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        st = data["verification"]["status"]
        statuses[st] = statuses.get(st, 0) + 1
    assert statuses.get("verified", 0) >= 20
    assert statuses.get("reviewed", 0) >= 100


def test_data_schema_doc_exists() -> None:
    assert (ROOT / "docs" / "DATA_SCHEMA.md").is_file()
    assert (ROOT / "docs" / "SCHEMA_MIGRATION_V2.md").is_file()


TASKS_PROFILES_VALIDATE = ROOT / "scripts" / "validate_tasks_profiles.py"


def test_tasks_profiles_validate() -> None:
    proc = run(TASKS_PROFILES_VALIDATE, "--require")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "OK:" in proc.stdout


def test_tasks_and_profiles_trees_exist() -> None:
    tasks = sorted((ROOT / "tasks").glob("*.yaml"))
    profiles = sorted((ROOT / "profiles").glob("*.yaml"))
    assert len(tasks) >= 10
    assert len(profiles) >= 8
    assert (ROOT / "schema" / "task.schema.json").is_file()
    assert (ROOT / "schema" / "profile.schema.json").is_file()
    assert TASKS_PROFILES_VALIDATE.is_file()


def test_task_ids_do_not_collide_with_commands() -> None:
    cmd_ids = set()
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cmd_ids.add(data["id"])
    for path in (ROOT / "tasks").glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == path.stem
        assert data["kind"] == "task"
        assert data["id"] not in cmd_ids
        assert data["verification"]["status"] in ("draft", "reviewed", "verified")
        for lang in ("tr", "en"):
            assert data["name"][lang].strip()
            assert data["summary"][lang].strip()
            assert data["intent"][lang]


def test_profile_ids_and_refs() -> None:
    task_ids = {
        yaml.safe_load(p.read_text(encoding="utf-8"))["id"]
        for p in (ROOT / "tasks").glob("*.yaml")
    }
    for path in (ROOT / "profiles").glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["id"] == path.stem
        assert data["kind"] == "profile"
        assert data["verification"]["status"] != "verified" or data["verification"].get(
            "sources"
        )
        for tid in data.get("related_tasks") or []:
            assert tid in task_ids, (path, tid)


def test_catalog_indexes_tasks_profiles() -> None:
    """Faz 9: tasks/profiles are in catalog + content_sha256 payload."""
    import hashlib

    run(BUILD)
    cat = json.loads((ROOT / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    assert isinstance(cat.get("tasks"), list) and cat["tasks"]
    assert isinstance(cat.get("profiles"), list) and cat["profiles"]
    assert cat["command_count"] >= 200
    assert cat["task_count"] == len(cat["tasks"]) >= 10
    assert cat["profile_count"] == len(cat["profiles"]) >= 8

    def digest(commands, concepts, tasks, profiles) -> str:
        payload = {
            "schema_version": 2,
            "kind": "nova-commands-bank",
            "commands": commands,
            "concepts": concepts,
            "tasks": tasks,
            "profiles": profiles,
        }
        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    cmds_only = digest(cat["commands"], cat["concepts"], [], [])
    assert cat["content_sha256"] != cmds_only
    assert cat["content_sha256"] == digest(
        cat["commands"], cat["concepts"], cat["tasks"], cat["profiles"]
    )


SECURITY_VALIDATE = ROOT / "scripts" / "validate_security.py"


def test_security_validate_passes() -> None:
    proc = run(SECURITY_VALIDATE)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "OK:" in proc.stdout


def test_minisign_pubkey_present_no_private_keys() -> None:
    pub = ROOT / "keys" / "minisign.pub"
    assert pub.is_file()
    text = pub.read_text(encoding="utf-8")
    assert "minisign public key" in text.lower() or "RW" in text
    assert not list((ROOT / "keys").glob("*.key"))
    assert not (ROOT / "keys" / "nova-commands.key").exists()


def test_example_schema_allows_warnings() -> None:
    live = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    v2 = json.loads((ROOT / "schema" / "command.schema.v2.json").read_text())
    assert "warnings" in live["$defs"]["example"]["properties"]
    assert "warnings" in v2["$defs"]["example"]["properties"]


def test_learning_level_schema_independent_of_risk() -> None:
    """learning_level is optional pedagogy; risk stays the danger enum."""
    live = json.loads((ROOT / "schema" / "command.schema.json").read_text())
    v2 = json.loads((ROOT / "schema" / "command.schema.v2.json").read_text())
    for schema in (live, v2):
        ll = schema["properties"]["learning_level"]
        assert set(ll["enum"]) == {
            "beginner",
            "intermediate",
            "advanced",
            "unspecified",
        }
        assert "learning_level" not in schema["required"]
        assert "risk" in schema["required"]
        assert set(schema["properties"]["risk"]["enum"]) == {
            "safe",
            "caution",
            "dangerous",
            "destructive",
        }
        diff = schema["$defs"]["example"]["properties"]["difficulty"]
        assert set(diff["enum"]) == {"beginner", "intermediate", "advanced"}
        assert "difficulty" not in schema["$defs"]["example"]["required"]


def test_learning_level_missing_becomes_unspecified_not_from_risk() -> None:
    """Build must emit explicit unspecified; never map destructive → advanced."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_catalog", BUILD)
    assert spec and spec.loader
    build_catalog = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_catalog)
    normalize = build_catalog.normalize_learning_level

    destructive = {
        "id": "fake-wipe",
        "risk": "destructive",
        "examples": [{"risk": "destructive"}],
    }
    safe = {"id": "fake-ls", "risk": "safe", "examples": [{"risk": "safe"}]}
    assert normalize(destructive)["learning_level"] == "unspecified"
    assert normalize(safe)["learning_level"] == "unspecified"
    # explicit values preserved; still independent of risk
    tagged = {
        "id": "rm-like",
        "risk": "destructive",
        "learning_level": "beginner",
        "examples": [{"risk": "destructive", "difficulty": "beginner"}],
    }
    assert normalize(dict(tagged))["learning_level"] == "beginner"

    # Invalid learning_level fails closed (risk-like value rejected)
    bad = {"id": "x", "risk": "safe", "learning_level": "dangerous"}
    try:
        normalize(bad)
        raise AssertionError("expected SystemExit for risk-like learning_level")
    except SystemExit:
        pass

    # Catalog rebuild always has explicit learning_level on every command
    run(BUILD)
    cat = json.loads((ROOT / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    allowed = {"beginner", "intermediate", "advanced", "unspecified"}
    for cmd in cat["commands"]:
        assert cmd.get("learning_level") in allowed, cmd["id"]
        # risk markers unchanged enum
        assert cmd["risk"] in {"safe", "caution", "dangerous", "destructive"}
    idx = json.loads(
        (ROOT / "metadata" / "search-index.json").read_text(encoding="utf-8")
    )
    for entry in idx["entries"]:
        if entry["type"] == "command":
            assert entry.get("learning_level") in allowed, entry["id"]

    # Honesty: at least one destructive beginner (risk ≠ learning)
    assert any(
        c["risk"] == "destructive" and c["learning_level"] == "beginner"
        for c in cat["commands"]
    )
    # And some commands remain explicitly unspecified
    assert any(c["learning_level"] == "unspecified" for c in cat["commands"])


def test_example_difficulty_not_required_and_not_risk() -> None:
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for i, ex in enumerate(data.get("examples") or []):
            diff = ex.get("difficulty")
            if diff is not None:
                assert diff in {"beginner", "intermediate", "advanced"}, (path, i)
                # difficulty uses pedagogy labels, not risk vocabulary
                assert diff not in {
                    "safe",
                    "caution",
                    "dangerous",
                    "destructive",
                }, (path, i)


def test_related_refs_resolve() -> None:
    cmd_ids = {
        yaml.safe_load(p.read_text(encoding="utf-8"))["id"]
        for p in (ROOT / "commands").glob("*/*.yaml")
    }
    for path in (ROOT / "commands").glob("*/*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for rid in data.get("related") or []:
            assert rid in cmd_ids, (path, rid)


def test_ci_workflows_pin_action_shas() -> None:
    """Faz 10: third-party Actions must be pinned to full commit SHAs."""
    import re

    sha_re = re.compile(r"^[0-9a-f]{40}$")
    for name in ("ci.yml", "publish-catalog.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- uses:") and not stripped.startswith("uses:"):
                continue
            # uses: owner/repo@ref  or  uses: owner/repo/path@ref
            ref = stripped.split("@", 1)[-1].split("#", 1)[0].strip()
            assert sha_re.match(ref), f"{name}: unpinned action ref {ref!r} in {stripped}"


def test_ci_helper_scripts_exist() -> None:
    assert (ROOT / "scripts" / "ci_check_committed_sha.py").is_file()
    assert (ROOT / "scripts" / "ci_check_rebuild_coherence.py").is_file()
    assert SECURITY_VALIDATE.is_file()
    assert GENERATED_VALIDATE.is_file()


def test_both_command_schema_versions_load() -> None:
    """Archived v1 + live v2 must both be valid Draft 2020-12 schemas."""
    from jsonschema import Draft202012Validator

    for name in ("command.schema.v1.json", "command.schema.json", "command.schema.v2.json"):
        doc = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(doc)


def test_rebuild_leaves_clean_git_tree() -> None:
    """After an idempotent rebuild, metadata/ must not show unexpected dirty diffs."""
    before = subprocess.run(
        ["git", "status", "--porcelain", "--", "metadata/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert before.returncode == 0, before.stderr
    assert before.stdout.strip() == "", (
        "metadata/ already dirty before rebuild; commit or restore first:\n"
        f"{before.stdout}"
    )

    proc = run(BUILD)
    assert proc.returncode == 0, proc.stderr + proc.stdout

    after = subprocess.run(
        ["git", "status", "--porcelain", "--", "metadata/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert after.returncode == 0, after.stderr
    assert after.stdout.strip() == "", (
        "rebuild left unexpected dirty diffs under metadata/ "
        "(content_sha256 match should preserve generated_at):\n"
        f"{after.stdout}"
    )

    # Hash triple still agrees after the clean rebuild.
    gen = run(GENERATED_VALIDATE)
    assert gen.returncode == 0, gen.stderr + gen.stdout


def test_validation_scripts_use_sys_executable_not_usr_bin() -> None:
    """Regression: nested validators must launch via sys.executable, not a fixed system path."""
    system_py = "/usr/" + "bin/python3"
    catalog_src = (ROOT / "scripts" / "validate_catalog.py").read_text(encoding="utf-8")
    assert "sys.executable" in catalog_src
    assert f'"{system_py}"' not in catalog_src
    assert f"'{system_py}'" not in catalog_src
    helper_src = Path(__file__).read_text(encoding="utf-8")
    assert "[sys.executable, str(script)" in helper_src
