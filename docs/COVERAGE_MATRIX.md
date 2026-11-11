# Nova-Commands coverage matrix (NV-103)

Last updated: 2026-11-11  
Scope rule: common, useful, **source-cited** commands — not every binary on every OS.  
Bank ≠ Store catalog ≠ local PATH discovery.  
Counts below must match committed `metadata/search-index.json` / `manifest.json`
(see `tests/test_doc_snapshot_counts.py`).

## Legend

| Cell | Meaning |
|------|---------|
| **V** | Has `verified` command rows (human-reviewed) |
| **R** | Has `reviewed` rows |
| **D** | Mostly/only `draft` |
| **—** | Intentionally thin / out of near-term scope |
| **Gap** | High-value missing content tracked below |

Platform honesty: Linux distro families are not interchangeable; BSD ≠ Linux; Nix ≠ NixOS;
PowerShell cmdlets are not Linux aliases.

## Area × platform (honest snapshot)

| Area | Linux (Arch-first) | Debian/Ubuntu | Fedora/RHEL | Nix/NixOS | Windows | macOS | BSD |
|------|--------------------|---------------|-------------|-----------|---------|-------|-----|
| Shell fundamentals | R + new drafts | R | R | — | D (PS/cmd) | R/D (zsh) | R |
| Files / search / text | V/R | V/R | V/R | — | D (Get-*) | R (BSD utils differ) | R |
| Users / perms / process | V/R | V/R | V/R | — | D (icacls/…) | D (dscl) | R (doas) |
| systemd / services / logs | R | R | R | NixOS via nixos-rebuild | D (Get-Service/…) | D (launchctl) | D (service/rcctl) |
| apt / dpkg | — | R | — | — | — | — | — |
| pacman | R (preferred) | — | — | — | — | — | — |
| dnf / rpm | — | — | R | — | — | — | — |
| Nix (+ NixOS distinct) | R/D + concept | R/D | R/D | R/D | — | R/D (nix) | — |
| Network / SSH / TLS | R | R | R | — | D | D | D |
| Storage / backup | R/D | R/D | R/D | — | D | D | D (zfs) |
| Git / dev basics | R | R | R | — | D | D (xcode) | R |
| Containers / proxy | D/R | D/R | D/R | — | — | — | D (jails) |
| Server security checklist | platform-split `security-check-*` | distro-aware | distro-aware | nixos-rebuild (≠ nix) | Win paths filled | macOS paths filled | BSD paths filled (Docker=na/jails gap) |

## Counts (committed catalog — current)

| Kind | Count | Notes |
|------|------:|-------|
| Commands | **267** | |
| Tasks | **36** | includes sequential `security-check-*` stages |
| Profiles | **14** | includes `server-security-checklist` |
| Concepts | **21** | includes `server-security-checklist` |
| Search entries | **338** | `metadata/search-index.json` `entry_count` |
| `content_sha256` | `a31207ef405b8319e4db0602f2bce599213a1fbf400055156b5139584108976f` | must match catalog/manifest/search-index |

### Historical (NV-103 teachable bank, before that merge)

On pre–NV-103 `main` the bank was commands **256** / tasks **26** / profiles **13** /
concepts **20** / search **315**, digest `e17437d6…`. Treat **315** as history only —
not a current-status figure.

## High-priority gaps still remaining after this PR

Honest remainder (not an infinite encyclopedia):

1. **Mass `verified` promotions** — human-only; many enrichments stay `reviewed`/`draft`.
2. **Windows Server depth** — DISM/SFC/diskpart/schtasks still thin drafts; more Graded PS examples needed.
3. **macOS admin** — `softwareupdate`, `launchctl`, `diskutil`, `networksetup` still draft/thin.
4. **BSD service/firewall teaching** — present but mostly draft; OpenBSD `rcctl` vs FreeBSD `service` deepen.
5. **Firewall write-path safety** — `ufw`/`nft`/`iptables` drafts; checklist uses **read-only** diagnostics only.
6. **VPN tooling** — WireGuard/`wg`, OpenVPN client banks thin/absent; checklist DNS/VPN stage uses resolvers + notes.
7. **Productivity / AI-LLM categories** — still out of taxonomy (master optional).
8. **Appliance CLIs** — Proxmox `qm`, RouterOS, etc. explicitly not claimed.
9. **illumos/Solaris/AIX** — registry skeletons only.
10. **certbot / ACME / fail2ban** — common homelab tools not yet first-class (TLS stage uses openssl/nginx/caddy).

## Security checklist states (Nova local UI)

Content bank publishes stages; **Nova** stores per-host checklist state locally:

| State | Meaning |
|-------|---------|
| `unchecked` | Not yet assessed |
| `ok` | Read-only checks look healthy for this host |
| `review` | Suspicious/unknown — needs human judgment |
| `na` | Not applicable (e.g. no Docker on host) |

No auto-run. No port-scan/attack steps. Optional fixes always require backup → change → verify → rollback notes.

## Product boundaries

- **Bank**: curated YAML here.
- **Store**: installable apps (Nova-Store) — different catalog.
- **Local PATH**: discovery contract only; presence ≠ verified knowledge.
