# Verification keys

| File | Role |
|------|------|
| [`minisign.pub`](./minisign.pub) | Public key for verifying signed bank Releases |

**Private keys are never stored in this repository.** Maintainers keep the
matching minisign secret in a password manager and in the GitHub Actions secret
`MINISIGN_SECRET_KEY`.

Setup and verify steps: [docs/catalog-signing.md](../docs/catalog-signing.md) ·
[SECURITY.md](../SECURITY.md).
