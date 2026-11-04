# Platform support (metadata registries)

Faz 1 introduces **additive** platform metadata. These registries describe
operating systems, distributions, shells, package managers, and related
concepts as **separate models**. They do **not** yet drive command schema
enums for the **live** bank. Catalog `schema_version` is still **1**.
Command schema **v2** (dual-path) is documented in [DATA_SCHEMA.md](DATA_SCHEMA.md);
fixtures soft-validate v2 without migrating `commands/`.

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
support levels). Live `commands/` are **not** required to cite registry ids yet
(v1 schema). Schema v2 fixtures may cite them via `package_refs` /
`operating_systems`.

## Arch / pacman

Per project preference, **Arch Linux** and **pacman** are first-class in the
package-manager and distribution registries (install-hint policy for Arch
family remains pacman-first). Schema v2 `package_refs` should keep pacman
first-class for Arch-family install hints.

## Out of scope (later fazes)

- Migrating the 143 v1 commands onto `command.schema.v2.json` (Faz 3)
- Tasks / profiles **content** trees (schemas stubbed in Faz 2; content Faz 8)
- Catalog index counts for registry kinds
- Bumping catalog `schema_version` or rotating minisign keys

## Maintainer note

`scripts/_seed_platform_registries.py` produced the initial Faz 1 YAML.
**Registries under `metadata/` are now the source of truth** — do not re-run
the seeder casually (it overwrites). Prefer editing YAML directly.