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

## Learning level (not risk)

| Level | Use |
|-------|-----|
| `beginner` | Few conceptual prerequisites; early terminal literacy |
| `intermediate` | Needs pipes/permissions/services/packages/network models |
| `advanced` | Deep systems, low-level, or complex orchestration |
| `unspecified` | Unclear — omit in YAML; catalog build emits this explicitly |

`learning_level` is **independent** of `risk`. Do not mark a command `advanced`
because it is `destructive`. Optional `examples[].difficulty` labels pedagogy
when examples span easy→advanced; never substitute risk for missing difficulty.

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

CI (`scripts/validate_security.py`) additionally:

- Requires bilingual `examples[].warnings` for live wipe-class patterns
  (`dd of=/dev/…`, live `mkfs` / `wipefs -a` / `shred` on devices)
- Rejects `curl|sh` / fork-bomb style examples unless risk is elevated and
  warnings are present
- Rejects dangling `related` command ids and duplicate aliases
- Confirms `keys/minisign.pub` exists and no `*.key` private material is committed

Dry-run / probe-only examples (`mkfs -n`, `wipefs` without `-a`, etc.) are not
treated as live wipes.

## Dual concept reminder

Local discovery must not inherit `verified` from “file exists on disk”.
See [dual-concept.md](./dual-concept.md).
