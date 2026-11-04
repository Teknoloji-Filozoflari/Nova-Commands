# Package managers — comparison tables

Bilingual quick reference for the curated bank. Companion concept articles:
`concepts/package-managers-comparison.yaml`, `concepts/package-managers.yaml`,
`concepts/nix-guix.yaml`. Arch / pacman rows are listed first (Nova preference).
**Do not invent** package names or flags not confirmed for a distro.

Türkçe özet aynı tablolardadır; komutlar evrensel olduğundan tek tablo yeterlidir.

Many Faz 4 rows are **draft** (agent-sourced from official docs; not human-verified).

## Update / install / remove (core + broader Linux)

| Goal / Amaç | Arch (`pacman`) | Debian/Ubuntu (`apt`) | Fedora/RHEL (`dnf`) | openSUSE (`zypper`) | Alpine (`apk`) | Void (`xbps`) |
|-------------|-----------------|------------------------|---------------------|---------------------|----------------|---------------|
| Refresh DB + upgrade | `pacman -Syu` | `apt update && apt full-upgrade` | `dnf upgrade` | Leap: `zypper refresh && zypper update` · TW: `zypper dup` | `apk update && apk upgrade` | `xbps-install -Su` |
| Install package | `pacman -S name` | `apt install name` | `dnf install name` | `zypper install name` | `apk add name` | `xbps-install name` |
| Remove (+ unused deps, common) | `pacman -Rns name` | `apt autoremove --purge name` | `dnf remove name` | `zypper remove name` | `apk del name` | `xbps-remove [-R] name` |
| Search | `pacman -Ss query` | `apt search query` | `dnf search query` | `zypper search query` | `apk search query` | `xbps-query -Rs query` |
| Clean caches (careful) | `pacman -Sc` | `apt clean` | `dnf clean all` | `zypper clean` | `apk cache clean` | (see Void docs) |

Notes:

- `full-upgrade` vs `upgrade` on apt depends on policy; prefer the distro’s documented path.
- openSUSE **Leap `update` ≠ Tumbleweed `dup`**.
- Gentoo: `emerge --sync`, then `emerge --ask -uDN @world` / `emerge --ask name`.
- Solus: `eopkg upgrade` / `eopkg install name`.
- Slackware: `slackpkg update` / `slackpkg install name` (low-level: `installpkg` / `removepkg` / `upgradepkg`).
- OpenWrt: `opkg update` / `opkg install name` — watch flash space and arch.
- Atomic Fedora (Silverblue/Kinoite/IoT): `rpm-ostree upgrade` / `rpm-ostree install name` — usually requires reboot; not classic `dnf`.

## Query local packages

| Goal / Amaç | pacman | dpkg | rpm | xbps | apk |
|-------------|--------|------|-----|------|-----|
| Is it installed? | `pacman -Q name` | `dpkg -l name` | `rpm -q name` | `xbps-query name` | `apk info -e name` |
| Which package owns a file? | `pacman -Qo /path` | `dpkg -S /path` | `rpm -qf /path` | `xbps-query -o /path` | `apk info -W /path` |
| List files in a package | `pacman -Ql name` | `dpkg -L name` | `rpm -ql name` | `xbps-query -f name` | `apk info -L name` |
| Package info | `pacman -Qi name` | `apt show name` / `dpkg -s name` | `dnf info name` / `rpm -qi name` | `xbps-query -S name` | `apk info name` |

High-level frontends (`apt`, `dnf`, `zypper`) wrap these; low-level tools remain useful in rescue shells.

## Nix and Guix (declarative)

| Goal | Nix (modern) | Guix |
|------|--------------|------|
| Search | `nix search nixpkgs query` | `guix search query` |
| Profile install | `nix profile install nixpkgs#name` | `guix install name` |
| Ephemeral shell | `nix shell` / `nix develop` | `guix shell` |
| Run without lasting install | `nix run nixpkgs#name` | (use `guix shell` / package) |
| Update channels / inputs | flake/`nix flake update` (project) | `guix pull` |
| Apply OS config | `nixos-rebuild switch` (NixOS) | `guix system …` (Guix System) |
| GC store | `nix-collect-garbage` | Guix GC via manual (`guix gc`) |

**Do not mix** legacy `nix-env` / classic `nix-shell` with modern `nix profile` /
`nix shell` / `nix develop`. See `concepts/nix-guix.yaml`.

Nix is installable on non-NixOS Linux and macOS; Guix is primarily Linux. On Arch
hosts, **pacman remains the system package manager** — Nix/Guix may coexist.

## Windows and macOS (Faz 5 draft)

These are **not** Linux system PMs and are **not** interchangeable with pacman/apt/dnf.

| Goal / Amaç | Windows (`winget`) | macOS Homebrew (`brew`) | macOS MacPorts (`port`) |
|-------------|--------------------|-------------------------|-------------------------|
| Search | `winget search name` | `brew search name` | `port search name` |
| Info / show | `winget show id` | `brew info name` | `port info name` |
| List installed | `winget list` | `brew list` | `port installed` |
| Install | `winget install id` | `brew install name` | `sudo port install name` |
| Upgrade | `winget upgrade` | `brew update` then `brew upgrade` | `sudo port selfupdate` / `upgrade outdated` |
| OS updates | (Windows Update / `softwareupdate` N/A) | use `softwareupdate` — **not** `brew upgrade` | same — OS ≠ ports |

Notes:

- WinGet ≠ Chocolatey ≠ Scoop (separate ecosystems; only `winget` is banked in Faz 5).
- Homebrew formulae vs casks differ; Linuxbrew exists but this bank’s `brew` record is macOS-first.
- MacPorts `port` is a separate record from `brew` — do not treat as aliases.
- On Arch hosts, **pacman remains** the preferred system package manager.

## Flatpak (cross-distro apps)

| Goal | Command |
|------|---------|
| Search | `flatpak search name` |
| Install (Flathub remotes must exist) | `flatpak install flathub app.id` |
| List | `flatpak list` |
| Run | `flatpak run app.id` |
| Update | `flatpak update` |

Flatpak does **not** replace the OS package manager for kernels, drivers, or base toolchain.

## AUR helpers (Arch)

Helpers such as `paru` / `yay` are **not** official pacman. Document as `draft` when
packaging or flags are uncertain. Prefer official repos first.

## Nova catalog rules

- Prefer `packages.arch` + Arch-first `install_notes` when the tool exists on Arch.
- Prefer schema v2 `package_refs` with registry PM ids; keep legacy `packages` for dual-read.
- Omit unknown `packages.*` keys; never guess.
- `verification.status: verified` only after human review against man pages / distro docs.
- See also: [safety.md](safety.md), [nova-consumption.md](nova-consumption.md),
  [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md).
