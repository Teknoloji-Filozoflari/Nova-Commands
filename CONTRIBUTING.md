# Contributing to Nova-Commands

This repository owns the curated **Komut Bilgi Bankası** for
[Nova](https://github.com/Teknoloji-Filozoflari/Nova). It is not the local
“commands found on my system” list — see
[docs/dual-concept.md](docs/dual-concept.md).

Security-sensitive catalog mistakes: [SECURITY.md](SECURITY.md).

## Issue templates

Use GitHub issue forms when proposing work:

| Template | Use |
|----------|-----|
| **Bug** | Wrong flags, packages, risk, i18n, CI |
| **New command** | Propose a command id + category + sources |
| **Category** | New taxonomy slug (§8.x / `categories.yaml`) |
| **Translation** | tr/en fixes for commands, concepts, docs |

## Pull requests

PRs use [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).
CI must pass: validate → build → pytest → committed `content_sha256` match.

## Add a command

1. Pick a category under `commands/` (must match `metadata/categories.yaml`
   and `schema/command.schema.json` — **schema v2**).
2. Create `commands/<category>/<id>.yaml` (filename stem **must** equal `id`).
   Set `schema_version: 2` and an honest `kind` (`executable`, `shell_builtin`,
   `package_manager`, …).
3. Fill required fields (**both** `tr` and `en` on every localized object).
   Prefer Arch/`pacman` first in `install_notes` / `package_refs` when relevant.
   Prefer `package_refs` (`manager` from `metadata/package-managers.yaml`);
   legacy `packages.{arch,debian,…}` may remain for dual-read.
4. Optionally set `nova.concepts` to ids from `metadata/concepts.yaml`.
5. Set `verification.status` to `draft` unless a human already reviewed
   flags, packages, and examples against man pages / `--help`.
6. For each flag, set `verified: false` until confirmed. Do **not** invent
   flags or package names. Schema migration notes:
   [docs/SCHEMA_MIGRATION_V2.md](docs/SCHEMA_MIGRATION_V2.md).
7. Run locally:

   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 scripts/validate_catalog.py
   python3 scripts/build_catalog.py
   python3 -m pytest tests/
   ```

8. Commit updated `metadata/catalog.json`, `search-index.json`, and
   `manifest.json` (CI checks `content_sha256` against a rebuild).
9. Open a pull request.

## Add a concept article

1. Register the id in `metadata/concepts.yaml` (label tr/en; set `article:`).
2. Create `concepts/<id>.yaml` with `kind: nova-commands-concept`, bilingual
   `title` / `summary` / `body`, `difficulty`, and honest `verification`.
3. `related_commands` must reference existing command ids.
4. Do **not** mark `verified` without human review of the teaching text.
5. Rebuild metadata as above.

## Add a task or profile (Faz 8+)

1. Tasks: create `tasks/<id>.yaml` (`kind: task`). Id must **not** collide with
   a command id. `implementations[].commands` and `related_commands` must
   reference existing command bank ids. Prefer multi-OS implementations over
   fake cross-platform aliases.
2. Profiles: create `profiles/<id>.yaml` (`kind: profile`) as a guiding
   reference collection (related commands + tasks). Not an executable runbook.
3. Keep `verification.status: draft` until human review. Do not invent
   command ids or secret-bearing examples.
4. Run `python3 scripts/validate_tasks_profiles.py --require` (also wired into
   `validate_catalog.py`), then `python3 scripts/build_catalog.py` so
   `catalog.json` / `search-index.json` / `manifest.json` pick up
   `task_count` / `profile_count` (included in `content_sha256`).

## Propose a category

Open a **Category** issue first. Adding a slug requires updating:

- `metadata/categories.yaml`
- `schema/command.schema.json` `category` enum
- at least a few seed commands (avoid empty taxonomy)

## Translations (i18n)

Every localized mapping needs non-empty **`tr` and `en`**. Validator and CI
reject empty strings. Prefer consistent terminology with existing entries;
open a **Translation** issue for large sweeps.

## Required fields

| Field | Rule |
|-------|------|
| `schema_version` | Must be `2` |
| `id` | Unique, `^[a-z0-9][a-z0-9+._-]*$`, matches filename |
| `kind` | e.g. `executable`, `shell_builtin`, `package_manager`, … |
| `summary` / `description` | Both `tr` and `en` |
| `category` | One of the taxonomy slugs |
| `risk` | `safe` \| `caution` \| `dangerous` \| `destructive` |
| `requires_elevated` | Boolean for typical useful use |
| `platforms` | Non-empty (`linux`, `macos`, `bsd`, `windows`, …) |
| `examples` | ≥1; each with `risk` |
| `intent.tr` / `intent.en` | Natural-language search phrases |
| `verification.status` | `draft` \| `reviewed` \| `verified` |

## Risk guide

| Level | Meaning | Examples |
|-------|---------|----------|
| `safe` | Read-only / reversible everyday use | `ls`, `cat`, `df` |
| `caution` | Can confuse, overwrite with care, or need understanding | `chmod`, `mv`, `kill` |
| `dangerous` | Easy to break access/services or leak secrets | `dd`, `iptables`, `chmod -R 777` patterns |
| `destructive` | Data loss / wipe likely | `rm -rf`, `mkfs`, disk wipe |

Example `risk` must be ≥ command-level `risk` when the example is riskier
(validator enforces ordering).

## Verification policy

- **Never** mark AI-authored content `verified` without human review.
- `verified` requires `sources` and `last_reviewed` (validator + tests).
- Prefer citing sources: `man 1 <cmd>`, distro wiki, upstream docs URLs.
- Do not execute destructive commands to “test” catalog entries.
- Local PATH presence must not inherit curated `verified`
  ([docs/safety.md](docs/safety.md)).

## Quality over quantity

Prefer a few accurate entries over many guessed ones. Unknown package names
should be omitted, not invented.

## License of contributions

By contributing, you agree catalog metadata may be redistributed with
Nova-Commands under the MIT license.
