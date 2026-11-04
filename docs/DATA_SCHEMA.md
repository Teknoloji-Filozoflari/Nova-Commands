# Data schema — dual-path (v1 bank + v2 design)

## Strategy: **dual**, not breaking

| Layer | File | Role today (Faz 2) |
|-------|------|--------------------|
| **Live bank** | `schema/command.schema.json` (**v1**) | Validates all `commands/**/*.yaml` |
| **v2 design** | `schema/command.schema.v2.json` | Soft-validated via `fixtures/schema-v2/` only |
| **Stubs** | `task.schema.json`, `profile.schema.json`, `compatibility.schema.json` | Shapes for Faz 8+; fixtures only |
| **Catalog** | `metadata/catalog.json` | Remains `schema_version: **1**` until Faz 3 migrate |

Faz 3 will migrate the 143 command YAML files onto v2 and then bump the catalog.
This PR does **not** mass-migrate, demote `verified`, or change LICENSE / minisign.

## Why dual (not a single additive v1)?

v1 uses `additionalProperties: false`, hard enums without `windows` /
`powershell` / `cmd`, and fixed `packages.{arch,debian,ubuntu,fedora,rhel}`
keys. Expanding that file in place would either reject new fields or force an
immediate bank rewrite. Keeping v1 untouched preserves CI + Nova vendor pins;
v2 evolves beside it.

## Command schema v2 highlights

- **`platforms`**: adds `windows` (and finer OS tags); optional
  `operating_systems` / `distributions` / `architectures` /
  `execution_environments` registry refs (Faz 1 metadata).
- **`shells`**: PowerShell, Windows PowerShell, cmd, nushell, … plus v1 short
  names (`bash`, `sh`, `any`, …).
- **`kind`**: `executable`, `shell_builtin`, `powershell_cmdlet`,
  `vendor_cli`, …
- **`package_refs`**: `{ manager: <package-managers.yaml id>, package: name }`
  — preferred over legacy fixed keys. Legacy `packages` object still allowed
  for migration dual-read.
- **`implementations`**: optional per-command platform/shell variants.
  Multi-command **tasks** use `task.schema.json` (not command records).
- Examples may carry `shell`, `platforms`, `privilege` (admin/UAC-aware).

## Tasks vs commands

Master §9 example (`show-network-config` with linux-ip / windows-powershell /
windows-cmd) is a **task**. Individual tools (`ip`, `Get-NetIPConfiguration`,
`ipconfig`) remain **command** records. Do not reuse command ids for tasks.

## Soft validation

```bash
python3 scripts/validate_schema_v2.py
python3 scripts/validate_catalog.py   # still v1 bank + soft platform + soft v2
```

Fixtures live under `fixtures/schema-v2/` and must stay `verification.status:
draft`. They are **not** part of the published catalog hash.

## Out of scope here

- Migrating `commands/` or `concepts/`
- Creating `tasks/` or `profiles/` trees with real content
- Bumping catalog / search-index / manifest `schema_version`
- Rotating `keys/minisign.pub` or changing LICENSE

See also: [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md), [architecture.md](architecture.md).
