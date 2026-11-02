# Local discovery contract (Nova client)

**Status:** documentation-only in Nova-Commands. Implementation lives in Nova
(or a future helper crate), not in this data repo.

This contract describes how **Sistemimde Bulunan Komutlar** should behave so
it never pollutes the curated bank.

## Goals

1. List executables visible to the user (PATH, optionally login shell PATH).
2. Optionally enrich with package ownership (`pacman -Qo`, `dpkg -S`, `rpm -qf`)
   when available — **Arch/pacman preferred** when multiple managers exist.
3. Join to Nova-Commands bank by `id`/`name` when present.
4. Never write discovered binaries into `commands/` automatically.

## Suggested record shape (non-normative JSON)

```json
{
  "schema_version": 1,
  "kind": "nova-local-commands",
  "hostname_hash": "optional-opaque",
  "scanned_at": "2026-11-02T00:00:00Z",
  "entries": [
    {
      "name": "ls",
      "path": "/usr/bin/ls",
      "source": "path",
      "package": {
        "manager": "pacman",
        "name": "coreutils"
      },
      "bank_id": "ls",
      "bank_match": "exact-name"
    }
  ]
}
```

### Field notes

| Field | Rule |
|-------|------|
| `kind` | Always `nova-local-commands` (≠ `nova-commands-bank`) |
| `source` | `path` \| `shell-hash` \| `package-file` \| `other` |
| `bank_id` | Set only when curated catalog contains matching `id`/`name` |
| `package` | Omit if unknown; do not guess |

## Safety

- Do not execute discovered binaries during scan.
- Do not follow user-writable PATH entries into “trusted” without UI warning.
- Privilege: discovery is read-only; package queries should avoid requiring
  sudo. If a query needs root, skip and mark `package: null`.

## Out of scope for this repo

- Performing scans
- Shipping host-specific JSON
- Auto-PRs that add local binaries to the bank

## Related

- [dual-concept.md](./dual-concept.md)
- [nova-consumption.md](./nova-consumption.md)
