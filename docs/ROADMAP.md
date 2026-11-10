# Roadmap — Nova-Commands

Status reflects **merged `main` after [#30](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/30)** (IA fill) plus trust-audit honesty fixes.  
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
| Commands | 267 |
| Concepts | 21 (reviewed **1** / draft **20**) |
| Tasks | 36 (`draft`) |
| Profiles | 14 (`draft`) |
| Search entries | 338 |
| OS registry | 11 |
| Package managers | 60 |
| Catalog `schema_version` | 2 |
| commands verified / reviewed / draft | 26 / 105 / 136 |
| `content_sha256` | `406fe04002c47c592009c71f6d9dbb1f0ec7c9faa6c19165f58bebe29265b716` |

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
| Nova re-vendor after trust-audit digest bump | Separate Nova PR when `content_sha256` changes |
| Mass `verified` promotions | Human review only — CI never auto-verifies |
| Concept human spot-check → selective `reviewed`/`verified` | Agent-authored articles stay `draft` until maintainer review |
| illumos / Solaris / AIX **command banks** | Metadata skeletons only |
| Full vendor appliance CLIs | Proxmox `qm`, RouterOS, Cisco IOS, … not claimed |
| OpenTofu / Pulumi / Nomad / full observability CLIs | Not in bank yet |
| Local discovery implementation | Contract only in this repo; Nova owns runtime |
| Soft safety notices | Destructive `rm`/`fdisk`/`parted`/`userdel` examples now carry bilingual `warnings[]`; wipe-class hard gates unchanged |

## Near-term priorities

1. Human review of high-traffic `draft` Windows/macOS/BSD/PM rows → `reviewed` / selective `verified`
2. Deepen task implementations where a platform still falls back to notes
3. Nova client consume PR for schema v2 + tasks/profiles kinds (if not already)
4. First signed `catalog-v*` Release when secret is configured
5. Optional deepen: appliance CLIs, additional cloud/IaC tools — as sourced drafts only
6. Close remaining gaps listed in [COVERAGE_MATRIX.md](COVERAGE_MATRIX.md) (VPN/`wg`, certbot, macOS/Windows admin depth) without inventing flags

## Docs map

| Doc | Role |
|-----|------|
| [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md) | Support matrix / registries |
| [SCHEMA_MIGRATION_V2.md](SCHEMA_MIGRATION_V2.md) | v1→v2 + release policy |
| [SECURITY_MODEL.md](SECURITY_MODEL.md) | Risk / trust model |
| [catalog-signing.md](catalog-signing.md) | Signed Releases |
| [NOVA_INTEGRATION.md](NOVA_INTEGRATION.md) | Client consume contract |
| [DATA_SCHEMA.md](DATA_SCHEMA.md) | Live schema policy |
| [COVERAGE_MATRIX.md](COVERAGE_MATRIX.md) | Area×platform gaps (honest) |
| [SERVER_SECURITY_CHECKLIST.md](SERVER_SECURITY_CHECKLIST.md) | 10-stage Sunucu güvenlik kontrolü |

## Non-goals

- Inventing package names, flags, or `verified` statuses
- Executing catalog commands on CI or contributor machines “to prove” YAML
- Rotating `keys/minisign.pub` or changing LICENSE without a dedicated review
