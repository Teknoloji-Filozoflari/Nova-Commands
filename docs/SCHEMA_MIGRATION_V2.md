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

See [NOVA_INTEGRATION.md](NOVA_INTEGRATION.md) § Schema v2. Catalog consumers that hard-require `schema_version == 1` will reject this bank until updated. Do **not** edit the Nova repo in docs-only PRs — Nova follow-up re-vendor is a separate change.

## Post–Faz 9/10 catalog shape (still schema v2)

After [#22](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/22) /
[#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23) on `main`:

| Artifact field | Notes |
|----------------|-------|
| `schema_version` | **2** on catalog, manifest, search-index |
| Arrays | `commands`, `concepts`, **`tasks`**, **`profiles`** |
| Manifest counts | `command_count`, `concept_count`, `task_count`, `profile_count`, `operating_system_count`, `package_manager_count` |
| `content_sha256` | Deterministic over commands+concepts+tasks+profiles (no `generated_at`) |
| Command YAML | Still v2; Faz 10 may add optional `examples[].warnings` |

Faz 4–8 **added content** under schema v2; they did not introduce a schema v3.

### Additive pedagogy fields (still schema v2)

| Field | Notes |
|-------|-------|
| `learning_level` | Optional on commands; `beginner` \| `intermediate` \| `advanced` \| `unspecified`. Independent of `risk`. Build emits `unspecified` when missing. |
| `examples[].difficulty` | Optional; `beginner` \| `intermediate` \| `advanced` when examples span easy→advanced. Not derived from example `risk`. |

No catalog `schema_version` bump — consumers should tolerate unknown additive keys (see [NOVA_INTEGRATION.md](NOVA_INTEGRATION.md)).
Re-running `migrate_v1_to_v2.py` on an already-v2 tree remains idempotent and
must **not** change `verification.status`.

## Release policy (publish)

1. **Merge gate:** CI green on the PR head (validate + security + build +
   pytest + committed digest; Ubuntu/Windows/macOS matrix for tooling).
2. **Digest:** Any YAML change that affects hashed arrays requires a
   `build_catalog.py` refresh of `metadata/{catalog,manifest,search-index}.json`
   in the same PR.
3. **Signed Release:** Maintainers tag `catalog-v*` (or `workflow_dispatch`
   **Publish signed catalog**). With `MINISIGN_SECRET_KEY` set, assets are
   minisign-signed; without it the workflow **dry-runs** only.
4. **Trust anchor:** Do not rotate [`keys/minisign.pub`](../keys/minisign.pub)
   without coordinating the Actions secret and Nova client pins.
5. **Client rule:** Verify signatures before replacing a trusted bank; on
   failure keep the last good catalog ([catalog-signing.md](catalog-signing.md)).
6. **No silent verify:** Publishing never promotes `draft` → `verified`.

Historical post-#23 digest (Faz 10 era, 21 tasks):  
`content_sha256=7b24390eb92de6cda76b330d61fd34dcdb304afe27c1595355621717b653bf54`.  
Live pin: always read `metadata/manifest.json` (post-#30 bank + later honesty fixes).

## Rollback / dual-read notes

- Archived v1 schema: `schema/command.schema.v1.json` (historical only).
- Legacy `packages.{arch,debian,…}` keys remain for dual-read install hints;
  prefer `package_refs`.
- Consumers that only understand commands+concepts should ignore unknown
  `tasks` / `profiles` arrays rather than reject schema v2 wholesale when
  possible; hard `schema_version == 1` checks must be updated.
