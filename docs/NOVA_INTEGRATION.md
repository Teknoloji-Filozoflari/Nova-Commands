# Nova integration — Komut Rehberi

How [Nova](https://github.com/Teknoloji-Filozoflari/Nova) (and other clients) should
consume this repository. Companion to [nova-consumption.md](./nova-consumption.md)
and [dual-concept.md](./dual-concept.md).

Repository: https://github.com/Teknoloji-Filozoflari/Nova-Commands

## Artifacts

| Path | Kind | Role |
|------|------|------|
| `commands/<category>/<id>.yaml` | source | One curated command |
| `concepts/<id>.yaml` | source | Learnable concept articles (TR/EN) |
| `metadata/categories.yaml` | taxonomy | §8.1–8.16 labels |
| `metadata/concepts.yaml` | registry | Concept ids + optional `article` pointer |
| `metadata/catalog.json` | `nova-commands-bank` | Aggregate commands + concepts |
| `metadata/search-index.json` | `nova-commands-search-index` | Flattened search fields |
| `metadata/manifest.json` | `nova-commands-manifest` | Counts + **deterministic** `content_sha256` |
| `schema/*.json` | schema | Validation contracts |
| `docs/local-discovery-contract.md` | contract | Local PATH discovery (client-only) |

## Integrity (`content_sha256`)

`build_catalog.py` hashes the **canonical** JSON of:

```json
{ "schema_version": 1, "kind": "nova-commands-bank", "commands": [...], "concepts": [...] }
```

- Keys sorted; UTF-8; compact separators.
- **`generated_at` is excluded** so rebuilds with the same content keep the same digest.
- The same digest is copied into `catalog.json`, `search-index.json`, and `manifest.json`.

Clients should:

1. Fetch `manifest.json` (or catalog).
2. Compare `content_sha256` to a pinned release digest when offline-caching.
3. Reject payloads whose `kind` / `schema_version` do not match.

## Client flow

```
Nova Komut Rehberi
  ├─ curated bank
  │     ├─ prefer manifest.content_sha256 pin
  │     ├─ load catalog.json (commands + concepts)
  │     ├─ optional: search-index.json for intent/tag UI search
  │     └─ show verification.status (draft watermark ≠ verified badge)
  └─ local discovery (optional, device-only)
        ├─ kind == nova-local-commands
        └─ join on bank_id — never inherit verified from PATH hits
```

## Field mapping

| Bank field | UI use |
|------------|--------|
| `summary` / `description` / concept `body` | Locale from Nova settings (`tr` / `en`) |
| `risk` + example `risk` | Warning badges / confirm gates |
| `requires_elevated` | Sudo affordance |
| `packages` + `install_notes` | Install hints — **Arch/pacman first** on Arch hosts |
| `intent` | Natural-language search phrases |
| `nova.concepts` | Cross-links into concept articles / chips |
| `verification.status` | Trust chrome |

## Distro preference

When the host is Arch, prefer `packages.arch` and pacman lines in `install_notes`
(project preference).

## Non-goals for Nova UI

- Auto-promoting `draft` → `verified`
- Treating PATH presence as bank verification
- Executing destructive examples from the catalog to “test” them

## Related repos

- **Nova** — UI / Komut Rehberi
- **Nova-Store** — installable apps (different catalog `kind`)
- **Nova-Commands** — this knowledge bank
