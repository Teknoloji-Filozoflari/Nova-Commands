# Server administration scope (Faz 7–8)

This document describes **what the command bank covers today** for server,
network, and DevOps operations. It is not a runbook and does not execute
commands.

## Covered areas (draft command banks)

| Area | Examples in bank | Notes |
|------|------------------|-------|
| Network diagnostics | `ip`, `ss`, `tcpdump`, `nmap`, `mtr`, `ethtool` | Authorized targets only for scans |
| Remote access | `ssh`, `scp`, `sftp`, … | Existing security category |
| Services | `systemctl`, BSD `service`/`rcctl`, … | Prior fazes |
| Containers | `docker`, `podman`, `nerdctl`, `crictl` | Runtime ≠ orchestrator |
| Kubernetes | `kubectl`, `helm` | Wrong kubeconfig context risk |
| Virtualization | `virsh`, `qemu-img` | Not the same as containers |
| Web / reverse proxy | `nginx`, `caddy` | Prefer config test before reload |
| Databases (clients) | `mysql`, `redis-cli`, `psql`, `sqlite3` | No passwords on argv |
| Backup | `restic`, `borg`, `rclone`, `rsync` | No secret-bearing examples |
| Cloud CLI | `aws`, `az`, `gcloud` | No API keys in YAML |
| IaC / automation | `terraform`, `ansible`, `gh` | `apply`/playbooks mutate systems |

## Explicit non-claims

- Registry presence ≠ installed on a host ([dual-concept.md](dual-concept.md)).
- AI-authored Faz 7 records stay `verification.status: draft` until human review.
- Vendor appliance CLIs (Proxmox `qm`, MikroTik, Cisco IOS, …) are **not**
  first-class command banks yet (metadata may exist as `planned`/`skeleton`).
- Tasks (`tasks/`) and server **profiles** (`profiles/`) are Faz 8 teaching
  collections: multi-OS intents + role maps. They do **not** auto-run commands
  and are not yet in the signed catalog hash (Faz 9 indexes them).

## Profiles (Faz 8)

| Profile | Focus |
|---------|--------|
| `linux-server` | General Linux admin (services, net, disk, SSH) |
| `debian-server` / `fedora-server` / `arch-server` | Distro-specific PM + firewall |
| `windows-server` | PowerShell services / net / WinGet |
| `freebsd-server` | pkg / service / sysrc / pfctl |
| `homelab` / `docker-host` / `kubernetes` | Self-host + containers + k8s |
| `web-server` / `database-server` / `nas-server` / `virtualization-host` | Role maps |

## Safety

See [safety.md](safety.md) and [SECURITY.md](../SECURITY.md). Destructive
storage/network examples use placeholders; CI does not execute dangerous
commands to “verify” the bank.
