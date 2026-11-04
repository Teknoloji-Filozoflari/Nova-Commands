#!/usr/bin/env python3
"""Faz 10 security / compatibility / duplicate gates for Nova-Commands.

Complements validate_catalog.py. Static checks only — never executes catalog
commands. Does not promote verification.status.

Hard fails on:
  - Known-dangerous shell patterns without elevated risk labels / warnings
  - Destructive device-wipe examples missing bilingual warnings
  - Broken command `related` cross-references
  - Duplicate aliases across distinct command ids
  - Private key material under keys/
  - Missing or empty keys/minisign.pub
  - Fake-looking verified tasks/profiles without sources (belt-and-suspenders)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / "commands"
TASKS_DIR = ROOT / "tasks"
PROFILES_DIR = ROOT / "profiles"
KEYS_DIR = ROOT / "keys"
MINISIGN_PUB = KEYS_DIR / "minisign.pub"

# Patterns that must never be presented as safe/caution-only examples.
UNSAFE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"curl\s+[^\n|]*\|\s*(?:ba)?sh\b", re.I), "curl|shell"),
    (re.compile(r"wget\s+[^\n|]*\|\s*(?:ba)?sh\b", re.I), "wget|shell"),
    (re.compile(r":\(\)\s*\{\s*: \|:\s*&\s*\}\s*;", re.I), "fork-bomb"),
    (re.compile(r"\brm\s+(-[^\s]*\s+)*-(?:[^\s]*f[^\s]*|/)\s+/\s*$"), "rm -rf /"),
    (re.compile(r"\brm\s+-[^\s]*r[^\s]*f[^\s]*.*/\s*$"), "rm -rf /"),
]

# Device / filesystem wipe class — requires risk=destructive + warnings.
# Dry-run / probe-only invocations are excluded via is_real_wipe().
WIPE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bdd\b[^\n]*\bof=/dev/", re.I), "dd of=/dev"),
    (re.compile(r"\bmkfs(?:\.\w+)?\b[^\n]*/dev/", re.I), "mkfs /dev"),
    (re.compile(r"\bwipefs\b[^\n]*/dev/", re.I), "wipefs /dev"),
    (re.compile(r"\bshred\b[^\n]*/dev/", re.I), "shred /dev"),
]

DRY_RUN_FLAG = re.compile(
    r"(?:^|\s)(?:-[nN]\b|--dry-run\b|--no-act\b)",
)
WIPEFS_ALL = re.compile(r"(?:^|\s)(?:-a\b|--all\b)")


def is_real_wipe(command: str, label: str) -> bool:
    """True when the command string is a live wipe, not a dry-run/probe."""
    if DRY_RUN_FLAG.search(command):
        return False
    if label.startswith("wipefs") and not WIPEFS_ALL.search(command):
        # wipefs without -a/--all only lists signatures.
        return False
    return True


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def example_warnings(ex: dict) -> list:
    raw = ex.get("warnings")
    return raw if isinstance(raw, list) else []


def has_bilingual_warnings(ex: dict) -> bool:
    for w in example_warnings(ex):
        if not isinstance(w, dict):
            continue
        tr = w.get("tr")
        en = w.get("en")
        if isinstance(tr, str) and tr.strip() and isinstance(en, str) and en.strip():
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--commands-dir",
        type=Path,
        default=COMMANDS_DIR,
        help="Override commands directory",
    )
    args = parser.parse_args()
    commands_dir: Path = args.commands_dir

    errors: list[str] = []
    notices: list[str] = []

    # --- signing material ---
    if not MINISIGN_PUB.is_file():
        errors.append("keys/minisign.pub missing (minisign trust anchor required)")
    else:
        pub = MINISIGN_PUB.read_text(encoding="utf-8").strip()
        if "minisign public key" not in pub.lower() and "RW" not in pub:
            errors.append("keys/minisign.pub does not look like a minisign pubkey")
        if len(pub) < 40:
            errors.append("keys/minisign.pub is empty or truncated")

    if KEYS_DIR.is_dir():
        for path in KEYS_DIR.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".key", ".sec", ".secret"}:
                errors.append(
                    f"{path.relative_to(ROOT)}: private key material must not be committed"
                )
            if path.is_file() and path.name.lower() in {
                "nova-commands.key",
                "minisign.key",
                "secret.key",
            }:
                errors.append(
                    f"{path.relative_to(ROOT)}: private key material must not be committed"
                )

    files = sorted(commands_dir.glob("*/*.yaml")) if commands_dir.is_dir() else []
    if not files:
        errors.append(f"no command YAML under {commands_dir}")
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    cmd_ids: dict[str, Path] = {}
    alias_owners: dict[str, list[str]] = defaultdict(list)
    records: list[tuple[Path, dict]] = []

    for path in files:
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        try:
            raw = load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {exc}")
            continue
        if not isinstance(raw, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue
        cid = raw.get("id")
        if isinstance(cid, str):
            if cid in cmd_ids:
                errors.append(f"{rel}: duplicate command id {cid!r}")
            else:
                cmd_ids[cid] = path
            for alias in raw.get("aliases") or []:
                if isinstance(alias, str) and alias.strip():
                    alias_owners[alias].append(cid)
        records.append((path, raw))

    # Duplicate aliases across distinct commands.
    for alias, owners in sorted(alias_owners.items()):
        uniq = sorted(set(owners))
        if len(uniq) > 1:
            errors.append(
                f"alias {alias!r} claimed by multiple commands: {', '.join(uniq)}"
            )

    # Alias equal to another command id is allowed for cross-platform synonyms
    # (e.g. PowerShell Get-ChildItem alias `ls`) — notice only.
    for alias, owners in sorted(alias_owners.items()):
        if alias in cmd_ids and cmd_ids[alias].stem not in owners:
            notices.append(
                f"alias {alias!r} on {', '.join(owners)} also matches command id "
                f"{alias!r} (cross-platform synonym; OK)"
            )

    for path, raw in records:
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        cid = raw.get("id")
        cmd_risk = raw.get("risk")

        for rid in raw.get("related") or []:
            if rid == cid:
                errors.append(f"{rel}: related must not include self")
            elif rid not in cmd_ids:
                errors.append(f"{rel}: related unknown command id {rid!r}")

        for i, ex in enumerate(raw.get("examples") or []):
            if not isinstance(ex, dict):
                continue
            command = ex.get("command") or ""
            if not isinstance(command, str):
                continue
            ex_risk = ex.get("risk") or cmd_risk
            elevated = ex.get("requires_elevated")
            if elevated is None:
                elevated = raw.get("requires_elevated")

            for pat, label in UNSAFE_PATTERNS:
                if pat.search(command):
                    if ex_risk in (None, "safe", "caution"):
                        errors.append(
                            f"{rel}: examples[{i}] matches unsafe pattern {label!r} "
                            f"but risk={ex_risk!r} (need dangerous|destructive)"
                        )
                    if not has_bilingual_warnings(ex):
                        errors.append(
                            f"{rel}: examples[{i}] matches unsafe pattern {label!r} "
                            "but has no bilingual warnings[]"
                        )

            for pat, label in WIPE_PATTERNS:
                if pat.search(command) and is_real_wipe(command, label):
                    if ex_risk != "destructive":
                        errors.append(
                            f"{rel}: examples[{i}] matches wipe pattern {label!r} "
                            f"but risk={ex_risk!r} (need destructive)"
                        )
                    if not elevated:
                        errors.append(
                            f"{rel}: examples[{i}] matches wipe pattern {label!r} "
                            "but requires_elevated is not true"
                        )
                    if not has_bilingual_warnings(ex):
                        errors.append(
                            f"{rel}: examples[{i}] matches wipe pattern {label!r} "
                            "but has no bilingual warnings[]"
                        )

            # Destructive examples should carry explicit warnings when present.
            if ex_risk == "destructive" and not has_bilingual_warnings(ex):
                # Allow non-wipe destructive (e.g. rm file) with notice only —
                # wipe class already hard-failed above.
                if not any(p.search(command) for p, _ in WIPE_PATTERNS + UNSAFE_PATTERNS):
                    notices.append(
                        f"{rel}: examples[{i}] risk=destructive without warnings[]"
                    )

            # Never silently treat examples as verified via flags.
            if ex.get("verified") is True:
                errors.append(
                    f"{rel}: examples[{i}].verified is not a schema field and "
                    "must not invent verification"
                )

        # Draft commands must not claim verified flags (also in validate_catalog).
        if (raw.get("verification") or {}).get("status") == "draft":
            for i, flag in enumerate(raw.get("flags") or []):
                if isinstance(flag, dict) and flag.get("verified") is True:
                    errors.append(
                        f"{rel}: flags[{i}].verified cannot be true while draft"
                    )

    # Tasks / profiles: no fake verified without sources.
    for kind, directory in (("task", TASKS_DIR), ("profile", PROFILES_DIR)):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.yaml")):
            rel = path.relative_to(ROOT)
            try:
                raw = load_yaml(path)
            except yaml.YAMLError as exc:
                errors.append(f"{rel}: YAML parse error: {exc}")
                continue
            if not isinstance(raw, dict):
                continue
            ver = raw.get("verification") or {}
            if ver.get("status") == "verified":
                if not (ver.get("sources") or []):
                    errors.append(f"{rel}: verified {kind} requires sources")
                if not ver.get("last_reviewed"):
                    errors.append(f"{rel}: verified {kind} requires last_reviewed")

    if notices:
        print(f"NOTICE: {len(notices)} soft finding(s)")
        for n in notices:
            print(f"  - {n}")

    if errors:
        print(f"FAIL: {len(errors)} security/compat issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK: security gates passed on {len(cmd_ids)} commands "
        f"(minisign pubkey present; no private keys)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
