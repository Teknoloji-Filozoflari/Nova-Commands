#!/usr/bin/env python3
"""One-shot Faz 6 seeder: BSD family command YAML (schema v2).

Not for re-run after content is curated — edits go in commands/ directly.
Windows already owns id `netstat`; BSD netstat uses id `netstat-bsd` (name: netstat).
FreeBSD owns id `pkg`; DragonFly pkg is registry-only (not the same tool).
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "commands"

yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, _: dumper.represent_scalar("tag:yaml.org,2002:null", ""),
)


def dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )
    path.write_text(text, encoding="utf-8")


def L(tr: str, en: str) -> dict:
    return {"tr": tr, "en": en}


def draft_sources(
    *urls: str,
    note: str = "Agent-authored Faz 6 draft from official docs; not human-verified.",
) -> dict:
    return {"status": "draft", "sources": list(urls), "notes": note}


def flag(name: str, tr: str, en: str, **extra) -> dict:
    f = {"flag": name, "meaning": L(tr, en), "verified": False}
    f.update(extra)
    return f


def ex(
    title_tr: str,
    title_en: str,
    command: str,
    expl_tr: str,
    expl_en: str,
    *,
    risk: str = "safe",
    elevated: bool | None = None,
    platforms: list[str] | None = None,
) -> dict:
    e: dict = {
        "title": L(title_tr, title_en),
        "command": command,
        "explanation": L(expl_tr, expl_en),
        "risk": risk,
    }
    if elevated is not None:
        e["requires_elevated"] = elevated
    if platforms:
        e["platforms"] = platforms
    return e


def cmd(
    *,
    id_: str,
    name: str,
    category: str,
    summary: dict,
    description: dict,
    tags: list[str],
    risk: str,
    elevated: bool,
    platforms: list[str],
    operating_systems: list[str],
    sources: list[str],
    examples: list[dict],
    kind: str = "executable",
    flags: list[dict] | None = None,
    related: list[str] | None = None,
    intent: dict | None = None,
    package_refs: list[dict] | None = None,
    concepts: list[str] | None = None,
    aliases: list[str] | None = None,
) -> dict:
    data: dict = {
        "schema_version": 2,
        "id": id_,
        "name": name,
        "kind": kind,
        "category": category,
        "summary": summary,
        "description": description,
        "tags": tags,
        "risk": risk,
        "requires_elevated": elevated,
        "platforms": platforms,
        "operating_systems": operating_systems,
        "flags": flags or [],
        "examples": examples,
        "intent": intent
        or {
            "tr": [name, id_.replace("-", " ")],
            "en": [name, id_.replace("-", " ")],
        },
        "verification": draft_sources(*sources),
    }
    if aliases:
        data["aliases"] = aliases
    if related:
        data["related"] = related
    if package_refs:
        data["package_refs"] = package_refs
    if concepts:
        data["nova"] = {"concepts": concepts}
    return data


BSD: list[tuple[str, dict]] = []

# --- Package managers ---

BSD.append(
    (
        "packages/pkg.yaml",
        cmd(
            id_="pkg",
            name="pkg",
            kind="package_manager",
            category="packages",
            summary=L(
                "FreeBSD ikili paket yöneticisi (pkgng).",
                "FreeBSD binary package manager (pkgng).",
            ),
            description=L(
                "FreeBSD `pkg`, uzak depolardan ikili paket kurar/sorgular. FreeBSD Ports "
                "(`ports` kaydı) kaynak ağacıdır — aynı değildir. OpenBSD `pkg_add`, NetBSD "
                "`pkgin`/`pkgsrc` ve DragonFly `pkg` ayrı ekosistemlerdir; isim benzerliği "
                "özdeşlik değildir. Arch host’ta sistem PM olarak pacman tercih edilir.",
                "FreeBSD pkg installs/queries binary packages from remote repos. FreeBSD Ports "
                "(ports record) is the source tree — not the same. OpenBSD pkg_add, NetBSD "
                "pkgin/pkgsrc, and DragonFly pkg are separate ecosystems; similar names are not "
                "identity. On Arch hosts prefer pacman as the system PM.",
            ),
            tags=["bsd", "freebsd", "packages", "pkg"],
            risk="caution",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            package_refs=[
                {
                    "manager": "freebsd-pkg",
                    "package": "pkg",
                    "distributions": ["freebsd-release"],
                    "notes": L(
                        "Base/pkgng; Handbook ports bölümü.",
                        "Base/pkgng; see Handbook ports chapter.",
                    ),
                }
            ],
            sources=[
                "https://docs.freebsd.org/en/books/handbook/ports/#pkgng-intro",
                "https://man.freebsd.org/cgi/man.cgi?query=pkg&sektion=8",
            ],
            flags=[
                flag("install", "Paket kur.", "Install package."),
                flag("delete", "Paket kaldır.", "Delete package."),
                flag("upgrade", "Kurulu paketleri yükselt.", "Upgrade installed packages."),
                flag("search", "Depoda ara.", "Search repository."),
                flag("info", "Kurulu/uzak paket bilgisi.", "Installed/remote package info."),
                flag("update", "Depo kataloğunu yenile.", "Refresh repository catalog."),
            ],
            examples=[
                ex(
                    "Ara",
                    "Search",
                    "pkg search nginx",
                    "Depoda nginx ile eşleşen paketleri listeler.",
                    "Lists packages matching nginx in the repo.",
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Bilgi",
                    "Info",
                    "pkg info -x nginx",
                    "Kurulu paketlerde nginx geçenleri gösterir (salt okuma).",
                    "Shows installed packages matching nginx (read-only).",
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Katalog güncelle",
                    "Update catalog",
                    "pkg update",
                    "Uzak paket indeksini yeniler (paket yükseltmez).",
                    "Refreshes the remote package index (does not upgrade packages).",
                    risk="caution",
                    elevated=True,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["ports", "pkg_add", "pkgin", "pkgsrc", "pacman", "brew"],
            intent={
                "tr": ["pkg kur", "freebsd paket", "pkg search"],
                "en": ["pkg install", "freebsd package", "pkg search"],
            },
            concepts=["packages", "package-managers", "package-managers-comparison"],
        ),
    )
)

BSD.append(
    (
        "packages/ports.yaml",
        cmd(
            id_="ports",
            name="ports",
            kind="package_manager",
            category="packages",
            summary=L(
                "FreeBSD Ports kaynak ağacı (make tabanlı).",
                "FreeBSD Ports source tree (make-based).",
            ),
            description=L(
                "FreeBSD Ports, `/usr/ports` altında kaynaktan derleme ağacıdır. İkili `pkg` "
                "ile karıştırılmaz. Bu kayıt Ports iş akışını belgeler; genel `make` (GNU/BSD "
                "make) ayrı kayıttır. Yıkıcı `make install`/`deinstall` örnekleri verilmez — "
                "yalnız arama/açıklama. OpenBSD ports ve NetBSD pkgsrc ayrıdır.",
                "FreeBSD Ports is a from-source build tree under /usr/ports. Do not confuse with "
                "binary pkg. This record documents the Ports workflow; generic make is a separate "
                "record. No destructive make install/deinstall examples — search/describe only. "
                "OpenBSD ports and NetBSD pkgsrc are separate.",
            ),
            tags=["bsd", "freebsd", "ports", "packages"],
            risk="caution",
            elevated=False,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            package_refs=[
                {
                    "manager": "freebsd-ports",
                    "package": "ports",
                    "distributions": ["freebsd-release"],
                    "notes": L(
                        "Ports Collection; pkg ile ikili alternatif.",
                        "Ports Collection; pkg is the binary alternative.",
                    ),
                }
            ],
            sources=[
                "https://docs.freebsd.org/en/books/handbook/ports/",
                "https://docs.freebsd.org/en/books/porters-handbook/",
            ],
            flags=[
                flag("search", "make search / port arama.", "make search / port lookup."),
                flag("describe", "Port açıklaması.", "Port description."),
            ],
            examples=[
                ex(
                    "İsimle ara",
                    "Search by name",
                    "cd /usr/ports && make search name=nginx",
                    "Ports ağacında isim arar (ağaç kurulu olmalı).",
                    "Searches the Ports tree by name (tree must be present).",
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Port açıklaması",
                    "Describe port",
                    "cd /usr/ports/www/nginx && make describe",
                    "Port özetini basar; kurulum yapmaz.",
                    "Prints the port summary; does not install.",
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["pkg", "pkgsrc", "make"],
            intent={
                "tr": ["freebsd ports", "ports ara", "make search"],
                "en": ["freebsd ports", "ports search", "make search"],
            },
            concepts=["packages", "package-managers", "package-managers-comparison"],
        ),
    )
)

BSD.append(
    (
        "packages/pkg_add.yaml",
        cmd(
            id_="pkg_add",
            name="pkg_add",
            kind="package_manager",
            category="packages",
            summary=L(
                "OpenBSD paket kurucu (pkg_* ailesi).",
                "OpenBSD package installer (pkg_* family).",
            ),
            description=L(
                "OpenBSD `pkg_add`, resmi paketleri kurar. FreeBSD `pkg` ve NetBSD `pkgin` ile "
                "aynı değildir. Sorgu için `pkg_info`, kaldırma için `pkg_delete` ayrı "
                "araçlardır; bu kayıt kurulum odaklıdır. Salt okuma örnekleri tercih edilir.",
                "OpenBSD pkg_add installs official packages. Not the same as FreeBSD pkg or "
                "NetBSD pkgin. Query via pkg_info, removal via pkg_delete — separate tools; "
                "this record is install-oriented. Prefer read-only examples.",
            ),
            tags=["bsd", "openbsd", "packages"],
            risk="caution",
            elevated=True,
            platforms=["bsd", "openbsd"],
            operating_systems=["openbsd"],
            package_refs=[
                {
                    "manager": "openbsd-pkg",
                    "package": "pkg_add",
                    "distributions": ["openbsd-release"],
                }
            ],
            sources=[
                "https://www.openbsd.org/faq/faq15.html",
                "https://man.openbsd.org/pkg_add.1",
            ],
            flags=[
                flag("-n", "Kuru çalıştır / göster.", "Dry-run / show."),
                flag("-v", "Ayrıntılı.", "Verbose."),
                flag("-u", "Güncelle.", "Update."),
            ],
            examples=[
                ex(
                    "Paket bilgisi (pkg_info)",
                    "Package info (pkg_info)",
                    "pkg_info -Q nginx",
                    "Depoda nginx geçen paket adlarını sorar (kurmaz).",
                    "Queries package names matching nginx (does not install).",
                    platforms=["bsd", "openbsd"],
                ),
                ex(
                    "Kuru kurulum denemesi",
                    "Dry-run install",
                    "pkg_add -n nginx",
                    "Ne yapılacağını gösterir; yazmaz (ortama göre değişir).",
                    "Shows what would be done without writing (environment-dependent).",
                    risk="safe",
                    elevated=True,
                    platforms=["bsd", "openbsd"],
                ),
            ],
            related=["pkg", "pkgin", "rcctl"],
            intent={
                "tr": ["pkg_add", "openbsd paket", "pkg_info"],
                "en": ["pkg_add", "openbsd package", "pkg_info"],
            },
            concepts=["packages", "package-managers", "package-managers-comparison"],
        ),
    )
)

BSD.append(
    (
        "packages/pkgin.yaml",
        cmd(
            id_="pkgin",
            name="pkgin",
            kind="package_manager",
            category="packages",
            summary=L(
                "NetBSD ikili paket aracı (pkgsrc ön yüzü).",
                "NetBSD binary package tool (pkgsrc frontend).",
            ),
            description=L(
                "`pkgin`, NetBSD’te pkgsrc ikili paketlerini yönetir. Kaynak ağacı `pkgsrc` "
                "ayrı kayıttır. FreeBSD `pkg` / OpenBSD `pkg_add` ile karıştırılmaz.",
                "pkgin manages NetBSD pkgsrc binary packages. The pkgsrc source tree is a "
                "separate record. Do not confuse with FreeBSD pkg or OpenBSD pkg_add.",
            ),
            tags=["bsd", "netbsd", "packages", "pkgsrc"],
            risk="caution",
            elevated=True,
            platforms=["bsd", "netbsd"],
            operating_systems=["netbsd"],
            package_refs=[
                {
                    "manager": "pkgin",
                    "package": "pkgin",
                    "distributions": ["netbsd-release"],
                }
            ],
            sources=[
                "https://www.netbsd.org/docs/pkgsrc/using.html",
                "https://man.netbsd.org/pkgin.1",
            ],
            flags=[
                flag("search", "Ara.", "Search."),
                flag("avail", "Uzakta uygun paketler.", "Available remote packages."),
                flag("list", "Kurulu liste.", "List installed."),
                flag("update", "İndeks güncelle.", "Update index."),
                flag("install", "Kur.", "Install."),
            ],
            examples=[
                ex(
                    "Ara",
                    "Search",
                    "pkgin search nginx",
                    "İkili depoda nginx arar.",
                    "Searches the binary repo for nginx.",
                    platforms=["bsd", "netbsd"],
                ),
                ex(
                    "Kurulu liste",
                    "List installed",
                    "pkgin list",
                    "Kurulu pkgin paketlerini listeler.",
                    "Lists installed pkgin packages.",
                    platforms=["bsd", "netbsd"],
                ),
            ],
            related=["pkgsrc", "pkg", "pkg_add"],
            intent={
                "tr": ["pkgin", "netbsd paket", "pkgin search"],
                "en": ["pkgin", "netbsd package", "pkgin search"],
            },
            concepts=["packages", "package-managers", "package-managers-comparison"],
        ),
    )
)

BSD.append(
    (
        "packages/pkgsrc.yaml",
        cmd(
            id_="pkgsrc",
            name="pkgsrc",
            kind="package_manager",
            category="packages",
            summary=L(
                "NetBSD pkgsrc kaynak paket koleksiyonu.",
                "NetBSD pkgsrc source package collection.",
            ),
            description=L(
                "pkgsrc, NetBSD kökenli taşınabilir kaynak paket ağacıdır (`bmake` ile). "
                "İkili `pkgin` ön yüzü ayrıdır. FreeBSD Ports ve OpenBSD ports ile aynı "
                "değildir. Yıkıcı kurulum örnekleri yok — yalnızca bilgi/arama odaklı.",
                "pkgsrc is a portable NetBSD-origin source package tree (via bmake). Binary "
                "pkgin frontend is separate. Not the same as FreeBSD Ports or OpenBSD ports. "
                "No destructive install examples — info/search oriented only.",
            ),
            tags=["bsd", "netbsd", "pkgsrc", "packages"],
            risk="caution",
            elevated=False,
            platforms=["bsd", "netbsd"],
            operating_systems=["netbsd"],
            package_refs=[
                {
                    "manager": "pkgsrc",
                    "package": "pkgsrc",
                    "distributions": ["netbsd-release"],
                }
            ],
            sources=[
                "https://www.netbsd.org/docs/pkgsrc/",
                "https://www.netbsd.org/docs/pkgsrc/getting.html",
            ],
            flags=[],
            examples=[
                ex(
                    "Ağaç var mı",
                    "Check tree present",
                    "test -d /usr/pkgsrc && echo pkgsrc-tree-ok",
                    "pkgsrc kökünün varlığını kontrol eder.",
                    "Checks whether the pkgsrc root exists.",
                    platforms=["bsd", "netbsd"],
                ),
                ex(
                    "Kategori listele",
                    "List category",
                    "ls /usr/pkgsrc/www 2>/dev/null | head",
                    "Örnek kategori içeriğinin başını listeler (ağaç yoksa boş).",
                    "Lists the head of a sample category (empty if no tree).",
                    platforms=["bsd", "netbsd"],
                ),
            ],
            related=["pkgin", "ports", "pkg"],
            intent={
                "tr": ["pkgsrc", "netbsd kaynak paket"],
                "en": ["pkgsrc", "netbsd source packages"],
            },
            concepts=["packages", "package-managers", "package-managers-comparison"],
        ),
    )
)

# --- System / services (NOT systemd) ---

BSD.append(
    (
        "system/freebsd-update.yaml",
        cmd(
            id_="freebsd-update",
            name="freebsd-update",
            kind="administrative_tool",
            category="system",
            summary=L(
                "FreeBSD taban sistemi ikili güncelleyicisi.",
                "FreeBSD base-system binary updater.",
            ),
            description=L(
                "`freebsd-update`, FreeBSD base (çekirdek/userland) ikili yamalarını yönetir. "
                "`pkg upgrade` paketleri günceller — aynı değildir. `fetch`/`show` salt "
                "okumaya yakındır; `install` yükseltir. systemd/apt ile karıştırılmaz.",
                "freebsd-update manages FreeBSD base (kernel/userland) binary patches. "
                "pkg upgrade updates packages — not the same. fetch/show are near-read-only; "
                "install applies upgrades. Not systemd/apt.",
            ),
            tags=["bsd", "freebsd", "update", "base"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://docs.freebsd.org/en/books/handbook/cutting-edge/#updating-src-quick-start",
                "https://man.freebsd.org/cgi/man.cgi?query=freebsd-update&sektion=8",
            ],
            flags=[
                flag("fetch", "Güncellemeleri indir.", "Fetch updates."),
                flag("show", "Bekleyen güncellemeleri göster.", "Show pending updates."),
                flag("install", "İndirilenleri uygula.", "Install fetched updates."),
            ],
            examples=[
                ex(
                    "Bekleyenleri göster",
                    "Show pending",
                    "freebsd-update fetch && freebsd-update show | head",
                    "İndirir ve bekleyen değişiklik özetinin başını basmaya çalışır.",
                    "Fetches and attempts to print the head of pending changes.",
                    risk="caution",
                    elevated=True,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["pkg", "service"],
            intent={
                "tr": ["freebsd-update", "freebsd taban güncelle"],
                "en": ["freebsd-update", "freebsd base update"],
            },
            concepts=["packages"],
        ),
    )
)

BSD.append(
    (
        "system/sysrc.yaml",
        cmd(
            id_="sysrc",
            name="sysrc",
            kind="administrative_tool",
            category="system",
            summary=L(
                "FreeBSD rc.conf güvenli okuma/yazma yardımcısı.",
                "FreeBSD rc.conf safe get/set helper.",
            ),
            description=L(
                "`sysrc`, FreeBSD `/etc/rc.conf` değerlerini okur/yazar. `service` ile birlikte "
                "rc tabanlı servis modelinin parçasıdır — **systemd değildir**. Yanlış yazma "
                "önyüklemeyi bozabilir; önce sorgu örnekleri.",
                "sysrc reads/writes FreeBSD /etc/rc.conf values. Together with service it is "
                "part of the rc-based service model — **not systemd**. Bad writes can break "
                "boot; prefer query examples first.",
            ),
            tags=["bsd", "freebsd", "rc", "services"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=sysrc&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/config/#configtuning-rcng",
            ],
            flags=[
                flag("-a", "Tüm ayarları listele.", "List all settings."),
                flag("-n", "Yalnız değer.", "Value only."),
            ],
            examples=[
                ex(
                    "Değer oku",
                    "Read value",
                    "sysrc sshd_enable",
                    "sshd_enable rc.conf değerini basar.",
                    "Prints the sshd_enable rc.conf value.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Tümünü listele (özet)",
                    "List all (summary)",
                    "sysrc -a | head",
                    "rc.conf değişkenlerinin başını listeler.",
                    "Lists the head of rc.conf variables.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["service", "rcctl", "systemctl"],
            intent={
                "tr": ["sysrc", "rc.conf", "freebsd servis ayar"],
                "en": ["sysrc", "rc.conf", "freebsd service config"],
            },
            concepts=["systemd"],
        ),
    )
)

BSD.append(
    (
        "system/service.yaml",
        cmd(
            id_="service",
            name="service",
            kind="administrative_tool",
            category="system",
            summary=L(
                "FreeBSD/NetBSD rc.d servis denetimi (systemd değil).",
                "FreeBSD/NetBSD rc.d service control (not systemd).",
            ),
            description=L(
                "`service`, BSD rc.d betiklerini başlatır/durdurur/sorgular. Linux "
                "`systemctl` veya OpenBSD `rcctl` ile **eşitlenmez**. `service -e` etkin "
                "servisleri listeler; start/stop yükseltme ister ve yıkıcı olabilir.",
                "service starts/stops/queries BSD rc.d scripts. It is **not** equivalent to "
                "Linux systemctl or OpenBSD rcctl. service -e lists enabled services; "
                "start/stop need elevation and can be disruptive.",
            ),
            tags=["bsd", "freebsd", "netbsd", "rc", "services"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd", "netbsd"],
            operating_systems=["freebsd", "netbsd", "dragonflybsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=service&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/config/#configtuning-rcng",
            ],
            flags=[
                flag("-e", "Etkin servisleri listele.", "List enabled services."),
                flag("-l", "Tüm rc.d betiklerini listele.", "List all rc.d scripts."),
                flag("status", "Servis durumu (argüman).", "Service status (argument)."),
            ],
            examples=[
                ex(
                    "Etkin servisler",
                    "Enabled services",
                    "service -e",
                    "rc.conf ile etkinleştirilmiş servisleri listeler.",
                    "Lists services enabled via rc.conf.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "sshd durumu",
                    "sshd status",
                    "service sshd status",
                    "sshd rc.d durumunu sorar (systemd status değildir).",
                    "Queries sshd rc.d status (not systemd status).",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["sysrc", "rcctl", "systemctl", "launchctl"],
            intent={
                "tr": ["freebsd servis", "service status", "rc.d"],
                "en": ["freebsd service", "service status", "rc.d"],
            },
            concepts=["systemd"],
        ),
    )
)

BSD.append(
    (
        "system/rcctl.yaml",
        cmd(
            id_="rcctl",
            name="rcctl",
            kind="administrative_tool",
            category="system",
            summary=L(
                "OpenBSD rc.d servis denetimi (systemd / FreeBSD service değil).",
                "OpenBSD rc.d service control (not systemd / FreeBSD service).",
            ),
            description=L(
                "`rcctl`, OpenBSD’te rc.d servislerini yönetir. FreeBSD `service`/`sysrc` ve "
                "Linux `systemctl` ayrı modellerdir — **eş anlamlı değildir**. `get`/`ls` "
                "güvenli sorgu; `enable`/`start` yapılandırmayı değiştirir.",
                "rcctl manages OpenBSD rc.d services. FreeBSD service/sysrc and Linux "
                "systemctl are separate models — **not synonyms**. get/ls are safe queries; "
                "enable/start change configuration.",
            ),
            tags=["bsd", "openbsd", "rc", "services"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "openbsd"],
            operating_systems=["openbsd"],
            sources=[
                "https://man.openbsd.org/rcctl.8",
                "https://www.openbsd.org/faq/faq10.html",
            ],
            flags=[
                flag("get", "Servis değişkenini oku.", "Get service variable."),
                flag("ls", "Servisleri listele.", "List services."),
                flag("check", "Çalışıyor mu kontrol et.", "Check if running."),
                flag("enable", "Açılışta etkinleştir.", "Enable at boot."),
            ],
            examples=[
                ex(
                    "sshd ayarını oku",
                    "Get sshd setting",
                    "rcctl get sshd",
                    "sshd rc değişkenlerini basar.",
                    "Prints sshd rc variables.",
                    elevated=False,
                    platforms=["bsd", "openbsd"],
                ),
                ex(
                    "Çalışan servisler",
                    "Running services",
                    "rcctl ls started",
                    "Başlatılmış servisleri listeler.",
                    "Lists started services.",
                    elevated=False,
                    platforms=["bsd", "openbsd"],
                ),
            ],
            related=["service", "sysrc", "systemctl", "pkg_add"],
            intent={
                "tr": ["rcctl", "openbsd servis", "rc.d"],
                "en": ["rcctl", "openbsd service", "rc.d"],
            },
            concepts=["systemd"],
        ),
    )
)

BSD.append(
    (
        "system/newsyslog.yaml",
        cmd(
            id_="newsyslog",
            name="newsyslog",
            kind="administrative_tool",
            category="system",
            summary=L(
                "BSD günlük döndürme (newsyslog.conf).",
                "BSD log rotation (newsyslog.conf).",
            ),
            description=L(
                "`newsyslog`, FreeBSD/OpenBSD/NetBSD’te günlük dosyalarını döndürür. Linux "
                "`logrotate` ayrı araçtır. `-n` / `-v` ile kuru deneme tercih edilir; "
                "gerçek döndürme yazma yapar.",
                "newsyslog rotates log files on FreeBSD/OpenBSD/NetBSD. Linux logrotate is a "
                "separate tool. Prefer -n/-v dry runs; real rotation writes.",
            ),
            tags=["bsd", "logs", "rotation"],
            risk="caution",
            elevated=True,
            platforms=["bsd", "freebsd", "openbsd", "netbsd"],
            operating_systems=["freebsd", "openbsd", "netbsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=newsyslog&sektion=8",
                "https://man.openbsd.org/newsyslog.8",
            ],
            flags=[
                flag("-n", "Kuru çalıştır (yazma).", "Dry-run (no rotate)."),
                flag("-v", "Ayrıntılı.", "Verbose."),
                flag("-r", "Kök dışı çalışma notu.", "Non-root run note."),
            ],
            examples=[
                ex(
                    "Kuru döndürme",
                    "Dry-run rotation",
                    "newsyslog -n -v | head",
                    "Ne döndürüleceğini gösterir; dosya yazmaz.",
                    "Shows what would rotate without writing files.",
                    elevated=True,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["service"],
            intent={
                "tr": ["newsyslog", "bsd log döndür"],
                "en": ["newsyslog", "bsd log rotate"],
            },
        ),
    )
)

# --- Privilege / firewall / jails / zfs / network ---

BSD.append(
    (
        "users/doas.yaml",
        cmd(
            id_="doas",
            name="doas",
            kind="executable",
            category="users",
            summary=L(
                "OpenBSD sade yetki yükseltme (sudo alternatifi).",
                "OpenBSD minimal privilege elevation (sudo alternative).",
            ),
            description=L(
                "`doas`, OpenBSD’te `doas.conf` politikasıyla komut çalıştırır. Linux/macOS "
                "`sudo` ayrı kayıttır; eş anlamlı değildir. FreeBSD’de port olarak bulunabilir "
                "ama bu banka OpenBSD odaklıdır. Yanlış kural kilitleyebilir.",
                "doas runs commands under doas.conf policy on OpenBSD. Linux/macOS sudo is a "
                "separate record — not a synonym. May exist as a FreeBSD port but this bank is "
                "OpenBSD-first. Bad rules can lock you out.",
            ),
            tags=["bsd", "openbsd", "privilege", "security"],
            risk="dangerous",
            elevated=False,
            platforms=["bsd", "openbsd"],
            operating_systems=["openbsd"],
            sources=[
                "https://man.openbsd.org/doas.1",
                "https://man.openbsd.org/doas.conf.5",
            ],
            flags=[
                flag("-s", "Kabuk aç.", "Launch a shell."),
                flag("-u", "Hedef kullanıcı.", "Target user."),
                flag("-n", "Etkileşimsiz (başarısız olabilir).", "Non-interactive (may fail)."),
            ],
            examples=[
                ex(
                    "Kimlik",
                    "Identity",
                    "doas -n id",
                    "Politika izin veriyorsa id çalıştırır (etkileşimsiz).",
                    "Runs id if policy allows (non-interactive).",
                    risk="caution",
                    platforms=["bsd", "openbsd"],
                ),
            ],
            related=["sudo", "rcctl"],
            intent={
                "tr": ["doas", "openbsd sudo", "yetki yükselt"],
                "en": ["doas", "openbsd sudo", "privilege elevation"],
            },
            concepts=["permissions"],
        ),
    )
)

BSD.append(
    (
        "security/pfctl.yaml",
        cmd(
            id_="pfctl",
            name="pfctl",
            kind="administrative_tool",
            category="security",
            summary=L(
                "PF (Packet Filter) denetimi — OpenBSD/FreeBSD.",
                "PF (Packet Filter) control — OpenBSD/FreeBSD.",
            ),
            description=L(
                "`pfctl`, BSD Packet Filter kurallarını yükler/sorgular. Linux "
                "`iptables`/`nft`/`ufw` ile **eşitlenmez**. `-s rules` salt okuma; "
                "`-f` / `-d` yazma/devre dışı bırakma tehlikelidir — örneklerde yok.",
                "pfctl loads/queries BSD Packet Filter rules. **Not** equivalent to Linux "
                "iptables/nft/ufw. -s rules is read-only; -f/-d write/disable are dangerous — "
                "omitted from examples.",
            ),
            tags=["bsd", "openbsd", "freebsd", "firewall", "pf"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "openbsd", "freebsd"],
            operating_systems=["openbsd", "freebsd"],
            sources=[
                "https://man.openbsd.org/pfctl.8",
                "https://www.openbsd.org/faq/pf/",
                "https://docs.freebsd.org/en/books/handbook/firewalls/#firewalls-pf",
            ],
            flags=[
                flag("-s", "Durum göster (rules/info/…).", "Show state (rules/info/…)."),
                flag("-v", "Ayrıntılı.", "Verbose."),
                flag("-n", "Sözdizimi kontrol / kuru.", "Syntax check / dry."),
            ],
            examples=[
                ex(
                    "Kuralları göster",
                    "Show rules",
                    "pfctl -s rules | head",
                    "Yüklü PF kurallarının başını basar (salt okuma).",
                    "Prints the head of loaded PF rules (read-only).",
                    elevated=True,
                    platforms=["bsd", "openbsd"],
                ),
                ex(
                    "Bilgi",
                    "Info",
                    "pfctl -s info",
                    "PF durum özetini gösterir.",
                    "Shows PF status summary.",
                    elevated=True,
                    platforms=["bsd", "openbsd"],
                ),
            ],
            related=["iptables", "nft", "ufw", "firewall-cmd"],
            intent={
                "tr": ["pfctl", "pf firewall", "openbsd güvenlik duvarı"],
                "en": ["pfctl", "pf firewall", "openbsd firewall"],
            },
            concepts=["firewalls", "networking"],
        ),
    )
)

BSD.append(
    (
        "containers/jls.yaml",
        cmd(
            id_="jls",
            name="jls",
            kind="administrative_tool",
            category="containers",
            summary=L(
                "FreeBSD jail listesi.",
                "List FreeBSD jails.",
            ),
            description=L(
                "`jls`, çalışan FreeBSD jail’lerini listeler. Linux konteynerleri "
                "(Docker/Podman) veya zone’lar değildir. `jexec` ile birlikte jail "
                "yönetiminin salt okuma yüzüdür.",
                "jls lists running FreeBSD jails. Not Linux containers (Docker/Podman) or "
                "zones. With jexec it is the read-oriented face of jail management.",
            ),
            tags=["bsd", "freebsd", "jails", "containers"],
            risk="safe",
            elevated=False,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=jls&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/jails/",
            ],
            flags=[
                flag("-v", "Ayrıntılı.", "Verbose."),
                flag("-n", "İsimleri sayısal göster.", "Show names numerically."),
            ],
            examples=[
                ex(
                    "Jail listesi",
                    "List jails",
                    "jls",
                    "Çalışan jail’leri tablo olarak basar.",
                    "Prints running jails as a table.",
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["jexec", "docker"],
            intent={
                "tr": ["jls", "freebsd jail listele"],
                "en": ["jls", "list freebsd jails"],
            },
            concepts=["containers"],
        ),
    )
)

BSD.append(
    (
        "containers/jexec.yaml",
        cmd(
            id_="jexec",
            name="jexec",
            kind="administrative_tool",
            category="containers",
            summary=L(
                "FreeBSD jail içinde komut çalıştırır.",
                "Execute a command inside a FreeBSD jail.",
            ),
            description=L(
                "`jexec`, seçili jail içinde komut/kabuk çalıştırır. `docker exec` değildir. "
                "Yanlış jail kimliği zararlı olabilir; önce `jls` ile kimlik doğrulayın. "
                "Örnekler salt yardım/kimlik odaklıdır.",
                "jexec runs a command/shell inside a selected jail. Not docker exec. A wrong "
                "jail id can be harmful; confirm with jls first. Examples stay help/identity "
                "oriented.",
            ),
            tags=["bsd", "freebsd", "jails", "containers"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=jexec&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/jails/",
            ],
            flags=[],
            examples=[
                ex(
                    "Yardım",
                    "Help",
                    "jexec 2>&1 | head",
                    "Kullanım özetini basmaya çalışır (jail seçmeden).",
                    "Attempts to print usage summary (without selecting a jail).",
                    risk="safe",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["jls"],
            intent={
                "tr": ["jexec", "freebsd jail komut"],
                "en": ["jexec", "freebsd jail exec"],
            },
            concepts=["containers"],
        ),
    )
)

BSD.append(
    (
        "disks/zpool.yaml",
        cmd(
            id_="zpool",
            name="zpool",
            kind="administrative_tool",
            category="disks",
            summary=L(
                "ZFS depolama havuzu yönetimi (FreeBSD).",
                "ZFS storage pool management (FreeBSD).",
            ),
            description=L(
                "`zpool`, ZFS havuzlarını oluşturur/yönetir. FreeBSD’de taban ZFS yaygındır; "
                "OpenBSD’de yoktur. `list`/`status` salt okuma; `destroy`/`replace` yıkıcıdır "
                "ve örneklerde yoktur. Linux OpenZFS ayrı doğrulanmalıdır.",
                "zpool creates/manages ZFS pools. Common in FreeBSD base; not in OpenBSD. "
                "list/status are read-only; destroy/replace are destructive and omitted. "
                "Linux OpenZFS must be verified separately.",
            ),
            tags=["bsd", "freebsd", "zfs", "storage"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=zpool&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/zfs/",
            ],
            flags=[
                flag("list", "Havuzları listele.", "List pools."),
                flag("status", "Havuz durumu.", "Pool status."),
                flag("get", "Özellik oku.", "Get property."),
            ],
            examples=[
                ex(
                    "Havuz listesi",
                    "List pools",
                    "zpool list",
                    "ZFS havuzlarını listeler (yoksa boş/hata).",
                    "Lists ZFS pools (empty/error if none).",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Durum",
                    "Status",
                    "zpool status",
                    "Havuz sağlığını gösterir.",
                    "Shows pool health.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["zfs", "df"],
            intent={
                "tr": ["zpool", "zfs havuz", "freebsd disk"],
                "en": ["zpool", "zfs pool", "freebsd storage"],
            },
            concepts=["storage"],
        ),
    )
)

BSD.append(
    (
        "disks/zfs.yaml",
        cmd(
            id_="zfs",
            name="zfs",
            kind="administrative_tool",
            category="disks",
            summary=L(
                "ZFS veri kümesi / anlık görüntü yönetimi (FreeBSD).",
                "ZFS dataset / snapshot management (FreeBSD).",
            ),
            description=L(
                "`zfs`, veri kümeleri, anlık görüntüler ve özellikleri yönetir. `zpool` "
                "havuz katmanıdır. `list` güvenli; `destroy` yıkıcıdır — örneklerde yok. "
                "systemd veya Linux LVM ile karıştırılmaz.",
                "zfs manages datasets, snapshots, and properties. zpool is the pool layer. "
                "list is safe; destroy is destructive — omitted. Not systemd or Linux LVM.",
            ),
            tags=["bsd", "freebsd", "zfs", "storage"],
            risk="dangerous",
            elevated=True,
            platforms=["bsd", "freebsd"],
            operating_systems=["freebsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=zfs&sektion=8",
                "https://docs.freebsd.org/en/books/handbook/zfs/",
            ],
            flags=[
                flag("list", "Veri kümelerini listele.", "List datasets."),
                flag("get", "Özellik oku.", "Get property."),
                flag("snapshot", "Anlık görüntü (yazma).", "Snapshot (writes)."),
            ],
            examples=[
                ex(
                    "Veri kümeleri",
                    "List datasets",
                    "zfs list",
                    "ZFS veri kümelerini listeler.",
                    "Lists ZFS datasets.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Mountpoint özelliği",
                    "Mountpoint property",
                    "zfs get mountpoint 2>/dev/null | head",
                    "mountpoint özelliklerinin başını basar.",
                    "Prints the head of mountpoint properties.",
                    elevated=False,
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["zpool", "df", "mount"],
            intent={
                "tr": ["zfs list", "zfs snapshot", "freebsd zfs"],
                "en": ["zfs list", "zfs snapshot", "freebsd zfs"],
            },
            concepts=["storage"],
        ),
    )
)

BSD.append(
    (
        "network/ifconfig.yaml",
        cmd(
            id_="ifconfig",
            name="ifconfig",
            kind="executable",
            category="network",
            summary=L(
                "BSD ağ arayüzü yapılandırması / sorgusu.",
                "BSD network interface configuration / query.",
            ),
            description=L(
                "`ifconfig`, BSD userland’de arayüz adreslerini gösterir/ayarlar. Linux’ta "
                "modern karşılık `ip` ayrı kayıttır; Windows `ipconfig` / PowerShell "
                "`Get-NetIPConfiguration` ayrıdır. Yazma (`up`/`down`/adres ekleme) tehlikeli "
                "olabilir — örnekler salt okuma.",
                "ifconfig shows/sets interface addresses in BSD userland. On Linux the modern "
                "counterpart ip is a separate record; Windows ipconfig / PowerShell "
                "Get-NetIPConfiguration are separate. Writes (up/down/add address) can be "
                "dangerous — examples are read-only.",
            ),
            tags=["bsd", "network", "interfaces"],
            risk="dangerous",
            elevated=False,
            platforms=["bsd", "freebsd", "openbsd", "netbsd", "dragonflybsd"],
            operating_systems=["freebsd", "openbsd", "netbsd", "dragonflybsd"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=ifconfig&sektion=8",
                "https://man.openbsd.org/ifconfig.8",
            ],
            flags=[
                flag("-a", "Tüm arayüzler.", "All interfaces."),
                flag("-l", "Yalnız ad listesi.", "Name list only."),
            ],
            examples=[
                ex(
                    "Tüm arayüzler",
                    "All interfaces",
                    "ifconfig -a",
                    "Tüm arayüz yapılandırmasını basar.",
                    "Prints all interface configuration.",
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Ad listesi",
                    "Name list",
                    "ifconfig -l",
                    "Arayüz adlarını listeler.",
                    "Lists interface names.",
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["ip", "ipconfig", "get-netipconfiguration", "netstat-bsd", "networksetup"],
            intent={
                "tr": ["ifconfig", "bsd ip adresi", "ağ arayüzü"],
                "en": ["ifconfig", "bsd show ip", "network interface"],
            },
            concepts=["networking", "networking-basics"],
        ),
    )
)

BSD.append(
    (
        "network/netstat-bsd.yaml",
        cmd(
            id_="netstat-bsd",
            name="netstat",
            kind="executable",
            category="network",
            summary=L(
                "BSD netstat — soket ve yönlendirme tablosu.",
                "BSD netstat — sockets and routing table.",
            ),
            description=L(
                "BSD `netstat`, soket/yönlendirme istatistiklerini gösterir. Windows "
                "`netstat` kaydı (id: netstat) ayrıdır — bu kayıt BSD ailesi içindir. Linux "
                "`ss` modern alternatiftir. `-an` / `-r` salt okuma.",
                "BSD netstat shows socket/routing statistics. The Windows netstat record "
                "(id: netstat) is separate — this record is for the BSD family. Linux ss is "
                "the modern alternative. -an / -r are read-only.",
            ),
            tags=["bsd", "network", "sockets"],
            risk="safe",
            elevated=False,
            platforms=["bsd", "freebsd", "openbsd", "netbsd", "dragonflybsd"],
            operating_systems=["freebsd", "openbsd", "netbsd", "dragonflybsd"],
            aliases=["netstat"],
            sources=[
                "https://man.freebsd.org/cgi/man.cgi?query=netstat&sektion=1",
                "https://man.openbsd.org/netstat.1",
            ],
            flags=[
                flag("-a", "Tüm soketler.", "All sockets."),
                flag("-n", "Sayısal adres/port.", "Numeric addresses/ports."),
                flag("-r", "Yönlendirme tablosu.", "Routing table."),
                flag("-s", "İstatistikler.", "Statistics."),
            ],
            examples=[
                ex(
                    "Dinleyen soketler",
                    "Listening sockets",
                    "netstat -an | head",
                    "Soket tablosunun başını basar.",
                    "Prints the head of the socket table.",
                    platforms=["bsd", "freebsd"],
                ),
                ex(
                    "Yönlendirme tablosu",
                    "Routing table",
                    "netstat -rn",
                    "Sayısal yönlendirme tablosunu gösterir.",
                    "Shows the numeric routing table.",
                    platforms=["bsd", "freebsd"],
                ),
            ],
            related=["netstat", "ss", "ifconfig", "get-nettcpconnection"],
            intent={
                "tr": ["netstat bsd", "bsd dinleyen port", "yönlendirme tablosu"],
                "en": ["bsd netstat", "bsd listening ports", "routing table"],
            },
            concepts=["networking", "networking-basics"],
        ),
    )
)


def main() -> None:
    known = {p.stem for p in COMMANDS.rglob("*.yaml")}
    batch_ids = {d["id"] for _, d in BSD}
    for rel, data in BSD:
        related = data.get("related") or []
        data["related"] = [r for r in related if r in known or r in batch_ids]
        if not data["related"]:
            data.pop("related", None)
        dump(COMMANDS / rel, data)
        print(f"wrote {rel}")
    print(f"total new: {len(BSD)}")


if __name__ == "__main__":
    main()
