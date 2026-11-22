# First signed bank Release (`catalog-v*`)

One-time maintainer checklist to publish the first **signed** Nova-Commands
bank catalog. Complements [catalog-signing.md](./catalog-signing.md) and
[SECURITY.md](../SECURITY.md).

## Prerequisites

- Maintainer access to `Teknoloji-Filozoflari/Nova-Commands`
- `minisign` on your laptop (`apt install minisign` / brew / …)
- Ability to set repo Actions secrets

## 1. Confirm the public key

```bash
# Committed verification material (clients pin this):
cat keys/minisign.pub
```

If you need a **fresh** keypair (recommended before the first production
signed Release, or after a suspected leak):

```bash
minisign -G -W -p keys/minisign.pub -s nova-commands.key
# Commit keys/minisign.pub only.
# Paste the full contents of nova-commands.key into GitHub Actions secret
# MINISIGN_SECRET_KEY, then shred the local secret:
shred -u nova-commands.key
```

**Coordinate with Nova:** Nova pins the same pubkey in
`assets/keys/nova-commands-catalog.pub` / `src/commands/remote.rs`. Update that
pin in the same release window if you rotate.

## 2. Set the Actions secret

Repo → **Settings → Secrets and variables → Actions**:

| Secret | Value |
|--------|--------|
| `MINISIGN_SECRET_KEY` | Full contents of the minisign **secret** key file (both comment lines + `RWR…` / `RWS…` body) |

Without this secret, [`.github/workflows/publish-catalog.yml`](../.github/workflows/publish-catalog.yml)
**dry-runs**: builds unsigned workflow artifacts and **does not** create a
GitHub Release. Private keys are never invented by CI.

## 3. Dry-run (optional)

**Actions → Publish signed catalog → Run workflow** with `dry_run=true`
(default). Confirm the job builds `dist/{catalog,manifest,search-index}.json`
and skips Release publish.

## 4. Tag and publish

```bash
git checkout main
git pull --ff-only
# Optional: bump notes in the tag message
git tag -a catalog-v0.1.0 -m "catalog v0.1.0 — first signed bank Release"
git push origin catalog-v0.1.0
```

The workflow signs all three JSON files, verifies against `keys/minisign.pub`,
and uploads:

- `catalog.json` / `catalog.json.minisig`
- `manifest.json` / `manifest.json.minisig`
- `search-index.json` / `search-index.json.minisig`

## 5. Verify locally

```bash
# From the Release asset downloads (or dist/ after a local sign):
minisign -Vm catalog.json -p keys/minisign.pub -x catalog.json.minisig
minisign -Vm manifest.json -p keys/minisign.pub -x manifest.json.minisig
minisign -Vm search-index.json -p keys/minisign.pub -x search-index.json.minisig
```

## 6. Nova client check

Nova (Ayarlar → **Komut bankası**) prefers this signed Releases path
(`src/commands/remote.rs`), then falls back to **unsigned** `main` HTTPS
(`src/commands/repo_sync.rs`) with an explicit UI label.

Until a `catalog-v*` Release exists, Nova soft-fails signed fetch and keeps
the embedded / last-trusted bank — that is expected.

## What works without secrets

| Action | Without `MINISIGN_SECRET_KEY` | With secret |
|--------|-------------------------------|-------------|
| CI validate/build on PR | Yes | Yes |
| `workflow_dispatch` dry-run | Yes (unsigned artifacts) | Yes |
| Tag `catalog-v*` → signed GitHub Release | **No** (dry-run only) | Yes |

## Residual

- Empty Releases list until step 4 succeeds with the secret set
- Nova must stay on the matching pubkey pin after any rotation
- Unsigned `main` sync remains a weaker fallback — never treat it as equivalent
  to a verified Release
