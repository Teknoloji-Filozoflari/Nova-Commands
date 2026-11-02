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
commands/<category>/<id>.yaml   # kaynak gerçeği (bir komut = bir dosya)
concepts/<id>.yaml              # öğrenilebilir konsept makaleleri (TR/EN)
schema/{command,concept,catalog}.schema.json
metadata/categories.yaml        # §8.x kategori taksonomisi
metadata/concepts.yaml          # konsept kayıt defteri
metadata/catalog.json           # üretilen banka (commands + concepts)
metadata/search-index.json      # arama indeksi
metadata/manifest.json          # sayılar + deterministik content_sha256
scripts/validate_catalog.py     # CI kapısı (i18n + concepts)
scripts/build_catalog.py        # katalog / indeks / manifest
docs/NOVA_INTEGRATION.md        # Nova tüketim sözleşmesi
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
Paket notlarında **Arch / pacman tercihi** (Nova tercihleri ile uyumlu).
Karşılaştırma tabloları: [docs/package-managers-comparison.md](docs/package-managers-comparison.md).

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
