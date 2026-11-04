# Changelog

All notable **catalog / schema / tooling** changes for Nova-Commands.
Dates are UTC merge days when known. Digests are `metadata/manifest.json`
`content_sha256` values.

## Unreleased

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
