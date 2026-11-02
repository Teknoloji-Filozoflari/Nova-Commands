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

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/safety.md](docs/safety.md).
