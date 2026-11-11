# Changelog

All notable **catalog / schema / tooling** changes for Nova-Commands.
Dates are UTC merge days when known. Digests are `metadata/manifest.json`
`content_sha256` values.

## Unreleased

- PDF-depth topic guides (Komut Rehberi): deepen permissions (rwx/octal tables, chmod/chown/chgrp/umask/visudo),
  terminal basics, pipes, path, find, processes, text, archives, networking; add
  **Linux dizin yapısı** (`linux-directory-structure`). Paragraph-friendly `body`
  sections + richer graded examples/callouts/exercises. Teachable fields on
  chmod/chown/chgrp/umask/visudo (+ related_topics on ls/tree/du). Curriculum
  inserts the new guide after terminal-basics. No status promotions; no PDF
  verbatim copy (man/FHS-oriented original wording). Digest
  `e6466b7f777fe49019c2cc7d6d4bcf279857d76a209e7ca68b7292f5f945ec06`.

- NV-123 teachable topic catalog: concepts gain optional `format: topic-guide`
  structured sections (`intro`, `learning_path`, `subtopics`, `command_table`,
  `graded_examples`, `callouts`, `safe_exercises`, `next_steps`); commands gain
  optional `when_to_use` / `syntax` / `expected_effect` / `common_mistakes` /
  `related_topics`. Eight new category topic guides; existing articles upgraded;
  start-curriculum expanded. No status promotions; PDF not in env (bank + man
  oriented). See `docs/TEACHABLE_TOPICS.md`. Digest bumped on rebuild.
- NV-119 security checklist content audit: replace invented
  `freebsd-update show` with `fetch` (+ download warning); correct NixOS
  `dry-build` wording (evaluate/show, does not build/switch); prefer
  `winget list --upgrade-available` over bare `winget upgrade`; fix
  misplaced macOS Docker notes. Task schema allows example `warnings[]`.
  Add `tests/test_security_checklist.py` (never auto-run wording, platform
  match/no-match, draft-only). No status promotions. Digest
  `92e69b0cd8278b5685cf6d748769c1a22cc61bbd02924e5eee7267122d7e4a4b`.
- NV-110 / NV-109: additive `learning_level` on commands (`beginner` \|
  `intermediate` \| `advanced` \| `unspecified`) and optional
  `examples[].difficulty` — pedagogy independent of `risk`. Missing
  `learning_level` normalizes to `unspecified` at catalog build (no silent
  map from risk). Schema stays **v2** (compatible additive fields). Curated
  population leaves niche tools unspecified; `rm` stays `beginner` +
  `destructive`. Digest bumped on rebuild.
- NV-103 Komut Rehberi content bank: coverage matrix
  (`docs/COVERAGE_MATRIX.md`), high-priority command fills/enrichments
  (shell/users/ops + git/openssl/ip/docker/systemctl/journalctl/PM/SSH),
  sequential **Sunucu güvenlik kontrolü** (10 `security-check-*` tasks,
  profile + concept + `docs/SERVER_SECURITY_CHECKLIST.md`). No schema bump;
  new rows stay `draft` / enrichments keep prior status; examples not executed.
  Bank: **267** commands · **21** concepts · **36** tasks · **14** profiles;
  `content_sha256=406fe04002c47c592009c71f6d9dbb1f0ec7c9faa6c19165f58bebe29265b716`.
- Beginner trust audit: demote agent-authored concept articles that lacked
  human review proof (`reviewed` → `draft`); keep `storage` as the sole
  concept still `reviewed` (`last_reviewed` present). Add bilingual
  `warnings[]` on destructive `fdisk` / `parted` / `rm` / `userdel`
  examples (soft security notices cleared). Sync live-catalog counts in
  README / README.tr / ROADMAP / PLATFORM_SUPPORT after #30.
  Bank: **256** commands · **20** concepts · **26** tasks · **13** profiles;
  concepts reviewed **1** / draft **19**;
  `content_sha256=e17437d67113603c4e7e7cd46b7b5ad1ebb1043d032b4a38b651c3cd189b8169`.
  No `draft`→`reviewed`/`verified` promotions; no new desktop profiles;
  examples not executed.
- Komut Rehberi IA content fill (Nova #58 / [#30](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/30)):
  start-safe concept `related_commands`, task safe examples + bank-sourced
  explanations, profile↔task wiring, five new tasks, `metadata/start-curriculum.yaml`.
  Prior digest `ee1e5d186bdc7885cd18b945446a2d34673c7f7499d08f7da165fc011d5ae4db`.
- Faz 11 documentation: `README.tr.md`, `docs/ROADMAP.md`,
  `docs/SECURITY_MODEL.md`; PLATFORM_SUPPORT / SCHEMA_MIGRATION_V2 / README
  aligned with post-#23 `main`. No catalog YAML or digest change intended.

## 2026-11-04 — Cross-platform Faz 0–10 on `main`

Baseline before expansion (Linux-era signed bank era, NC #13): **143** commands,
**12** concept articles, catalog `schema_version: 1`,
`content_sha256=7331be6b…`.

| Merge | PR | Summary | Bank digest (when content changed) |
|-------|-----|---------|--------------------------------------|
| Faz 1 | [#14](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/14) | Platform metadata registries + schemas | (additive metadata) |
| Faz 2 | [#15](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/15) | Command schema v2 dual-path / fixtures | — |
| Faz 3 | [#16](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/16) | Live v1→v2 migrate; catalog schema 2 | digest bumped with v2 |
| Faz 4 | [#17](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/17) | Broader Linux PM command banks | — |
| Faz 5 | [#18](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/18) | Windows + macOS command banks | — |
| Faz 6 | [#19](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/19) | BSD family command banks | — |
| Faz 7 | [#20](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/20) | Server / network / DevOps banks | — |
| Faz 8 | [#21](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/21) | `tasks/` + `profiles/` trees | — |
| Faz 9 | [#22](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/22) | Index tasks/profiles into catalog/search | `f08edacc…` |
| Faz 10 | [#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23) | Security validator + SHA-pinned multi-OS CI | `7b24390e…` |

### Post-#23 snapshot

- Commands **256** · concepts **20** · tasks **21** · profiles **13**
- Search entries **310** · OS **11** · package managers **60**
- verification: verified **26** / reviewed **105** / draft **125** (unchanged by Faz 10)
- `content_sha256=7b24390eb92de6cda76b330d61fd34dcdb304afe27c1595355621717b653bf54`
- LICENSE + `keys/minisign.pub` unchanged; publish still dry-runs without secret

## Notes

- Do not invent changelog rows for unsigned Releases until a `catalog-v*` tag
  actually ships.
- Nova re-vendors are tracked in the Nova repository, not here.
