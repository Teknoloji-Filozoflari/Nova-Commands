# Package managers — comparison tables

Bilingual quick reference for the curated bank. Companion concept article:
`concepts/package-managers-comparison.yaml`. Arch / pacman rows are listed first
(Nova preference). **Do not invent** package names or flags not confirmed for a
distro.

Türkçe özet aynı tablolardadır; komutlar evrensel olduğundan tek tablo yeterlidir.

## Update / install / remove

| Goal / Amaç | Arch (`pacman`) | Debian/Ubuntu (`apt`) | Fedora/RHEL (`dnf`) |
|-------------|-----------------|------------------------|---------------------|
| Refresh DB + upgrade | `pacman -Syu` | `apt update && apt full-upgrade` | `dnf upgrade` |
| Install package | `pacman -S name` | `apt install name` | `dnf install name` |
| Remove (+ unused deps, common) | `pacman -Rns name` | `apt autoremove --purge name` | `dnf remove name` |
| Search | `pacman -Ss query` | `apt search query` | `dnf search query` |
| Clean caches (careful) | `pacman -Sc` | `apt clean` | `dnf clean all` |

`full-upgrade` vs `upgrade` on apt depends on policy; prefer the distro’s documented path.

## Query local packages

| Goal / Amaç | pacman | dpkg | rpm |
|-------------|--------|------|-----|
| Is it installed? | `pacman -Q name` | `dpkg -l name` | `rpm -q name` |
| Which package owns a file? | `pacman -Qo /path` | `dpkg -S /path` | `rpm -qf /path` |
| List files in a package | `pacman -Ql name` | `dpkg -L name` | `rpm -ql name` |
| Package info | `pacman -Qi name` | `apt show name` / `dpkg -s name` | `dnf info name` / `rpm -qi name` |

High-level frontends (`apt`, `dnf`) wrap these; low-level tools remain useful in rescue shells.

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
- Omit unknown `packages.*` keys; never guess.
- `verification.status: verified` only after human review against man pages / distro docs.
- See also: [safety.md](safety.md), [nova-consumption.md](nova-consumption.md).
