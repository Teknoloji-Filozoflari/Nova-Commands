# Security Policy

Nova-Commands is a **curated documentation catalog** (YAML). It does not
execute shell commands, install packages, or hold host secrets. Still, wrong
risk labels or invented destructive examples can mislead operators using
[Nova](https://github.com/Teknoloji-Filozoflari/Nova)’s Komut Rehberi.

## What to report here

Please report privately or via a carefully worded public issue when you find:

- Catalog entries that understate risk (`safe` / missing `requires_elevated`)
  for destructive or privilege-escalating usage
- Invented flags, package names, or examples that could cause data loss if followed
- Instructions that encourage running wipe/firewall/disk tools “to verify” YAML
- Supply-chain concerns in this repo’s **CI Python dependencies** or GitHub Actions

## What not to report here

- Nova desktop/TUI crashes, installers, or Store trust →
  [Nova](https://github.com/Teknoloji-Filozoflari/Nova) / [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store)
- Local “commands found on my machine” PATH bugs → Nova client; see
  [docs/dual-concept.md](docs/dual-concept.md)
- Typo-only i18n nits without safety impact → normal issues / PRs

## How to report

1. Prefer a GitHub Security Advisory (if enabled) or email the org maintainers
   for high-impact catalog errors (e.g. `rm`/`dd`/`mkfs` examples that omit
   critical warnings).
2. For lower severity catalog mistakes, open a **Bug** issue with sources
   (`man`, upstream docs) and **no secrets** in the body.
3. Do **not** attach private keys, tokens, or real host paths.

## Maintainer response expectations

- Acknowledge actionable reports when feasible
- Prefer correcting YAML + risk fields quickly over debating tone
- Never mark AI-authored content `verification.status: verified` while “fixing”
  a security report — human review still required ([docs/safety.md](docs/safety.md))

## Contributor rules (non-negotiable)

- Do not execute destructive or privileged commands to validate catalog entries
- Unknown flags/packages: omit or keep `draft` — do not invent
- Dual concept: file-on-disk ≠ curated `verified`
- Never commit minisign/cosign **private** keys or paste them into issues/PRs

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md),
and [docs/safety.md](docs/safety.md).

## CI security posture (Faz 10)

- Validators are **static**: CI never executes catalog shell/PowerShell examples
  on runners (Ubuntu / Windows / macOS matrix runs Python tooling only).
- Third-party GitHub Actions are pinned to **full commit SHAs** (see
  `.github/workflows/*.yml`); Dependabot may open pin-update PRs.
- `scripts/validate_security.py` hard-fails on wipe-class examples missing
  bilingual `warnings`, broken `related` refs, duplicate aliases, and any
  private key files under `keys/`.
- CI does **not** invent or promote `verification.status: verified`.

## Signed bank Releases (supply chain)

Published bank metadata (`catalog.json`, `manifest.json`, `search-index.json`)
is intended to ship as GitHub Release assets under tags `catalog-v*`, with
detached **minisign** signatures (`.minisig`). Full procedure:
[docs/catalog-signing.md](docs/catalog-signing.md).

### Public key (pin this)

File: [`keys/minisign.pub`](keys/minisign.pub)

```text
untrusted comment: minisign public key A9457AFA9828E8E8
RWTo6CiY+npFqZ+AZVwAkLAik1OQrNVhW7/6hbHnz8nPkWZF00TR9Mof
```

Clients should pin whatever pubkey is currently committed at that path (rotate
with the repo). **No private key is stored in git**; until maintainers set
`MINISIGN_SECRET_KEY` to the matching secret (or replace the pubkey after a
fresh `minisign -G -W`), the publish workflow only dry-runs.

### Verify a release asset

```bash
minisign -Vm catalog.json -p keys/minisign.pub -x catalog.json.minisig
# same for manifest.json and search-index.json
```

### Maintainer signing secret

- Repo Actions secret: `MINISIGN_SECRET_KEY` (full contents of the secret key file)
- If the secret is **absent**, [`.github/workflows/publish-catalog.yml`](.github/workflows/publish-catalog.yml)
  **dry-runs**: builds artifacts and skips signed Release publish (private keys
  are never invented or committed by CI)
- Recommended before first production signed Release: `minisign -G -W`, commit
  the new `keys/minisign.pub`, set `MINISIGN_SECRET_KEY`, shred the local secret,
  then tag `catalog-v*`
- Rotate pubkey + any Nova pin together if a secret may have leaked
