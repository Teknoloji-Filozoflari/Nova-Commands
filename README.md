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
schema/command.schema.json      # giriş şeması
metadata/categories.yaml        # §8.x kategori taksonomisi
metadata/catalog.json           # üretilen toplu indeks
scripts/validate_catalog.py     # CI kapısı
scripts/build_catalog.py        # katalog üretimi
docs/                           # tüketim, keşif sözleşmesi, güvenlik
```

## Geliştirici

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
python3 -m pytest tests/
```

Yeni komut ekleme: [CONTRIBUTING.md](CONTRIBUTING.md)

## Çok dağıtım

Debian/Ubuntu (`apt`), Fedora/RHEL (`dnf`), Arch (`pacman`) birinci sınıf.
Paket notlarında **Arch / pacman tercihi** (Nova tercihleri ile uyumlu).

## Güvenlik

- AI taslakları `verification.status: draft` kalır; `verified` yalnız insan incelemesi sonrası.
- Bilinmeyen bayrak / paket adı **uydurulmaz**; `unknown` / omit.
- Doğrulama için tehlikeli komutlar **çalıştırılmaz**.

## İlişkiler

- [Nova](https://github.com/Teknoloji-Filozoflari/Nova) — UI / Komut Rehberi
- [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store) — kurulabilir uygulama kataloğu
- **Nova-Commands** — komut bilgisi (bu repo)

## Lisans

MIT — [LICENSE](LICENSE)
