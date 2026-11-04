# Signed bank catalog publish

Nova (and other clients) must **not** blindly fetch a remote command bank.
Published bank metadata is a GitHub Release asset set:

| Asset | Purpose |
|-------|---------|
| `catalog.json` | Aggregated commands + concepts + tasks + profiles (`kind: nova-commands-bank`) |
| `manifest.json` | Counts + deterministic `content_sha256` |
| `search-index.json` | Flattened search fields |
| `*.minisig` | Detached **minisign** signatures over each JSON file’s exact bytes |

Clients pin the Nova-Commands **public key** ([`keys/minisign.pub`](../keys/minisign.pub))
and verify signatures before replacing a trusted bank. On failure they keep the
last trusted / embedded catalog.

This mirrors [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store)
signed catalog Releases (`docs/catalog-signing.md` there), for **command bank
metadata** — not installable apps, and not local PATH discovery
([dual-concept](./dual-concept.md)).

## Trust model

1. Contributors PR YAML under `commands/` / `concepts/` / `tasks/` / `profiles/`.
2. CI validates schema, ids, categories, i18n, concepts, tasks/profiles, and rebuilds metadata.
3. Maintainers merge to `main`.
4. Tag `catalog-v*` (or run **Publish signed catalog** via `workflow_dispatch`).
5. The workflow builds metadata, signs when `MINISIGN_SECRET_KEY` is set, and
   uploads assets to a GitHub Release.
6. Clients fetch the latest `catalog-v*` release over HTTPS, verify, then apply.

**Signing private keys never live in this repository.** Only the public
verification material is committed under `keys/`.

## One-time key generation (maintainer laptop)

```bash
# Prefer a fresh keypair before the first production signed release.
# -W = no passphrase (CI cannot prompt). Store the secret only in the
# GitHub Actions secret MINISIGN_SECRET_KEY (and a password manager).
minisign -G -W -p keys/minisign.pub -s nova-commands.key

# Commit keys/minisign.pub (replace any bootstrap pubkey).
# Paste the full contents of nova-commands.key into repo secret
# MINISIGN_SECRET_KEY, then delete the local secret file.
shred -u nova-commands.key   # or: rm -f nova-commands.key
```

If the committed pubkey and the Actions secret drift apart, signing verify in CI
fails closed — rotate both together and bump any Nova pin of this pubkey.

## Sign locally (optional)

```bash
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
mkdir -p dist
cp metadata/catalog.json metadata/manifest.json metadata/search-index.json dist/
minisign -S -s /path/to/nova-commands.key -W \
  -m dist/catalog.json -x dist/catalog.json.minisig
minisign -S -s /path/to/nova-commands.key -W \
  -m dist/manifest.json -x dist/manifest.json.minisig
minisign -S -s /path/to/nova-commands.key -W \
  -m dist/search-index.json -x dist/search-index.json.minisig
```

## Verify (what clients should do)

```bash
minisign -Vm catalog.json -p keys/minisign.pub -x catalog.json.minisig
minisign -Vm manifest.json -p keys/minisign.pub -x manifest.json.minisig
minisign -Vm search-index.json -p keys/minisign.pub -x search-index.json.minisig
```

Or with the inline public key string from [`keys/minisign.pub`](../keys/minisign.pub)
(`minisign -Vm … -P 'RWTo…'`).

After signature verify, clients should still check `kind` /
`schema_version` and `manifest.content_sha256` coherence
([NOVA_INTEGRATION.md](./NOVA_INTEGRATION.md)).

## CI workflow behaviour

Workflow: [`.github/workflows/publish-catalog.yml`](../.github/workflows/publish-catalog.yml)

| Condition | Behaviour |
|-----------|-----------|
| `MINISIGN_SECRET_KEY` **set** + `keys/minisign.pub` present | Sign all three JSON artifacts, verify against committed pubkey, create/update GitHub Release |
| Secret **absent** (forks, first setup, dry-run) | Build artifacts, upload **unsigned** workflow artifacts, **skip** Release publish — no invented keys |

Triggers:

- Push tag `catalog-v*`
- `workflow_dispatch` (optional `dry_run=true` forces the unsigned path even if the secret exists)

```bash
git tag -a catalog-v0.1.0 -m "catalog v0.1.0"
git push origin catalog-v0.1.0
```

## How Nova should consume (bank)

1. Pin `keys/minisign.pub` (or its key string) into the Nova binary / trusted store.
2. GET the latest GitHub Release with tag matching `catalog-v*` from
   `Teknoloji-Filozoflari/Nova-Commands`.
3. Download `catalog.json` (+ optional `manifest.json` / `search-index.json`) and
   matching `.minisig` assets over HTTPS.
4. Verify minisign; reject on failure.
5. Validate `schema_version == 1`, `kind == nova-commands-bank`, and
   `content_sha256` agreement.
6. On any failure: keep previous trusted / embedded bank; surface a non-fatal
   “bank update skipped” status.
7. Never conflate this bank with PATH discovery or Nova-Store app installs.

Unsigned `main` tree sync remains an optional fallback (separate from the
signed Releases trust path) — see [nova-consumption.md](./nova-consumption.md).
