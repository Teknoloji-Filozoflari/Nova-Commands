## Değişiklik

<!-- Komut / konsept / kategori / i18n / tooling özeti -->

## Gerekçe


## Kontrol listesi

- [ ] `python3 scripts/validate_catalog.py` geçti
- [ ] `python3 scripts/build_catalog.py` çalıştırıldı; `metadata/` commit’lendi
- [ ] `python3 -m pytest tests/` geçti
- [ ] Yeni/değişen komutlarda **tr + en** dolu
- [ ] `verification.status: verified` **yalnız** insan incelemesi sonrası (AI taslağı `draft` / `reviewed`)
- [ ] Bilinmeyen bayrak / paket adı uydurulmadı
- [ ] Tehlikeli komutlar doğrulama için çalıştırılmadı
- [ ] Risk seviyesi ve `requires_elevated` gözden geçirildi
- [ ] İlgili docs / CONTRIBUTING güncellendi (gerekirse)

## İnceleme notları

- Dual concept: bu PR **Komut Bilgi Bankası** mı, yoksa yerel PATH keşfi değil mi?
- Arch / pacman notları (ilgiliyse) tercih edildi mi?
