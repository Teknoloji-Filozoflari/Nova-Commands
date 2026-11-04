#!/usr/bin/env python3
"""Migrate commands/**/*.yaml from schema v1 → v2 (Faz 3).

Preserves:
  - command ids, TR/EN text, related, risk, examples, flags, nova hooks
  - verification.status (never silent demotion of reviewed/verified)

Adds / maps:
  - schema_version: 2
  - kind (conservative inference)
  - package_refs from legacy packages keys → package-managers.yaml ids
  - operating_systems from clear platform tags (linux/macos only; bsd stays
    platforms[] without inventing freebsd/openbsd/…)

Keeps legacy ``packages`` object for dual-read / Nova install hints.

Usage:
  python3 scripts/migrate_v1_to_v2.py           # rewrite commands/
  python3 scripts/migrate_v1_to_v2.py --dry-run # report only
  python3 scripts/migrate_v1_to_v2.py --check   # fail if any file still v1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"

# Legacy packages.<key> → (package-managers.yaml id, distributions.yaml ids)
PACKAGES_KEY_MAP: dict[str, tuple[str, list[str]]] = {
    "arch": ("pacman", ["arch"]),
    "debian": ("apt", ["debian"]),
    "ubuntu": ("apt", ["ubuntu"]),
    "fedora": ("dnf", ["fedora"]),
    "rhel": ("dnf", ["rhel"]),
}

# Clear shell builtins only (do not invent for echo/env/pwd ambiguity).
SHELL_BUILTINS = frozenset({"cd", "export", "history"})

# packages/ category managers (ids match command ids in this bank).
PACKAGE_MANAGER_IDS = frozenset(
    {"apt", "dnf", "dpkg", "flatpak", "pacman", "paru", "rpm", "yay"}
)

# Preferred top-level key order for rewritten YAML.
KEY_ORDER = [
    "schema_version",
    "id",
    "name",
    "kind",
    "category",
    "aliases",
    "summary",
    "description",
    "purpose",
    "tags",
    "risk",
    "requires_elevated",
    "platforms",
    "operating_systems",
    "distributions",
    "architectures",
    "execution_environments",
    "shells",
    "packages",
    "package_refs",
    "install_notes",
    "implementations",
    "flags",
    "examples",
    "related",
    "see_also",
    "documentation",
    "sources",
    "security",
    "version_constraints",
    "intent",
    "verification",
    "nova",
]


class _LiteralStr(str):
    """Marker for block-style multi-line strings (unused; reserved)."""


def _str_representer(dumper: yaml.Dumper, data: str) -> yaml.Node:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, _str_representer)


def infer_kind(raw: dict[str, Any]) -> str:
    cid = raw.get("id") or ""
    if cid in SHELL_BUILTINS:
        return "shell_builtin"
    if cid in PACKAGE_MANAGER_IDS or raw.get("category") == "packages":
        # packages/ category in this bank is package managers / PM frontends.
        return "package_manager"
    return "executable"


def packages_to_refs(packages: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Map v1 fixed distro keys → package_refs; Arch/pacman first."""
    if not packages:
        return []

    # Merge (manager, package) → distributions (preserve first-seen order).
    merged: dict[tuple[str, str], list[str]] = {}
    order: list[tuple[str, str]] = []

    # Emit arch/pacman first when present.
    keys = list(packages.keys())
    if "arch" in keys:
        keys = ["arch"] + [k for k in keys if k != "arch"]

    for key in keys:
        pkg = packages.get(key)
        if not isinstance(pkg, str) or not pkg.strip():
            continue
        mapping = PACKAGES_KEY_MAP.get(key)
        if mapping is None:
            continue
        manager, distros = mapping
        pair = (manager, pkg)
        if pair not in merged:
            merged[pair] = []
            order.append(pair)
        for d in distros:
            if d not in merged[pair]:
                merged[pair].append(d)

    refs: list[dict[str, Any]] = []
    for manager, pkg in order:
        refs.append(
            {
                "manager": manager,
                "package": pkg,
                "distributions": list(merged[(manager, pkg)]),
            }
        )
    return refs


