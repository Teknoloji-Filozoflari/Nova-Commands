# Sunucu güvenlik kontrolü / Server security checklist

Teaching guide for Nova Komut Rehberi. **Documentation only — never auto-run.**

Profile: `profiles/server-security-checklist.yaml`  
Concept: `concepts/server-security-checklist.yaml`  
Tasks: `tasks/security-check-*.yaml` (10 sequential stages)

## Checklist states (Nova local UI)

| State | Meaning |
|-------|---------|
| `unchecked` | Not assessed yet |
| `ok` | Read-only checks look healthy for this host |
| `review` | Suspicious or unclear — needs human judgment |
| `na` | Not applicable (e.g. no Docker) |

States are **not** stored in this bank; Nova keeps them per host locally.

## Stages (order matters)

| # | Task id | Focus |
|---|---------|--------|
| 1 | `security-check-os-accounts` | OS/version + sessions |
| 2 | `security-check-updates` | Pending updates (list only) |
| 3 | `security-check-ssh` | sshd status + effective settings |
| 4 | `security-check-firewall-ports` | Local listeners + firewall status |
| 5 | `security-check-users-sudo` | Human users + sudoers check |
| 6 | `security-check-docker` | Containers / privileged / publish |
| 7 | `security-check-reverse-proxy-tls` | nginx/caddy test + cert dates |
| 8 | `security-check-dns-vpn` | Resolvers; VPN often `na`/gap |
| 9 | `security-check-backup-restore` | Snapshot list + integrity + staging restore |
| 10 | `security-check-logs-incident` | journal/auth errors; no log wipe |

Each task documents: why, read-only diagnostic + privilege, **separate platform-tagged implementations**, healthy vs suspicious notes, outage risk, optional fix with backup/verify/rollback, official sources, `verification.status`.

## Platform honesty (NV-106)

| Stage | Linux | Windows | macOS | BSD |
|-------|-------|---------|-------|-----|
| OS/accounts | hostnamectl | Get-ComputerInfo | sw_vers | uname/who |
| Updates | pacman/apt/dnf + NixOS `nixos-rebuild` | winget list | softwareupdate | pkg + freebsd-update |
| SSH | systemctl + sshd -T | Get-Service sshd | launchctl + sshd | service + sshd |
| Firewall/ports | ss + ufw **or** firewalld (split) | Get-NetTCPConnection + netsh | lsof + pfctl note | netstat + pfctl |
| Users/sudo | getent/visudo | whoami groups (no sudo) | dscl + sudo | doas ≠ sudo |
| Docker | systemctl + docker | Docker Desktop CLI | Docker Desktop CLI | **na** (jails ≠ Docker) |
| Proxy/TLS | nginx/caddy + openssl | openssl/curl (:443) | nginx?/openssl | nginx?/openssl |
| DNS/VPN | resolvectl | ipconfig /all | scutil --dns | resolv.conf + dig |
| Backup | restic | restic (wbadmin gap) | restic | restic |
| Logs | journalctl | Get-WinEvent | `log show` | dmesg/last/newsyslog |

Still missing / intentional gaps: WireGuard/`wg` bank, macOS Application Firewall (`socketfilterfw`), Windows `Get-LocalUser`/`wbadmin`, OpenBSD `rcctl` depth, certbot/fail2ban, BSD jails checklist.

## Hard non-goals

- No remote port scans or “attack” steps
- No blind `PasswordAuthentication no` / firewall open/close without warnings and a second session
- No secret-bearing examples
- Distro honesty: pacman ≠ apt ≠ dnf; ufw ≠ firewalld ≠ pf ≠ netsh; Nix ≠ NixOS; doas ≠ sudo

## Related

- [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) — remaining gaps
- [SERVER_ADMINISTRATION.md](./SERVER_ADMINISTRATION.md) — broader server bank scope
- [safety.md](./safety.md) — risk model
