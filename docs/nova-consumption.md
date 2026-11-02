# How Nova consumes Nova-Commands

Repository: https://github.com/Teknoloji-Filozoflari/Nova-Commands

## Source of truth

| Path | Role |
|------|------|
| `commands/<category>/<id>.yaml` | One command per file; contributors PR here |
| `schema/command.schema.json` | Entry schema (risk, verification, i18n, …) |
| `metadata/categories.yaml` | Taxonomy §8.1–8.16 + TR/EN labels |
| `metadata/catalog.json` | Built aggregate for clients |
| `docs/local-discovery-contract.md` | Local PATH discovery (client-side) |

## Client flow (recommended)

```
Nova Komut Rehberi
  ├─ load curated bank (catalog.json from release or pinned commit)
  │     ├─ schema_version == 1 && kind == nova-commands-bank
  │     └─ index by id, name, tags, intent phrases (tr/en)
  └─ (optional) local discovery snapshot
        ├─ kind == nova-local-commands
        └─ join on bank_id — display both labels distinctly
```

Do **not** treat PATH presence as verification of bank content.

## Field mapping hints

| Bank field | UI use |
|------------|--------|
| `summary` / `description` | Locale from Nova settings (`tr`/`en`) |
| `risk` + example `risk` | Warning badges / confirm gates |
| `requires_elevated` | Sudo affordance |
| `packages` + `install_notes` | “How to install” — prefer pacman on Arch hosts |
| `intent` | Natural-language search |
| `verification.status` | Draft watermark vs verified badge |
| `nova.favorite_eligible` | Favorites hint |

## Distro preference

When showing install hints on an Arch host, prefer `packages.arch` and
pacman lines in `install_notes` (Nova project preference).

## Related repos

- Nova — UI
- Nova-Store — installable apps (different catalog)
- Nova-Commands — command knowledge (this repo)
