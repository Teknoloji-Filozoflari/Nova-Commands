# Nova-Commands coverage matrix (NV-103 / NV-121 / NV-123)

Last updated: 2026-11-11  
Scope rule: common, useful, **source-cited** commands — not every binary on every OS.  
Bank ≠ Store catalog ≠ local PATH discovery.  
Counts below must match committed `metadata/search-index.json` / `manifest.json`
(see `tests/test_doc_snapshot_counts.py`).
NV-121 expands honest multi-distro task/command tags (no invented package names; draft stays draft).
NV-123 separates **topic guides** from **command records** (`docs/TEACHABLE_TOPICS.md`).

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

| Area | Arch | Debian/Ubuntu | Fedora/RHEL | openSUSE | Alpine | NixOS | Void | Gentoo | Windows | macOS | BSD |
|------|------|---------------|-------------|----------|--------|-------|------|--------|---------|-------|-----|
| Shell fundamentals | R + drafts | R | R | R (shared GNU) | R/D (busybox notes thin) | R (shared) | R/D | R/D | D (PS/cmd) | R/D (zsh) | R |
| Files / search / text | V/R | V/R | V/R | V/R | V/R (utils may be busybox) | V/R | V/R | V/R | D (Get-*) | R (BSD utils) | R |
| Users / perms / process | V/R | V/R | V/R | V/R | V/R | V/R | V/R | V/R | D (icacls/…) | D (dscl) | R (doas) |
| Services / logs | R systemd | R systemd | R systemd | R systemd | D OpenRC (`rc-status`) | R systemd + nixos-rebuild | D runit (`sv`) | D OpenRC | D (Get-Service/…) | D (launchctl) | D (service/rcctl) |
| Packages / updates | R pacman | R apt | R dnf | D zypper | D apk | D nixos-rebuild (≠ nix) | D xbps | D emerge | D winget | D brew/softwareupdate | D pkg |
| Network / SSH / TLS | R | R | R | R | R/D | R/D | R/D | R/D | D | D | D |
| Firewall | D nft/ufw optional | D ufw | D firewalld | D firewalld | D nft | D nft/systemd | D nft | D nft | D netsh | D pfctl | D pfctl |
| Storage / backup | R/D | R/D | R/D | R/D | D thin | D thin | D thin | D thin | D | D | D (zfs) |
| Git / dev basics | R | R | R | R | R/D | R/D | R/D | R/D | D | D (xcode) | R |
| Containers / proxy | D/R | D (`docker.io`) | D/R | D | D | — | — | — | — | — | D (jails) |
| Server security checklist | pacman path | apt path | dnf path | zypper path | apk path | nixos-rebuild | xbps path | emerge path | Win paths | macOS paths | BSD paths |

## Counts (committed catalog — current)

| Kind | Count | Notes |
|------|------:|-------|
| Commands | **270** | +OpenRC `rc-status`/`rc-service` + Void `sv` (NV-121) |
| Tasks | **36** | includes sequential `security-check-*` stages |
| Profiles | **14** | includes `server-security-checklist` |
| Concepts | **29** | NV-123 topic guides (21 upgraded + 8 new category guides) |
| Search entries | **349** | `metadata/search-index.json` `entry_count` |
| `content_sha256` | `eb15d7f851993865a70094a66d8d08df3f9f230738d24efcca5b4e86c9d31844` | must match catalog/manifest/search-index |

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
11. **OpenRC/runit depth** — `rc-status`/`rc-service`/`sv` are new drafts; enable/add runlevels and logging daemons still thin.
12. **Non-systemd log ecosystems** — `/var/log/messages` path documented; distro-specific syslog/busybox `logread` (OpenWrt) not first-class.
13. **helm / nerdctl / terraform / aws / caddy package_refs** — Arch-known only with honesty notes; no invented multi-distro package names.
14. **Guix System / Solus / Slackware / OpenWrt task implementations** — PM commands exist; everyday tasks rarely tag those distros yet.

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
