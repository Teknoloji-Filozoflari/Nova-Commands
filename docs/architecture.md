# Architecture (Nova-Commands)

## Principles

1. **Data repo first** — YAML + schema + CI; no runtime daemon here.
2. **Dual concept** — curated bank ≠ local PATH discovery.
3. **Multi-distro** — Arch / Debian-Ubuntu / Fedora-RHEL notes; Arch preference in install hints.
4. **Quality over count** — unknown flags/packages omitted or marked draft.
5. **Safety** — risk labels; no destructive execution to validate.

## Layout

```
commands/<category>/<id>.yaml   # curated entries (schema_version: 2)
concepts/<id>.yaml              # learnable concept articles (TR/EN)
schema/command.schema.json      # v2 — live commands/ bank
schema/command.schema.v2.json   # v2 twin (distinct $id)
schema/command.schema.v1.json   # archived v1
schema/{task,profile,compatibility}.schema.json  # stubs (Faz 8 content)
schema/*.json                   # JSON Schema (Draft 2020-12) + platform regs
fixtures/schema-v2/             # stub/fixture samples (not catalog content)
metadata/categories.yaml        # §8.x taxonomy
metadata/concepts.yaml          # concept registry (+ optional article:)
metadata/operating-systems.yaml # Faz 1+ platform registries (additive)
metadata/distributions.yaml
metadata/shells.yaml
metadata/package-managers.yaml
metadata/architectures.yaml
metadata/execution-environments.yaml
metadata/server-platforms.yaml
metadata/cloud-providers.yaml
metadata/support-levels.yaml
metadata/catalog.json           # aggregate (kind: nova-commands-bank, schema_version 2)
metadata/search-index.json      # flattened search fields
metadata/manifest.json          # counts + deterministic content_sha256
scripts/validate_catalog.py     # CI gate (v2 bank, i18n, concepts, soft gates)
scripts/migrate_v1_to_v2.py     # v1→v2 migration (idempotent)
scripts/validate_platform_registries.py  # soft registry consistency
scripts/validate_schema_v2.py   # live v2 load + stub fixture check
scripts/build_catalog.py        # catalog + index + manifest
docs/                           # contracts + safety + NOVA_INTEGRATION + DATA_SCHEMA
tests/                          # pytest
```

Platform registries keep OS ≠ distribution ≠ shell ≠ package-manager as
separate models. See [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md),
[DATA_SCHEMA.md](DATA_SCHEMA.md), and [SCHEMA_MIGRATION_V2.md](SCHEMA_MIGRATION_V2.md).
Catalog `schema_version` is **2** (live command schema v2).
## Verification pipeline

```
PR → validate_catalog.py → build_catalog.py → pytest → merge
```

`verification.status` is never auto-promoted to `verified` by CI.
`content_sha256` hashes commands+concepts only (excludes `generated_at`).

## Phases (implementation track)

| Phase | Scope |
|-------|--------|
| 1 | Repo scaffold, license, docs, taxonomy, schema |
| 2 | Seed commands + validator + unit tests |
| 3 | CI workflow + catalog build artifact |
| 4 | Dual-concept + local discovery contract docs |
| 5 | Nova consumption + Arch-first package notes |
| 6 | Safety rules + draft/verified enforcement |
| 7 | Concepts metadata + CONTRIBUTING |
| 8 | Concept articles (`concepts/`) + i18n gates |
| 9 | Search index + manifest SHA + NOVA_INTEGRATION |
| 10 | CI/contrib polish (Actions, issue/PR templates, SECURITY) |
| 11+ | Grow coverage; human `verified` promotions |
| 17 | Signed `catalog-v*` Releases (minisign) + selective `verified` |

Signed publish: `docs/catalog-signing.md`, `keys/minisign.pub`,
`.github/workflows/publish-catalog.yml` (dry-run without `MINISIGN_SECRET_KEY`).

## Non-goals (this repo)

- Executing user shell commands
- Storing host PATH scans
- Auto-merging AI drafts as verified
- Committing minisign/cosign private keys
