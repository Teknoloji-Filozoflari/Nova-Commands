# Dual concept: bank vs local discovery

Nova-Commands and Nova UI must keep these **strictly separate**.

## 1. Komut Bilgi Bankası (this repository)

- Curated YAML under `commands/`
- Schema-validated, bilingual (TR/EN)
- Risk labels, examples, flags, package hints
- `verification.status` lifecycle (`draft` → `reviewed` → `verified`)
- Shipped/aggregated as `metadata/catalog.json` (`kind: nova-commands-bank`)

This answers: *“What does `rsync` do? What are safe examples? Which package
on Arch?”*

## 2. Sistemimde Bulunan Komutlar (Nova local only)

- Discovered from the user’s PATH, shells, and optionally package managers
- Device-specific; not a contribution target for this repo
- May **join** bank metadata by name/id when a curated entry exists
- Must never be presented as “verified catalog content” merely because a
  binary exists on disk

Contract for the local side (docs only in this phase):
[local-discovery-contract.md](./local-discovery-contract.md)

## UI wording checklist

| Do | Don’t |
|----|-------|
| “Bilgi bankasında” / “In the command bank” | Call PATH hits “verified” |
| “Bu cihazda bulundu” / “Found on this device” | Merge both lists without labels |
| Show bank risk badges from YAML | Infer safety from “binary exists” |

## Favorites

Favorites are a Nova client concern. Bank entries may set
`nova.favorite_eligible` as a hint; local-only discoveries can still be
favorited by path/name without implying bank verification.
