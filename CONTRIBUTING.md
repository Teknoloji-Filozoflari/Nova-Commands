# Contributing to Nova-Commands

This repository owns the curated **Komut Bilgi Bankası** for
[Nova](https://github.com/Teknoloji-Filozoflari/Nova). It is not the local
“commands found on my system” list — see
[docs/dual-concept.md](docs/dual-concept.md).

## Add a command

1. Pick a category under `commands/` (must match `metadata/categories.yaml`
   and `schema/command.schema.json`).
2. Create `commands/<category>/<id>.yaml` (filename stem **must** equal `id`).
3. Fill required fields (**both** `tr` and `en` on every localized object).
   Prefer Arch/`pacman` first in `install_notes` when relevant.
4. Optionally set `nova.concepts` to ids from `metadata/concepts.yaml`.
5. Set `verification.status` to `draft` unless a human already reviewed
   flags, packages, and examples against man pages / `--help`.
6. For each flag, set `verified: false` until confirmed. Do **not** invent
   flags or package names.
7. Run locally:

   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 scripts/validate_catalog.py
   python3 scripts/build_catalog.py
   python3 -m pytest tests/
   ```

8. Open a pull request. CI must pass.

## Add a concept article

1. Register the id in `metadata/concepts.yaml` (label tr/en; set `article:`).
2. Create `concepts/<id>.yaml` with `kind: nova-commands-concept`, bilingual
   `title` / `summary` / `body`, `difficulty`, and honest `verification`.
3. `related_commands` must reference existing command ids.
4. Do **not** mark `verified` without human review of the teaching text.

## Required fields

| Field | Rule |
|-------|------|
| `id` | Unique, `^[a-z0-9][a-z0-9+._-]*$`, matches filename |
| `summary` / `description` | Both `tr` and `en` |
| `category` | One of the 16 taxonomy slugs |
| `risk` | `safe` \| `caution` \| `dangerous` \| `destructive` |
| `requires_elevated` | Boolean for typical useful use |
| `platforms` | Non-empty (`linux`, …) |
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
- Prefer citing sources: `man 1 <cmd>`, distro wiki, upstream docs URLs.
- Do not execute destructive commands to “test” catalog entries.

## Quality over quantity

Prefer a few accurate entries over many guessed ones. Unknown package names
should be omitted, not invented.

## License of contributions

By contributing, you agree catalog metadata may be redistributed with
Nova-Commands under the MIT license.
