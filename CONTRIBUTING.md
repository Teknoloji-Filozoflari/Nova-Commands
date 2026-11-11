# Contributing to Nova-Commands

This repository owns the curated **Komut Bilgi Bankası** for
[Nova](https://github.com/Teknoloji-Filozoflari/Nova). It is not the local
“commands found on my system” list — see
[docs/dual-concept.md](docs/dual-concept.md).

Security-sensitive catalog mistakes: [SECURITY.md](SECURITY.md) ·
[docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md).  
Roadmap / faz status: [docs/ROADMAP.md](docs/ROADMAP.md).  
Türkçe README: [README.tr.md](README.tr.md).

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
   Live wipe examples (`dd of=/dev/…`, live `mkfs` / `wipefs -a`) need
   bilingual `warnings` under the example ([docs/safety.md](docs/safety.md)).
   `related` must reference existing command ids only.
7. Run locally in a **venv** (do not install into system Python):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   python -m pip install -r requirements-dev.txt
   python scripts/validate_catalog.py # schema v1+v2, security, platforms,
                                      # tasks/profiles, generated catalog hashes
   python scripts/build_catalog.py
   python -m pytest tests/            # uses sys.executable for nested scripts
   ```

8. Commit updated `metadata/catalog.json`, `search-index.json`, and
   `manifest.json` (CI checks `content_sha256` against a rebuild).
9. If bank counts or the digest changed, refresh the **current-status**
   snapshot tables in `README.md`, `README.tr.md`,
   `docs/PLATFORM_SUPPORT.md`, `docs/ROADMAP.md`, and
   `docs/COVERAGE_MATRIX.md` (search `entry_count`, command/concept/task/
   profile counts, and `content_sha256`). Keep historical “was N”
   wording clearly historical — never as the live figure.
   `tests/test_doc_snapshot_counts.py` fails when these drift.
10. Open a pull request.

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
4. Run `python scripts/validate_tasks_profiles.py --require` (also wired into
   `validate_catalog.py`), then `python scripts/build_catalog.py` so
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
| `learning_level` | Optional pedagogy: `beginner` \| `intermediate` \| `advanced` (omit → `unspecified` at build; **not** risk) |
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

Optional `examples[].difficulty` (`beginner` \| `intermediate` \| `advanced`)
when examples span easy→advanced. Do not invent difficulty from example risk.

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
