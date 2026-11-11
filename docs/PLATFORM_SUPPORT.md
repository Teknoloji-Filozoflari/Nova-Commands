# Platform support (metadata registries)

Faz 1 introduced **additive** platform metadata. These registries describe
operating systems, distributions, shells, package managers, and related
concepts as **separate models**.

**Post–[#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23)
(Faz 10 on `main`):** live command bank is schema **v2**; tasks/profiles are
indexed (Faz 9); CI/security gates are static. Docs/roadmap polish is Faz 11
([ROADMAP.md](ROADMAP.md)).

**Faz 3:** commands may cite registry ids via `operating_systems`,
`package_refs.manager` / `distributions`, and expanded `shells`. Presence of a
registry id is still **not** proof of local install or full coverage. See
[DATA_SCHEMA.md](DATA_SCHEMA.md) and [SCHEMA_MIGRATION_V2.md](SCHEMA_MIGRATION_V2.md).

## Snapshot counts (committed catalog)

| Registry / bank | Count | Notes |
|-----------------|------:|-------|
| Operating systems | 11 | linux, windows, macos, freebsd, openbsd, netbsd, dragonflybsd, illumos, solaris, aix, android |
| Distributions | 36 | includes Windows/macOS/BSD product rows |
| Shells | 15 | includes powershell / windows-powershell / cmd / nushell |
| Package managers | 60 | system + language + Flatpak/Snap/AppImage |
| Server platforms | 23 | many `planned` / `experimental` without command banks |
| Cloud providers | 6 | aws, azure, gcp, oci, digitalocean, hetzner |
| Execution environments | 11 | WSL, Termux, container, … |
| Architectures | 8 | |
| Commands / concepts / tasks / profiles | 270 / 30 / 36 / 14 | tasks+profiles all `draft`; concepts mostly `draft` |
| Search entries | 350 | `entry_count` in `metadata/search-index.json` (= commands+concepts+tasks+profiles) |
| `content_sha256` | `e6466b7f…` | full digest in `metadata/manifest.json` |

## Dual concept (unchanged)

| Concept | Meaning |
|---------|---------|
| **Command bank** | Curated YAML under `commands/` (+ concepts) |
| **Local discovery** | Host PATH / install state — contract only in this repo |

Platform registries sit with the **bank metadata**. Presence of a registry id
is **not** proof that the command is installed on a machine, and is **not** a
claim that every command is verified on that platform.

See [dual-concept.md](dual-concept.md) and [local-discovery-contract.md](local-discovery-contract.md).

## Registry files

| File | Role |
|------|------|
| `metadata/operating-systems.yaml` | OS families / products |
| `metadata/distributions.yaml` | Distros & product editions (`ID_LIKE` / parent hints) |
| `metadata/shells.yaml` | Shells / interpreters |
| `metadata/package-managers.yaml` | Independent PM catalog (not nested under one OS) |
| `metadata/architectures.yaml` | CPU architectures |
| `metadata/execution-environments.yaml` | WSL, Termux, containers, … |
| `metadata/server-platforms.yaml` | Hypervisor / NAS / appliance / orchestration |
| `metadata/cloud-providers.yaml` | Cloud CLI providers |
| `metadata/support-levels.yaml` | `planned` … `full` / `unsupported` labels |

Schemas live under `schema/*` with matching names
(`operating-system.schema.json`, …).

## Support levels

Entries use `support_level` referencing `support-levels.yaml`:

- **planned** — model ready; little or no command content
- **experimental** — skeleton / limited draft
- **partial** — some coverage (e.g. existing Linux bank overlap)
- **full** — first-class expansion target (not “complete”)
- **unsupported** — reference only

`status` on registry rows is `skeleton` or `draft` in Faz 1. **`verified` is
not used** for seed metadata.

## Validation

```bash
python3 scripts/validate_platform_registries.py
python3 scripts/validate_catalog.py   # also invokes platform soft-check
```

Soft checks: schema conformance, unique ids, and cross-refs (OS ↔ distro ↔ PM,
support levels). Live `commands/` may omit registry citations; citing an id is
optional and does not imply every example was run on that OS. Schema v2 fields
`package_refs` / `operating_systems` are the preferred cite path when used.

## Arch / pacman

Per project preference, **Arch Linux** and **pacman** are first-class in the
package-manager and distribution registries (install-hint policy for Arch
family remains pacman-first). Schema v2 `package_refs` should keep pacman
first-class for Arch-family install hints.

## Faz 4 Linux PM coverage

Command bank now includes draft records for broader Linux package managers
(zypper, apk, emerge, xbps-*, eopkg, slackpkg/pkgtools, nix*, guix, opkg,
rpm-ostree) plus expanded comparison docs. Registry rows for those PMs are
`status: draft` / `support_level: partial` where command content exists.
**No `verified` without human review.** LICENSE and `keys/minisign.pub` unchanged.

## Faz 5 Windows / macOS command banks

Live bank now includes **draft** Windows and macOS command records (schema v2):

- **Windows:** PowerShell cmdlets (separate from CMD), CMD/executables (`ipconfig`,
  `sc.exe`, …), WinGet, admin/UAC notes via `security` + example `privilege`.
- **macOS:** Homebrew / MacPorts, `launchctl`, `diskutil`, `networksetup`,
  `softwareupdate`, Keychain/`security`, Xcode CLT helpers, etc.
- Existing Unix tools (`sed`, `tar`, `find`, `stat`, `date`) note **BSD vs GNU**
  differences for macOS without changing verification status.

Registry rows for `winget` / `homebrew` / `macports` and shells
`powershell` / `windows-powershell` / `cmd` are `status: draft` /
`support_level: partial`. **No fake `verified`.** LICENSE and
`keys/minisign.pub` unchanged.

## Faz 6 BSD command banks (+ Unix extensibility metadata)

Live bank now includes **draft** BSD-family command records (schema v2):

- **FreeBSD:** `pkg`, Ports (`ports`), `freebsd-update`, `service`, `sysrc`, jails
  (`jls` / `jexec`), ZFS (`zfs` / `zpool`), plus shared `ifconfig` / `newsyslog` /
  `pfctl` where applicable.
- **OpenBSD:** `pkg_add`, `rcctl`, `doas`, `pfctl` (PF ≠ Linux nft/iptables).
- **NetBSD:** `pkgin`, `pkgsrc` (source tree ≠ binary pkgin).
- **DragonFly:** OS/PM registry rows only for the similarly named `pkg` — **not**
  aliased to FreeBSD `pkg` (separate ecosystems).
- **Service model:** BSD `service` / `sysrc` / `rcctl` are **not** `systemctl`.
- **netstat:** Windows owns id `netstat`; BSD family uses id `netstat-bsd`
  (`name: netstat`).

Registry rows for FreeBSD/OpenBSD/NetBSD/DragonFly OS + release distros and BSD
PMs are `status: draft` / `support_level: partial`. **illumos / Solaris / AIX**
remain extensibility skeletons (`experimental`) — **no fake command banks**.
**No fake `verified`.** LICENSE and `keys/minisign.pub` unchanged.

## Faz 7 server / network / DevOps deepen

Live bank adds **draft** server-oriented command records (schema v2) plus five
additive categories: `virtualization`, `backup`, `databases`, `cloud`, `devops`.

- **Network:** `tcpdump`, `nmap`, `mtr`, `ethtool` (authorized-target / read-first habits).
- **Containers / orchestration:** `nerdctl`, `crictl`, `kubectl`, `helm`.
- **Virtualization:** `virsh`, `qemu-img` (libvirt/QEMU; not equated with containers).
- **Web / proxy (system):** `nginx`, `caddy` (config test / version examples).
- **Databases (clients):** `mysql`, `redis-cli` (`psql`/`sqlite3` already exist).
- **Backup:** `restic`, `borg`, `rclone` (no secret-bearing examples).
- **Cloud CLI:** `aws`, `az`, `gcloud` (no API keys / tokens in YAML).
- **DevOps / IaC:** `terraform`, `ansible`, `gh`.

Concepts: `kubernetes`, `virtualization`, `infrastructure-as-code`, `reverse-proxy`,
`backup`, `databases`, `cloud` (all `draft`). Cloud provider rows for aws/azure/gcp
and server platforms kvm/qemu/libvirt/docker-engine/kubernetes are
`status: draft` / `support_level: partial` where command content exists.
**No fake `verified`.** LICENSE and `keys/minisign.pub` unchanged.

## Faz 8 tasks + profiles

Live trees (all `draft`):

- **`tasks/`** — intent → multi-platform implementations (e.g. `show-local-ip`,
  `check-disk-space`, `update-system`, `inspect-container`). Implementations
  reference existing **command** ids only; task ids never collide with commands.
- **`profiles/`** — guiding server/role collections (e.g. `linux-server`,
  `arch-server`, `docker-host`, `kubernetes`, `homelab`). Not auto-executed
  scripts.

Validated by `scripts/validate_tasks_profiles.py` (wired into
`validate_catalog.py`). Indexed into `catalog.json` / `search-index.json` /
`manifest.json` with `task_count` / `profile_count` (Faz 9); included in
`content_sha256`. Arch/pacman preference preserved on update/install tasks.
**No fake `verified`.** LICENSE / `keys/minisign.pub` unchanged.

## Faz 9 — catalog / search indexing

`tasks/` and `profiles/` are loaded into `catalog.json`, `search-index.json`,
and `manifest.json` (`task_count` / `profile_count` / OS+PM registry counts).
`content_sha256` hashes `{schema_version, kind, commands, concepts, tasks,
profiles}`. Search may prefer a platform when `--os` is passed to
`scripts/search_bank.py`. **No new platform claims** beyond the YAML already in
tree.

## Faz 10 — CI / security (merged #23)

- Multi-OS GitHub Actions matrix runs **Python validate + pytest only**
- `scripts/validate_security.py` hard gates wipe-class warnings, related refs,
  aliases, and minisign pubkey presence
- Third-party Actions pinned to full commit SHAs
- Verification counts unchanged; minisign pubkey unchanged

## Faz 11 — documentation

README (EN/TR), this matrix, [ROADMAP.md](ROADMAP.md),
[SECURITY_MODEL.md](SECURITY_MODEL.md), and migration/release notes are kept
aligned with the committed catalog. **No fake features** — unfinished items
stay listed as unfinished.

## Out of scope (still)

- illumos / Solaris / AIX **command banks** (metadata only in Faz 6)
- Full vendor appliance CLIs (Proxmox `qm`, RouterOS, Cisco IOS, …)
- OpenTofu / Pulumi / Nomad / observability CLIs (follow-up deepen)
- Native Windows `Resolve-DnsName` command bank row (task notes dig fallback)
- Rotating minisign keys / LICENSE changes
- Claiming `support_level: full` means “complete OS coverage”

## Maintainer note

`scripts/_seed_platform_registries.py` produced the initial Faz 1 YAML.
**Registries under `metadata/` are now the source of truth** — do not re-run
the seeder casually (it overwrites). Prefer editing YAML directly.