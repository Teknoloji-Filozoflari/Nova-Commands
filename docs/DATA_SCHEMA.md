# Data schema — live v2 (Faz 3)

## Strategy: **live catalog on schema v2**

| Layer | File | Role (Faz 3+) |
|-------|------|---------------|
| **Live bank** | `schema/command.schema.json` (**v2**) | Validates all `commands/**/*.yaml` |
| **v2 twin** | `schema/command.schema.v2.json` | Same properties; distinct `$id` for tooling |
| **Archived v1** | `schema/command.schema.v1.json` | Historical Linux-era schema |
| **Tasks** | `schema/task.schema.json` + `tasks/*.yaml` | Live intent → multi-OS implementations (Faz 8) |
| **Profiles** | `schema/profile.schema.json` + `profiles/*.yaml` | Server / role reference collections (Faz 8) |
| **Compatibility** | `schema/compatibility.schema.json` | Fixtures / later deepen |
| **Catalog** | `metadata/catalog.json` | `schema_version: **2**` (commands+concepts+tasks+profiles) |

Faz 2 used a dual-path (v1 bank + v2 fixtures). **Faz 3 ends dual forever for the live bank:** all 143 commands migrated; catalog/manifest/search-index bumped to 2.

See [SCHEMA_MIGRATION_V2.md](SCHEMA_MIGRATION_V2.md) for the field map and `migrate_v1_to_v2.py`.

## Command schema v2 highlights

- **`schema_version: 2`** required on every command YAML.
- **`platforms`**: includes `windows` (capability); existing bank entries keep their honest linux/macos/bsd tags.
- **`shells`**: PowerShell, cmd, nushell, … plus v1 short names.
- **`kind`**: `executable`, `shell_builtin`, `package_manager`, …
- **`package_refs`**: `{ manager: <package-managers.yaml id>, package, distributions? }` — preferred. Legacy `packages` keys kept for dual-read.
- **`operating_systems` / `distributions` / …**: optional registry refs (Faz 1 metadata).
- **`implementations`**: optional per-command variants (tasks use `task.schema.json`).
- Examples may carry `shell`, `platforms`, `privilege`, and optional bilingual
  `warnings` (required by `validate_security.py` for live wipe-class patterns).
- **`learning_level`** (optional on commands): `beginner` \| `intermediate` \|
  `advanced` \| `unspecified`. Pedagogical complexity / prerequisites — **not**
  security risk. Omit when unclear; `build_catalog.py` normalizes missing →
  `unspecified`. Never derive from `risk` (e.g. `rm` can be `beginner` +
  `destructive`). Does **not** authorize skipping beginner explanation fields.
- **`examples[].difficulty`** (optional): `beginner` \| `intermediate` \|
  `advanced` when examples span easy→advanced. Do **not** rank examples by
  `risk` when difficulty is missing.
- **Teachable command fields** (optional; omit empty): `when_to_use`, `syntax`,
  `expected_effect`, `common_mistakes[]`, `related_topics[]` (concept ids).
- **Topic guides** (`concepts/*.yaml`): optional `format: topic-guide` plus
  structured sections `intro`, `learning_path`, `subtopics`, `command_table`,
  `graded_examples`, `callouts`, `safe_exercises`, `next_steps`,
  `categories` / `platforms` / `distributions`. See
  [TEACHABLE_TOPICS.md](TEACHABLE_TOPICS.md).

## Tasks vs commands

Multi-tool user goals (`show-local-ip` with linux-ip / windows-powershell / windows-cmd) are **tasks** under `tasks/`. Individual tools remain **command** records. Do not reuse command ids for tasks. Server / role **profiles** under `profiles/` point at related commands + tasks; they are teaching collections, not runbooks.

`content_sha256` hashes **commands + concepts + tasks + profiles** (Faz 9). `generated_at` stays excluded.

## Validation

```bash
# Use the project venv interpreter (see README Developer section).
python scripts/validate_catalog.py            # live v2 bank + concepts + tasks/profiles + security + generated artifacts
python scripts/validate_security.py           # wipe/related/minisign gates (also via validate_catalog)
python scripts/validate_tasks_profiles.py --require
python scripts/validate_schema_v2.py          # schema v1+v2 load + fixtures (fail on missing fields)
python scripts/validate_generated_artifacts.py
python scripts/migrate_v1_to_v2.py --check
```

Fixtures under `fixtures/schema-v2/` stay `draft` and are **not** in the catalog hash.

## Non-goals of Faz 3 (historical)

- Adding Windows/macOS/BSD **command content** (done in Faz 5–6)
- Creating real `tasks/` or `profiles/` trees (done in Faz 8)
- Demoting honest `verified` / `reviewed` statuses
- Changing LICENSE or `keys/minisign.pub`

See also: [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md), [ROADMAP.md](ROADMAP.md),
[SECURITY_MODEL.md](SECURITY_MODEL.md), [architecture.md](architecture.md),
[NOVA_INTEGRATION.md](NOVA_INTEGRATION.md).
