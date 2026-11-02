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
schema/*.json                   # JSON Schema (Draft 2020-12)
metadata/categories.yaml        # §8.x taxonomy
metadata/concepts.yaml          # cross-cutting labels
metadata/catalog.json           # built aggregate (kind: nova-commands-bank)
scripts/validate_catalog.py     # CI gate
scripts/build_catalog.py        # aggregator
docs/                           # contracts + safety + Nova consumption
tests/                          # pytest
```

## Verification pipeline

```
PR → validate_catalog.py → build_catalog.py → pytest → merge
```

`verification.status` is never auto-promoted to `verified` by CI.

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
| 8+ | Grow coverage category-by-category (human review) |

## Non-goals (this repo)

- Executing user shell commands
- Storing host PATH scans
- Auto-merging AI drafts as verified
