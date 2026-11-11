## Değişiklik

<!-- Komut / konsept / kategori / i18n / tooling özeti -->

## Gerekçe


## Kontrol listesi

- [ ] Proje venv + `pip install -r requirements-dev.txt` (sistem Python’a kurulum yok)
- [ ] `python scripts/validate_catalog.py` geçti
- [ ] `python scripts/build_catalog.py` çalıştırıldı; `metadata/` commit’lendi
- [ ] Snapshot docs (README / PLATFORM_SUPPORT / ROADMAP / COVERAGE_MATRIX) counts + `content_sha256` bank ile eşleşiyor
- [ ] `python -m pytest tests/` geçti
- [ ] Yeni/değişen komutlarda **tr + en** dolu
- [ ] `verification.status: verified` **yalnız** insan incelemesi sonrası (AI taslağı `draft` / `reviewed`)
- [ ] Bilinmeyen bayrak / paket adı uydurulmadı
- [ ] Tehlikeli komutlar doğrulama için çalıştırılmadı (CI de çalıştırmaz)
- [ ] Risk seviyesi ve `requires_elevated` gözden geçirildi
- [ ] Wipe-class örneklerde bilingual `warnings` var; `related` id’leri mevcut
- [ ] `keys/*.key` / secret eklenmedi; minisign pubkey’e dokunulmadı (gerekmedikçe)
- [ ] İlgili docs / CONTRIBUTING güncellendi (gerekirse)

## İnceleme notları

- Dual concept: bu PR **Komut Bilgi Bankası** mı, yoksa yerel PATH keşfi değil mi?
- Arch / pacman notları (ilgiliyse) tercih edildi mi?
