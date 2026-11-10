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

Each task documents: why, read-only diagnostic + privilege, platforms, healthy vs suspicious notes, outage risk, optional fix with backup/verify/rollback, official sources, `verification.status`.

## Hard non-goals

- No remote port scans or “attack” steps
- No blind `PasswordAuthentication no` / firewall open/close without warnings and a second session
- No secret-bearing examples
- Distro honesty: pacman ≠ apt ≠ dnf; Nix ≠ NixOS

## Related

- [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) — remaining gaps
- [SERVER_ADMINISTRATION.md](./SERVER_ADMINISTRATION.md) — broader server bank scope
- [safety.md](./safety.md) — risk model
