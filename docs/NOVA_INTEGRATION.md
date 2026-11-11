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
| `metadata/catalog.json` | `nova-commands-bank` | Aggregate commands + concepts + tasks + profiles |
| `metadata/search-index.json` | `nova-commands-search-index` | Flattened search fields |
| `metadata/manifest.json` | `nova-commands-manifest` | Counts + **deterministic** `content_sha256` |
| `schema/*.json` | schema | Validation contracts |
| `docs/local-discovery-contract.md` | contract | Local PATH discovery (client-only) |

## Integrity (`content_sha256`)

`build_catalog.py` hashes the **canonical** JSON of:

```json
{ "schema_version": 2, "kind": "nova-commands-bank", "commands": [...], "concepts": [...], "tasks": [...], "profiles": [...] }
```

- Keys sorted; UTF-8; compact separators.
- **`generated_at` is excluded** so rebuilds with the same content keep the same digest.
- The same digest is copied into `catalog.json`, `search-index.json`, and `manifest.json`.
- **Faz 3:** `schema_version` inside the hash payload is **2** — digests are not comparable to v1 pins.

Clients should:

1. Fetch `manifest.json` (or catalog).
2. Compare `content_sha256` to a pinned release digest when offline-caching.
3. Reject payloads whose `kind` / `schema_version` do not match (**accept `schema_version == 2`**).

## Client flow

```
Nova Komut Rehberi
  ├─ curated bank
  │     ├─ prefer signed GitHub Release (catalog-v*) + minisign verify
  │     │     (keys/minisign.pub — see docs/catalog-signing.md)
  │     ├─ prefer manifest.content_sha256 pin
  │     ├─ load catalog.json (commands + concepts + tasks + profiles)
  │     ├─ optional: search-index.json for intent/tag UI search
  │     └─ show verification.status (draft watermark ≠ verified badge)
  └─ local discovery (optional, device-only)
        ├─ kind == nova-local-commands
        └─ join on bank_id — never inherit verified from PATH hits
```

Signed Releases are the preferred remote refresh path (mirror Nova-Store’s
catalog trust model). On signature failure, keep the last trusted / embedded
bank. Optional unsigned `main` sync is a separate, weaker fallback — never
treat it as equivalent to a verified Release.

## Field mapping

| Bank field | UI use |
|------------|--------|
| `summary` / `description` / concept `body` | Locale from Nova settings (`tr` / `en`) |
| `risk` + example `risk` | Warning badges / confirm gates |
| `learning_level` (+ example `difficulty`) | Pedagogy / learning filters — **independent of risk**; missing → `unspecified` |
| `requires_elevated` | Sudo affordance |
| `packages` + `install_notes` | Install hints — **Arch/pacman first** on Arch hosts (legacy keys kept) |
| `package_refs` | Preferred PM-registry install mapping (`manager` + `package`) |
| `kind` | Optional UI chrome (builtin vs executable vs package manager) |
| `platforms` / `operating_systems` | Platform filters (schema allows `windows`) |
| `intent` | Natural-language search phrases |
| `nova.concepts` | Cross-links into concept articles / chips |
| `verification.status` | Trust chrome |

## Distro preference

When the host is Arch, prefer `packages.arch` / `package_refs` with `manager: pacman`
and pacman lines in `install_notes` (project preference).

## Schema v2 — Nova follow-up required (do not ignore)

Faz 3 made the **live** catalog schema v2. Nova (and any vendor pin at
`schema_version: 1` / `content_sha256` from the Linux-era bank) will **break hard**
if it still asserts `schema_version == 1` or rejects unknown command fields under a
strict decoder.

**Required Nova follow-up (separate PR; not in this repo):**

1. Accept catalog / manifest / search-index `schema_version: **2**`.
2. Re-vendor / re-pin `content_sha256` after this bank merges (digest changes).
3. Prefer `package_refs` for install hints; keep reading legacy `packages.*` during transition.
4. Tolerate additive fields (`kind`, `operating_systems`, `package_refs`, `learning_level`, example `shell` / `privilege` / `difficulty`). Ignore unknown keys rather than failing the whole bank load.
5. Do **not** treat `platforms` containing only linux/macos/bsd as a regression — Windows content arrives in later fazes; the schema merely allows `windows`.

Dual-concept (bank ≠ local PATH discovery) is unchanged — see [dual-concept.md](./dual-concept.md).

## Non-goals for Nova UI

- Auto-promoting `draft` → `verified`
- Treating PATH presence as bank verification
- Executing destructive examples from the catalog to “test” them

## Related repos

- **Nova** — UI / Komut Rehberi
- **Nova-Store** — installable apps (different catalog `kind`)
- **Nova-Commands** — this knowledge bank
