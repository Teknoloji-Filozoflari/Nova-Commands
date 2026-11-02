# Safety and verification

## Risk levels

| Level | Use |
|-------|-----|
| `safe` | Everyday read-only or easily reversible |
| `caution` | Needs care; mistakes inconvenient |
| `dangerous` | Can break access, networking, or expose secrets |
| `destructive` | Likely irreversible data loss |

Validators ensure an example’s `risk` is not *lower* than a more severe
command-level expectation when the example clearly escalates (ordering check
on known severity ranks).

## Elevated privileges

`requires_elevated: true` means typical *useful* invocations need root/sudo
(e.g. `pacman -Syu`, `systemctl restart`). Read-only cousins may still be
documented with `requires_elevated: false` on the command if that is the
common path — call out sudo in specific examples instead.

## Verification statuses

| Status | Meaning |
|--------|---------|
| `draft` | AI or incomplete human draft — show as untrusted |
| `reviewed` | Human checked content; minor gaps OK |
| `verified` | Human confirmed flags/packages/examples against authoritative sources |

**Rule:** never promote to `verified` without human review. Catalog CI does
not auto-verify.

## Flag `verified` boolean

Each flag entry has its own `verified` boolean. Default new flags to
`false`. Only set `true` after checking `man` / `--help` for the documented
platform family.

## No unsafe execution in CI or contribution workflows

Do not run destructive or privileged commands to validate YAML. Prefer:

- `man` pages / packaged documentation
- upstream HTML docs
- static `--help` only for **safe** binaries already on the maintainer machine

## Dual concept reminder

Local discovery must not inherit `verified` from “file exists on disk”.
See [dual-concept.md](./dual-concept.md).
