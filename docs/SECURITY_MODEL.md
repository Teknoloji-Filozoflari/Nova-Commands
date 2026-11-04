# Security model

Nova-Commands is a **curated documentation catalog**. It does not execute
commands, install packages, or store host secrets. The threat model is
**misleading operators** (understated risk, invented flags, missing wipe
warnings) and **supply-chain trust** for published bank JSON.

Canonical policy docs: [SECURITY.md](../SECURITY.md) · [safety.md](safety.md) ·
[catalog-signing.md](catalog-signing.md).

## Two-layer risk

1. **Command character** — entry-level `risk` (`safe` / `caution` / `dangerous` /
   `destructive`) plus `requires_elevated` / `security` metadata where present.
2. **Example risk** — each example may carry its own `risk`, `privilege`, and
   bilingual `warnings`. Do not infer every example from the command name alone
   (e.g. `ip` can be read-only or mutating).

Hard CI gate (`scripts/validate_security.py`, Faz 10):

- Live wipe-class patterns (`dd` of a device, live `mkfs*`, `wipefs -a`, …)
  require bilingual `warnings`
- Unsafe `curl|sh` / fork-bomb style patterns rejected
- `related` must resolve; duplicate aliases fail
- `keys/minisign.pub` must exist; no `*.key` under `keys/`

Dry-run / non-destructive flag combinations are excluded from the wipe hard gate.
Some destructive examples (e.g. certain `rm` / `fdisk` rows) may still only
emit **soft** notices until authors add `warnings[]` — that is intentional
honesty, not a claim of “fully warned.”

## Verification statuses

| Status | Meaning |
|--------|---------|
| `draft` | Not human-reviewed for flags/packages/examples |
| `reviewed` | Human looked; still not a guarantee of every flag |
| `verified` | Human confirmed against primary sources |

CI **never** promotes to `verified`. AI-authored content stays `draft` until
review. Tasks and profiles shipped in Faz 8 remain `draft`.

## Privilege and platform notes

- Windows admin / UAC, BSD `doas`, and Linux `sudo` are documented per entry —
  not equated.
- PowerShell cmdlets are not treated as Bash executables.
- Vendor CLIs and appliance shells are labeled when present; absence means
  **not claimed**.

## What CI does and does not do

| Does | Does not |
|------|----------|
| Schema / i18n / referential validation | Run catalog shell/PowerShell on runners |
| Security static gates | Auto-`verified` |
| Rebuild + committed `content_sha256` check | Rotate minisign keys |
| SHA-pinned Actions on Ubuntu/Windows/macOS | Invent packages/flags |

## Signed catalog trust

Published `catalog.json` / `manifest.json` / `search-index.json` are intended
for `catalog-v*` GitHub Releases with detached **minisign** signatures.
Clients pin [`keys/minisign.pub`](../keys/minisign.pub) and keep the last trusted
bank on verify failure. Without `MINISIGN_SECRET_KEY`, publish **dry-runs** only.

## Dual concept

Curated bank rows are **not** “installed on this host.” Local discovery is a
separate Nova concern ([dual-concept.md](dual-concept.md),
[local-discovery-contract.md](local-discovery-contract.md)).
