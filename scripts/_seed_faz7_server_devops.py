#!/usr/bin/env python3
"""One-shot Faz 7 seeder: server / network / DevOps command YAML (schema v2).

Not for re-run after content is curated — edits go in commands/ directly.
All records are draft; never mark verified. No secret-bearing cloud examples.
Profiles/tasks content remains Faz 8 (schemas already stubbed).
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
    note: str = "Agent-authored Faz 7 draft from official docs; not human-verified.",
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
    privilege: str | None = None,
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
    if privilege:
        e["privilege"] = privilege
    return e


def pkg_refs(*triples: tuple[str, str, list[str]]) -> list[dict]:
    out = []
    for manager, package, dists in triples:
        out.append({"manager": manager, "package": package, "distributions": dists})
    return out


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
    packages: dict | None = None,
    concepts: list[str] | None = None,
    aliases: list[str] | None = None,
    install_notes: dict | None = None,
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
    if packages:
        data["packages"] = packages
    if install_notes:
        data["install_notes"] = install_notes
    if concepts:
        data["nova"] = {
            "favorite_eligible": True,
            "ui_priority": 60,
            "concepts": concepts,
        }
    return data


ROWS: list[tuple[str, dict]] = []

# --- Network deepen ---

ROWS.append(
    (
        "network/tcpdump.yaml",
        cmd(
            id_="tcpdump",
            name="tcpdump",
            category="network",
            summary=L("Paket yakalama (pcap).", "Packet capture (pcap)."),
            description=L(
                "Ağ arayüzünde paketleri yakalar/filtreler. Çoğu yararlı kullanım root ister. "
                "Üretimde hassas trafik içerebilir — çıktıyı dikkatli saklayın.",
                "Captures/filters packets on an interface. Most useful use needs root. "
                "May contain sensitive traffic — store output carefully.",
            ),
            tags=["network", "pcap", "diagnostics", "server"],
            risk="caution",
            elevated=True,
            platforms=["linux", "macos", "bsd"],
            operating_systems=["linux", "macos", "freebsd", "openbsd", "netbsd"],
            package_refs=pkg_refs(
                ("pacman", "tcpdump", ["arch"]),
                ("apt", "tcpdump", ["debian", "ubuntu"]),
                ("dnf", "tcpdump", ["fedora"]),
            ),
            packages={"arch": "tcpdump", "debian": "tcpdump", "ubuntu": "tcpdump", "fedora": "tcpdump"},
            sources=[
                "https://www.tcpdump.org/manpages/tcpdump.1.html",
                "https://www.tcpdump.org/",
            ],
            flags=[
                flag("-i", "Arayüz seç.", "Select interface."),
                flag("-n", "DNS çözümleme yapma.", "Do not resolve hostnames."),
                flag("-c", "Paket sayısı sınırı.", "Packet count limit."),
            ],
            examples=[
                ex(
                    "Arayüzler",
                    "List interfaces",
                    "tcpdump -D",
                    "Yakalama için kullanılabilir arayüzleri listeler.",
                    "Lists interfaces available for capture.",
                ),
                ex(
                    "Kısa yakalama",
                    "Short capture",
                    "tcpdump -i any -n -c 20",
                    "any arayüzünde 20 paket (elevated). Hassas veri içerebilir.",
                    "20 packets on any interface (elevated). May include sensitive data.",
                    risk="caution",
                    elevated=True,
                ),
            ],
            related=["ss", "nmap", "mtr", "ip"],
            intent={
                "tr": ["paket yakala", "tcpdump", "pcap"],
                "en": ["capture packets", "tcpdump", "pcap"],
            },
            concepts=["networking", "networking-basics"],
        ),
    )
)

ROWS.append(
    (
        "network/nmap.yaml",
        cmd(
            id_="nmap",
            name="nmap",
            category="network",
            summary=L("Ağ keşfi ve port tarama.", "Network discovery and port scanning."),
            description=L(
                "Host/port keşfi ve servis parmak izi. Yalnızca yetkili hedeflerde kullanın; "
                "yetkisiz tarama yasal sorun yaratabilir. Örnekler TEST-NET / localhost ile sınırlı.",
                "Host/port discovery and service fingerprinting. Use only on authorized targets; "
                "unauthorized scanning can be illegal. Examples limited to TEST-NET / localhost.",
            ),
            tags=["network", "security", "scanning", "server"],
            risk="caution",
            elevated=False,
            platforms=["linux", "macos", "bsd", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "nmap", ["arch"]),
                ("apt", "nmap", ["debian", "ubuntu"]),
                ("dnf", "nmap", ["fedora"]),
            ),
            packages={"arch": "nmap", "debian": "nmap", "ubuntu": "nmap", "fedora": "nmap"},
            sources=[
                "https://nmap.org/book/man.html",
                "https://nmap.org/",
            ],
            flags=[
                flag("-sn", "Ping taraması (port yok).", "Ping scan (no port scan)."),
                flag("-sV", "Servis/sürüm tespiti.", "Service/version detection."),
                flag("-p", "Port aralığı.", "Port range."),
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "nmap -V",
                    "Nmap sürümünü gösterir (ağ taraması yok).",
                    "Shows Nmap version (no network scan).",
                ),
                ex(
                    "Yerel portlar",
                    "Localhost ports",
                    "nmap -p 22,80,443 127.0.0.1",
                    "Yalnızca localhost üzerinde seçili portları tarar.",
                    "Scans selected ports on localhost only.",
                    risk="caution",
                ),
            ],
            related=["ss", "tcpdump", "nc", "ping"],
            intent={
                "tr": ["port tara", "nmap", "açık port"],
                "en": ["scan ports", "nmap", "open ports"],
            },
            concepts=["networking", "networking-basics", "firewalls"],
        ),
    )
)

ROWS.append(
    (
        "network/mtr.yaml",
        cmd(
            id_="mtr",
            name="mtr",
            category="network",
            summary=L("Birleşik traceroute + ping.", "Combined traceroute + ping."),
            description=L(
                "Yol üzerindeki kayıp/gecikmeyi sürekli günceller. traceroute + ping birleşimi.",
                "Continuously updates loss/latency along a path. Combines traceroute and ping.",
            ),
            tags=["network", "diagnostics", "latency"],
            risk="safe",
            elevated=False,
            platforms=["linux", "macos", "bsd"],
            operating_systems=["linux", "macos"],
            package_refs=pkg_refs(
                ("pacman", "mtr", ["arch"]),
                ("apt", "mtr", ["debian", "ubuntu"]),
                ("dnf", "mtr", ["fedora"]),
            ),
            packages={"arch": "mtr", "debian": "mtr", "ubuntu": "mtr", "fedora": "mtr"},
            sources=[
                "https://www.bitwizard.nl/mtr/",
                "https://github.com/traviscross/mtr",
            ],
            flags=[
                flag("-r", "Rapor modu (bir kez).", "Report mode (one shot)."),
                flag("-c", "Döngü sayısı.", "Cycle count."),
                flag("-n", "DNS çözme.", "No DNS resolution."),
            ],
            examples=[
                ex(
                    "Rapor",
                    "Report",
                    "mtr -rn -c 5 example.com",
                    "5 döngülük metin raporu (DNS çözmez).",
                    "5-cycle text report (no DNS).",
                ),
            ],
            related=["traceroute", "ping", "dig"],
            intent={
                "tr": ["yol izle", "mtr", "gecikme"],
                "en": ["trace path", "mtr", "latency"],
            },
            concepts=["networking", "networking-basics"],
        ),
    )
)

ROWS.append(
    (
        "network/ethtool.yaml",
        cmd(
            id_="ethtool",
            name="ethtool",
            category="network",
            summary=L("NIC bağlantı/ayar sorgusu.", "NIC link/settings query."),
            description=L(
                "Linux ağ kartı hız/duplex/offload bilgisi. Çoğu yazma işlemi elevated ister; "
                "örnekler salt okuma.",
                "Linux NIC speed/duplex/offload info. Most write ops need elevated; "
                "examples are read-only.",
            ),
            tags=["network", "hardware", "linux", "server"],
            risk="caution",
            elevated=True,
            platforms=["linux"],
            operating_systems=["linux"],
            package_refs=pkg_refs(
                ("pacman", "ethtool", ["arch"]),
                ("apt", "ethtool", ["debian", "ubuntu"]),
                ("dnf", "ethtool", ["fedora"]),
            ),
            packages={"arch": "ethtool", "debian": "ethtool", "ubuntu": "ethtool", "fedora": "ethtool"},
            sources=[
                "https://www.kernel.org/pub/software/network/ethtool/",
                "https://man7.org/linux/man-pages/man8/ethtool.8.html",
            ],
            examples=[
                ex(
                    "Link durumu",
                    "Link status",
                    "ethtool eth0",
                    "eth0 için link hızı/duplex (arayüz adı sisteme göre değişir).",
                    "Link speed/duplex for eth0 (iface name varies).",
                    risk="safe",
                    elevated=True,
                ),
            ],
            related=["ip", "ss", "nmcli"],
            intent={
                "tr": ["nic durumu", "ethtool", "link hızı"],
                "en": ["nic status", "ethtool", "link speed"],
            },
            concepts=["networking"],
        ),
    )
)

# --- Containers / orchestration ---

ROWS.append(
    (
        "containers/nerdctl.yaml",
        cmd(
            id_="nerdctl",
            name="nerdctl",
            category="containers",
            summary=L("containerd için Docker uyumlu CLI.", "Docker-compatible CLI for containerd."),
            description=L(
                "nerdctl, containerd üzerinde Docker-benzeri komutlar sunar. Docker Engine ile "
                "aynı daemon değildir; Kubernetes node’larında sık görülür.",
                "nerdctl provides Docker-like commands on containerd. Not the same daemon as "
                "Docker Engine; common on Kubernetes nodes.",
            ),
            tags=["containers", "containerd", "devops"],
            risk="dangerous",
            elevated=False,
            platforms=["linux"],
            operating_systems=["linux"],
            package_refs=pkg_refs(("pacman", "nerdctl", ["arch"])),
            packages={"arch": "nerdctl"},
            install_notes=L(
                "Arch: pacman -S nerdctl. Diğer dağıtımlarda paket adı/kurulum yolu değişebilir.",
                "Arch: pacman -S nerdctl. Other distros may use different package names/paths.",
            ),
            sources=[
                "https://github.com/containerd/nerdctl",
                "https://github.com/containerd/nerdctl/blob/main/docs/command-reference.md",
            ],
            examples=[
                ex(
                    "Çalışanlar",
                    "Running",
                    "nerdctl ps",
                    "containerd üzerinden çalışan konteynerler.",
                    "Running containers via containerd.",
                ),
                ex(
                    "İmajlar",
                    "Images",
                    "nerdctl images",
                    "Yerel imaj listesi.",
                    "Local image list.",
                ),
            ],
            related=["docker", "podman", "crictl", "kubectl"],
            intent={
                "tr": ["nerdctl", "containerd konteyner"],
                "en": ["nerdctl", "containerd containers"],
            },
            concepts=["containers", "kubernetes"],
        ),
    )
)

ROWS.append(
    (
        "containers/crictl.yaml",
        cmd(
            id_="crictl",
            name="crictl",
            category="containers",
            summary=L("CRI runtime hata ayıklama CLI.", "CRI runtime debugging CLI."),
            description=L(
                "Kubernetes CRI (containerd/CRI-O) için düşük seviye teşhis aracı. "
                "Günlük pod yönetimi için kubectl tercih edilir.",
                "Low-level diagnostics for Kubernetes CRI (containerd/CRI-O). "
                "Prefer kubectl for day-to-day pod management.",
            ),
            tags=["containers", "kubernetes", "cri", "devops"],
            risk="caution",
            elevated=False,
            platforms=["linux"],
            operating_systems=["linux"],
            sources=[
                "https://github.com/kubernetes-sigs/cri-tools",
                "https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/",
            ],
            examples=[
                ex(
                    "Pod’lar",
                    "Pods",
                    "crictl pods",
                    "CRI pod’larını listeler (kubelet/runtime erişimi gerekir).",
                    "Lists CRI pods (needs kubelet/runtime access).",
                    risk="caution",
                ),
                ex(
                    "Konteynerler",
                    "Containers",
                    "crictl ps",
                    "Çalışan CRI konteynerleri.",
                    "Running CRI containers.",
                ),
            ],
            related=["kubectl", "nerdctl", "docker"],
            intent={
                "tr": ["crictl", "cri teşhis"],
                "en": ["crictl", "cri debug"],
            },
            concepts=["containers", "kubernetes"],
        ),
    )
)

ROWS.append(
    (
        "containers/kubectl.yaml",
        cmd(
            id_="kubectl",
            name="kubectl",
            category="containers",
            kind="remote_cli",
            summary=L("Kubernetes küme CLI.", "Kubernetes cluster CLI."),
            description=L(
                "Kubernetes API ile kaynak yönetir. kubeconfig bağlamına bağlıdır; yanlış "
                "bağlam üretim kümesini etkileyebilir. Örnekler salt okuma odaklı.",
                "Manages resources via the Kubernetes API. Depends on kubeconfig context; "
                "wrong context can affect production. Examples favor read-only ops.",
            ),
            tags=["kubernetes", "containers", "devops", "orchestration"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(("pacman", "kubectl", ["arch"])),
            packages={"arch": "kubectl"},
            sources=[
                "https://kubernetes.io/docs/reference/kubectl/",
                "https://kubernetes.io/docs/reference/kubectl/quick-reference/",
            ],
            flags=[
                flag("get", "Kaynak listele.", "List resources."),
                flag("describe", "Ayrıntılı durum.", "Detailed status."),
                flag("-n", "Namespace.", "Namespace."),
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "kubectl version --client",
                    "İstemci sürümü (küme gerekmez).",
                    "Client version (no cluster required).",
                ),
                ex(
                    "Pod’lar",
                    "Pods",
                    "kubectl get pods -A",
                    "Tüm namespace’lerde pod’lar (küme erişimi gerekir).",
                    "Pods across namespaces (needs cluster access).",
                    risk="caution",
                ),
                ex(
                    "Bağlamlar",
                    "Contexts",
                    "kubectl config get-contexts",
                    "kubeconfig bağlamlarını listeler.",
                    "Lists kubeconfig contexts.",
                ),
            ],
            related=["helm", "crictl", "nerdctl", "docker"],
            intent={
                "tr": ["kubectl", "kubernetes pod listele", "k8s"],
                "en": ["kubectl", "list kubernetes pods", "k8s"],
            },
            concepts=["containers", "kubernetes"],
        ),
    )
)

ROWS.append(
    (
        "containers/helm.yaml",
        cmd(
            id_="helm",
            name="helm",
            category="containers",
            kind="remote_cli",
            summary=L("Kubernetes paket yöneticisi.", "Kubernetes package manager."),
            description=L(
                "Chart’larla Kubernetes uygulamalarını paketler/kurar. Küme yazma işlemleri "
                "caution/dangerous; örnekler sürüm ve liste odaklı.",
                "Packages/installs Kubernetes apps via charts. Cluster-mutating ops are "
                "caution/dangerous; examples focus on version/list.",
            ),
            tags=["kubernetes", "helm", "devops", "packages"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(("pacman", "helm", ["arch"])),
            packages={"arch": "helm"},
            sources=[
                "https://helm.sh/docs/",
                "https://helm.sh/docs/helm/helm/",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "helm version",
                    "Helm istemci sürümü.",
                    "Helm client version.",
                ),
                ex(
                    "Release listesi",
                    "List releases",
                    "helm list -A",
                    "Tüm namespace release’leri (küme erişimi).",
                    "Releases across namespaces (needs cluster access).",
                    risk="caution",
                ),
            ],
            related=["kubectl", "terraform"],
            intent={
                "tr": ["helm", "chart kur", "kubernetes paket"],
                "en": ["helm", "install chart", "kubernetes package"],
            },
            concepts=["containers", "kubernetes", "infrastructure-as-code"],
        ),
    )
)

# --- Virtualization ---

ROWS.append(
    (
        "virtualization/virsh.yaml",
        cmd(
            id_="virsh",
            name="virsh",
            category="virtualization",
            kind="administrative_tool",
            summary=L("libvirt yönetim kabuğu.", "libvirt management shell."),
            description=L(
                "KVM/QEMU ve diğer libvirt hipervizörlerini yönetir. Domain oluşturma/silme "
                "yıkıcı olabilir; örnekler liste/durum odaklı.",
                "Manages KVM/QEMU and other libvirt hypervisors. Create/destroy can be "
                "destructive; examples focus on list/status.",
            ),
            tags=["virtualization", "kvm", "libvirt", "server"],
            risk="dangerous",
            elevated=True,
            platforms=["linux"],
            operating_systems=["linux"],
            package_refs=pkg_refs(
                ("pacman", "libvirt", ["arch"]),
                ("apt", "libvirt-clients", ["debian", "ubuntu"]),
                ("dnf", "libvirt-client", ["fedora"]),
            ),
            sources=[
                "https://libvirt.org/manpages/virsh.html",
                "https://libvirt.org/docs.html",
            ],
            examples=[
                ex(
                    "Domain listesi",
                    "List domains",
                    "virsh list --all",
                    "Tüm sanal makineleri listeler (libvirt erişimi).",
                    "Lists all VMs (needs libvirt access).",
                    elevated=True,
                ),
                ex(
                    "Node bilgisi",
                    "Node info",
                    "virsh nodeinfo",
                    "Hipervizör düğüm özeti.",
                    "Hypervisor node summary.",
                    elevated=True,
                ),
            ],
            related=["qemu-img", "systemctl"],
            intent={
                "tr": ["virsh", "sanal makine listele", "kvm"],
                "en": ["virsh", "list vms", "kvm"],
            },
            concepts=["virtualization"],
        ),
    )
)

ROWS.append(
    (
        "virtualization/qemu-img.yaml",
        cmd(
            id_="qemu-img",
            name="qemu-img",
            category="virtualization",
            summary=L("QEMU disk imajı aracı.", "QEMU disk image utility."),
            description=L(
                "qcow2/raw vb. disk imajlarını oluşturur/dönüştürür/sorgular. Yanlış convert "
                "veri kaybına yol açabilir — örnekler info odaklı.",
                "Creates/converts/queries qcow2/raw disk images. Bad convert can lose data — "
                "examples focus on info.",
            ),
            tags=["virtualization", "qemu", "storage"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos"],
            operating_systems=["linux", "macos"],
            package_refs=pkg_refs(
                ("pacman", "qemu-img", ["arch"]),
                ("apt", "qemu-utils", ["debian", "ubuntu"]),
                ("dnf", "qemu-img", ["fedora"]),
            ),
            sources=[
                "https://www.qemu.org/docs/master/tools/qemu-img.html",
                "https://www.qemu.org/docs/master/",
            ],
            examples=[
                ex(
                    "İmaj bilgisi",
                    "Image info",
                    "qemu-img info disk.qcow2",
                    "Mevcut imajın format/boyut bilgisini gösterir.",
                    "Shows format/size info for an existing image.",
                ),
                ex(
                    "Yardım",
                    "Help",
                    "qemu-img --help",
                    "Alt komut özeti.",
                    "Subcommand summary.",
                ),
            ],
            related=["virsh", "dd", "lsblk"],
            intent={
                "tr": ["qemu-img", "qcow2 bilgi", "disk imajı"],
                "en": ["qemu-img", "qcow2 info", "disk image"],
            },
            concepts=["virtualization", "storage"],
        ),
    )
)

# --- Web servers (system category — no dedicated web slug yet) ---

ROWS.append(
    (
        "system/nginx.yaml",
        cmd(
            id_="nginx",
            name="nginx",
            category="system",
            kind="administrative_tool",
            summary=L("HTTP reverse proxy / web sunucu.", "HTTP reverse proxy / web server."),
            description=L(
                "Yüksek performanslı web sunucu ve reverse proxy. Yapılandırma testi (-t) "
                "güvenli; reload servis yöneticisi üzerinden yapılır.",
                "High-performance web server and reverse proxy. Config test (-t) is safe; "
                "reload via the service manager.",
            ),
            tags=["web", "proxy", "server", "http"],
            risk="caution",
            elevated=True,
            platforms=["linux", "macos", "bsd"],
            operating_systems=["linux", "macos", "freebsd"],
            package_refs=pkg_refs(
                ("pacman", "nginx", ["arch"]),
                ("apt", "nginx", ["debian", "ubuntu"]),
                ("dnf", "nginx", ["fedora"]),
            ),
            packages={"arch": "nginx", "debian": "nginx", "ubuntu": "nginx", "fedora": "nginx"},
            sources=[
                "https://nginx.org/en/docs/",
                "https://nginx.org/en/docs/switches.html",
            ],
            flags=[
                flag("-t", "Yapılandırmayı test et.", "Test configuration."),
                flag("-T", "Test + dump config.", "Test and dump config."),
                flag("-s", "Sinyal (reload/stop).", "Signal (reload/stop)."),
            ],
            examples=[
                ex(
                    "Config test",
                    "Config test",
                    "nginx -t",
                    "Yapılandırma sözdizimini test eder (yazmaz).",
                    "Tests config syntax (does not write).",
                    elevated=True,
                ),
                ex(
                    "Sürüm",
                    "Version",
                    "nginx -v",
                    "nginx sürümü.",
                    "nginx version.",
                ),
            ],
            related=["caddy", "systemctl", "curl", "ss"],
            intent={
                "tr": ["nginx", "reverse proxy", "web sunucu"],
                "en": ["nginx", "reverse proxy", "web server"],
            },
            concepts=["reverse-proxy", "networking"],
        ),
    )
)

ROWS.append(
    (
        "system/caddy.yaml",
        cmd(
            id_="caddy",
            name="caddy",
            category="system",
            kind="administrative_tool",
            summary=L("Otomatik TLS’li web sunucu.", "Web server with automatic TLS."),
            description=L(
                "Caddy, ACME ile otomatik HTTPS sunabilen web sunucu/proxy. "
                "Üretimde Caddyfile değişiklikleri dikkat ister.",
                "Caddy is a web server/proxy that can obtain HTTPS via ACME. "
                "Production Caddyfile changes need care.",
            ),
            tags=["web", "proxy", "tls", "server"],
            risk="caution",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(("pacman", "caddy", ["arch"])),
            packages={"arch": "caddy"},
            sources=[
                "https://caddyserver.com/docs/",
                "https://caddyserver.com/docs/command-line",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "caddy version",
                    "Caddy sürümü.",
                    "Caddy version.",
                ),
                ex(
                    "Config validate",
                    "Validate config",
                    "caddy validate --config Caddyfile",
                    "Caddyfile’ı doğrular (servisi değiştirmez).",
                    "Validates a Caddyfile (does not change the service).",
                    risk="safe",
                ),
            ],
            related=["nginx", "openssl", "curl"],
            intent={
                "tr": ["caddy", "otomatik https", "web sunucu"],
                "en": ["caddy", "automatic https", "web server"],
            },
            concepts=["reverse-proxy", "networking"],
        ),
    )
)

# --- Databases ---

ROWS.append(
    (
        "databases/mysql.yaml",
        cmd(
            id_="mysql",
            name="mysql",
            category="databases",
            summary=L("MySQL/MariaDB istemci CLI.", "MySQL/MariaDB client CLI."),
            description=L(
                "MySQL protokolü istemcisi (MariaDB `mariadb` istemcisiyle çoğu kullanımda "
                "uyumlu). Parola komut satırına yazılmaz — etkileşimli veya config kullanın.",
                "MySQL protocol client (often compatible with MariaDB `mariadb` client). "
                "Do not put passwords on the argv — use interactive or config files.",
            ),
            tags=["database", "mysql", "mariadb", "server"],
            risk="caution",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "mariadb-clients", ["arch"]),
                ("apt", "mariadb-client", ["debian", "ubuntu"]),
                ("dnf", "mariadb", ["fedora"]),
            ),
            sources=[
                "https://dev.mysql.com/doc/refman/8.4/en/mysql.html",
                "https://mariadb.com/kb/en/mysql-command-line-client/",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "mysql --version",
                    "İstemci sürümü.",
                    "Client version.",
                ),
                ex(
                    "Yardım",
                    "Help",
                    "mysql --help",
                    "Bayrak özeti (bağlantı açmaz).",
                    "Flag summary (does not open a connection).",
                ),
            ],
            related=["psql", "redis-cli", "sqlite3"],
            intent={
                "tr": ["mysql istemci", "mariadb bağlan"],
                "en": ["mysql client", "connect mariadb"],
            },
            concepts=["databases"],
        ),
    )
)

ROWS.append(
    (
        "databases/redis-cli.yaml",
        cmd(
            id_="redis-cli",
            name="redis-cli",
            category="databases",
            summary=L("Redis komut satırı istemcisi.", "Redis command-line client."),
            description=L(
                "Redis sunucusuna komut gönderir. AUTH/parola örneklerinde gerçek sır kullanmayın.",
                "Sends commands to a Redis server. Never put real secrets in AUTH examples.",
            ),
            tags=["database", "redis", "cache", "server"],
            risk="caution",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "redis", ["arch"]),
                ("apt", "redis-tools", ["debian", "ubuntu"]),
                ("dnf", "redis", ["fedora"]),
            ),
            sources=[
                "https://redis.io/docs/latest/develop/tools/cli/",
                "https://redis.io/docs/latest/commands/",
            ],
            examples=[
                ex(
                    "Ping",
                    "Ping",
                    "redis-cli PING",
                    "Yerel Redis’e PING (çalışıyorsa PONG).",
                    "PING local Redis (PONG if running).",
                    risk="caution",
                ),
                ex(
                    "Bilgi",
                    "Info",
                    "redis-cli INFO server",
                    "Sunucu INFO bölümü (bağlantı gerekir).",
                    "Server INFO section (needs connection).",
                    risk="caution",
                ),
            ],
            related=["mysql", "psql", "sqlite3"],
            intent={
                "tr": ["redis-cli", "redis ping"],
                "en": ["redis-cli", "redis ping"],
            },
            concepts=["databases"],
        ),
    )
)

# --- Backup ---

ROWS.append(
    (
        "backup/restic.yaml",
        cmd(
            id_="restic",
            name="restic",
            category="backup",
            summary=L("Şifreli artımlı yedekleme.", "Encrypted incremental backups."),
            description=L(
                "Deduplicate/şifreli yedekler. Repo parolası ve backend kimlik bilgileri gizli "
                "tutulmalı; örneklerde gerçek secret yok.",
                "Deduplicated encrypted backups. Keep repo password and backend credentials "
                "secret; examples contain no real secrets.",
            ),
            tags=["backup", "encryption", "server"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows", "bsd"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "restic", ["arch"]),
                ("apt", "restic", ["debian", "ubuntu"]),
                ("dnf", "restic", ["fedora"]),
            ),
            packages={"arch": "restic", "debian": "restic", "ubuntu": "restic", "fedora": "restic"},
            sources=[
                "https://restic.readthedocs.io/",
                "https://restic.readthedocs.io/en/stable/010_introduction.html",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "restic version",
                    "restic sürümü.",
                    "restic version.",
                ),
                ex(
                    "Snapshots (placeholder)",
                    "Snapshots (placeholder)",
                    "restic -r /path/to/repo snapshots",
                    "Repo snapshot listesi (RESTIC_PASSWORD gerekir; yol yer tutucu).",
                    "Lists repo snapshots (needs RESTIC_PASSWORD; path is placeholder).",
                    risk="caution",
                ),
            ],
            related=["borg", "rclone", "rsync"],
            intent={
                "tr": ["restic yedek", "şifreli yedek"],
                "en": ["restic backup", "encrypted backup"],
            },
            concepts=["backup", "storage"],
        ),
    )
)

ROWS.append(
    (
        "backup/borg.yaml",
        cmd(
            id_="borg",
            name="borg",
            category="backup",
            summary=L("BorgBackup dedupe yedekleme.", "BorgBackup deduplicating backups."),
            description=L(
                "Borg, sıkıştırılmış/dedupe arşivler oluşturur. `borg create` veri yazar; "
                "örnekler info/list odaklı.",
                "Borg creates compressed/deduplicated archives. `borg create` writes data; "
                "examples focus on info/list.",
            ),
            tags=["backup", "borg", "server"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "bsd"],
            operating_systems=["linux", "macos"],
            package_refs=pkg_refs(
                ("pacman", "borg", ["arch"]),
                ("apt", "borgbackup", ["debian", "ubuntu"]),
                ("dnf", "borgbackup", ["fedora"]),
            ),
            packages={"arch": "borg", "debian": "borgbackup", "ubuntu": "borgbackup", "fedora": "borgbackup"},
            sources=[
                "https://borgbackup.readthedocs.io/",
                "https://borgbackup.readthedocs.io/en/stable/usage/general.html",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "borg --version",
                    "Borg sürümü.",
                    "Borg version.",
                ),
                ex(
                    "Yardım",
                    "Help",
                    "borg help",
                    "Alt komut yardımı.",
                    "Subcommand help.",
                ),
            ],
            related=["restic", "rclone", "rsync"],
            intent={
                "tr": ["borg yedek", "borgbackup"],
                "en": ["borg backup", "borgbackup"],
            },
            concepts=["backup", "storage"],
        ),
    )
)

ROWS.append(
    (
        "backup/rclone.yaml",
        cmd(
            id_="rclone",
            name="rclone",
            category="backup",
            summary=L("Bulut depolama senkron aracı.", "Cloud storage sync tool."),
            description=L(
                "S3/Drive/SFTP vb. uzak depolara kopyalar/senkronlar. Kimlik bilgileri "
                "rclone.conf’tadır — örneklerde gerçek key yok.",
                "Copies/syncs to remote storage (S3/Drive/SFTP/…). Credentials live in "
                "rclone.conf — no real keys in examples.",
            ),
            tags=["backup", "cloud", "sync", "storage"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "rclone", ["arch"]),
                ("apt", "rclone", ["debian", "ubuntu"]),
                ("dnf", "rclone", ["fedora"]),
            ),
            packages={"arch": "rclone", "debian": "rclone", "ubuntu": "rclone", "fedora": "rclone"},
            sources=[
                "https://rclone.org/docs/",
                "https://rclone.org/commands/",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "rclone version",
                    "rclone sürümü.",
                    "rclone version.",
                ),
                ex(
                    "Uzak listesi",
                    "List remotes",
                    "rclone listremotes",
                    "Yapılandırılmış uzak adları (içerik/secret göstermez).",
                    "Configured remote names (does not show secrets).",
                ),
            ],
            related=["restic", "borg", "rsync", "aws"],
            intent={
                "tr": ["rclone", "bulut senkron", "s3 kopyala"],
                "en": ["rclone", "cloud sync", "copy s3"],
            },
            concepts=["backup", "storage"],
        ),
    )
)

# --- Cloud CLIs ---

ROWS.append(
    (
        "cloud/aws.yaml",
        cmd(
            id_="aws",
            name="aws",
            category="cloud",
            kind="remote_cli",
            summary=L("AWS Command Line Interface.", "AWS Command Line Interface."),
            description=L(
                "Amazon Web Services API istemcisi. Örneklerde gerçek access key / secret / "
                "session token kullanılmaz. Kimlik `aws configure` veya ortam değişkenleri ile.",
                "Amazon Web Services API client. Examples never include real access keys, "
                "secrets, or session tokens. Auth via `aws configure` or env vars.",
            ),
            tags=["cloud", "aws", "devops"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(("pacman", "aws-cli", ["arch"])),
            sources=[
                "https://docs.aws.amazon.com/cli/",
                "https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "aws --version",
                    "AWS CLI sürümü.",
                    "AWS CLI version.",
                ),
                ex(
                    "Kimlik (okuma)",
                    "Caller identity",
                    "aws sts get-caller-identity",
                    "Yapılandırılmış kimliğin ARN/Account bilgisini gösterir (secret yazdırmaz).",
                    "Shows ARN/Account for configured identity (does not print secrets).",
                    risk="caution",
                ),
            ],
            related=["az", "gcloud", "terraform", "rclone"],
            intent={
                "tr": ["aws cli", "aws kimlik", "sts"],
                "en": ["aws cli", "aws identity", "sts"],
            },
            concepts=["cloud", "infrastructure-as-code"],
        ),
    )
)

ROWS.append(
    (
        "cloud/az.yaml",
        cmd(
            id_="az",
            name="az",
            category="cloud",
            kind="remote_cli",
            summary=L("Azure CLI.", "Azure CLI."),
            description=L(
                "Microsoft Azure yönetim CLI. Gerçek tenant/abonelik gizli bilgisi örneklerde yok.",
                "Microsoft Azure management CLI. No real tenant/subscription secrets in examples.",
            ),
            tags=["cloud", "azure", "devops"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            sources=[
                "https://learn.microsoft.com/cli/azure/",
                "https://learn.microsoft.com/cli/azure/get-started-with-azure-cli",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "az version",
                    "Azure CLI sürüm JSON’u.",
                    "Azure CLI version JSON.",
                ),
                ex(
                    "Hesap göster",
                    "Show account",
                    "az account show",
                    "Aktif abonelik özeti (oturum açıkken).",
                    "Active subscription summary (when logged in).",
                    risk="caution",
                ),
            ],
            related=["aws", "gcloud", "terraform"],
            intent={
                "tr": ["azure cli", "az account"],
                "en": ["azure cli", "az account"],
            },
            concepts=["cloud", "infrastructure-as-code"],
        ),
    )
)

ROWS.append(
    (
        "cloud/gcloud.yaml",
        cmd(
            id_="gcloud",
            name="gcloud",
            category="cloud",
            kind="remote_cli",
            summary=L("Google Cloud CLI.", "Google Cloud CLI."),
            description=L(
                "Google Cloud SDK komut satırı. API anahtarı/service-account JSON örneklerde yok.",
                "Google Cloud SDK command line. No API keys or service-account JSON in examples.",
            ),
            tags=["cloud", "gcp", "devops"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            sources=[
                "https://cloud.google.com/sdk/docs",
                "https://cloud.google.com/sdk/gcloud/reference",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "gcloud version",
                    "gcloud bileşen sürümleri.",
                    "gcloud component versions.",
                ),
                ex(
                    "Config list",
                    "Config list",
                    "gcloud config list",
                    "Aktif proje/bölge ayarları (secret değil).",
                    "Active project/region settings (not secrets).",
                    risk="caution",
                ),
            ],
            related=["aws", "az", "terraform"],
            intent={
                "tr": ["gcloud", "gcp cli", "google cloud"],
                "en": ["gcloud", "gcp cli", "google cloud"],
            },
            concepts=["cloud", "infrastructure-as-code"],
        ),
    )
)

# --- DevOps / IaC ---

ROWS.append(
    (
        "devops/terraform.yaml",
        cmd(
            id_="terraform",
            name="terraform",
            category="devops",
            kind="remote_cli",
            summary=L("HashiCorp Terraform (IaC).", "HashiCorp Terraform (IaC)."),
            description=L(
                "Altyapıyı deklaratif kodla yönetir. `apply`/`destroy` yıkıcı olabilir; "
                "OpenTofu ayrı bir araçtır (henüz ayrı kayıt yok). Provider credential "
                "örneklerinde gerçek secret yok.",
                "Manages infrastructure as declarative code. `apply`/`destroy` can be "
                "destructive; OpenTofu is a separate tool (no separate record yet). "
                "Provider credential examples never include real secrets.",
            ),
            tags=["iac", "terraform", "devops", "cloud"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(("pacman", "terraform", ["arch"])),
            packages={"arch": "terraform"},
            sources=[
                "https://developer.hashicorp.com/terraform/cli",
                "https://developer.hashicorp.com/terraform/cli/commands",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "terraform version",
                    "Terraform sürümü.",
                    "Terraform version.",
                ),
                ex(
                    "Validate",
                    "Validate",
                    "terraform validate",
                    "Çalışma dizinindeki yapılandırmayı doğrular (uygulamaz).",
                    "Validates config in the working directory (does not apply).",
                    risk="safe",
                ),
                ex(
                    "Plan",
                    "Plan",
                    "terraform plan",
                    "Değişiklik planı (uygulamaz). Provider kimliği gerekir.",
                    "Change plan (does not apply). Needs provider credentials.",
                    risk="caution",
                ),
            ],
            related=["ansible", "aws", "az", "gcloud", "kubectl"],
            intent={
                "tr": ["terraform", "altyapı kodu", "iac"],
                "en": ["terraform", "infrastructure as code", "iac"],
            },
            concepts=["infrastructure-as-code", "cloud"],
        ),
    )
)

ROWS.append(
    (
        "devops/ansible.yaml",
        cmd(
            id_="ansible",
            name="ansible",
            category="devops",
            kind="remote_cli",
            summary=L("Ansible otomasyon motoru.", "Ansible automation engine."),
            description=L(
                "SSH/WinRM üzerinden yapılandırma otomasyonu. Playbook çalıştırmak uzak "
                "sistemleri değiştirir — örnekler sürüm/inventory odaklı. "
                "`ansible-playbook` ayrı binary olabilir.",
                "Configuration automation over SSH/WinRM. Running playbooks mutates remote "
                "systems — examples focus on version/inventory. "
                "`ansible-playbook` may be a separate binary.",
            ),
            tags=["ansible", "automation", "devops", "iac"],
            risk="dangerous",
            elevated=False,
            platforms=["linux", "macos"],
            operating_systems=["linux", "macos"],
            package_refs=pkg_refs(
                ("pacman", "ansible", ["arch"]),
                ("apt", "ansible", ["debian", "ubuntu"]),
                ("dnf", "ansible", ["fedora"]),
            ),
            packages={"arch": "ansible", "debian": "ansible", "ubuntu": "ansible", "fedora": "ansible"},
            sources=[
                "https://docs.ansible.com/",
                "https://docs.ansible.com/ansible/latest/command_guide/index.html",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "ansible --version",
                    "Ansible sürüm ve yollar.",
                    "Ansible version and paths.",
                ),
                ex(
                    "Inventory list",
                    "Inventory list",
                    "ansible-inventory --list",
                    "Yapılandırılmış envanteri JSON olarak listeler.",
                    "Lists configured inventory as JSON.",
                    risk="safe",
                ),
            ],
            related=["terraform", "ssh", "systemctl"],
            intent={
                "tr": ["ansible", "playbook", "otomasyon"],
                "en": ["ansible", "playbook", "automation"],
            },
            concepts=["infrastructure-as-code"],
        ),
    )
)

ROWS.append(
    (
        "devops/gh.yaml",
        cmd(
            id_="gh",
            name="gh",
            category="devops",
            kind="remote_cli",
            summary=L("GitHub resmi CLI.", "Official GitHub CLI."),
            description=L(
                "Issue/PR/Actions işlemleri. `gh auth` token’ları güvenli depolar; "
                "örneklerde gerçek token yok.",
                "Issue/PR/Actions operations. `gh auth` stores tokens securely; "
                "examples never include real tokens.",
            ),
            tags=["github", "cicd", "devops", "git"],
            risk="caution",
            elevated=False,
            platforms=["linux", "macos", "windows"],
            operating_systems=["linux", "macos", "windows"],
            package_refs=pkg_refs(
                ("pacman", "github-cli", ["arch"]),
                ("apt", "gh", ["debian", "ubuntu"]),
                ("dnf", "gh", ["fedora"]),
            ),
            packages={"arch": "github-cli", "debian": "gh", "ubuntu": "gh", "fedora": "gh"},
            sources=[
                "https://cli.github.com/manual/",
                "https://docs.github.com/en/github-cli",
            ],
            examples=[
                ex(
                    "Sürüm",
                    "Version",
                    "gh --version",
                    "gh sürümü.",
                    "gh version.",
                ),
                ex(
                    "Auth durumu",
                    "Auth status",
                    "gh auth status",
                    "Oturum durumunu gösterir (token’ı yazdırmaz).",
                    "Shows login status (does not print the token).",
                    risk="safe",
                ),
            ],
            related=["git", "ansible", "terraform"],
            intent={
                "tr": ["gh", "github cli", "pr oluştur"],
                "en": ["gh", "github cli", "create pr"],
            },
            concepts=["infrastructure-as-code"],
        ),
    )
)


def main() -> None:
    written = []
    for rel, data in ROWS:
        path = COMMANDS / rel
        dump(path, data)
        written.append(rel)
    print(f"wrote {len(written)} command YAML files:")
    for rel in written:
        print(f"  commands/{rel}")


if __name__ == "__main__":
    main()
