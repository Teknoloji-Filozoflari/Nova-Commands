# Nova-Commands

Open-source **cross-platform command & system-administration knowledge base** —
searchable, categorized, bilingual (TR/EN), schema-validated YAML.

Feeds Nova’s **Komut Rehberi**; usable standalone. Data format is
application-independent.

**Repository:** https://github.com/Teknoloji-Filozoflari/Nova-Commands  
**Türkçe:** [README.tr.md](README.tr.md)

## Live catalog (after [#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23))

| Metric | Value |
|--------|------:|
| Commands | **256** |
| Concepts | **20** |
| Tasks / profiles | **21** / **13** (all `draft`) |
| Search entries | **310** |
| OS / package-manager registry rows | **11** / **60** |
| `schema_version` | **2** |
| verification | verified **26** / reviewed **105** / draft **125** |
| `content_sha256` | `7b24390eb92de6cda76b330d61fd34dcdb304afe27c1595355621717b653bf54` |

Registry presence ≠ every command verified on that OS. Roadmap:
[docs/ROADMAP.md](docs/ROADMAP.md).

## İki alan — karıştırma

| Alan | Ne | Bu repo? |
|------|----|----------|
| **Komut Bilgi Bankası** | Kürate / şemalı / doğrulama durumlu komut bilgisi | Evet (`commands/`) |
| **Sistemimde Bulunan Komutlar** | Cihaz PATH / paket keşfi (Nova yerel) | Hayır — yalnızca [sözleşme](docs/local-discovery-contract.md) |

Ayrıntı: [docs/dual-concept.md](docs/dual-concept.md)

## Hızlı bakış

```
commands/<category>/<id>.yaml   # kaynak gerçeği (schema_version: 2)
concepts/<id>.yaml              # öğrenilebilir konsept makaleleri (TR/EN)
tasks/<id>.yaml                 # niyet → çok platform uygulama (Faz 8)
profiles/<id>.yaml              # sunucu / rol referans koleksiyonları (Faz 8)
schema/command.schema.json      # v2 — canlı commands/ bankası
schema/command.schema.v2.json   # v2 twin (ayrı $id; tooling)
schema/command.schema.v1.json   # arşiv v1
schema/{task,profile}.schema.json
schema/{concept,catalog,compatibility,operating-system,…}.schema.json
fixtures/schema-v2/             # şema örnekleri (katalogda yok)
metadata/categories.yaml        # §8.x kategori taksonomisi
metadata/concepts.yaml          # konsept kayıt defteri
metadata/operating-systems.yaml # platform kayıtları (OS ≠ distro ≠ shell ≠ PM)
metadata/{distributions,shells,package-managers,…}.yaml
metadata/catalog.json           # üretilen banka (commands + concepts; schema_version 2)
metadata/search-index.json      # arama indeksi
metadata/manifest.json          # sayılar + deterministik content_sha256
scripts/validate_catalog.py     # CI kapısı (v2 bank + soft gates + tasks/profiles)
scripts/validate_tasks_profiles.py
scripts/migrate_v1_to_v2.py     # v1→v2 göç (idempotent)
scripts/validate_platform_registries.py
scripts/validate_schema_v2.py
scripts/build_catalog.py        # katalog / indeks / manifest
docs/DATA_SCHEMA.md             # live v2 schema policy
docs/SCHEMA_MIGRATION_V2.md     # migration + release policy
docs/PLATFORM_SUPPORT.md        # platform support matrix
docs/ROADMAP.md                 # faz status + follow-ups
docs/SECURITY_MODEL.md          # risk / trust model
docs/SERVER_ADMINISTRATION.md   # server / task / profile scope
docs/NOVA_INTEGRATION.md        # Nova consume contract (v2 notes)
```

