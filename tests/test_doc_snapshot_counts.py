"""Guard current-status doc counts/digests against committed catalog drift (NV-117)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"


def _artifacts() -> tuple[dict, dict, dict]:
    cat = json.loads((META / "catalog.json").read_text(encoding="utf-8"))
    man = json.loads((META / "manifest.json").read_text(encoding="utf-8"))
    idx = json.loads((META / "search-index.json").read_text(encoding="utf-8"))
    return cat, man, idx


def _require_search_count(text: str, label: str, expected: int) -> None:
    """Match a current-status '| Search entries | N |' (or TR 'Arama girdisi') row."""
    patterns = (
        rf"\|\s*Search entries\s*\|\s*\**{expected}\**\s*\|",
        rf"\|\s*Arama girdisi\s*\|\s*\**{expected}\**\s*\|",
    )
    if not any(re.search(p, text) for p in patterns):
        raise AssertionError(
            f"{label}: expected current Search entries / Arama girdisi count {expected}"
        )


def _require_digest(text: str, label: str, digest: str) -> None:
    """Published current digest must appear (full or unambiguous 8+ hex prefix)."""
    prefix = digest[:8]
    if digest not in text and not re.search(
        rf"`?{re.escape(prefix)}[0-9a-f…\.]*`?", text
    ):
        raise AssertionError(
            f"{label}: expected content_sha256 {digest} (or prefix {prefix}…) "
            "in current-status snapshot"
        )
    # Stale main digest from pre-stack tip must not remain as the live figure
    # once the committed catalog moved (prefix match on a current-status line).
    for stale in ("406fe040",):
        if digest.startswith(stale):
            continue
        # Allow historical mentions that are clearly not the live digest cell.
        live_rows = re.findall(
            rf"\|\s*`?content_sha256`?\s*\|\s*`?({stale}[0-9a-f…]*)`?",
            text,
        )
        if live_rows:
            raise AssertionError(
                f"{label}: stale content_sha256 prefix {stale} still listed as current"
            )


def test_doc_snapshot_counts_match_catalog() -> None:
    cat, man, idx = _artifacts()
    assert man["content_sha256"] == cat["content_sha256"] == idx["content_sha256"]
    digest = man["content_sha256"]
    search = idx["entry_count"]
    assert search == (
        man["command_count"]
        + man["concept_count"]
        + man["task_count"]
        + man["profile_count"]
    )
    assert search == len(idx["entries"])

    files = {
        "README.md": ROOT / "README.md",
        "README.tr.md": ROOT / "README.tr.md",
        "docs/PLATFORM_SUPPORT.md": ROOT / "docs" / "PLATFORM_SUPPORT.md",
        "docs/ROADMAP.md": ROOT / "docs" / "ROADMAP.md",
        "docs/COVERAGE_MATRIX.md": ROOT / "docs" / "COVERAGE_MATRIX.md",
    }
    for label, path in files.items():
        text = path.read_text(encoding="utf-8")
        _require_search_count(text, label, search)
        _require_digest(text, label, digest)

    # PLATFORM_SUPPORT combo row
    ps = files["docs/PLATFORM_SUPPORT.md"].read_text(encoding="utf-8")
    combo = (
        f"{man['command_count']} / {man['concept_count']} / "
        f"{man['task_count']} / {man['profile_count']}"
    )
    assert combo in ps, f"PLATFORM_SUPPORT missing combo counts {combo}"

    # COVERAGE_MATRIX current table (bold counts)
    cm = files["docs/COVERAGE_MATRIX.md"].read_text(encoding="utf-8")
    assert "## Counts (committed catalog — current)" in cm
    for kind, key in (
        ("Commands", "command_count"),
        ("Tasks", "task_count"),
        ("Profiles", "profile_count"),
        ("Concepts", "concept_count"),
    ):
        assert re.search(
            rf"\|\s*{kind}\s*\|\s*\**{man[key]}\**\s*\|", cm
        ), f"COVERAGE_MATRIX current {kind} != {man[key]}"
    # Historical 315 only under the Historical heading
    hist = cm.split("### Historical", 1)
    assert len(hist) == 2, "COVERAGE_MATRIX must keep a Historical section for 315"
    assert "315" in hist[1]
    assert not re.search(
        r"\|\s*Search entries\s*\|\s*315\s*\|", hist[0]
    ), "315 must not appear as a current Search entries cell"


def test_platform_support_registry_counts() -> None:
    """Registry snapshot rows in PLATFORM_SUPPORT match metadata YAML lengths."""
    import yaml

    ps = (ROOT / "docs" / "PLATFORM_SUPPORT.md").read_text(encoding="utf-8")
    expected = {
        "Operating systems": ("operating-systems.yaml", "operating_systems"),
        "Distributions": ("distributions.yaml", "distributions"),
        "Shells": ("shells.yaml", "shells"),
        "Package managers": ("package-managers.yaml", "package_managers"),
        "Server platforms": ("server-platforms.yaml", "server_platforms"),
        "Cloud providers": ("cloud-providers.yaml", "cloud_providers"),
        "Execution environments": (
            "execution-environments.yaml",
            "execution_environments",
        ),
        "Architectures": ("architectures.yaml", "architectures"),
    }
    for label, (yaml_name, list_key) in expected.items():
        data = yaml.safe_load((META / yaml_name).read_text(encoding="utf-8")) or {}
        n = len(data.get(list_key) or [])
        assert re.search(
            rf"\|\s*{re.escape(label)}\s*\|\s*{n}\s*\|", ps
        ), f"PLATFORM_SUPPORT {label} expected {n}"
