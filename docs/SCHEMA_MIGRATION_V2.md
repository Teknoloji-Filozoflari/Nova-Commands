# Schema migration v1 → v2 (Faz 3)

**Date:** 2026-11-04  
**Tool:** `scripts/migrate_v1_to_v2.py`  
**Live schema:** `schema/command.schema.json` (v2)  
**Archived:** `schema/command.schema.v1.json`

## What changed

| Area | v1 | v2 (live) |
|------|----|-----------|
| Command YAML | no `schema_version` | `schema_version: 2` |
| Platforms | `linux` \| `macos` \| `bsd` | + `windows` and finer OS tags |
| Shells | `sh/bash/zsh/fish/any` | + PowerShell, cmd, nushell, … |
| Packages | fixed keys `packages.{arch,debian,…}` | + `package_refs[]` → PM registry ids |
| Kind | absent | `executable` / `shell_builtin` / `package_manager` / … |
| Catalog / manifest / search-index | `schema_version: 1` | `schema_version: 2` |
| `content_sha256` input | includes `schema_version: 1` | includes `schema_version: 2` (digest changes) |

## Preservation rules

- **IDs** unchanged.
- **TR/EN** summary, description, intent, examples, flags unchanged.
- **related**, **risk**, **requires_elevated**, **examples** unchanged.
- **verification.status** unchanged — no silent demotion of `reviewed` / `verified`.
- Legacy **`packages`** retained for dual-read (Nova install hints).
- Platform tag **`bsd`** kept on `platforms[]`; `operating_systems` only gets unambiguous registry ids (`linux`, `macos`, …). Specific BSD flavours are **not** invented.

## Package key → registry map

| v1 key | `package_refs.manager` | `distributions` |
|--------|------------------------|-----------------|
| `arch` | `pacman` | `[arch]` |
| `debian` | `apt` | `[debian]` |
| `ubuntu` | `apt` | `[ubuntu]` |
| `fedora` | `dnf` | `[fedora]` |
| `rhel` | `dnf` | `[rhel]` |

Same manager+package pairs are merged (e.g. debian+ubuntu → one apt ref). **Arch/pacman is emitted first** when `packages.arch` exists.

## Kind inference (conservative)

| Rule | `kind` |
|------|--------|
| `cd`, `export`, `history` | `shell_builtin` |
| `packages/` category PMs (`apt`, `pacman`, …) | `package_manager` |
| everything else | `executable` |

Ambiguous cases (`echo` may be builtin or `/bin/echo`) stay `executable`.

## How to re-run

```bash
python3 scripts/migrate_v1_to_v2.py --dry-run
python3 scripts/migrate_v1_to_v2.py
python3 scripts/migrate_v1_to_v2.py --check
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
```

Migration is **idempotent**: re-running refreshes derived `package_refs` / `operating_systems` without touching verification.

## Nova impact

See [NOVA_INTEGRATION.md](NOVA_INTEGRATION.md) § Schema v2. Catalog consumers that hard-require `schema_version == 1` will reject this bank until updated. Do **not** edit the Nova repo in this PR — Nova follow-up is required.