## Geliştirici

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
python3 -m pytest tests/
```

Yeni komut / konsept: [CONTRIBUTING.md](CONTRIBUTING.md) · Nova: [docs/NOVA_INTEGRATION.md](docs/NOVA_INTEGRATION.md)

## Çok dağıtım

Debian/Ubuntu (`apt`), Fedora/RHEL (`dnf`), Arch (`pacman`) birinci sınıf.
Faz 4 genişlemesi (çoğu `draft`): openSUSE (`zypper`), Alpine (`apk`), Gentoo
(`emerge`), Void (`xbps-*`), Solus (`eopkg`), Slackware (`slackpkg`/pkgtools),
Nix/Guix, OpenWrt (`opkg`), atomik Fedora (`rpm-ostree`).
Faz 5 (`draft`): **Windows** (PowerShell 7+ / Windows PowerShell 5.1 / cmd.exe
ayrımı, WinGet, UAC notları) ve **macOS** (Homebrew/MacPorts, launchd, diskutil,
networksetup, softwareupdate, …; BSD vs GNU araç notları).
Faz 6 (`draft`): **BSD** (FreeBSD `pkg`/Ports/`service`/`sysrc`/jails/ZFS;
OpenBSD `pkg_add`/`rcctl`/`doas`/`pfctl`; NetBSD `pkgin`/`pkgsrc`; shared
`ifconfig`/`newsyslog`; systemd ile eşitlenmez). illumos/Solaris/AIX yalnız
genişletilebilirlik metadata’sı.
Faz 7 (`draft`): **sunucu / network / DevOps** — `tcpdump`/`nmap`/`mtr`,
Kubernetes (`kubectl`/`helm`/`nerdctl`/`crictl`), libvirt/`qemu-img`,
nginx/Caddy, DB istemcileri, restic/Borg/rclone, AWS/Azure/GCP CLI,
Terraform/Ansible/`gh`; yeni kategoriler `virtualization`/`backup`/
`databases`/`cloud`/`devops`.
Faz 8 (`draft`): **`tasks/`** (çok platform niyet tarifleri) + **`profiles/`**
(linux/debian/fedora/arch/windows/freebsd sunucu, homelab, docker-host,
kubernetes, web/db/nas/virt).
Faz 9: tasks/profiles indexed in `catalog.json` / `search-index.json` /
`manifest.json`; `content_sha256` covers commands+concepts+tasks+profiles.
Faz 10 ([#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23)):
static security validator + SHA-pinned multi-OS CI (tooling only; no catalog
command execution on runners).
Faz 11: docs / migration / release policy polish (this track).
Install notes prefer **Arch / pacman** when Arch-family applies.
Compare: [docs/package-managers-comparison.md](docs/package-managers-comparison.md)
· Nix/Guix: `concepts/nix-guix.yaml`
· Platform: [docs/PLATFORM_SUPPORT.md](docs/PLATFORM_SUPPORT.md)
· Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)
· Server: [docs/SERVER_ADMINISTRATION.md](docs/SERVER_ADMINISTRATION.md).

## İmzalı katalog Releases

Bank metadata (`catalog.json` / `manifest.json` / `search-index.json`) GitHub
Release etiketleri `catalog-v*` ile yayımlanır; **minisign** ile imzalanır.

- Genel anahtar: [`keys/minisign.pub`](keys/minisign.pub)
- Doğrulama + yayın: [docs/catalog-signing.md](docs/catalog-signing.md) · [SECURITY.md](SECURITY.md)
- CI: [`.github/workflows/publish-catalog.yml`](.github/workflows/publish-catalog.yml)
  — `MINISIGN_SECRET_KEY` yoksa dry-run (imzasız artifact; private key üretilmez/commit edilmez)

```bash
minisign -Vm catalog.json -p keys/minisign.pub -x catalog.json.minisig
```

Bu, **komut bilgi bankası** imzasıdır; yerel PATH keşfi veya Nova-Store uygulama
katalogu değildir ([docs/dual-concept.md](docs/dual-concept.md)).

## Security

- AI drafts stay `verification.status: draft`; `verified` only after human review.
- Unknown flags / package names are **not invented**; omit or keep draft.
- Dangerous commands are **not executed** to validate YAML; CI runners never
  execute catalog examples.
- Policy: [SECURITY.md](SECURITY.md) · [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) ·
  [docs/safety.md](docs/safety.md)

## Contributing

- [CONTRIBUTING.md](CONTRIBUTING.md) · [docs/ROADMAP.md](docs/ROADMAP.md)
- Issue forms: bug · new command · category · translation (`.github/ISSUE_TEMPLATE/`)
- PR template: `.github/PULL_REQUEST_TEMPLATE.md`
- CI: validate → security gates → build → pytest → committed `content_sha256`
  (Ubuntu / Windows / macOS matrix for Python tooling)

## İlişkiler

- [Nova](https://github.com/Teknoloji-Filozoflari/Nova) — UI / Komut Rehberi
- [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store) — kurulabilir uygulama kataloğu
- **Nova-Commands** — komut bilgisi (bu repo)

## Lisans

MIT — [LICENSE](LICENSE)
