# Teachable topics — guides vs command records (NV-123)

Nova-Commands is the **only** source of truth for the curated Komut Bilgi
Bankası. This document defines the split between **topic guides** (learning
path) and **command detail** records (lookup cards) for Nova TUI.

PDF teaching references (e.g. user `Linux_Komutlari_Rehberi.pdf`) are optional
narration sources. When the PDF is **not** present in the agent environment,
guides are authored from the existing bank + official man/`--help` oriented
wording — **not** invented PDF content, and examples are **not** re-executed to
“verify.”

## Two surfaces

| Surface | Path | Role |
|---------|------|------|
| **Topic guide** | `concepts/<id>.yaml` with `format: topic-guide` | Learning path: intro → order → subtopics → command table → graded examples → callouts → safe exercises → next steps |
| **Command record** | `commands/<category>/<id>.yaml` | Lookup card: purpose, when, syntax, beginner example, flags, effect, OS/shell, risk, mistakes, related topics/cmds, sources+status |
| **Tasks / profiles** | `tasks/`, `profiles/` | Intent multi-OS implementations / role collections — not topic guides |

Omit empty optional sections. Keep `draft` / `reviewed` / `verified` honest.
`learning_level` is pedagogical and **never** replaces a beginner explanation.

## Topic guide fields

Required (unchanged): `id`, `kind: nova-commands-concept`, `title`, `summary`,
`body`, `difficulty`, `verification`.

Additive structured sections (all optional; prefer for TUI):

| Field | Purpose |
|-------|---------|
| `format` | `topic-guide` (structured) or `article` (body-first legacy) |
| `intro` | Short intro for the first pane |
| `categories` | Command-category slugs this guide teaches |
| `platforms` / `distributions` | Honest scope — no silent Arch default |
| `learning_path` | Ordered `{ref, kind: command\|concept\|subtopic, note?}` |
| `subtopics` | `{id, title, summary, related_commands?}` |
| `command_table` | `{id, purpose, learning_level?}` links into the bank |
| `graded_examples` | Topic-level examples with `difficulty` + `risk` |
| `callouts` | `tip` \| `warning` \| `note` \| `caution` |
| `safe_exercises` | Practice prompts; `risk` only `safe`\|`caution` |
| `next_steps` | Follow-on concept ids |

`body` remains the bilingual narrative fallback for clients that do not yet
render structured sections.

## Command teachable fields

Additive optional fields on schema v2 (compatible; no schema_version bump):

| Field | Purpose |
|-------|---------|
| `when_to_use` | When this command is the right tool |
| `syntax` | Compact SYNOPSIS-style pattern |
| `expected_effect` | Typical effect/output for beginners |
| `common_mistakes` | Curated bilingual mistakes |
| `related_topics` | Concept/topic-guide ids |

Existing fields still carry the rest of the card: `summary`/`description`/
`purpose`, `examples` (+ `difficulty`), `flags`, `platforms`/`shells`/
`package_refs`, `risk`, `related`, `nova.concepts`, `verification`.

## Distro / OS honesty

Group variants by OS/distro family. Supported teaching targets include
Debian/Ubuntu, Arch, Fedora/RHEL, openSUSE, Alpine, NixOS, Void, Gentoo, plus
macOS/Windows/BSD when bank rows are real. Do not invent OS variants or package
names. Prefer explicit “not on this family” notes over silent substitutes.

## Curriculum

`metadata/start-curriculum.yaml` `concept_order` lists the Start-tab learning
path (safe/caution filtered on the Nova side).

## Client notes (Nova NV-124)

- Prefer structured guide sections when `format: topic-guide`.
- Command detail: omit empty optional sections; show `when_to_use` when present.
- Never auto-run examples or exercises.
- Tolerate unknown additive keys.

See also: [NOVA_INTEGRATION.md](./NOVA_INTEGRATION.md),
[DATA_SCHEMA.md](./DATA_SCHEMA.md), [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md).


## PDF-depth pass (follow-up)

`Linux_Komutlari_Rehberi.pdf` was analyzed for pedagogy (section map, tables,
graded examples, tip/risk callouts). Guides were **rewritten in original
wording** (no verbatim PDF copy) and checked against man/FHS-oriented sources.
New guide: `linux-directory-structure`. Permissions now include rwx arithmetic,
755/644/600/700/777 table, and chmod/chown/chgrp/umask/visudo examples.
Start curriculum places the directory guide immediately after `terminal-basics`.
