# Roadmap — Nova-Commands

Status reflects **merged `main` after [#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23)** (Faz 10 CI/security).  
Do not treat registry rows or `draft` YAML as “full platform support.”

## Cross-platform expansion (master §22)

| Faz | Scope | Status | PR |
|-----|--------|--------|-----|
| 0 | Audit + migration risks | Done (report-only) | — |
| 1 | Platform metadata registries | Done | [#14](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/14) |
| 2 | Command schema v2 dual-path | Done | [#15](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/15) |
| 3 | v1→v2 live migrate | Done | [#16](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/16) |
| 4 | Broader Linux PMs | Done | [#17](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/17) |
| 5 | Windows + macOS banks | Done | [#18](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/18) |
| 6 | BSD family banks | Done | [#19](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/19) |
| 7 | Server / network / DevOps | Done | [#20](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/20) |
| 8 | Tasks + profiles | Done | [#21](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/21) |
| 9 | Search / catalog index | Done | [#22](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/22) |
| 10 | CI / test / security | Done | [#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23) |
| 11 | Docs + migration / release policy | This track | — |

## Live bank snapshot

| Metric | Value |
|--------|------:|
| Commands | 256 |
| Concepts | 20 |
| Tasks | 21 (`draft`) |
| Profiles | 13 (`draft`) |
| Search entries | 310 |
| OS registry | 11 |
| Package managers | 60 |
| Catalog `schema_version` | 2 |
| verified / reviewed / draft | 26 / 105 / 125 |
| `content_sha256` | `7b24390eb92de6cda76b330d61fd34dcdb304afe27c1595355621717b653bf54` |

## Done (honest)

- Schema **v2** live bank + idempotent `migrate_v1_to_v2.py`
- Separate OS / distro / shell / PM / server / cloud registries
- Meaningful **draft** coverage for Windows, macOS, BSD, broader Linux PMs, server/DevOps
- Intent **tasks** + server **profiles**, indexed into catalog/search/manifest
- Static security validator + SHA-pinned multi-OS CI (Python tooling only)
- minisign public trust anchor preserved; publish dry-runs without secret

## Explicitly not done / follow-ups

| Item | Notes |
|------|--------|
| Production signed `catalog-v*` Release | Needs maintainer `MINISIGN_SECRET_KEY` + tag; workflow dry-runs until then |
| Nova re-vendor of `7b24390e…` | Separate Nova PR after this bank lands on consumers |
| Mass `verified` promotions | Human review only — CI never auto-verifies |
| illumos / Solaris / AIX **command banks** | Metadata skeletons only |
| Full vendor appliance CLIs | Proxmox `qm`, RouterOS, Cisco IOS, … not claimed |
| OpenTofu / Pulumi / Nomad / full observability CLIs | Not in bank yet |
| Local discovery implementation | Contract only in this repo; Nova owns runtime |
| Soft safety notices | e.g. some `rm`/`fdisk` destructive examples still lack optional `warnings[]` (hard wipe-class gates already enforced) |

## Near-term priorities

1. Human review of high-traffic `draft` Windows/macOS/BSD/PM rows → `reviewed` / selective `verified`
2. Deepen task implementations where a platform still falls back to notes
3. Nova client consume PR for schema v2 + tasks/profiles kinds (if not already)
4. First signed `catalog-v*` Release when secret is configured
5. Optional deepen: appliance CLIs, additional cloud/IaC tools — as sourced drafts only

## Docs map

| Doc | Role |
|-----|------|
| [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md) | Support matrix / registries |
| [SCHEMA_MIGRATION_V2.md](SCHEMA_MIGRATION_V2.md) | v1→v2 + release policy |
| [SECURITY_MODEL.md](SECURITY_MODEL.md) | Risk / trust model |
| [catalog-signing.md](catalog-signing.md) | Signed Releases |
| [NOVA_INTEGRATION.md](NOVA_INTEGRATION.md) | Client consume contract |
| [DATA_SCHEMA.md](DATA_SCHEMA.md) | Live schema policy |

## Non-goals

- Inventing package names, flags, or `verified` statuses
- Executing catalog commands on CI or contributor machines “to prove” YAML
- Rotating `keys/minisign.pub` or changing LICENSE without a dedicated review
