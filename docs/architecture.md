# Architecture (Nova-Commands)

## Principles

1. **Data repo first** — YAML + schema + CI; no runtime daemon here.
2. **Dual concept** — curated bank ≠ local PATH discovery.
3. **Multi-distro** — Arch / Debian-Ubuntu / Fedora-RHEL notes; Arch preference in install hints.
4. **Quality over count** — unknown flags/packages omitted or marked draft.
5. **Safety** — risk labels; no destructive execution to validate.

## Layout

```
commands/<category>/<id>.yaml   # curated entries
concepts/<id>.yaml              # learnable concept articles (TR/EN)
schema/*.json                   # JSON Schema (Draft 2020-12)
metadata/categories.yaml        # §8.x taxonomy
metadata/concepts.yaml          # concept registry (+ optional article:)
metadata/catalog.json           # aggregate (kind: nova-commands-bank)
metadata/search-index.json      # flattened search fields
metadata/manifest.json          # counts + deterministic content_sha256
scripts/validate_catalog.py     # CI gate (schema, i18n, concepts)
scripts/build_catalog.py        # catalog + index + manifest
docs/                           # contracts + safety + NOVA_INTEGRATION
tests/                          # pytest
```

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

## Non-goals (this repo)

- Executing user shell commands
- Storing host PATH scans
- Auto-merging AI drafts as verified
