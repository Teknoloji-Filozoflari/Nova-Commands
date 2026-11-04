# Nova-Commands

Linux terminal **komut bilgi bankası** — aranabilir, kategorize, çok dilli (TR/EN),
doğrulanabilir YAML kataloğu.

Nova’nın **Komut Rehberi**ni besler; tek başına da kullanılabilir.

**Repository:** https://github.com/Teknoloji-Filozoflari/Nova-Commands

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
schema/command.schema.json      # v2 — canlı commands/ bankası
schema/command.schema.v2.json   # v2 twin (ayrı $id; tooling)
schema/command.schema.v1.json   # arşiv v1
schema/{task,profile,compatibility}.schema.json  # stub (içerik Faz 8)
schema/{concept,catalog,operating-system,…}.schema.json
fixtures/schema-v2/             # stub/örnek fixtures (katalogda yok)
metadata/categories.yaml        # §8.x kategori taksonomisi
metadata/concepts.yaml          # konsept kayıt defteri
metadata/operating-systems.yaml # platform kayıtları (OS ≠ distro ≠ shell ≠ PM)
metadata/{distributions,shells,package-managers,…}.yaml
metadata/catalog.json           # üretilen banka (commands + concepts; schema_version 2)
metadata/search-index.json      # arama indeksi
metadata/manifest.json          # sayılar + deterministik content_sha256
scripts/validate_catalog.py     # CI kapısı (v2 bank + soft platform + stubs)
scripts/migrate_v1_to_v2.py     # v1→v2 göç (idempotent)
scripts/validate_platform_registries.py
scripts/validate_schema_v2.py
scripts/build_catalog.py        # katalog / indeks / manifest
docs/DATA_SCHEMA.md             # canlı v2 şema politikası
docs/SCHEMA_MIGRATION_V2.md     # göç notları
docs/PLATFORM_SUPPORT.md        # platform metadata kapsamı
docs/NOVA_INTEGRATION.md        # Nova tüketim sözleşmesi (v2 breakage notes)
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
Paket notlarında **Arch / pacman tercihi** (Nova tercihleri ile uyumlu).
Karşılaştırma: [docs/package-managers-comparison.md](docs/package-managers-comparison.md)
· Nix/Guix: `concepts/nix-guix.yaml`.

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

## Güvenlik

- AI taslakları `verification.status: draft` kalır; `verified` yalnız insan incelemesi sonrası.
- Bilinmeyen bayrak / paket adı **uydurulmaz**; `unknown` / omit.
- Doğrulama için tehlikeli komutlar **çalıştırılmaz**.
- Politika: [SECURITY.md](SECURITY.md) · [docs/safety.md](docs/safety.md)

## Katkı

- [CONTRIBUTING.md](CONTRIBUTING.md)
- Issue formları: bug · yeni komut · kategori · çeviri (`.github/ISSUE_TEMPLATE/`)
- PR şablonu: `.github/PULL_REQUEST_TEMPLATE.md`
- CI: validate → build → pytest → committed `content_sha256` eşleşmesi

## İlişkiler

- [Nova](https://github.com/Teknoloji-Filozoflari/Nova) — UI / Komut Rehberi
- [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store) — kurulabilir uygulama kataloğu
- **Nova-Commands** — komut bilgisi (bu repo)

## Lisans

MIT — [LICENSE](LICENSE)