def platforms_to_operating_systems(platforms: list[str] | None) -> list[str]:
    """Map only unambiguous platform tags to OS registry ids.

    ``bsd`` stays on platforms[] — do not invent freebsd/openbsd/netbsd.
    """
    if not platforms:
        return []
    out: list[str] = []
    for p in platforms:
        if p in ("linux", "macos", "windows", "android"):
            if p not in out:
                out.append(p)
        # bsd / finer tags: leave for platforms only unless already specific
        elif p in (
            "freebsd",
            "openbsd",
            "netbsd",
            "dragonflybsd",
            "illumos",
            "solaris",
            "aix",
        ):
            if p not in out:
                out.append(p)
    return out


def ordered(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in KEY_ORDER:
        if key in raw and raw[key] is not None:
            out[key] = raw[key]
    for key, val in raw.items():
        if key not in out and val is not None:
            out[key] = val
    return out


def migrate_command(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)

    # Already migrated — refresh derived fields idempotently without demoting.
    data["schema_version"] = 2

    if not data.get("kind"):
        data["kind"] = infer_kind(data)

    packages = data.get("packages")
    if isinstance(packages, dict) and packages:
        # Always rebuild package_refs from packages for consistency.
        refs = packages_to_refs(packages)
        if refs:
            data["package_refs"] = refs
    elif not data.get("package_refs"):
        # No packages and no refs — leave absent (valid).
        data.pop("package_refs", None)

    os_refs = platforms_to_operating_systems(data.get("platforms"))
    if os_refs:
        data["operating_systems"] = os_refs

    return ordered(data)


def dump_yaml(data: dict[str, Any]) -> str:
    text = yaml.dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
        indent=2,
    )
    # PyYAML may quote some dates; keep trailing newline.
    if not text.endswith("\n"):
        text += "\n"
    return text


def is_v1(raw: dict[str, Any]) -> bool:
    return raw.get("schema_version") in (None, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commands-dir",
        type=Path,
        default=COMMANDS_DIR,
        help="Override commands directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes; do not write files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any command YAML is still schema v1",
    )
    args = parser.parse_args()
    commands_dir: Path = args.commands_dir

    files = sorted(commands_dir.glob("*/*.yaml"))
    if not files:
        print(f"FAIL: no command YAML under {commands_dir}", file=sys.stderr)
        return 1

    still_v1 = 0
    migrated = 0
    unchanged = 0
    kind_counts: dict[str, int] = {}
    refs_total = 0
    status_counts: dict[str, int] = {}

    for path in files:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            print(f"FAIL: {path}: root must be mapping", file=sys.stderr)
            return 1

        status = (raw.get("verification") or {}).get("status") or "?"
        status_counts[status] = status_counts.get(status, 0) + 1

        if is_v1(raw):
            still_v1 += 1

        new = migrate_command(raw)
        kind = new.get("kind") or "?"
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        refs_total += len(new.get("package_refs") or [])

        # Integrity: never change verification.status
        old_status = (raw.get("verification") or {}).get("status")
        new_status = (new.get("verification") or {}).get("status")
        if old_status != new_status:
            print(
                f"FAIL: {path}: verification.status changed {old_status!r} → {new_status!r}",
                file=sys.stderr,
            )
            return 1
        if new.get("id") != raw.get("id"):
            print(f"FAIL: {path}: id changed", file=sys.stderr)
            return 1

        new_text = dump_yaml(new)
        old_text = path.read_text(encoding="utf-8")
        if new_text == old_text:
            unchanged += 1
            continue

        migrated += 1
        if args.dry_run or args.check:
            # --check must never rewrite on-disk YAML (field-order / dumper drift
            # would mutate the bank and break catalog content_sha256 in CI).
            if args.dry_run:
                rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                print(
                    f"would migrate {rel} kind={kind} "
                    f"refs={len(new.get('package_refs') or [])}"
                )
        else:
            path.write_text(new_text, encoding="utf-8")

    print(
        f"commands={len(files)} migrated={migrated} unchanged={unchanged} "
        f"still_v1_before={still_v1}"
    )
    print(f"kinds={dict(sorted(kind_counts.items()))}")
    print(f"verification={dict(sorted(status_counts.items()))}")
    print(f"package_refs_total={refs_total}")

    if args.check:
        # Re-read after optional writes
        left = 0
        for path in files:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if is_v1(raw) or raw.get("schema_version") != 2:
                left += 1
                print(f"  still not v2: {path}", file=sys.stderr)
        if left:
            print(f"FAIL: {left} command(s) not on schema_version 2", file=sys.stderr)
            return 1
        print("OK: all commands schema_version=2")
        return 0

    if args.dry_run:
        print("dry-run complete (no files written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
