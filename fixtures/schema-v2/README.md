# Schema fixtures (task / profile / compatibility + sample commands)

These YAML files exercise live `command.schema.json` (v2) and
`task` / `profile` / `compatibility` schemas.

- **Not** part of the live `commands/` bank.
- **Not** included in `content_sha256` / catalog.
- Must remain `verification.status: draft`.
- Soft-checked by `scripts/validate_schema_v2.py`.

Live task/profile **content** lives under `tasks/` and `profiles/` (Faz 8) and
is validated by `scripts/validate_tasks_profiles.py`. These fixtures stay as
small schema samples and may diverge from published content.
