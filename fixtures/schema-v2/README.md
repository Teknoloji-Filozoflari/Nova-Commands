# Schema fixtures (task / profile / compatibility + sample commands)

These YAML files exercise live `command.schema.json` (v2) and stub
`task` / `profile` / `compatibility` schemas.

- **Not** part of the live `commands/` bank.
- **Not** included in `content_sha256` / catalog.
- Must remain `verification.status: draft`.
- Soft-checked by `scripts/validate_schema_v2.py`.

The live bank under `commands/` is schema v2 (Faz 3). Task/profile **content**
trees remain **Faz 8**.
