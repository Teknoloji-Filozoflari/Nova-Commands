# Nova-Commands

Linux’tan Windows / macOS / BSD ve sunucu–DevOps araçlarına uzanan **açık kaynak komut ve sistem yönetimi bilgi bankası** — aranabilir, kategorize, çok dilli (TR/EN), doğrulanabilir YAML kataloğu.

Nova’nın **Komut Rehberi**ni besler; tek başına da kullanılabilir. Veri formatı uygulamadan bağımsızdır.

**Repository:** https://github.com/Teknoloji-Filozoflari/Nova-Commands  
**English:** [README.md](README.md)

```
YAML bankası  →  doğrula + derle  →  katalog / arama / manifest  →  Nova UI · imzalı Releases
```

---

## İçindekiler

1. [Canlı katalog](#canlı-katalog-post23)
2. [İki alan](#iki-alan--karıştırma)
3. [Mimari](#mimari)
4. [Depo haritası](#depo-haritası)
5. [Platform ve paket yöneticileri](#platform-ve-paket-yöneticileri)
6. [Geliştirici](#geliştirici)
7. [İmzalı katalog Releases](#imzalı-katalog-releases)
8. [Güvenlik](#güvenlik)
9. [Katkı](#katkı)
10. [İlişkiler](#ilişkiler)

---

## Canlı katalog (post–[#30](https://github.com/Teknoloji-Filozoflari/Nova-Commands/pull/30))

Sayılar üretilmiş `metadata/manifest.json` / `search-index.json` ile uyumludur —
pazarlama hedefi değildir. Güven denetimi sonrası özette uyarı/`status`
dürüstlüğü digest’i güncelleyebilir.

| Metrik | Değer |
|--------|------:|
| Komut | **267** |
| Konsept makalesi | **21** |
| Görev (`tasks/`) | **36** (hepsi `draft`) |
| Profil (`profiles/`) | **14** (hepsi `draft`) |
| Arama girdisi | **338** |
| OS kaydı | **11** |
| Paket yöneticisi kaydı | **60** |
| `schema_version` | **2** |
| `verification` (komut) | verified **26** / reviewed **105** / draft **136** |
| `verification` (konsept) | reviewed **1** / draft **20** (sahte `verified` yok) |
| `content_sha256` | `406fe04002c47c592009c71f6d9dbb1f0ec7c9faa6c19165f58bebe29265b716` |

```mermaid
pie title Komut verification.status (267)
  "verified" : 26
  "reviewed" : 105
  "draft" : 136
```

Kayıt defterinde bir OS/PM id’si olması, o platformda her komutun doğrulandığı
anlamına **gelmez**. Yol haritası: [docs/ROADMAP.md](docs/ROADMAP.md).

---

## İki alan — karıştırma

Bunları **kesin ayır** — UI ve dokümanlar karıştırmamalı.

| Alan | Ne | Bu repo? |
|------|----|----------|
| **Komut Bilgi Bankası** | Kürate / şemalı / doğrulama durumlu bilgi | Evet — `commands/`, `concepts/`, `tasks/`, `profiles/` |
| **Sistemimde Bulunan Komutlar** | Cihaz PATH / paket keşfi (Nova yerel) | Hayır — yalnız [sözleşme](docs/local-discovery-contract.md) |

```mermaid
flowchart LR
  subgraph Bank["Komut Bilgi Bankası — bu repo"]
    YAML["commands/ · concepts/<br/>tasks/ · profiles/"]
    CAT["metadata/catalog.json"]
    YAML --> CAT
  end
  subgraph Local["Sistemimde Bulunan Komutlar — yalnız Nova"]
    PATH["PATH / shell / PM keşfi"]
  end
  CAT -.->|"id/name ile birleşebilir"| PATH
  PATH -.->|"verified anlamına gelmez"| CAT
```

Ayrıntı: [docs/dual-concept.md](docs/dual-concept.md)

---

## Mimari

Önce veri reposu: YAML + JSON Schema + CI. Burada çalışma zamanı daemon’u yok.

```mermaid
flowchart TB
  subgraph Sources["Kaynak gerçeği"]
    C["commands/category/id.yaml"]
    N["concepts/*.yaml"]
    T["tasks/*.yaml"]
    P["profiles/*.yaml"]
    R["metadata kayıt defterleri<br/>OS · distro · shell · PM"]
    S["schema/*.json"]
  end

  V["scripts/validate_catalog.py<br/>+ validate_security.py<br/>+ platform soft kapılar"]
  B["scripts/build_catalog.py"]

  subgraph Artifacts["Commit edilen artefaktlar"]
    CAT["catalog.json"]
    IDX["search-index.json"]
    MAN["manifest.json<br/>content_sha256"]
  end

  subgraph Consumers["Tüketiciler"]
    Nova["Nova — Komut Rehberi"]
    Rel["GitHub Release catalog-v*<br/>minisign"]
  end

  C --> V
  N --> V
  T --> V
  P --> V
  R --> V
  S --> V
  V --> B
  B --> CAT
  B --> IDX
  B --> MAN
  CAT --> Nova
  CAT --> Rel
  IDX --> Nova
  MAN --> Rel
```

```mermaid
flowchart LR
  PR["PR"] --> Val["validate"] --> Sec["güvenlik"] --> Build["build"] --> Test["pytest"] --> SHA["content_sha256 eşleşmesi"] --> Merge["merge"]
```

- CI `verification.status` değerini **asla** otomatik `verified` yapmaz.
- `content_sha256` commands + concepts + tasks + profiles kapsar (`generated_at` hariç).
- Ayrıntılı yerleşim: [docs/architecture.md](docs/architecture.md)

---

## Depo haritası

```
commands/<category>/<id>.yaml     # kaynak gerçeği (schema_version: 2)
concepts/<id>.yaml                # öğrenilebilir makaleler (TR/EN)
tasks/<id>.yaml                   # niyet → çok OS uygulamaları
profiles/<id>.yaml                # sunucu / rol referans koleksiyonları

schema/command.schema.json        # v2 — canlı commands/ bankası
schema/command.schema.v2.json     # v2 twin (tooling $id)
schema/command.schema.v1.json     # arşiv v1
schema/{task,profile,concept,…}.schema.json

metadata/categories.yaml          # §8.x taksonomi (21 kategori)
metadata/operating-systems.yaml   # OS ≠ distro ≠ shell ≠ PM
metadata/{distributions,shells,package-managers,…}.yaml
metadata/catalog.json             # üretilen banka (schema_version 2)
metadata/search-index.json
metadata/manifest.json            # sayılar + deterministik content_sha256

scripts/validate_catalog.py       # CI kapısı
scripts/validate_security.py      # statik güvenlik hard kapıları
scripts/build_catalog.py          # katalog / indeks / manifest
scripts/migrate_v1_to_v2.py       # idempotent v1→v2

docs/PLATFORM_SUPPORT.md
docs/ROADMAP.md
docs/SECURITY_MODEL.md
docs/SCHEMA_MIGRATION_V2.md
docs/NOVA_INTEGRATION.md
```

Canlı bankadaki komut kategorileri:

`filesystem` · `text` · `search` · `processes` · `system` · `network` · `users` ·
`packages` · `archives` · `disks` · `shell` · `development` · `containers` ·
`security` · `monitoring` · `hardware` · `virtualization` · `backup` ·
`databases` · `cloud` · `devops`

---

## Platform ve paket yöneticileri

Dürüst kapsam — kayıt satırı veya `draft` banka, tam doğrulama demek **değildir**.
Arch ailesinde kurulum notlarında **pacman** tercihi korunur.

```mermaid
flowchart TB
  subgraph OS["İşletim sistemi kaydı — 11 satır"]
    L["linux"]
    W["windows"]
    M["macos"]
    B["freebsd · openbsd · netbsd"]
    X["dragonflybsd · illumos · solaris · aix · android"]
  end

  subgraph Banks["Komut bankası derinliği"]
    L -->|birinci sınıf PM notları + derin banka| LF["apt · dnf · pacman"]
    L -->|Faz 4 draft bankalar| LD["zypper · apk · emerge · xbps · eopkg · slackpkg · nix/guix · opkg · rpm-ostree"]
    W -->|Faz 5 draft| WB["PowerShell 7+ / WinPS 5.1 / cmd · WinGet · UAC"]
    M -->|Faz 5 draft| MB["Homebrew / MacPorts · launchd · diskutil · …"]
    B -->|Faz 6 draft| BB["pkg / Ports · pkg_add · pkgin · service/rcctl ≠ systemctl"]
    X -->|metadata / genişletilebilirlik| XB["sahte tam komut bankası yok"]
  end
```

```mermaid
flowchart LR
  subgraph PM["Paket yöneticisi kaydı — 60 satır"]
    SYS["Sistem PM<br/>apt · dnf · pacman · …"]
    LANG["Dil PM<br/>pip · npm · cargo · …"]
    UNI["Evrensel<br/>Flatpak · Snap · AppImage"]
  end
  SYS --> HINT["commands → package_refs"]
  LANG --> HINT
  UNI --> HINT
```

| Alan | Ağaçta ne var | Dürüst not |
|------|---------------|------------|
| Linux PM | apt / dnf / pacman birinci sınıf; diğerleri `draft` | Çoğu satır `draft` / `partial` |
| Windows / macOS | Draft komut bankaları + shell/PM kayıtları | Toplu `verified` iddiası yok |
| BSD | FreeBSD / OpenBSD / NetBSD draft bankalar | DragonFly / illumos / Solaris / AIX çoğunlukla iskelet |
| Sunucu / DevOps | Ağ, K8s istemcileri, libvirt, yedek, bulut CLI, IaC (`draft`) | Kategori var; derinlik değişir |
| Görevler / profiller | 26 + 13, hepsi `draft` | Yol gösterici — **otomatik çalıştırılmaz** |

Karşılaştırma: [docs/package-managers-comparison.md](docs/package-managers-comparison.md) ·
Platform: [docs/PLATFORM_SUPPORT.md](docs/PLATFORM_SUPPORT.md) ·
Sunucu: [docs/SERVER_ADMINISTRATION.md](docs/SERVER_ADMINISTRATION.md) ·
Yol haritası: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## Geliştirici

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_catalog.py
python3 scripts/build_catalog.py
python3 -m pytest tests/
```

Yeni komut / konsept: [CONTRIBUTING.md](CONTRIBUTING.md) ·
Nova: [docs/NOVA_INTEGRATION.md](docs/NOVA_INTEGRATION.md)

---

## İmzalı katalog Releases

Bank metadata (`catalog.json` / `manifest.json` / `search-index.json`) GitHub
Release etiketleri `catalog-v*` ile yayımlanır; **minisign** ile imzalanır.

```mermaid
flowchart LR
  Build["build_catalog.py"] --> Art["catalog.json + manifest + search-index"]
  Art --> WF["publish-catalog.yml"]
  WF -->|"MINISIGN_SECRET_KEY var"| Sig["imzalı catalog-v* Release"]
  WF -->|"secret yok"| Dry["dry-run · imzasız artefakt"]
  Sig --> Verify["minisign -Vm … -p keys/minisign.pub"]
```

- Genel anahtar: [`keys/minisign.pub`](keys/minisign.pub)
- Doğrulama + yayın: [docs/catalog-signing.md](docs/catalog-signing.md) · [SECURITY.md](SECURITY.md)
- Private key CI’da **üretilmez / commit edilmez**

```bash
minisign -Vm catalog.json -p keys/minisign.pub -x catalog.json.minisig
```

Bu, **komut bilgi bankası** imzasıdır; yerel PATH keşfi veya Nova-Store uygulama
katalogu değildir ([docs/dual-concept.md](docs/dual-concept.md)).

---

## Güvenlik

- AI taslakları `verification.status: draft` kalır; `verified` yalnız insan incelemesi sonrası.
- Bilinmeyen bayrak / paket adı **uydurulmaz**.
- Doğrulama için tehlikeli komutlar **çalıştırılmaz**; CI runner’ları katalog komutlarını yürütmez.
- Politika: [SECURITY.md](SECURITY.md) · [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) ·
  [docs/safety.md](docs/safety.md)

---

## Katkı

- [CONTRIBUTING.md](CONTRIBUTING.md) · [docs/ROADMAP.md](docs/ROADMAP.md)
- Göç: [docs/SCHEMA_MIGRATION_V2.md](docs/SCHEMA_MIGRATION_V2.md)
- Issue formları: bug · yeni komut · kategori · çeviri (`.github/ISSUE_TEMPLATE/`)
- CI: validate → güvenlik kapıları → build → pytest → committed `content_sha256`
  eşleşmesi (Ubuntu / Windows / macOS matrix — **yalnız Python tooling**)

---

## İlişkiler

```mermaid
flowchart TB
  NC["Nova-Commands<br/>komut bilgi bankası"]
  Nova["Nova<br/>UI / Komut Rehberi"]
  Store["Nova-Store<br/>kurulabilir uygulama kataloğu"]
  NC -->|"besler"| Nova
  Store -->|"ayrı katalog"| Nova
```

- [Nova](https://github.com/Teknoloji-Filozoflari/Nova) — UI / Komut Rehberi
- [Nova-Store](https://github.com/Teknoloji-Filozoflari/Nova-Store) — kurulabilir uygulama kataloğu
- **Nova-Commands** — komut bilgisi (bu repo)

---

## Lisans

MIT — [LICENSE](LICENSE)
