"""Security checklist bank honesty (NV-119).

Static content gates for `tasks/security-check-*.yaml`. Never executes catalog
commands. Complements Nova TUI tests that assert Enter never auto-runs and that
OS/distro/shell filters return empty on no-match (no cross-OS substitute).
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"

SECURITY_CHECK_IDS = [
    "security-check-os-accounts",
    "security-check-updates",
    "security-check-ssh",
    "security-check-firewall-ports",
    "security-check-users-sudo",
    "security-check-docker",
    "security-check-reverse-proxy-tls",
    "security-check-dns-vpn",
    "security-check-backup-restore",
    "security-check-logs-incident",
]


def load_task(task_id: str) -> dict:
    path = TASKS / f"{task_id}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data["id"] == task_id
    return data


def all_security_tasks() -> list[dict]:
    return [load_task(tid) for tid in SECURITY_CHECK_IDS]


def test_security_checklist_tasks_exist_and_stay_draft() -> None:
    for task in all_security_tasks():
        ver = task["verification"]
        assert ver["status"] == "draft", task["id"]
        assert ver.get("sources"), task["id"]
        # Schema pass / doc links alone must not promote status.
        assert ver.get("last_reviewed") in (None, "") or "verified" not in (
            ver["status"],
        )


def test_security_checklist_never_claims_auto_run() -> None:
    markers = (
        "never auto-run",
        "otomatik çalışmaz",
        "otomatik calismaz",
    )
    for task in all_security_tasks():
        blob = " ".join(
            [
                task.get("description", {}).get("en", ""),
                task.get("description", {}).get("tr", ""),
                task.get("summary", {}).get("en", ""),
                task.get("summary", {}).get("tr", ""),
            ]
        ).lower()
        assert any(m in blob for m in markers), (
            f"{task['id']} must document documentation-only / never auto-run"
        )


def test_security_checklist_profile_and_concept_never_auto_run() -> None:
    profile = yaml.safe_load(
        (ROOT / "profiles" / "server-security-checklist.yaml").read_text(
            encoding="utf-8"
        )
    )
    concept = yaml.safe_load(
        (ROOT / "concepts" / "server-security-checklist.yaml").read_text(
            encoding="utf-8"
        )
    )
    for blob in (
        profile["summary"]["en"],
        profile["summary"]["tr"],
        concept["body"]["en"],
        concept["body"]["tr"],
    ):
        low = blob.lower()
        assert "auto-run" in low or "otomatik" in low
    assert profile["verification"]["status"] == "draft"
    assert concept["verification"]["status"] == "draft"
    assert profile["related_tasks"] == SECURITY_CHECK_IDS


def _platforms(impl: dict) -> set[str]:
    return {p.lower() for p in (impl.get("platforms") or [])}


def test_security_checklist_platform_tags_no_cross_os_generalization() -> None:
    """Each example inherits only its implementation platforms (Nova selects; bank must tag)."""
    for task in all_security_tasks():
        for impl in task["implementations"]:
            plats = _platforms(impl)
            assert plats, f"{task['id']}/{impl['id']} missing platforms"
            # No single impl may claim both linux and windows (would invite silent mix).
            if "linux" in plats and "windows" in plats:
                raise AssertionError(
                    f"{task['id']}/{impl['id']} mixes linux+windows platforms"
                )
            cmds = " ".join(ex["command"] for ex in impl["examples"]).lower()
            if "windows" in plats:
                assert "ufw" not in cmds and "pacman" not in cmds and "systemctl" not in cmds, (
                    task["id"],
                    impl["id"],
                    cmds,
                )
            if "linux" in plats:
                assert "get-nettcpconnection" not in cmds and "winget" not in cmds, (
                    task["id"],
                    impl["id"],
                )
            if "macos" in plats:
                assert "hostnamectl" not in cmds and "ufw " not in cmds, (
                    task["id"],
                    impl["id"],
                )
            if "bsd" in plats:
                assert "systemctl" not in cmds and "ufw" not in cmds, (
                    task["id"],
                    impl["id"],
                )


def test_security_checklist_docker_has_no_bsd_impl() -> None:
    docker = load_task("security-check-docker")
    plats = set()
    for impl in docker["implementations"]:
        plats |= _platforms(impl)
    assert "bsd" not in plats
    assert {"linux", "windows", "macos"} <= plats


def _filter_impls(task: dict, *, os: str | None = None, distro: str | None = None) -> list[dict]:
    """Bank-side mirror of Nova selection: empty on no-match, no cross-OS substitute."""
    matched = []
    for impl in task["implementations"]:
        plats = _platforms(impl)
        if os and os not in plats:
            continue
        dists = {d.lower() for d in (impl.get("distributions") or [])}
        if distro:
            if dists and distro not in dists:
                # ubuntu may accept debian-family tags in Nova; keep strict here for bank honesty.
                if not (distro == "ubuntu" and "debian" in dists):
                    if not (distro in dists):
                        continue
            elif dists and distro not in dists:
                continue
        matched.append(impl)
    return matched


def test_security_checklist_platform_match_and_no_match() -> None:
    fw = load_task("security-check-firewall-ports")
    win = _filter_impls(fw, os="windows")
    assert win and all("windows" in _platforms(i) for i in win)
    assert all(
        "ufw" not in ex["command"] and not ex["command"].startswith("ss ")
        for i in win
        for ex in i["examples"]
    )

    updates = load_task("security-check-updates")
    deb = _filter_impls(updates, os="linux", distro="debian")
    assert any("apt" in " ".join(ex["command"] for ex in i["examples"]) for i in deb)
    assert all(
        "pacman" not in " ".join(ex["command"] for ex in i["examples"])
        and "checkupdates" not in " ".join(ex["command"] for ex in i["examples"])
        for i in deb
    )

    docker = load_task("security-check-docker")
    assert _filter_impls(docker, os="bsd") == []


def test_security_checklist_updates_labels_downloads_and_dry_build() -> None:
    updates = load_task("security-check-updates")
    cmds = []
    for impl in updates["implementations"]:
        for ex in impl["examples"]:
            cmds.append((impl["id"], ex))

    # Invented `freebsd-update show` must stay gone (man 8: fetch/install/updatesready/…).
    assert all("freebsd-update show" not in ex["command"] for _, ex in cmds)

    freebsd = next(ex for iid, ex in cmds if iid == "freebsd-check" and "freebsd-update" in ex["command"])
    assert freebsd["risk"] == "caution"
    assert freebsd["privilege"] == "elevated"
    assert "fetch" in freebsd["command"]
    assert "install" not in freebsd["command"]
    assert any("download" in (w.get("en") or "").lower() for w in (freebsd.get("warnings") or []))

    nix = next(ex for iid, ex in cmds if iid == "nixos-check")
    assert "dry-build" in nix["command"]
    en = nix["explanation"]["en"].lower()
    assert "does not build" in en
    assert "without switching" not in en  # old inaccurate phrasing
    assert "switch" in en

    winget = next(ex for iid, ex in cmds if iid == "windows-winget")
    assert "list --upgrade-available" in winget["command"]
    assert winget["command"].strip() != "winget upgrade"
    assert "--all" not in winget["command"]


def test_security_checklist_safe_examples_are_non_mutating_heuristics() -> None:
    """Safe-labeled examples must not look like install/upgrade/reload/write paths."""
    banned_substrings = (
        "upgrade --all",
        "ufw --force",
        "userdel ",
        "rm -rf",
        "winget upgrade --all",
        "freebsd-update install",
        "nixos-rebuild switch",
        "softwareupdate --install",
        "softwareupdate --download",
    )
    # Leading / chained mutators (avoid matching `getent passwd`).
    banned_tokens = {"install", "reload", "restart", "useradd", "usermod", "userdel"}
    for task in all_security_tasks():
        for impl in task["implementations"]:
            for ex in impl["examples"]:
                if ex.get("risk") != "safe":
                    continue
                cmd = ex["command"]
                low = cmd.lower()
                for bad in banned_substrings:
                    assert bad not in low, (task["id"], impl["id"], cmd, bad)
                for chunk in low.replace(";", "|").split("|"):
                    head = chunk.strip().split(" ", 1)[0] if chunk.strip() else ""
                    assert head not in banned_tokens, (task["id"], impl["id"], cmd, head)
                    assert not head.endswith("/passwd") and head != "passwd", (
                        task["id"],
                        impl["id"],
                        cmd,
                    )


def test_security_checklist_no_remote_scan_or_attack_examples() -> None:
    for task in all_security_tasks():
        for impl in task["implementations"]:
            for ex in impl["examples"]:
                cmd = ex["command"].lower()
                assert "nmap " not in cmd
                assert "| bash" not in cmd and "| sh" not in cmd
