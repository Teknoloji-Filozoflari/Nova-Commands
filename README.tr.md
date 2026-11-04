# Nova-Commands

Linux’tan Windows / macOS / BSD ve sunucu–DevOps araçlarına uzanan **açık kaynak komut ve sistem yönetimi bilgi bankası** — aranabilir, kategorize, çok dilli (TR/EN), doğrulanabilir YAML kataloğu.

Nova’nın **Komut Rehberi**ni besler; tek başına da kullanılabilir. Veri formatı uygulamadan bağımsızdır.

**Repository:** https://github.com/Teknoloji-Filozoflari/Nova-Commands  
**English:** [README.md](README.md)

## İki alan — karıştırma

| Alan | Ne | Bu repo? |
|------|----|----------|
| **Komut Bilgi Bankası** | Kürate / şemalı / doğrulama durumlu komut bilgisi | Evet (`commands/`, `concepts/`, `tasks/`, `profiles/`) |
| **Sistemimde Bulunan Komutlar** | Cihaz PATH / paket keşfi (Nova yerel) | Hayır — yalnız [sözleşme](docs/local-discovery-contract.md) |

Ayrıntı: [docs/dual-concept.md](docs/dual-concept.md)

## Canlı katalog (post–[#23](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/23))

| Metrik | Değer |
|--------|------:|
| Komut | **256** |
| Konsept makalesi | **20** |
| Görev (`tasks/`) | **21** (hepsi `draft`) |
| Profil (`profiles/`) | **13** (hepsi `draft`) |
| Arama girdisi | **310** |
| OS kaydı | **11** |
| Paket yöneticisi kaydı | **60** |
| `schema_version` | **2** |
| `verification` | verified **26** / reviewed **105** / draft **125** |
| `content_sha256` | `7b24390eb92de6cda76b330d61fd34dcdb304afe27c1595355621717b653bf54` |

Bu sayılar üretilmiş `metadata/manifest.json` ile uyumludur. Kayıt defterinde bir OS/PM id’si olması, o platformda her komutun doğrulandığı anlamına **gelmez**.

## Hızlı bakış

```
commands/<category>/<id>.yaml   # kaynak gerçeği (schema_version: 2)
concepts/<id>.yaml              # öğrenilebilir konsept makaleleri (TR/EN)
tasks/<id>.yaml                 # niyet → çok platform uygulama
profiles/<id>.yaml              # sunucu / rol referans koleksiyonları
schema/command.schema.json      # v2 — canlı commands/ bankası
schema/command.schema.v1.json   # arşiv v1
schema/{task,profile,…}.schema.json
metadata/operating-systems.yaml # OS ≠ distro ≠ shell ≠ PM
metadata/{distributions,shells,package-managers,…}.yaml
metadata/catalog.json           # üretilen banka (schema_version 2)
metadata/search-index.json
metadata/manifest.json          # sayılar + deterministik content_sha256
scripts/validate_catalog.py     # CI kapısı (+ güvenlik)
scripts/validate_security.py
scripts/migrate_v1_to_v2.py
scripts/build_catalog.py
docs/PLATFORM_SUPPORT.md
docs/SCHEMA_MIGRATION_V2.md
docs/ROADMAP.md
docs/SECURITY_MODEL.md
```

## Geliştirici

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
python3 -m pytest tests/
```

Yeni komut / konsept: [CONTRIBUTING.md](CONTRIBUTING.md) · Nova: [docs/NOVA_INTEGRATION.md](docs/NOVA_INTEGRATION.md)

## Platform kapsamı (dürüst özet)

- **Linux PM:** Debian/Ubuntu (`apt`), Fedora/RHEL (`dnf`), Arch (`pacman` — tercih) birinci sınıf; ayrıca zypper, apk, emerge, xbps, eopkg, slackpkg, nix/guix, opkg, rpm-ostree (çoğu `draft`).
- **Windows / macOS:** PowerShell 7+ / Windows PowerShell 5.1 / cmd ayrımı; WinGet; Homebrew/MacPorts; launchd / diskutil / … (`draft` bankalar).
- **BSD:** FreeBSD / OpenBSD / NetBSD komutları; DragonFly / illumos / Solaris / AIX çoğunlukla metadata iskeleti.
- **Sunucu / DevOps:** ağ, konteyner/K8s, libvirt, yedekleme, bulut CLI, IaC başlangıç kapsamı (`draft`).
- **Görevler / profiller:** niyet → çok OS uygulamaları; sunucu rol koleksiyonları — otomatik çalıştırılmaz.

Ayrıntı: [docs/PLATFORM_SUPPORT.md](docs/PLATFORM_SUPPORT.md) · [docs/ROADMAP.md](docs/ROADMAP.md) · [docs/package-managers-comparison.md](docs/package-managers-comparison.md)

## İmzalı katalog Releases

Bank metadata (`catalog.json` / `manifest.json` / `search-index.json`) GitHub Release etiketleri `catalog-v*` ile yayımlanır; **minisign** ile imzalanır.

- Genel anahtar: [`keys/minisign.pub`](keys/minisign.pub)
- Doğrulama + yayın: [docs/catalog-signing.md](docs/catalog-signing.md) · [SECURITY.md](SECURITY.md)
- `MINISIGN_SECRET_KEY` yoksa publish workflow **dry-run** (imzasız; private key üretilmez/commit edilmez)

Bu, **komut bilgi bankası** imzasıdır; yerel PATH keşfi veya Nova-Store uygulama katalogu değildir.

## Güvenlik

- AI taslakları `verification.status: draft` kalır; `verified` yalnız insan incelemesi sonrası.
- Bilinmeyen bayrak / paket adı **uydurulmaz**.
- Doğrulama için tehlikeli komutlar **çalıştırılmaz**; CI runner’ları katalog komutlarını yürütmez.
- Politika: [SECURITY.md](SECURITY.md) · [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) · [docs/safety.md](docs/safety.md)

## Katkı

- [CONTRIBUTING.md](CONTRIBUTING.md)
- Yol haritası: [docs/ROADMAP.md](docs/ROADMAP.md)
- Göç: [docs/SCHEMA_MIGRATION_V2.md](docs/SCHEMA_MIGRATION_V2.md)
- CI: validate → güvenlik kapıları → build → pytest → committed `content_sha256` eşleşmesi (Ubuntu / Windows / macOS matrix)

## İlişkiler

- [Nova](https://github.com/Teknoloji-Filozoflari/Nova) — UI / Komut Rehberi
- [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store) — kurulabilir uygulama kataloğu
- **Nova-Commands** — komut bilgisi (bu repo)

## Lisans

MIT — [LICENSE](LICENSE)
