# Nova-Commands coverage matrix (NV-103)

Last updated: 2026-11-10  
Scope rule: common, useful, **source-cited** commands — not every binary on every OS.  
Bank ≠ Store catalog ≠ local PATH discovery.

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
| Server security checklist | **NEW** tasks+profile+concept | shared | shared | notes | partial | partial | partial |

## Counts (pre → target this PR)

| Kind | Before (main) | After this PR |
|------|---------------|---------------|
| Commands | 256 | **267** (+11 high-priority drafts; several reviewed rows enriched) |
| Tasks | 26 | **36** (+10 sequential `security-check-*` stages) |
| Profiles | 13 | **14** (+`server-security-checklist`; homelab linked) |
| Concepts | 20 | **21** (+`server-security-checklist`) |
| Search entries | 315 | **338** |
| Coverage doc | absent | this file + in-repo `docs/COVERAGE_MATRIX.md` |
| `content_sha256` | `e17437d6…` | `406fe04002c47c592009c71f6d9dbb1f0ec7c9faa6c19165f58bebe29265b716` |

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
