#!/usr/bin/env python3
"""One-shot generator for Faz 1 platform registry YAML (not a CI tool).

Run: python3 scripts/_seed_platform_registries.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"


def L(tr: str, en: str) -> dict[str, str]:
    return {"tr": tr, "en": en}


def dump(path: Path, data: dict) -> None:
    text = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    path.write_text(
        "# Auto-seeded Faz 1 platform registry. Status is skeleton|draft only.\n"
        "# Do not mark verified without human review.\n"
        + text,
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    # --- support levels ---
    dump(
        META / "support-levels.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-support-level-registry",
            "support_levels": [
                {
                    "id": "planned",
                    "label": L("Planlandı", "Planned"),
                    "summary": L(
                        "Veri modeli hazır; içerik henüz yok.",
                        "Data model ready; content not started.",
                    ),
                    "rank": 10,
                },
                {
                    "id": "experimental",
                    "label": L("Deneysel", "Experimental"),
                    "summary": L(
                        "İskelet veya sınırlı taslak; üretim iddiası yok.",
                        "Skeleton or limited draft; no production claim.",
                    ),
                    "rank": 30,
                },
                {
                    "id": "partial",
                    "label": L("Kısmi", "Partial"),
                    "summary": L(
                        "Bazı komut/konseptler var; kapsam eksik.",
                        "Some commands/concepts present; coverage incomplete.",
                    ),
                    "rank": 60,
                },
                {
                    "id": "full",
                    "label": L("Geniş", "Broad"),
                    "summary": L(
                        "Birinci sınıf hedef; kapsam büyütülüyor.",
                        "First-class target; coverage being expanded.",
                    ),
                    "rank": 90,
                },
                {
                    "id": "unsupported",
                    "label": L("Desteklenmiyor", "Unsupported"),
                    "summary": L(
                        "Kayıt referans için var; destek iddiası yok.",
                        "Present for reference; no support claim.",
                    ),
                    "rank": 0,
                },
            ],
        },
    )

    # --- operating systems ---
    os_entries = [
        ("linux", "Linux", "Linux", "family", "linux", True, "full", ["https://kernel.org/"], "os-family"),
        ("windows", "Windows", "Windows", "family", "nt", False, "planned", ["https://learn.microsoft.com/windows/"], "os-family"),
        ("macos", "macOS", "macOS", "product", "xnu", True, "planned", ["https://developer.apple.com/documentation/"], "os-family"),
        ("freebsd", "FreeBSD", "FreeBSD", "product", "freebsd", True, "planned", ["https://docs.freebsd.org/"], "bsd"),
        ("openbsd", "OpenBSD", "OpenBSD", "product", "openbsd", True, "planned", ["https://www.openbsd.org/faq/"], "bsd"),
        ("netbsd", "NetBSD", "NetBSD", "product", "netbsd", True, "planned", ["https://www.netbsd.org/docs/"], "bsd"),
        ("dragonflybsd", "DragonFly BSD", "DragonFly BSD", "product", "dragonfly", True, "experimental", ["https://www.dragonflybsd.org/docs/"], "bsd"),
        ("illumos", "illumos", "illumos", "research", "illumos", True, "experimental", ["https://illumos.org/docs/"], "unix"),
        ("solaris", "Oracle Solaris", "Oracle Solaris", "research", "other", True, "experimental", ["https://docs.oracle.com/en/operating-systems/solaris.html"], "unix"),
        ("aix", "IBM AIX", "IBM AIX", "research", "aix", True, "experimental", ["https://www.ibm.com/docs/en/aix"], "unix"),
        ("android", "Android", "Android", "family", "linux", False, "experimental", ["https://developer.android.com/docs"], "mobile"),
    ]
    operating_systems = []
    for oid, tr, en, fk, kernel, posix, support, docs, tag in os_entries:
        operating_systems.append(
            {
                "id": oid,
                "name": L(tr, en),
                "summary": L(
                    f"{tr} işletim sistemi / ailesi için metadata kaydı.",
                    f"Metadata entry for the {en} operating system / family.",
                ),
                "family_kind": fk,
                "kernel_family": kernel,
                "posix_like": posix,
                "status": "draft" if support in ("full", "partial") else "skeleton",
                "support_level": support,
                "documentation": docs,
                "tags": [tag],
            }
        )
    dump(
        META / "operating-systems.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-operating-system-registry",
            "operating_systems": operating_systems,
        },
    )

    # --- distributions ---
    # (id, name_tr, name_en, os, id_like, parent, variant, pms, init, support, docs)
    distros = [
        ("debian", "Debian", "Debian", "linux", [], None, "general", ["apt", "dpkg"], ["systemd"], "partial", ["https://www.debian.org/doc/"]),
        ("ubuntu", "Ubuntu", "Ubuntu", "linux", ["debian"], "debian", "general", ["apt", "dpkg"], ["systemd"], "partial", ["https://documentation.ubuntu.com/"]),
        ("linux-mint", "Linux Mint", "Linux Mint", "linux", ["ubuntu", "debian"], "ubuntu", "desktop", ["apt", "dpkg"], ["systemd"], "experimental", ["https://linuxmint.com/documentation.php"]),
        ("pop-os", "Pop!_OS", "Pop!_OS", "linux", ["ubuntu", "debian"], "ubuntu", "desktop", ["apt", "dpkg"], ["systemd"], "experimental", ["https://support.system76.com/"]),
        ("fedora", "Fedora", "Fedora", "linux", [], None, "general", ["dnf", "rpm"], ["systemd"], "partial", ["https://docs.fedoraproject.org/"]),
        ("fedora-server", "Fedora Server", "Fedora Server", "linux", ["fedora"], "fedora", "server", ["dnf", "rpm"], ["systemd"], "experimental", ["https://docs.fedoraproject.org/en-US/fedora-server/"]),
        ("fedora-kde", "Fedora KDE", "Fedora KDE Plasma Desktop", "linux", ["fedora"], "fedora", "desktop", ["dnf", "rpm"], ["systemd"], "experimental", ["https://fedoraproject.org/kde/"]),
        ("fedora-silverblue", "Fedora Silverblue", "Fedora Silverblue", "linux", ["fedora"], "fedora", "immutable", ["rpm-ostree", "flatpak"], ["systemd"], "experimental", ["https://docs.fedoraproject.org/en-US/fedora-silverblue/"]),
        ("fedora-kinoite", "Fedora Kinoite", "Fedora Kinoite", "linux", ["fedora"], "fedora", "immutable", ["rpm-ostree", "flatpak"], ["systemd"], "experimental", ["https://docs.fedoraproject.org/en-US/fedora-kinoite/"]),
        ("fedora-iot", "Fedora IoT", "Fedora IoT", "linux", ["fedora"], "fedora", "iot", ["rpm-ostree"], ["systemd"], "experimental", ["https://docs.fedoraproject.org/en-US/iot/"]),
        ("rhel", "Red Hat Enterprise Linux", "Red Hat Enterprise Linux", "linux", ["fedora"], None, "server", ["dnf", "yum", "rpm"], ["systemd"], "experimental", ["https://docs.redhat.com/en/documentation/red_hat_enterprise_linux"]),
        ("rocky", "Rocky Linux", "Rocky Linux", "linux", ["rhel", "fedora"], "rhel", "server", ["dnf", "rpm"], ["systemd"], "experimental", ["https://docs.rockylinux.org/"]),
        ("almalinux", "AlmaLinux", "AlmaLinux", "linux", ["rhel", "fedora"], "rhel", "server", ["dnf", "rpm"], ["systemd"], "experimental", ["https://wiki.almalinux.org/"]),
        ("centos-stream", "CentOS Stream", "CentOS Stream", "linux", ["rhel", "fedora"], "rhel", "server", ["dnf", "rpm"], ["systemd"], "experimental", ["https://docs.centos.org/"]),
        ("arch", "Arch Linux", "Arch Linux", "linux", [], None, "general", ["pacman"], ["systemd"], "partial", ["https://wiki.archlinux.org/"]),
        ("manjaro", "Manjaro", "Manjaro", "linux", ["arch"], "arch", "desktop", ["pacman", "pamac"], ["systemd"], "experimental", ["https://wiki.manjaro.org/"]),
        ("endeavouros", "EndeavourOS", "EndeavourOS", "linux", ["arch"], "arch", "desktop", ["pacman"], ["systemd"], "experimental", ["https://discovery.endeavouros.com/"]),
        ("opensuse-leap", "openSUSE Leap", "openSUSE Leap", "linux", [], None, "general", ["zypper", "rpm"], ["systemd"], "experimental", ["https://doc.opensuse.org/"]),
        ("opensuse-tumbleweed", "openSUSE Tumbleweed", "openSUSE Tumbleweed", "linux", [], None, "general", ["zypper", "rpm"], ["systemd"], "experimental", ["https://doc.opensuse.org/"]),
        ("sles", "SUSE Linux Enterprise", "SUSE Linux Enterprise", "linux", ["opensuse-leap"], None, "server", ["zypper", "rpm"], ["systemd"], "experimental", ["https://documentation.suse.com/"]),
        ("alpine", "Alpine Linux", "Alpine Linux", "linux", [], None, "general", ["apk"], ["openrc"], "experimental", ["https://wiki.alpinelinux.org/"]),
        ("gentoo", "Gentoo", "Gentoo", "linux", [], None, "general", ["portage"], ["openrc", "systemd"], "experimental", ["https://wiki.gentoo.org/"]),
        ("void", "Void Linux", "Void Linux", "linux", [], None, "general", ["xbps"], ["runit"], "experimental", ["https://docs.voidlinux.org/"]),
        ("solus", "Solus", "Solus", "linux", [], None, "desktop", ["eopkg"], ["systemd"], "experimental", ["https://help.getsol.us/"]),
        ("slackware", "Slackware", "Slackware", "linux", [], None, "general", ["slackpkg"], ["sysvinit"], "experimental", ["http://www.slackware.com/"]),
        ("nixos", "NixOS", "NixOS", "linux", [], None, "immutable", ["nix"], ["systemd"], "experimental", ["https://nixos.org/manual/nixos/stable/"]),
        ("guix-system", "Guix System", "Guix System", "linux", [], None, "immutable", ["guix"], ["shepherd"], "experimental", ["https://guix.gnu.org/manual/"]),
        ("openwrt", "OpenWrt", "OpenWrt", "linux", [], None, "appliance", ["opkg"], ["procd"], "experimental", ["https://openwrt.org/docs/start"]),
        ("windows-10", "Windows 10", "Windows 10", "windows", [], None, "desktop", ["winget"], [], "planned", ["https://learn.microsoft.com/windows/"]),
        ("windows-11", "Windows 11", "Windows 11", "windows", [], None, "desktop", ["winget"], [], "planned", ["https://learn.microsoft.com/windows/"]),
        ("windows-server", "Windows Server", "Windows Server", "windows", [], None, "server", ["winget"], [], "planned", ["https://learn.microsoft.com/windows-server/"]),
        ("macos-desktop", "macOS (masaüstü)", "macOS (desktop)", "macos", [], None, "desktop", ["homebrew", "macports"], ["launchd"], "planned", ["https://support.apple.com/guide/mac-help/welcome/mac"]),
        ("freebsd-release", "FreeBSD", "FreeBSD", "freebsd", [], None, "general", ["freebsd-pkg", "freebsd-ports"], ["freebsd-rc"], "planned", ["https://docs.freebsd.org/en/books/handbook/"]),
        ("openbsd-release", "OpenBSD", "OpenBSD", "openbsd", [], None, "general", ["openbsd-pkg"], ["openbsd-rc"], "planned", ["https://www.openbsd.org/faq/"]),
        ("netbsd-release", "NetBSD", "NetBSD", "netbsd", [], None, "general", ["pkgin", "pkgsrc"], ["netbsd-rc"], "planned", ["https://www.netbsd.org/docs/"]),
        ("dragonflybsd-release", "DragonFly BSD", "DragonFly BSD", "dragonflybsd", [], None, "general", ["dragonfly-pkg"], [], "experimental", ["https://www.dragonflybsd.org/docs/"]),
    ]
    distributions = []
    for row in distros:
        did, tr, en, os_id, id_like, parent, variant, pms, inits, support, docs = row
        entry = {
            "id": did,
            "name": L(tr, en),
            "summary": L(
                f"{tr} dağıtım / ürün kaydı (iskelet).",
                f"{en} distribution / product registry entry (skeleton).",
            ),
            "operating_system": os_id,
            "variant": variant,
            "package_managers": pms,
            "status": "draft" if support == "partial" else "skeleton",
            "support_level": support,
            "documentation": docs,
        }
        if id_like:
            entry["id_like"] = id_like
        if parent:
            entry["parent"] = parent
        if inits:
            entry["init_systems"] = inits
        if did == "arch":
            entry["notes"] = L(
                "Arch birincil Linux hedefi; paket notlarında pacman tercih edilir.",
                "Arch is the primary Linux target; install hints prefer pacman.",
            )
            entry["tags"] = ["arch-first"]
        distributions.append(entry)
    dump(
        META / "distributions.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-distribution-registry",
            "distributions": distributions,
        },
    )

    # --- shells ---
    shells_data = [
        ("posix-sh", "POSIX sh", "POSIX sh", "posix", ["sh"], True, ["linux", "macos", "freebsd", "openbsd", "netbsd"], ["https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html"]),
        ("bash", "Bash", "Bash", "bourne-like", ["bash"], True, ["linux", "macos", "windows", "freebsd"], ["https://www.gnu.org/software/bash/manual/"]),
        ("zsh", "Zsh", "Zsh", "bourne-like", ["zsh"], True, ["linux", "macos", "freebsd"], ["https://zsh.sourceforge.io/Doc/"]),
        ("fish", "Fish", "Fish", "other", ["fish"], False, ["linux", "macos", "freebsd"], ["https://fishshell.com/docs/current/"]),
        ("nushell", "Nushell", "Nushell", "structured", ["nu"], False, ["linux", "macos", "windows"], ["https://www.nushell.sh/book/"]),
        ("powershell", "PowerShell 7+", "PowerShell 7+", "powershell", ["pwsh"], False, ["windows", "linux", "macos"], ["https://learn.microsoft.com/powershell/"]),
        ("windows-powershell", "Windows PowerShell 5.1", "Windows PowerShell 5.1", "powershell", ["powershell"], False, ["windows"], ["https://learn.microsoft.com/powershell/scripting/windows-powershell/starting-windows-powershell"]),
        ("cmd", "cmd.exe", "cmd.exe", "cmd", ["cmd"], False, ["windows"], ["https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands"]),
        ("elvish", "Elvish", "Elvish", "structured", ["elvish"], False, ["linux", "macos", "windows"], ["https://elv.sh/ref/"]),
        ("tcsh", "tcsh", "tcsh", "csh-like", ["tcsh"], False, ["linux", "macos", "freebsd", "netbsd"], ["https://www.tcsh.org/tcsh.html/top.html"]),
        ("csh", "csh", "csh", "csh-like", ["csh"], False, ["freebsd", "netbsd", "macos"], ["https://man.freebsd.org/cgi/man.cgi?csh"]),
        ("ksh", "ksh", "ksh", "bourne-like", ["ksh"], True, ["linux", "aix", "solaris"], ["http://www.kornshell.org/doc/"]),
        ("dash", "dash", "dash", "posix", ["dash"], True, ["linux"], ["https://manpages.debian.org/dash"]),
        ("busybox-ash", "BusyBox ash", "BusyBox ash", "embedded", ["ash"], True, ["linux"], ["https://busybox.net/downloads/BusyBox.html"]),
        ("xonsh", "Xonsh", "Xonsh", "other", ["xonsh"], False, ["linux", "macos", "windows"], ["https://xon.sh/contents.html"]),
    ]
    shells = []
    for sid, tr, en, kind, exe, posix, oss, docs in shells_data:
        shells.append(
            {
                "id": sid,
                "name": L(tr, en),
                "summary": L(
                    f"{tr} kabuk / komut yorumlayıcısı kaydı.",
                    f"{en} shell / command interpreter registry entry.",
                ),
                "shell_kind": kind,
                "executable_names": exe,
                "operating_systems": oss,
                "posix_compatible": posix,
                "status": "skeleton",
                "support_level": "planned" if sid in ("powershell", "cmd", "windows-powershell") else "experimental",
                "documentation": docs,
            }
        )
    dump(
        META / "shells.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-shell-registry",
            "shells": shells,
        },
    )

    # --- package managers ---
    # Keep Arch/pacman first-class. AppImage = distribution-format.
    pms = [
        # Debian family
        ("apt", "APT", "APT", "system", ["apt"], "deb", "system", ["linux"], ["debian", "ubuntu", "linux-mint", "pop-os"], "central-repos", ["https://www.debian.org/doc/manuals/debian-reference/ch02.en.html"]),
        ("apt-get", "apt-get", "apt-get", "system", ["apt-get"], "deb", "system", ["linux"], ["debian", "ubuntu"], "central-repos", ["https://manpages.debian.org/apt-get"]),
        ("dpkg", "dpkg", "dpkg", "system", ["dpkg"], "deb", "system", ["linux"], ["debian", "ubuntu"], "central-repos", ["https://manpages.debian.org/dpkg"]),
        ("aptitude", "aptitude", "aptitude", "system", ["aptitude"], "deb", "system", ["linux"], ["debian", "ubuntu"], "central-repos", ["https://wiki.debian.org/Aptitude"]),
        ("nala", "Nala", "Nala", "system", ["nala"], "deb", "system", ["linux"], ["debian", "ubuntu"], "central-repos", ["https://gitlab.com/volian/nala"]),
        ("apt-file", "apt-file", "apt-file", "system", ["apt-file"], "deb", "system", ["linux"], ["debian", "ubuntu"], "central-repos", ["https://manpages.debian.org/apt-file"]),
        # Fedora/RHEL
        ("dnf", "DNF", "DNF", "system", ["dnf"], "rpm", "system", ["linux"], ["fedora", "rhel", "rocky", "almalinux", "centos-stream"], "central-repos", ["https://dnf.readthedocs.io/"]),
        ("dnf5", "DNF5", "DNF5", "system", ["dnf5"], "rpm", "system", ["linux"], ["fedora"], "central-repos", ["https://dnf5.readthedocs.io/"]),
        ("rpm", "RPM", "RPM", "system", ["rpm"], "rpm", "system", ["linux"], ["fedora", "rhel", "opensuse-leap", "sles"], "central-repos", ["https://rpm.org/documentation.html"]),
        ("yum", "Yum", "Yum", "system", ["yum"], "rpm", "system", ["linux"], ["rhel"], "central-repos", ["https://manned.org/yum"]),
        ("rpm-ostree", "rpm-ostree", "rpm-ostree", "system", ["rpm-ostree"], "ostree", "system", ["linux"], ["fedora-silverblue", "fedora-kinoite", "fedora-iot"], "channels", ["https://coreos.github.io/rpm-ostree/"]),
        # Arch — first-class
        ("pacman", "pacman", "pacman", "system", ["pacman"], "pkg.tar.zst", "system", ["linux"], ["arch", "manjaro", "endeavouros"], "central-repos", ["https://wiki.archlinux.org/title/Pacman"]),
        ("makepkg", "makepkg", "makepkg", "system", ["makepkg"], "pkg.tar.zst", "system", ["linux"], ["arch"], "ports-tree", ["https://wiki.archlinux.org/title/Makepkg"]),
        ("yay", "yay", "yay", "meta", ["yay"], "pkg.tar.zst", "system", ["linux"], ["arch"], "ports-tree", ["https://github.com/Jguer/yay"]),
        ("paru", "paru", "paru", "meta", ["paru"], "pkg.tar.zst", "system", ["linux"], ["arch"], "ports-tree", ["https://github.com/Morganamilo/paru"]),
        ("pamac", "Pamac", "Pamac", "system", ["pamac"], "pkg.tar.zst", "system", ["linux"], ["manjaro"], "central-repos", ["https://wiki.manjaro.org/index.php/Pamac"]),
        # SUSE
        ("zypper", "Zypper", "Zypper", "system", ["zypper"], "rpm", "system", ["linux"], ["opensuse-leap", "opensuse-tumbleweed", "sles"], "central-repos", ["https://en.opensuse.org/SDB:Zypper_manual"]),
        # Alpine / Gentoo / Void / Solus / Slackware / OpenWrt
        ("apk", "apk", "apk", "system", ["apk"], "apk", "system", ["linux"], ["alpine"], "central-repos", ["https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper"]),
        ("portage", "Portage", "Portage", "system", ["emerge", "ebuild"], "ebuild", "system", ["linux"], ["gentoo"], "ports-tree", ["https://wiki.gentoo.org/wiki/Portage"]),
        ("xbps", "XBPS", "XBPS", "system", ["xbps-install", "xbps-query", "xbps-remove"], "xbps", "system", ["linux"], ["void"], "central-repos", ["https://docs.voidlinux.org/xbps/"]),
        ("eopkg", "eopkg", "eopkg", "system", ["eopkg"], "eopkg", "system", ["linux"], ["solus"], "central-repos", ["https://help.getsol.us/docs/user/software/package-management/eopkg"]),
        ("slackpkg", "slackpkg", "slackpkg", "system", ["slackpkg", "installpkg", "removepkg", "upgradepkg"], "txz", "system", ["linux"], ["slackware"], "central-repos", ["http://www.slackware.com/config/packages.php"]),
        ("opkg", "opkg", "opkg", "system", ["opkg"], "ipk", "system", ["linux"], ["openwrt"], "central-repos", ["https://openwrt.org/docs/guide-user/additional-software/opkg"]),
        # Nix / Guix — cross-OS capable
        ("nix", "Nix", "Nix", "system", ["nix", "nix-shell", "nix-env"], "nar", "mixed", ["linux", "macos"], ["nixos"], "flakes", ["https://nixos.org/manual/nix/stable/"]),
        ("guix", "GNU Guix", "GNU Guix", "system", ["guix"], "guix", "mixed", ["linux"], ["guix-system"], "store-profiles", ["https://guix.gnu.org/manual/en/html_node/"]),
        # macOS
        ("homebrew", "Homebrew", "Homebrew", "user", ["brew"], "bottle", "user", ["macos", "linux"], ["macos-desktop"], "central-repos", ["https://docs.brew.sh/"]),
        ("macports", "MacPorts", "MacPorts", "system", ["port"], "port", "system", ["macos"], ["macos-desktop"], "ports-tree", ["https://guide.macports.org/"]),
        # Windows
        ("winget", "WinGet", "WinGet", "system", ["winget"], "msix/exe", "mixed", ["windows"], ["windows-10", "windows-11", "windows-server"], "app-store", ["https://learn.microsoft.com/windows/package-manager/winget/"]),
        ("chocolatey", "Chocolatey", "Chocolatey", "system", ["choco"], "nupkg", "system", ["windows"], ["windows-10", "windows-11"], "central-repos", ["https://docs.chocolatey.org/"]),
        ("scoop", "Scoop", "Scoop", "user", ["scoop"], "scoop", "user", ["windows"], ["windows-10", "windows-11"], "central-repos", ["https://github.com/ScoopInstaller/Scoop"]),
        # BSD
        ("freebsd-pkg", "FreeBSD pkg", "FreeBSD pkg", "system", ["pkg"], "txz", "system", ["freebsd"], ["freebsd-release"], "central-repos", ["https://docs.freebsd.org/en/books/handbook/ports/#pkgng-intro"]),
        ("freebsd-ports", "FreeBSD Ports", "FreeBSD Ports", "ports-source", ["make"], "ports", "system", ["freebsd"], ["freebsd-release"], "ports-tree", ["https://docs.freebsd.org/en/books/handbook/ports/"]),
        ("openbsd-pkg", "OpenBSD pkg_add", "OpenBSD pkg_add", "system", ["pkg_add", "pkg_info", "pkg_delete"], "tgz", "system", ["openbsd"], ["openbsd-release"], "central-repos", ["https://www.openbsd.org/faq/faq15.html"]),
        ("pkgin", "pkgin", "pkgin", "system", ["pkgin"], "tgz", "system", ["netbsd"], ["netbsd-release"], "central-repos", ["https://www.netbsd.org/docs/pkgsrc/using.html"]),
        ("pkgsrc", "pkgsrc", "pkgsrc", "ports-source", ["bmake"], "pkgsrc", "system", ["netbsd", "linux", "macos"], ["netbsd-release"], "ports-tree", ["https://www.netbsd.org/docs/pkgsrc/"]),
        ("dragonfly-pkg", "DragonFly pkg", "DragonFly BSD pkg", "system", ["pkg"], "txz", "system", ["dragonflybsd"], ["dragonflybsd-release"], "central-repos", ["https://www.dragonflybsd.org/docs/handbook/pkgsrc/"]),
        # Language ecosystems
        ("npm", "npm", "npm", "language", ["npm"], "npm", "project", ["linux", "macos", "windows"], [], "language-index", ["https://docs.npmjs.com/"]),
        ("pnpm", "pnpm", "pnpm", "language", ["pnpm"], "npm", "project", ["linux", "macos", "windows"], [], "language-index", ["https://pnpm.io/"]),
        ("yarn", "Yarn", "Yarn", "language", ["yarn"], "npm", "project", ["linux", "macos", "windows"], [], "language-index", ["https://yarnpkg.com/"]),
        ("bun", "Bun", "Bun", "language", ["bun"], "npm", "project", ["linux", "macos", "windows"], [], "language-index", ["https://bun.sh/docs/cli/install"]),
        ("pip", "pip", "pip", "language", ["pip"], "wheel", "project", ["linux", "macos", "windows"], [], "language-index", ["https://pip.pypa.io/"]),
        ("pipx", "pipx", "pipx", "language", ["pipx"], "wheel", "user", ["linux", "macos", "windows"], [], "language-index", ["https://pipx.pypa.io/"]),
        ("uv", "uv", "uv", "language", ["uv"], "wheel", "mixed", ["linux", "macos", "windows"], [], "language-index", ["https://docs.astral.sh/uv/"]),
        ("poetry", "Poetry", "Poetry", "language", ["poetry"], "wheel", "project", ["linux", "macos", "windows"], [], "language-index", ["https://python-poetry.org/docs/"]),
        ("conda", "Conda", "Conda", "language", ["conda"], "conda", "mixed", ["linux", "macos", "windows"], [], "channels", ["https://docs.conda.io/"]),
        ("mamba", "Mamba", "Mamba", "language", ["mamba"], "conda", "mixed", ["linux", "macos", "windows"], [], "channels", ["https://mamba.readthedocs.io/"]),
        ("cargo", "Cargo", "Cargo", "language", ["cargo"], "crate", "project", ["linux", "macos", "windows"], [], "language-index", ["https://doc.rust-lang.org/cargo/"]),
        ("cargo-binstall", "cargo-binstall", "cargo-binstall", "language", ["cargo-binstall"], "crate", "user", ["linux", "macos", "windows"], [], "language-index", ["https://github.com/cargo-bins/cargo-binstall"]),
        ("rustup", "rustup", "rustup", "language", ["rustup"], "toolchain", "user", ["linux", "macos", "windows"], [], "channels", ["https://rust-lang.github.io/rustup/"]),
        ("go-install", "go install", "go install", "language", ["go"], "module", "user", ["linux", "macos", "windows"], [], "language-index", ["https://go.dev/ref/mod#go-install"]),
        ("gem", "RubyGems", "RubyGems", "language", ["gem"], "gem", "mixed", ["linux", "macos", "windows"], [], "language-index", ["https://guides.rubygems.org/"]),
        ("bundler", "Bundler", "Bundler", "language", ["bundle"], "gem", "project", ["linux", "macos", "windows"], [], "language-index", ["https://bundler.io/"]),
        ("composer", "Composer", "Composer", "language", ["composer"], "php", "project", ["linux", "macos", "windows"], [], "language-index", ["https://getcomposer.org/doc/"]),
        ("dotnet-tool", "dotnet tool", "dotnet tool", "language", ["dotnet"], "nuget", "user", ["linux", "macos", "windows"], [], "language-index", ["https://learn.microsoft.com/dotnet/core/tools/global-tools"]),
        ("nuget", "NuGet", "NuGet", "language", ["nuget"], "nupkg", "project", ["linux", "macos", "windows"], [], "language-index", ["https://learn.microsoft.com/nuget/"]),
        ("maven", "Maven", "Maven", "language", ["mvn"], "jar", "project", ["linux", "macos", "windows"], [], "language-index", ["https://maven.apache.org/guides/"]),
        ("gradle", "Gradle", "Gradle", "language", ["gradle"], "jar", "project", ["linux", "macos", "windows"], [], "language-index", ["https://docs.gradle.org/"]),
        # Application distribution
        ("flatpak", "Flatpak", "Flatpak", "application-runtime", ["flatpak"], "flatpak", "user", ["linux"], [], "app-store", ["https://docs.flatpak.org/"]),
        ("snap", "Snap", "Snap", "application-runtime", ["snap"], "snap", "system", ["linux"], [], "app-store", ["https://snapcraft.io/docs"]),
        ("appimage", "AppImage", "AppImage", "distribution-format", [], "AppImage", "user", ["linux"], [], "sidecar-file", ["https://docs.appimage.org/"]),
    ]
    package_managers = []
    for row in pms:
        pid, tr, en, kind, cli, fmt, scope, oss, dists, repo, docs = row
        entry = {
            "id": pid,
            "name": L(tr, en),
            "summary": L(
                f"{tr} paket yöneticisi / dağıtım aracı kaydı.",
                f"{en} package manager / distribution tooling registry entry.",
            ),
            "pm_kind": kind,
            "package_format": fmt,
            "scope": scope,
            "operating_systems": oss,
            "repository_model": repo,
            "status": "draft" if pid == "pacman" else "skeleton",
            "support_level": "partial" if pid == "pacman" else ("planned" if kind in ("system", "user") else "experimental"),
            "documentation": docs,
        }
        if cli:
            entry["cli_names"] = cli
        if dists:
            entry["distributions"] = dists
        if pid == "pacman":
            entry["notes"] = L(
                "Arch ailesi için birincil sistem paket yöneticisi; Nova tercihleri ile uyumlu.",
                "Primary system package manager for the Arch family; aligns with Nova preferences.",
            )
            entry["tags"] = ["arch-first"]
        if pid == "appimage":
            entry["notes"] = L(
                "AppImage bir paket yöneticisi değil; taşınabilir uygulama dağıtım biçimidir.",
                "AppImage is not a package manager; it is a portable application distribution format.",
            )
            entry["tags"] = ["not-a-package-manager"]
        if pid == "nix":
            entry["notes"] = L(
                "NixOS'a özgü değildir; Linux ve macOS üzerinde de kurulabilir.",
                "Not NixOS-only; installable on other Linux distros and macOS.",
            )
        package_managers.append(entry)
    dump(
        META / "package-managers.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-package-manager-registry",
            "package_managers": package_managers,
        },
    )

    # --- architectures ---
    arches = [
        ("x86-64", "x86-64", "x86-64", ["x86_64", "amd64"], 64, "little", ["https://en.wikipedia.org/wiki/X86-64"]),
        ("aarch64", "AArch64", "AArch64", ["aarch64", "arm64"], 64, "little", ["https://developer.arm.com/documentation/102374/latest/"]),
        ("armv7", "ARMv7", "ARMv7", ["armv7l", "armhf"], 32, "little", ["https://developer.arm.com/documentation/"]),
        ("i686", "i686", "i686", ["i686", "i386"], 32, "little", ["https://en.wikipedia.org/wiki/P6_(microarchitecture)"]),
        ("riscv64", "RISC-V 64", "RISC-V 64", ["riscv64"], 64, "little", ["https://riscv.org/technical/specifications/"]),
        ("ppc64le", "ppc64le", "ppc64le", ["ppc64le"], 64, "little", ["https://openpowerfoundation.org/"]),
        ("s390x", "s390x", "s390x", ["s390x"], 64, "big", ["https://www.ibm.com/docs/en/linux-on-systems"]),
        ("loongarch64", "LoongArch64", "LoongArch64", ["loongarch64"], 64, "little", ["https://loongson.github.io/LoongArch-Documentation/"]),
    ]
    architectures = []
    for aid, tr, en, uname, bits, endian, docs in arches:
        architectures.append(
            {
                "id": aid,
                "name": L(tr, en),
                "summary": L(
                    f"{tr} donanım mimarisi kaydı.",
                    f"{en} hardware architecture registry entry.",
                ),
                "uname_machines": uname,
                "bits": bits,
                "endianness": endian,
                "status": "skeleton",
                "support_level": "experimental",
                "documentation": docs,
            }
        )
    dump(
        META / "architectures.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-architecture-registry",
            "architectures": architectures,
        },
    )

    # --- execution environments ---
    envs = [
        ("native", "Yerel", "Native", "native", [], [], "full", ["https://en.wikipedia.org/wiki/Execution_(computing)"]),
        ("wsl1", "WSL 1", "WSL 1", "compatibility-layer", ["windows"], ["linux"], "planned", ["https://learn.microsoft.com/windows/wsl/"]),
        ("wsl2", "WSL 2", "WSL 2", "vm-guest", ["windows"], ["linux"], "planned", ["https://learn.microsoft.com/windows/wsl/"]),
        ("termux", "Termux", "Termux", "mobile-userspace", ["android"], ["linux"], "experimental", ["https://termux.dev/en/"]),
        ("crostini", "ChromeOS Crostini", "ChromeOS Linux (Crostini)", "container", [], ["linux"], "experimental", ["https://chromium.googlesource.com/chromiumos/docs/+/HEAD/containers_and_vms.md"]),
        ("msys2", "MSYS2", "MSYS2", "compatibility-layer", ["windows"], ["linux"], "experimental", ["https://www.msys2.org/docs/"]),
        ("cygwin", "Cygwin", "Cygwin", "compatibility-layer", ["windows"], ["linux"], "experimental", ["https://cygwin.com/cygwin-ug-net/"]),
        ("container", "Konteyner", "Container", "container", [], [], "partial", ["https://opencontainers.org/"]),
        ("chroot", "chroot", "chroot", "chroot", ["linux", "freebsd"], [], "experimental", ["https://man.archlinux.org/man/chroot.1"]),
        ("vm-guest", "VM misafiri", "VM guest", "vm-guest", [], [], "experimental", ["https://www.qemu.org/docs/master/"]),
        ("ssh-session", "SSH oturumu", "SSH session", "remote-session", [], [], "partial", ["https://www.openssh.com/manual.html"]),
    ]
    execution_environments = []
    for eid, tr, en, kind, hosts, guests, support, docs in envs:
        entry = {
            "id": eid,
            "name": L(tr, en),
            "summary": L(
                f"{tr} yürütme ortamı kaydı.",
                f"{en} execution environment registry entry.",
            ),
            "env_kind": kind,
            "status": "skeleton",
            "support_level": support,
            "documentation": docs,
        }
        if hosts:
            entry["host_operating_systems"] = hosts
        if guests:
            entry["guest_operating_systems"] = guests
        if eid.startswith("wsl"):
            entry["notes"] = L(
                "WSL bağımsız bir işletim sistemi değildir; Windows üzerinde Linux ortamıdır.",
                "WSL is not a standalone OS; it is a Linux environment on Windows.",
            )
        if eid == "termux":
            entry["notes"] = L(
                "Termux Android üzerinde Linux kullanıcı alanı araçları sunar; ayrı OS değildir.",
                "Termux provides Linux userspace tools on Android; it is not a separate OS.",
            )
        execution_environments.append(entry)
    dump(
        META / "execution-environments.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-execution-environment-registry",
            "execution_environments": execution_environments,
        },
    )

    # --- server platforms ---
    servers = [
        ("proxmox-ve", "Proxmox VE", "Proxmox VE", "hypervisor", True, "debian", ["linux"], ["https://pve.proxmox.com/pve-docs/"]),
        ("kvm", "KVM", "KVM", "hypervisor", False, None, ["linux"], ["https://www.linux-kvm.org/page/Documents"]),
        ("qemu", "QEMU", "QEMU", "hypervisor", False, None, ["linux", "macos", "windows"], ["https://www.qemu.org/docs/master/"]),
        ("libvirt", "libvirt", "libvirt", "hypervisor", False, None, ["linux"], ["https://libvirt.org/docs.html"]),
        ("xen", "Xen", "Xen", "hypervisor", False, None, ["linux"], ["https://xenproject.org/help/documentation/"]),
        ("hyper-v", "Hyper-V", "Hyper-V", "hypervisor", True, None, ["windows"], ["https://learn.microsoft.com/windows-server/virtualization/hyper-v/"]),
        ("vmware-esxi", "VMware ESXi", "VMware ESXi", "hypervisor", True, None, [], ["https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html"]),
        ("truenas-scale", "TrueNAS SCALE", "TrueNAS SCALE", "nas", True, "debian", ["linux"], ["https://www.truenas.com/docs/scale/"]),
        ("truenas-core", "TrueNAS CORE", "TrueNAS CORE", "nas", True, None, ["freebsd"], ["https://www.truenas.com/docs/core/"]),
        ("openmediavault", "OpenMediaVault", "OpenMediaVault", "nas", True, "debian", ["linux"], ["https://docs.openmediavault.org/"]),
        ("unraid", "Unraid", "Unraid", "nas", True, None, ["linux"], ["https://docs.unraid.net/"]),
        ("synology-dsm", "Synology DSM", "Synology DSM", "nas", True, None, ["linux"], ["https://kb.synology.com/"]),
        ("qnap-qts", "QNAP QTS", "QNAP QTS", "nas", True, None, ["linux"], ["https://www.qnap.com/en/how-to/"]),
        ("pfsense", "pfSense", "pfSense", "network-appliance", True, None, ["freebsd"], ["https://docs.netgate.com/pfsense/"]),
        ("opnsense", "OPNsense", "OPNsense", "network-appliance", True, None, ["freebsd"], ["https://docs.opnsense.org/"]),
        ("mikrotik-routeros", "MikroTik RouterOS", "MikroTik RouterOS", "network-appliance", True, None, [], ["https://help.mikrotik.com/docs/"]),
        ("cisco-ios", "Cisco IOS / IOS XE", "Cisco IOS / IOS XE", "network-appliance", True, None, [], ["https://www.cisco.com/c/en/us/support/ios-nx-os-software/index.html"]),
        ("cisco-nx-os", "Cisco NX-OS", "Cisco NX-OS", "network-appliance", True, None, [], ["https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/series.html"]),
        ("juniper-junos", "Juniper Junos", "Juniper Junos", "network-appliance", True, None, [], ["https://www.juniper.net/documentation/"]),
        ("arista-eos", "Arista EOS", "Arista EOS", "network-appliance", True, None, [], ["https://www.arista.com/en/support/product-documentation"]),
        ("openwrt-appliance", "OpenWrt (cihaz)", "OpenWrt (appliance)", "network-appliance", True, "openwrt", ["linux"], ["https://openwrt.org/docs/start"]),
        ("docker-engine", "Docker Engine", "Docker Engine", "container-runtime", False, None, ["linux", "windows", "macos"], ["https://docs.docker.com/engine/"]),
        ("kubernetes", "Kubernetes", "Kubernetes", "orchestration", False, None, ["linux"], ["https://kubernetes.io/docs/"]),
    ]
    server_platforms = []
    for sid, tr, en, kind, vendor, based, oss, docs in servers:
        entry = {
            "id": sid,
            "name": L(tr, en),
            "summary": L(
                f"{tr} sunucu / altyapı platformu kaydı.",
                f"{en} server / infrastructure platform registry entry.",
            ),
            "platform_kind": kind,
            "vendor_cli": vendor,
            "status": "skeleton",
            "support_level": "planned",
            "documentation": docs,
        }
        if based:
            entry["based_on_distribution"] = based
        if oss:
            entry["operating_systems"] = oss
        if kind == "network-appliance":
            entry["notes"] = L(
                "Vendor CLI Linux shell ile aynı kabul edilmemelidir.",
                "Vendor CLI must not be treated as a generic Linux shell.",
            )
        server_platforms.append(entry)
    dump(
        META / "server-platforms.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-server-platform-registry",
            "server_platforms": server_platforms,
        },
    )

    # --- cloud providers ---
    clouds = [
        ("aws", "Amazon Web Services", "Amazon Web Services", ["aws"], ["https://docs.aws.amazon.com/cli/"]),
        ("azure", "Microsoft Azure", "Microsoft Azure", ["az"], ["https://learn.microsoft.com/cli/azure/"]),
        ("gcp", "Google Cloud", "Google Cloud", ["gcloud"], ["https://cloud.google.com/sdk/docs"]),
        ("oci", "Oracle Cloud Infrastructure", "Oracle Cloud Infrastructure", ["oci"], ["https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm"]),
        ("digitalocean", "DigitalOcean", "DigitalOcean", ["doctl"], ["https://docs.digitalocean.com/reference/doctl/"]),
        ("hetzner", "Hetzner Cloud", "Hetzner Cloud", ["hcloud"], ["https://docs.hetzner.com/cloud/"]),
    ]
    cloud_providers = []
    for cid, tr, en, cli, docs in clouds:
        cloud_providers.append(
            {
                "id": cid,
                "name": L(tr, en),
                "summary": L(
                    f"{tr} bulut sağlayıcısı metadata kaydı (CLI iskeleti).",
                    f"{en} cloud provider metadata entry (CLI skeleton).",
                ),
                "cli_names": cli,
                "status": "skeleton",
                "support_level": "planned",
                "documentation": docs,
                "notes": L(
                    "Gerçek API anahtarı veya gizli kimlik içeren örnek kullanılmaz.",
                    "Examples must never include real API tokens or secrets.",
                ),
            }
        )
    dump(
        META / "cloud-providers.yaml",
        {
            "schema_version": 1,
            "kind": "nova-commands-cloud-provider-registry",
            "cloud_providers": cloud_providers,
        },
    )


if __name__ == "__main__":
    main()
