#!/usr/bin/env python3
"""One-shot Faz 8 seeder: tasks/ + profiles/ trees (schema v2 stubs → live content).

Not for re-run after content is curated — edits go in tasks/ and profiles/ directly.
All records are draft; never mark verified. Implementations reference existing
command bank ids only. Re-run build_catalog.py after edits so tasks/profiles
enter catalog / search-index / content_sha256 (Faz 9).
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
PROFILES = ROOT / "profiles"

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


def draft(*sources: str, note: str = "Agent-authored Faz 8 draft; not human-verified.") -> dict:
    return {"status": "draft", "sources": list(sources), "notes": note}


def impl(
    id_: str,
    *,
    commands: list[str],
    examples: list[dict],
    operating_systems: list[str] | None = None,
    platforms: list[str] | None = None,
    shells: list[str] | None = None,
    distributions: list[str] | None = None,
    notes: dict | None = None,
) -> dict:
    data: dict = {"id": id_, "commands": commands, "examples": examples}
    if operating_systems:
        data["operating_systems"] = operating_systems
    if platforms:
        data["platforms"] = platforms
    if shells:
        data["shells"] = shells
    if distributions:
        data["distributions"] = distributions
    if notes:
        data["notes"] = notes
    return data


def ex(
    command: str,
    *,
    risk: str = "safe",
    shell: str | None = None,
    privilege: str | None = "none",
    title: dict | None = None,
    explanation: dict | None = None,
) -> dict:
    e: dict = {"command": command, "risk": risk}
    if shell:
        e["shell"] = shell
    if privilege:
        e["privilege"] = privilege
    if title:
        e["title"] = title
    if explanation:
        e["explanation"] = explanation
    return e


def task(
    *,
    id_: str,
    name: dict,
    summary: dict,
    category: str,
    intent: dict,
    implementations: list[dict],
    sources: list[str],
    description: dict | None = None,
    tags: list[str] | None = None,
    related_commands: list[str] | None = None,
    related_tasks: list[str] | None = None,
) -> dict:
    data: dict = {
        "schema_version": 2,
        "kind": "task",
        "id": id_,
        "name": name,
        "summary": summary,
        "category": category,
        "intent": intent,
        "implementations": implementations,
        "verification": draft(*sources),
    }
    if description:
        data["description"] = description
    if tags:
        data["tags"] = tags
    if related_commands:
        data["related_commands"] = related_commands
    if related_tasks:
        data["related_tasks"] = related_tasks
    return data


def profile(
    *,
    id_: str,
    name: dict,
    summary: dict,
    sources: list[str],
    description: dict | None = None,
    operating_systems: list[str] | None = None,
    distributions: list[str] | None = None,
    server_platforms: list[str] | None = None,
    related_commands: list[str] | None = None,
    related_tasks: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict:
    data: dict = {
        "schema_version": 2,
        "kind": "profile",
        "id": id_,
        "name": name,
        "summary": summary,
        "verification": draft(*sources),
    }
    if description:
        data["description"] = description
    if operating_systems:
        data["operating_systems"] = operating_systems
    if distributions:
        data["distributions"] = distributions
    if server_platforms:
        data["server_platforms"] = server_platforms
    if related_commands:
        data["related_commands"] = related_commands
    if related_tasks:
        data["related_tasks"] = related_tasks
    if tags:
        data["tags"] = tags
    return data


def build_tasks() -> list[tuple[str, dict]]:
    items: list[tuple[str, dict]] = []

    items.append(
        (
            "show-local-ip.yaml",
            task(
                id_="show-local-ip",
                name=L("Yerel IP adresini göster", "Show local IP address"),
                summary=L(
                    "Farklı platformlarda yerel IP / ağ yapılandırmasını öğrenme.",
                    "Learn local IP / network configuration across platforms.",
                ),
                description=L(
                    "Aynı kullanıcı amacını Linux `ip`, Windows PowerShell/CMD ve "
                    "macOS/BSD `ifconfig` ile ayrı uygulamalar olarak gösterir. "
                    "Komutlar eşitlenmez.",
                    "Shows the same user goal via Linux ip, Windows PowerShell/CMD, "
                    "and macOS/BSD ifconfig as separate implementations. Commands "
                    "are not equated.",
                ),
                category="network",
                tags=["network", "ip", "diagnostics"],
                intent={
                    "tr": [
                        "ip adresimi öğren",
                        "ağ yapılandırmasını göster",
                        "yerel IP adresini bul",
                    ],
                    "en": [
                        "show local ip",
                        "inspect network configuration",
                        "find my ip address",
                    ],
                },
                implementations=[
                    impl(
                        "linux-ip",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["ip"],
                        examples=[
                            ex(
                                "ip -br addr",
                                shell="bash",
                                title=L("Kısa adres listesi", "Brief address list"),
                                explanation=L(
                                    "Arayüz adı, durum ve IPv4/IPv6 adreslerini kısaca listeler.",
                                    "Briefly lists interface name, state, and IPv4/IPv6 addresses.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "windows-powershell",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-netipconfiguration"],
                        examples=[
                            ex(
                                "Get-NetIPConfiguration",
                                shell="powershell",
                                title=L("IP yapılandırması", "IP configuration"),
                                explanation=L(
                                    "Windows NetTCPIP modülü ile arayüz IP bilgisi.",
                                    "Interface IP info via Windows NetTCPIP module.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "windows-cmd",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["cmd"],
                        commands=["ipconfig"],
                        examples=[
                            ex(
                                "ipconfig",
                                shell="cmd",
                                title=L("ipconfig özeti", "ipconfig summary"),
                                explanation=L(
                                    "Klasik CMD ile adapter IP özeti.",
                                    "Classic CMD adapter IP summary.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "macos-bsd-ifconfig",
                        operating_systems=["macos", "freebsd", "openbsd", "netbsd"],
                        platforms=["macos", "bsd"],
                        shells=["bash", "zsh"],
                        commands=["ifconfig"],
                        examples=[
                            ex(
                                "ifconfig -a",
                                shell="zsh",
                                title=L("Tüm arayüzler", "All interfaces"),
                                explanation=L(
                                    "macOS/BSD ifconfig; GNU ip ile aynı araç değildir.",
                                    "macOS/BSD ifconfig; not the same tool as GNU ip.",
                                ),
                            )
                        ],
                        notes=L(
                            "networksetup macOS GUI köprüsüdür; ayrı kayıt.",
                            "networksetup is a macOS GUI bridge; separate record.",
                        ),
                    ),
                ],
                related_commands=[
                    "ip",
                    "get-netipconfiguration",
                    "ipconfig",
                    "ifconfig",
                    "networksetup",
                ],
                related_tasks=["inspect-network-interfaces", "show-public-ip"],
                sources=[
                    "man 8 ip",
                    "https://learn.microsoft.com/powershell/module/nettcpip/get-netipconfiguration",
                    "man 8 ifconfig",
                ],
            ),
        )
    )

    items.append(
        (
            "show-public-ip.yaml",
            task(
                id_="show-public-ip",
                name=L("Genel (wan) IP adresini göster", "Show public (WAN) IP address"),
                summary=L(
                    "Harici HTTPS uç noktası ile görünen genel IP (ağ çıkışı).",
                    "Query an external HTTPS endpoint for the apparent public IP.",
                ),
                description=L(
                    "Üçüncü taraf uç noktalara güvenir; gizlilik ve oran sınırları "
                    "dikkate alın. Yerel IP görevi ile karıştırma.",
                    "Depends on third-party endpoints; consider privacy and rate "
                    "limits. Do not confuse with the local-IP task.",
                ),
                category="network",
                tags=["network", "ip", "wan"],
                intent={
                    "tr": ["genel ip adresim", "wan ip", "dış ip öğren"],
                    "en": ["show public ip", "wan ip address", "external ip"],
                },
                implementations=[
                    impl(
                        "curl-https",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash", "zsh", "powershell"],
                        commands=["curl"],
                        examples=[
                            ex(
                                "curl -4 -s https://ifconfig.me/ip",
                                shell="bash",
                                title=L("IPv4 genel IP", "IPv4 public IP"),
                                explanation=L(
                                    "HTTPS ile görünen IPv4; uç nokta değişebilir.",
                                    "Apparent IPv4 over HTTPS; endpoint may change.",
                                ),
                            )
                        ],
                    ),
                ],
                related_commands=["curl", "wget", "dig"],
                related_tasks=["show-local-ip", "check-internet-connectivity"],
                sources=["https://curl.se/docs/manpage.html"],
            ),
        )
    )

    items.append(
        (
            "check-dns.yaml",
            task(
                id_="check-dns",
                name=L("DNS çözümlemesini kontrol et", "Check DNS resolution"),
                summary=L(
                    "Bir adın DNS kaydını dig / Resolve-DnsName benzeri araçlarla sorgula.",
                    "Query a name's DNS records with dig / Resolve-DnsName-style tools.",
                ),
                category="network",
                tags=["network", "dns"],
                intent={
                    "tr": ["dns kontrol", "alan adı çözümle", "dig sorgusu"],
                    "en": ["check dns", "resolve hostname", "dig lookup"],
                },
                implementations=[
                    impl(
                        "unix-dig",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["dig"],
                        examples=[
                            ex(
                                "dig +short example.com A",
                                shell="bash",
                                title=L("A kaydı", "A record"),
                                explanation=L(
                                    "Kısa A yanıtı; yetkili sunucu için @ kullanın.",
                                    "Short A answer; use @ for a specific nameserver.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "windows-dig",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["dig"],
                        examples=[
                            ex(
                                "dig +short example.com A",
                                shell="powershell",
                                title=L("dig (Windows)", "dig (Windows)"),
                                explanation=L(
                                    "dig Windows'ta ayrı kurulum olabilir. Resolve-DnsName henüz bankada yok.",
                                    "dig may need a separate Windows install. Resolve-DnsName not in bank yet.",
                                ),
                            )
                        ],
                        notes=L(
                            "Native Resolve-DnsName kaydı sonraki derinleştirmeye bırakıldı.",
                            "Native Resolve-DnsName record deferred to a later deepen.",
                        ),
                    ),
                ],
                related_commands=["dig", "host", "resolvectl"],
                related_tasks=["check-internet-connectivity"],
                sources=["man 1 dig"],
            ),
        )
    )

    items.append(
        (
            "check-open-ports.yaml",
            task(
                id_="check-open-ports",
                name=L("Açık / dinleyen portları kontrol et", "Check listening / open ports"),
                summary=L(
                    "Yerel dinleyen soketleri ss/netstat veya Get-NetTCPConnection ile listele.",
                    "List local listening sockets with ss/netstat or Get-NetTCPConnection.",
                ),
                description=L(
                    "Uzak tarama (nmap) ayrı bir risk sınıfıdır; önce yerel dinleyenleri tercih et. "
                    "Yetkisiz tarama yapma.",
                    "Remote scanning (nmap) is a different risk class; prefer local listeners first. "
                    "Do not scan without authorization.",
                ),
                category="network",
                tags=["network", "ports", "security"],
                intent={
                    "tr": ["açık portlar", "dinleyen servisler", "hangi port dinliyor"],
                    "en": ["open ports", "listening sockets", "which ports are listening"],
                },
                implementations=[
                    impl(
                        "linux-ss",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["ss"],
                        examples=[
                            ex(
                                "ss -tulpn",
                                shell="bash",
                                title=L("Dinleyen TCP/UDP", "Listening TCP/UDP"),
                                explanation=L(
                                    "TCP/UDP dinleyenleri süreç bilgisiyle listeler.",
                                    "Lists listening TCP/UDP with process info.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "windows-nettcp",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-nettcpconnection"],
                        examples=[
                            ex(
                                "Get-NetTCPConnection -State Listen",
                                shell="powershell",
                                title=L("Dinleyen TCP", "Listening TCP"),
                                explanation=L(
                                    "Windows NetTCPIP dinleyen bağlantılar.",
                                    "Windows NetTCPIP listening connections.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "bsd-netstat",
                        platforms=["bsd", "macos"],
                        shells=["bash"],
                        commands=["netstat-bsd"],
                        examples=[
                            ex(
                                "netstat -an -p tcp",
                                shell="bash",
                                title=L("BSD netstat", "BSD netstat"),
                                explanation=L(
                                    "Windows netstat ile aynı kayıt değildir (id: netstat-bsd).",
                                    "Not the same bank record as Windows netstat (id: netstat-bsd).",
                                ),
                            )
                        ],
                    ),
                ],
                related_commands=["ss", "netstat", "netstat-bsd", "get-nettcpconnection", "nmap", "lsof"],
                related_tasks=["list-running-services", "check-firewall-status"],
                sources=[
                    "man 8 ss",
                    "https://learn.microsoft.com/powershell/module/nettcpip/get-nettcpconnection",
                    "man 1 netstat",
                ],
            ),
        )
    )

    items.append(
        (
            "inspect-network-interfaces.yaml",
            task(
                id_="inspect-network-interfaces",
                name=L("Ağ arayüzlerini incele", "Inspect network interfaces"),
                summary=L(
                    "Arayüz adı, durum ve adresleri platform araçlarıyla göster.",
                    "Show interface names, state, and addresses with platform tools.",
                ),
                category="network",
                tags=["network", "interfaces"],
                intent={
                    "tr": ["ağ kartları", "arayüz listesi", "ethernet wifi durumu"],
                    "en": ["list network interfaces", "nic status", "ethernet wifi state"],
                },
                implementations=[
                    impl(
                        "linux-ip-link",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["ip"],
                        examples=[ex("ip -br link", shell="bash")],
                    ),
                    impl(
                        "macos-networksetup",
                        operating_systems=["macos"],
                        platforms=["macos"],
                        shells=["zsh"],
                        commands=["networksetup"],
                        examples=[ex("networksetup -listallhardwareports", shell="zsh")],
                    ),
                    impl(
                        "windows-ipconfig-all",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["cmd"],
                        commands=["ipconfig"],
                        examples=[ex("ipconfig /all", shell="cmd")],
                    ),
                ],
                related_commands=["ip", "ifconfig", "networksetup", "ipconfig", "nmcli"],
                related_tasks=["show-local-ip", "inspect-routing-table"],
                sources=["man 8 ip", "man 8 networksetup"],
            ),
        )
    )

    items.append(
        (
            "inspect-routing-table.yaml",
            task(
                id_="inspect-routing-table",
                name=L("Yönlendirme tablosunu incele", "Inspect routing table"),
                summary=L(
                    "Varsayılan rota ve yönlendirme tablosunu oku (salt okuma).",
                    "Read the default route and routing table (read-only).",
                ),
                category="network",
                tags=["network", "routing"],
                intent={
                    "tr": ["routing tablosu", "varsayılan ağ geçidi", "route göster"],
                    "en": ["routing table", "default gateway", "show routes"],
                },
                implementations=[
                    impl(
                        "linux-ip-route",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["ip", "route"],
                        examples=[ex("ip route", shell="bash")],
                    ),
                    impl(
                        "unix-netstat-r",
                        platforms=["macos", "bsd"],
                        shells=["bash"],
                        commands=["netstat-bsd", "route"],
                        examples=[ex("netstat -rn", shell="bash")],
                    ),
                    impl(
                        "windows-route-print",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["cmd"],
                        commands=["route", "netsh"],
                        examples=[ex("route print", shell="cmd")],
                    ),
                ],
                related_commands=["ip", "route", "netstat-bsd", "netsh"],
                related_tasks=["inspect-network-interfaces", "check-internet-connectivity"],
                sources=["man 8 ip-route", "man 8 route"],
            ),
        )
    )

    items.append(
        (
            "check-internet-connectivity.yaml",
            task(
                id_="check-internet-connectivity",
                name=L("İnternet bağlantısını kontrol et", "Check internet connectivity"),
                summary=L(
                    "ICMP ping veya HTTPS ile temel erişilebilirlik testi.",
                    "Basic reachability via ICMP ping or HTTPS.",
                ),
                category="network",
                tags=["network", "connectivity"],
                intent={
                    "tr": ["internet var mı", "bağlantı testi", "ping at"],
                    "en": ["am i online", "connectivity test", "ping host"],
                },
                implementations=[
                    impl(
                        "ping-icmp",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash", "cmd"],
                        commands=["ping"],
                        examples=[
                            ex(
                                "ping -c 3 1.1.1.1",
                                shell="bash",
                                title=L("Üç ICMP", "Three ICMP"),
                                explanation=L(
                                    "Windows'ta -n kullanın; politikalar ICMP'yi engelleyebilir.",
                                    "Use -n on Windows; policies may block ICMP.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "curl-https",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash"],
                        commands=["curl"],
                        examples=[
                            ex(
                                "curl -I -m 5 https://example.com",
                                shell="bash",
                                risk="safe",
                            )
                        ],
                    ),
                ],
                related_commands=["ping", "curl", "mtr", "traceroute"],
                related_tasks=["check-dns", "show-public-ip"],
                sources=["man 8 ping", "https://curl.se/docs/manpage.html"],
            ),
        )
    )

    items.append(
        (
            "check-disk-space.yaml",
            task(
                id_="check-disk-space",
                name=L("Disk alanını kontrol et", "Check disk space"),
                summary=L(
                    "Dosya sistemlerinin doluluk oranını df / Get-Volume ile göster.",
                    "Show filesystem free space with df / Get-Volume.",
                ),
                category="disks",
                tags=["disks", "storage", "capacity"],
                intent={
                    "tr": ["disk dolu mu", "boş alan", "df çıktısı"],
                    "en": ["disk space", "free space", "df output"],
                },
                implementations=[
                    impl(
                        "unix-df",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["df"],
                        examples=[ex("df -h", shell="bash")],
                    ),
                    impl(
                        "windows-get-volume",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-volume"],
                        examples=[ex("Get-Volume", shell="powershell")],
                    ),
                ],
                related_commands=["df", "du", "lsblk", "get-volume", "diskutil"],
                related_tasks=["inspect-disk-usage"],
                sources=["man 1 df", "https://learn.microsoft.com/powershell/module/storage/get-volume"],
            ),
        )
    )

    items.append(
        (
            "inspect-disk-usage.yaml",
            task(
                id_="inspect-disk-usage",
                name=L("Dizin disk kullanımını incele", "Inspect directory disk usage"),
                summary=L(
                    "Bir yolun kapladığı alanı du ile özetle (silme yok).",
                    "Summarize space used by a path with du (no deletes).",
                ),
                category="disks",
                tags=["disks", "du"],
                intent={
                    "tr": ["hangi klasör yer kaplıyor", "du kullanımı"],
                    "en": ["which folder uses space", "du usage"],
                },
                implementations=[
                    impl(
                        "unix-du",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["du"],
                        examples=[ex("du -sh /* 2>/dev/null | sort -h", shell="bash", risk="caution")],
                    ),
                    impl(
                        "windows-measure",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-childitem"],
                        examples=[
                            ex(
                                "Get-ChildItem -Force | Measure-Object -Property Length -Sum",
                                shell="powershell",
                                risk="caution",
                            )
                        ],
                        notes=L(
                            "Measure-Object ayrı bir banka kaydı değildir; Get-ChildItem ile birlikte örnek.",
                            "Measure-Object is not a separate bank record; example pairs with Get-ChildItem.",
                        ),
                    ),
                ],
                related_commands=["du", "df", "get-childitem"],
                related_tasks=["check-disk-space"],
                sources=["man 1 du"],
            ),
        )
    )

    items.append(
        (
            "list-running-processes.yaml",
            task(
                id_="list-running-processes",
                name=L("Çalışan süreçleri listele", "List running processes"),
                summary=L(
                    "ps / Get-Process / top ile süreç envanteri.",
                    "Process inventory via ps / Get-Process / top.",
                ),
                category="processes",
                tags=["processes", "monitoring"],
                intent={
                    "tr": ["süreç listesi", "hangi program çalışıyor", "task manager cli"],
                    "en": ["list processes", "what is running", "task manager cli"],
                },
                implementations=[
                    impl(
                        "unix-ps",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["ps"],
                        examples=[ex("ps aux", shell="bash")],
                    ),
                    impl(
                        "windows-get-process",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-process"],
                        examples=[ex("Get-Process | Sort-Object CPU -Descending | Select-Object -First 20", shell="powershell")],
                    ),
                ],
                related_commands=["ps", "top", "htop", "get-process"],
                related_tasks=["check-memory", "list-running-services"],
                sources=["man 1 ps", "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-process"],
            ),
        )
    )

    items.append(
        (
            "check-memory.yaml",
            task(
                id_="check-memory",
                name=L("Bellek kullanımını kontrol et", "Check memory usage"),
                summary=L(
                    "free / vm_stat tarzı araçlarla bellek özeti (okuma).",
                    "Memory summary with free / vm_stat-style tools (read).",
                ),
                category="monitoring",
                tags=["memory", "monitoring"],
                intent={
                    "tr": ["ram kullanımı", "bellek dolu mu", "free çıktısı"],
                    "en": ["ram usage", "memory pressure", "free output"],
                },
                implementations=[
                    impl(
                        "linux-free",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["free"],
                        examples=[ex("free -h", shell="bash")],
                    ),
                    impl(
                        "unix-vmstat",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["vmstat"],
                        examples=[ex("vmstat 1 3", shell="bash")],
                    ),
                    impl(
                        "windows-get-process-mem",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-process", "get-computerinfo"],
                        examples=[
                            ex(
                                "Get-ComputerInfo | Select-Object OsTotalVisibleMemorySize, OsFreePhysicalMemory",
                                shell="powershell",
                            )
                        ],
                    ),
                ],
                related_commands=["free", "vmstat", "top", "get-process", "get-computerinfo"],
                related_tasks=["list-running-processes"],
                sources=["man 1 free", "man 8 vmstat"],
            ),
        )
    )

    items.append(
        (
            "list-running-services.yaml",
            task(
                id_="list-running-services",
                name=L("Çalışan servisleri listele", "List running services"),
                summary=L(
                    "systemd / BSD service / Windows Get-Service / launchctl ile servis durumu.",
                    "Service state via systemd / BSD service / Windows Get-Service / launchctl.",
                ),
                description=L(
                    "Servis modelleri eşitlenmez: systemctl ≠ service ≠ Get-Service ≠ launchctl.",
                    "Service models are not equated: systemctl ≠ service ≠ Get-Service ≠ launchctl.",
                ),
                category="system",
                tags=["services", "systemd"],
                intent={
                    "tr": ["servis listesi", "systemctl status", "hangi servisler aktif"],
                    "en": ["list services", "systemctl status", "which services are active"],
                },
                implementations=[
                    impl(
                        "linux-systemctl",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["systemctl"],
                        examples=[ex("systemctl list-units --type=service --state=running", shell="bash")],
                    ),
                    impl(
                        "bsd-service",
                        operating_systems=["freebsd", "netbsd", "dragonflybsd"],
                        platforms=["bsd"],
                        shells=["bash"],
                        commands=["service"],
                        examples=[ex("service -e", shell="bash")],
                    ),
                    impl(
                        "openbsd-rcctl",
                        operating_systems=["openbsd"],
                        platforms=["bsd"],
                        shells=["ksh"],
                        commands=["rcctl"],
                        examples=[ex("rcctl ls started", shell="ksh")],
                    ),
                    impl(
                        "windows-get-service",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-service"],
                        examples=[ex("Get-Service | Where-Object Status -eq Running", shell="powershell")],
                    ),
                    impl(
                        "macos-launchctl",
                        operating_systems=["macos"],
                        platforms=["macos"],
                        shells=["zsh"],
                        commands=["launchctl"],
                        examples=[ex("launchctl list", shell="zsh")],
                    ),
                ],
                related_commands=["systemctl", "service", "rcctl", "get-service", "sc", "launchctl", "sysrc"],
                related_tasks=["inspect-system-logs", "check-open-ports"],
                sources=[
                    "man 1 systemctl",
                    "man 8 service",
                    "man 8 rcctl",
                    "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-service",
                ],
            ),
        )
    )

    items.append(
        (
            "inspect-system-logs.yaml",
            task(
                id_="inspect-system-logs",
                name=L("Sistem günlüklerini incele", "Inspect system logs"),
                summary=L(
                    "journalctl / Get-WinEvent / log / dmesg ile okuma odaklı günlük inceleme.",
                    "Read-oriented log inspection via journalctl / Get-WinEvent / log / dmesg.",
                ),
                category="system",
                tags=["logs", "journal"],
                intent={
                    "tr": ["sistem logları", "journalctl oku", "hata günlükleri"],
                    "en": ["system logs", "read journalctl", "error logs"],
                },
                implementations=[
                    impl(
                        "linux-journalctl",
                        operating_systems=["linux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["journalctl"],
                        examples=[ex("journalctl -xe --no-pager | tail -n 50", shell="bash")],
                    ),
                    impl(
                        "windows-winevent",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["get-winevent"],
                        examples=[
                            ex(
                                "Get-WinEvent -LogName System -MaxEvents 20",
                                shell="powershell",
                            )
                        ],
                    ),
                    impl(
                        "macos-log",
                        operating_systems=["macos"],
                        platforms=["macos"],
                        shells=["zsh"],
                        commands=["log"],
                        examples=[ex("log show --last 5m --style compact", shell="zsh")],
                    ),
                    impl(
                        "kernel-dmesg",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["dmesg"],
                        examples=[ex("dmesg | tail -n 40", shell="bash")],
                    ),
                ],
                related_commands=["journalctl", "get-winevent", "log", "dmesg", "tail", "get-content"],
                related_tasks=["list-running-services"],
                sources=["man 1 journalctl", "man 1 log", "man 1 dmesg"],
            ),
        )
    )

    items.append(
        (
            "connect-ssh.yaml",
            task(
                id_="connect-ssh",
                name=L("SSH ile bağlan", "Connect over SSH"),
                summary=L(
                    "Uzak kabuğa OpenSSH istemcisi ile bağlanma (öğretici).",
                    "Connect to a remote shell with the OpenSSH client (teaching).",
                ),
                category="security",
                tags=["ssh", "remote"],
                intent={
                    "tr": ["ssh bağlan", "uzak sunucuya gir", "ssh user@host"],
                    "en": ["ssh connect", "remote shell", "ssh user@host"],
                },
                implementations=[
                    impl(
                        "openssh-client",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash", "powershell"],
                        commands=["ssh"],
                        examples=[
                            ex(
                                "ssh user@server.example",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                                explanation=L(
                                    "Host anahtarını doğrula; parola/anahtar sızdırma.",
                                    "Verify host keys; avoid leaking passwords/keys.",
                                ),
                            )
                        ],
                    ),
                ],
                related_commands=["ssh", "scp", "sftp", "rsync"],
                related_tasks=["transfer-files-ssh"],
                sources=["man 1 ssh"],
            ),
        )
    )

    items.append(
        (
            "transfer-files-ssh.yaml",
            task(
                id_="transfer-files-ssh",
                name=L("SSH üzerinden dosya aktar", "Transfer files over SSH"),
                summary=L(
                    "scp veya rsync ile güvenli kopyalama (öğretici örnekler).",
                    "Secure copy with scp or rsync (teaching examples).",
                ),
                category="security",
                tags=["ssh", "scp", "rsync"],
                intent={
                    "tr": ["scp ile kopyala", "rsync uzak", "dosya gönder"],
                    "en": ["scp copy", "rsync remote", "send files over ssh"],
                },
                implementations=[
                    impl(
                        "scp",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash"],
                        commands=["scp"],
                        examples=[
                            ex(
                                "scp ./report.txt user@server.example:~/inbox/",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                            )
                        ],
                    ),
                    impl(
                        "rsync-ssh",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["rsync", "ssh"],
                        examples=[
                            ex(
                                "rsync -avz -e ssh ./dir/ user@server.example:~/dir/",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                            )
                        ],
                    ),
                ],
                related_commands=["scp", "rsync", "ssh", "sftp"],
                related_tasks=["connect-ssh", "backup-directory"],
                sources=["man 1 scp", "man 1 rsync"],
            ),
        )
    )

    items.append(
        (
            "update-system.yaml",
            task(
                id_="update-system",
                name=L("Sistem paketlerini güncelle", "Update system packages"),
                summary=L(
                    "Dağıtıma özgü paket yöneticisi ile güncelleme (yıkıcı olabilir).",
                    "Distro-specific package manager update (may be disruptive).",
                ),
                description=L(
                    "Arch'ta pacman tercih edilir. Windows/macOS güncelleme modelleri ayrıdır. "
                    "Örnekler caution/elevated; otomatik çalıştırılmaz.",
                    "Prefer pacman on Arch. Windows/macOS update models differ. "
                    "Examples are caution/elevated; not auto-executed.",
                ),
                category="packages",
                tags=["packages", "update", "maintenance"],
                intent={
                    "tr": ["sistem güncelle", "paket upgrade", "güncelleme yap"],
                    "en": ["update system", "upgrade packages", "os update"],
                },
                implementations=[
                    impl(
                        "arch-pacman",
                        operating_systems=["linux"],
                        distributions=["arch", "endeavouros", "manjaro"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["pacman"],
                        examples=[
                            ex(
                                "sudo pacman -Syu",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                        notes=L(
                            "Arch-first: pacman -Syu; AUR yardımcıları ayrı kayıtlardır.",
                            "Arch-first: pacman -Syu; AUR helpers are separate records.",
                        ),
                    ),
                    impl(
                        "debian-apt",
                        operating_systems=["linux"],
                        distributions=["debian", "ubuntu", "linux-mint", "pop-os"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["apt"],
                        examples=[
                            ex(
                                "sudo apt update && sudo apt upgrade",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "fedora-dnf",
                        operating_systems=["linux"],
                        distributions=["fedora", "rhel", "rocky", "almalinux"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["dnf"],
                        examples=[
                            ex(
                                "sudo dnf upgrade",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "freebsd-pkg",
                        operating_systems=["freebsd"],
                        platforms=["bsd"],
                        shells=["bash"],
                        commands=["pkg", "freebsd-update"],
                        examples=[
                            ex(
                                "sudo pkg upgrade",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "macos-softwareupdate",
                        operating_systems=["macos"],
                        platforms=["macos"],
                        shells=["zsh"],
                        commands=["softwareupdate", "brew"],
                        examples=[
                            ex(
                                "softwareupdate -l",
                                shell="zsh",
                                risk="safe",
                                privilege="none",
                            )
                        ],
                    ),
                    impl(
                        "windows-winget",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["winget"],
                        examples=[
                            ex(
                                "winget upgrade --all",
                                shell="powershell",
                                risk="caution",
                                privilege="admin",
                            )
                        ],
                    ),
                ],
                related_commands=[
                    "pacman",
                    "apt",
                    "dnf",
                    "zypper",
                    "apk",
                    "pkg",
                    "brew",
                    "softwareupdate",
                    "winget",
                    "freebsd-update",
                ],
                related_tasks=["install-package"],
                sources=[
                    "man 8 pacman",
                    "man 8 apt",
                    "man 8 dnf",
                    "https://docs.brew.sh/",
                    "https://learn.microsoft.com/windows/package-manager/winget/",
                ],
            ),
        )
    )

    items.append(
        (
            "install-package.yaml",
            task(
                id_="install-package",
                name=L("Paket kur", "Install a package"),
                summary=L(
                    "İsim bilinen bir paketi platform PM ile kur (örnek placeholder).",
                    "Install a named package with the platform PM (placeholder examples).",
                ),
                category="packages",
                tags=["packages", "install"],
                intent={
                    "tr": ["paket kur", "yazılım yükle", "pacman -S"],
                    "en": ["install package", "add software", "pacman -S"],
                },
                implementations=[
                    impl(
                        "arch-pacman",
                        distributions=["arch"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["pacman"],
                        examples=[
                            ex(
                                "sudo pacman -S package-name",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "debian-apt",
                        distributions=["debian", "ubuntu"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["apt"],
                        examples=[
                            ex(
                                "sudo apt install package-name",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "fedora-dnf",
                        distributions=["fedora"],
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["dnf"],
                        examples=[
                            ex(
                                "sudo dnf install package-name",
                                shell="bash",
                                risk="caution",
                                privilege="elevated",
                            )
                        ],
                    ),
                    impl(
                        "macos-brew",
                        operating_systems=["macos"],
                        platforms=["macos"],
                        shells=["zsh"],
                        commands=["brew"],
                        examples=[ex("brew install package-name", shell="zsh", risk="caution")],
                    ),
                    impl(
                        "windows-winget",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["powershell"],
                        commands=["winget"],
                        examples=[
                            ex(
                                "winget install --id Vendor.Package",
                                shell="powershell",
                                risk="caution",
                                privilege="admin",
                            )
                        ],
                    ),
                ],
                related_commands=["pacman", "apt", "dnf", "brew", "winget", "pkg", "zypper", "apk"],
                related_tasks=["update-system"],
                sources=["man 8 pacman", "man 8 apt", "https://docs.brew.sh/Manpage"],
            ),
        )
    )

    items.append(
        (
            "check-firewall-status.yaml",
            task(
                id_="check-firewall-status",
                name=L("Güvenlik duvarı durumunu kontrol et", "Check firewall status"),
                summary=L(
                    "ufw / firewall-cmd / pfctl / netsh ile durum okuma (kural silme yok).",
                    "Read status via ufw / firewall-cmd / pfctl / netsh (no rule deletes).",
                ),
                category="security",
                tags=["firewall", "security"],
                intent={
                    "tr": ["firewall durumu", "ufw status", "pfctl kurallar"],
                    "en": ["firewall status", "ufw status", "pfctl rules"],
                },
                implementations=[
                    impl(
                        "linux-ufw",
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["ufw"],
                        examples=[ex("sudo ufw status verbose", shell="bash", privilege="elevated")],
                    ),
                    impl(
                        "linux-firewalld",
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["firewall-cmd"],
                        examples=[ex("firewall-cmd --state", shell="bash")],
                    ),
                    impl(
                        "bsd-pfctl",
                        platforms=["bsd", "macos"],
                        shells=["bash"],
                        commands=["pfctl"],
                        examples=[ex("sudo pfctl -s info", shell="bash", privilege="elevated")],
                    ),
                    impl(
                        "windows-netsh",
                        operating_systems=["windows"],
                        platforms=["windows"],
                        shells=["cmd"],
                        commands=["netsh"],
                        examples=[ex("netsh advfirewall show allprofiles", shell="cmd")],
                    ),
                ],
                related_commands=["ufw", "firewall-cmd", "nft", "iptables", "pfctl", "netsh"],
                related_tasks=["check-open-ports"],
                sources=["man 8 ufw", "man 1 firewall-cmd", "man 8 pfctl"],
            ),
        )
    )

    items.append(
        (
            "inspect-container.yaml",
            task(
                id_="inspect-container",
                name=L("Konteyneri incele", "Inspect a container"),
                summary=L(
                    "docker/podman/nerdctl ile çalışan konteyner envanteri (orkestrasyon değil).",
                    "Running container inventory via docker/podman/nerdctl (not orchestration).",
                ),
                category="containers",
                tags=["containers", "docker"],
                intent={
                    "tr": ["konteyner listesi", "docker ps", "podman konteyner"],
                    "en": ["list containers", "docker ps", "podman containers"],
                },
                implementations=[
                    impl(
                        "docker-ps",
                        platforms=["linux", "macos", "windows"],
                        shells=["bash"],
                        commands=["docker"],
                        examples=[ex("docker ps", shell="bash")],
                    ),
                    impl(
                        "podman-ps",
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["podman"],
                        examples=[ex("podman ps", shell="bash")],
                    ),
                    impl(
                        "nerdctl-ps",
                        platforms=["linux"],
                        shells=["bash"],
                        commands=["nerdctl"],
                        examples=[ex("nerdctl ps", shell="bash")],
                    ),
                ],
                related_commands=["docker", "podman", "nerdctl", "crictl", "kubectl"],
                related_tasks=["check-container-logs"],
                sources=[
                    "https://docs.docker.com/engine/reference/commandline/ps/",
                    "https://docs.podman.io/",
                ],
            ),
        )
    )

    items.append(
        (
            "check-container-logs.yaml",
            task(
                id_="check-container-logs",
                name=L("Konteyner günlüklerini kontrol et", "Check container logs"),
                summary=L(
                    "Runtime log akışını oku (kubectl logs ayrı orchestrator yolu).",
                    "Read runtime log streams (kubectl logs is a separate orchestrator path).",
                ),
                category="containers",
                tags=["containers", "logs"],
                intent={
                    "tr": ["docker logs", "konteyner log", "podman logs"],
                    "en": ["docker logs", "container logs", "podman logs"],
                },
                implementations=[
                    impl(
                        "docker-logs",
                        platforms=["linux", "macos", "windows"],
                        shells=["bash"],
                        commands=["docker"],
                        examples=[ex("docker logs --tail 100 mycontainer", shell="bash")],
                    ),
                    impl(
                        "kubectl-logs",
                        platforms=["linux", "macos", "windows"],
                        shells=["bash"],
                        commands=["kubectl"],
                        examples=[
                            ex(
                                "kubectl logs deploy/myapp --tail=100",
                                shell="bash",
                                risk="caution",
                            )
                        ],
                        notes=L(
                            "Yanlış kubeconfig bağlamı risklidir; önce context doğrula.",
                            "Wrong kubeconfig context is risky; verify context first.",
                        ),
                    ),
                ],
                related_commands=["docker", "podman", "nerdctl", "kubectl", "crictl"],
                related_tasks=["inspect-container"],
                sources=["https://docs.docker.com/engine/reference/commandline/logs/"],
            ),
        )
    )

    items.append(
        (
            "backup-directory.yaml",
            task(
                id_="backup-directory",
                name=L("Dizin yedekle", "Back up a directory"),
                summary=L(
                    "rsync / restic / borg ile dizin yedeği (gizli anahtar örnek yok).",
                    "Directory backup with rsync / restic / borg (no secret-key examples).",
                ),
                category="backup",
                tags=["backup", "storage"],
                intent={
                    "tr": ["klasör yedekle", "restic backup", "rsync yedek"],
                    "en": ["backup folder", "restic backup", "rsync backup"],
                },
                implementations=[
                    impl(
                        "rsync-local",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["rsync"],
                        examples=[
                            ex(
                                "rsync -aHAX --info=progress2 /path/to/src/ /path/to/backup/",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                            )
                        ],
                    ),
                    impl(
                        "restic-snapshot",
                        platforms=["linux", "macos", "bsd", "windows"],
                        shells=["bash"],
                        commands=["restic"],
                        examples=[
                            ex(
                                "restic -r /path/to/repo backup /path/to/data",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                                explanation=L(
                                    "Depo parolası/ortam değişkeni örneğe yazılmaz.",
                                    "Repo password/env vars are omitted from examples.",
                                ),
                            )
                        ],
                    ),
                    impl(
                        "borg-create",
                        platforms=["linux", "macos", "bsd"],
                        shells=["bash"],
                        commands=["borg"],
                        examples=[
                            ex(
                                "borg create /path/to/repo::'{hostname}-{now}' /path/to/data",
                                shell="bash",
                                risk="caution",
                                privilege="user",
                            )
                        ],
                    ),
                ],
                related_commands=["rsync", "restic", "borg", "rclone", "tar"],
                related_tasks=["transfer-files-ssh", "check-disk-space"],
                sources=[
                    "man 1 rsync",
                    "https://restic.readthedocs.io/",
                    "https://borgbackup.readthedocs.io/",
                ],
            ),
        )
    )

    return items


def build_profiles() -> list[tuple[str, dict]]:
    common_tasks = [
        "show-local-ip",
        "check-disk-space",
        "list-running-services",
        "inspect-system-logs",
        "update-system",
        "check-firewall-status",
        "connect-ssh",
    ]
    items: list[tuple[str, dict]] = []

    items.append(
        (
            "linux-server.yaml",
            profile(
                id_="linux-server",
                name=L("Linux sunucu (temel)", "Linux server (basics)"),
                summary=L(
                    "Genel amaçlı Linux sunucu: servisler, ağ, disk, güncelleme ve SSH.",
                    "General-purpose Linux server: services, network, disk, updates, SSH.",
                ),
                description=L(
                    "Yönlendirici referans koleksiyonu; komutları otomatik çalıştırmaz. "
                    "Dağıtıma özel profiller (debian/fedora/arch) ile birlikte kullan.",
                    "Guiding reference collection; does not auto-run commands. "
                    "Use with distro-specific profiles (debian/fedora/arch).",
                ),
                operating_systems=["linux"],
                distributions=["arch", "debian", "ubuntu", "fedora"],
                related_commands=[
                    "systemctl",
                    "journalctl",
                    "ip",
                    "ss",
                    "df",
                    "ssh",
                    "ufw",
                    "firewall-cmd",
                    "pacman",
                    "apt",
                    "dnf",
                ],
                related_tasks=common_tasks
                + ["check-open-ports", "check-memory", "list-running-processes"],
                tags=["server", "linux"],
                sources=["docs/SERVER_ADMINISTRATION.md"],
            ),
        )
    )

    items.append(
        (
            "debian-server.yaml",
            profile(
                id_="debian-server",
                name=L("Debian / Ubuntu sunucu", "Debian / Ubuntu server"),
                summary=L(
                    "apt tabanlı sunucu: servisler, ufw, günlükler, güncelleme.",
                    "apt-based server: services, ufw, logs, updates.",
                ),
                operating_systems=["linux"],
                distributions=["debian", "ubuntu", "linux-mint", "pop-os"],
                related_commands=["apt", "systemctl", "journalctl", "ufw", "ss", "ip", "ssh"],
                related_tasks=["update-system", "install-package", "list-running-services", "check-firewall-status"],
                tags=["server", "debian", "ubuntu"],
                sources=["https://www.debian.org/doc/", "https://ubuntu.com/server/docs"],
            ),
        )
    )

    items.append(
        (
            "fedora-server.yaml",
            profile(
                id_="fedora-server",
                name=L("Fedora / RHEL ailesi sunucu", "Fedora / RHEL-family server"),
                summary=L(
                    "dnf + firewalld + systemd odaklı sunucu profili.",
                    "dnf + firewalld + systemd oriented server profile.",
                ),
                operating_systems=["linux"],
                distributions=["fedora", "fedora-server", "rhel", "rocky", "almalinux"],
                related_commands=["dnf", "systemctl", "journalctl", "firewall-cmd", "ss", "ip"],
                related_tasks=["update-system", "install-package", "list-running-services", "check-firewall-status"],
                tags=["server", "fedora", "rhel"],
                sources=["https://docs.fedoraproject.org/", "https://access.redhat.com/documentation"],
            ),
        )
    )

    items.append(
        (
            "arch-server.yaml",
            profile(
                id_="arch-server",
                name=L("Arch Linux sunucu", "Arch Linux server"),
                summary=L(
                    "pacman-first Arch sunucu: rolling güncelleme, systemd, nft/ufw seçenekleri.",
                    "pacman-first Arch server: rolling updates, systemd, nft/ufw options.",
                ),
                description=L(
                    "Kurulum/güncelleme notlarında pacman tercih edilir (proje tercihi).",
                    "Install/update notes prefer pacman (project preference).",
                ),
                operating_systems=["linux"],
                distributions=["arch", "endeavouros", "manjaro"],
                related_commands=["pacman", "systemctl", "journalctl", "ip", "ss", "nft", "ufw", "ssh"],
                related_tasks=["update-system", "install-package", "list-running-services", "show-local-ip"],
                tags=["server", "arch", "pacman"],
                sources=["https://wiki.archlinux.org/title/Server"],
            ),
        )
    )

    items.append(
        (
            "windows-server.yaml",
            profile(
                id_="windows-server",
                name=L("Windows sunucu / masaüstü yönetim", "Windows server / admin basics"),
                summary=L(
                    "PowerShell odaklı servis, ağ, disk ve WinGet güncelleme referansı.",
                    "PowerShell-oriented services, network, disk, and WinGet update reference.",
                ),
                operating_systems=["windows"],
                distributions=["windows-server", "windows-11", "windows-10"],
                related_commands=[
                    "get-service",
                    "get-process",
                    "get-netipconfiguration",
                    "get-nettcpconnection",
                    "get-volume",
                    "get-winevent",
                    "winget",
                    "netsh",
                    "ipconfig",
                    "sc",
                ],
                related_tasks=[
                    "show-local-ip",
                    "check-open-ports",
                    "check-disk-space",
                    "list-running-services",
                    "inspect-system-logs",
                    "update-system",
                    "check-firewall-status",
                ],
                tags=["server", "windows", "powershell"],
                sources=["https://learn.microsoft.com/windows-server/", "https://learn.microsoft.com/powershell/"],
            ),
        )
    )

    items.append(
        (
            "freebsd-server.yaml",
            profile(
                id_="freebsd-server",
                name=L("FreeBSD sunucu", "FreeBSD server"),
                summary=L(
                    "pkg / service / sysrc / pfctl — systemd ile eşitlenmez.",
                    "pkg / service / sysrc / pfctl — not equated with systemd.",
                ),
                operating_systems=["freebsd"],
                distributions=["freebsd-release"],
                related_commands=["pkg", "freebsd-update", "service", "sysrc", "pfctl", "ifconfig", "ssh"],
                related_tasks=["update-system", "list-running-services", "check-firewall-status", "show-local-ip"],
                tags=["server", "freebsd", "bsd"],
                sources=["https://docs.freebsd.org/"],
            ),
        )
    )

    items.append(
        (
            "homelab.yaml",
            profile(
                id_="homelab",
                name=L("Homelab sunucu", "Homelab server"),
                summary=L(
                    "Ev laboratuvarı: Docker, reverse proxy, yedek, SSH ve temel ağ.",
                    "Home lab: Docker, reverse proxy, backup, SSH, and basic networking.",
                ),
                operating_systems=["linux"],
                server_platforms=["docker-engine", "proxmox-ve"],
                related_commands=[
                    "docker",
                    "docker-compose",
                    "nginx",
                    "caddy",
                    "restic",
                    "rsync",
                    "ssh",
                    "ufw",
                    "systemctl",
                ],
                related_tasks=[
                    "inspect-container",
                    "check-container-logs",
                    "backup-directory",
                    "connect-ssh",
                    "check-firewall-status",
                    "update-system",
                ],
                tags=["homelab", "server", "self-hosted"],
                sources=["docs/SERVER_ADMINISTRATION.md"],
            ),
        )
    )

    items.append(
        (
            "docker-host.yaml",
            profile(
                id_="docker-host",
                name=L("Docker ana makinesi", "Docker host"),
                summary=L(
                    "Konteyner runtime odaklı host: docker/podman/nerdctl, disk ve servisler.",
                    "Container-runtime host: docker/podman/nerdctl, disk, and services.",
                ),
                operating_systems=["linux"],
                server_platforms=["docker-engine"],
                related_commands=["docker", "docker-compose", "podman", "nerdctl", "systemctl", "df", "ss"],
                related_tasks=["inspect-container", "check-container-logs", "check-disk-space", "list-running-services"],
                tags=["containers", "docker"],
                sources=["https://docs.docker.com/engine/"],
            ),
        )
    )

    items.append(
        (
            "kubernetes.yaml",
            profile(
                id_="kubernetes",
                name=L("Kubernetes düğümü / operatör", "Kubernetes node / operator"),
                summary=L(
                    "kubectl/helm/crictl referansı; yanlış context riskine dikkat.",
                    "kubectl/helm/crictl reference; watch wrong-context risk.",
                ),
                operating_systems=["linux"],
                server_platforms=["kubernetes", "docker-engine"],
                related_commands=["kubectl", "helm", "crictl", "nerdctl", "ssh"],
                related_tasks=["inspect-container", "check-container-logs", "connect-ssh"],
                tags=["kubernetes", "containers", "devops"],
                sources=["https://kubernetes.io/docs/", "https://helm.sh/docs/"],
            ),
        )
    )

    items.append(
        (
            "web-server.yaml",
            profile(
                id_="web-server",
                name=L("Web / reverse proxy sunucu", "Web / reverse-proxy server"),
                summary=L(
                    "nginx/Caddy + TLS/servis alışkanlıkları (config test önce).",
                    "nginx/Caddy + TLS/service habits (config test first).",
                ),
                operating_systems=["linux"],
                related_commands=["nginx", "caddy", "systemctl", "ss", "ufw"],
                related_tasks=["list-running-services", "check-open-ports", "check-firewall-status", "inspect-system-logs"],
                tags=["web", "proxy", "server"],
                sources=["https://nginx.org/en/docs/", "https://caddyserver.com/docs/"],
            ),
        )
    )

    items.append(
        (
            "database-server.yaml",
            profile(
                id_="database-server",
                name=L("Veritabanı sunucu", "Database server"),
                summary=L(
                    "İstemci CLI odaklı DB profili (parola argv'de yok).",
                    "Client-CLI oriented DB profile (no passwords on argv).",
                ),
                operating_systems=["linux"],
                related_commands=["mysql", "psql", "redis-cli", "sqlite3", "systemctl", "ss"],
                related_tasks=["list-running-services", "check-open-ports", "backup-directory", "inspect-system-logs"],
                tags=["databases", "server"],
                sources=["docs/SERVER_ADMINISTRATION.md"],
            ),
        )
    )

    items.append(
        (
            "nas-server.yaml",
            profile(
                id_="nas-server",
                name=L("NAS / depolama sunucu", "NAS / storage server"),
                summary=L(
                    "Disk, paylaşım ve yedek odaklı depolama profili (vendor CLI bankası değil).",
                    "Disk, share, and backup oriented storage profile (not a vendor CLI bank).",
                ),
                operating_systems=["linux", "freebsd"],
                server_platforms=["truenas-scale", "truenas-core", "openmediavault", "synology-dsm"],
                related_commands=["df", "du", "lsblk", "mount", "rsync", "restic", "borg", "rclone", "zfs"],
                related_tasks=["check-disk-space", "inspect-disk-usage", "backup-directory", "connect-ssh"],
                tags=["nas", "storage", "backup"],
                sources=["docs/SERVER_ADMINISTRATION.md"],
            ),
        )
    )

    items.append(
        (
            "virtualization-host.yaml",
            profile(
                id_="virtualization-host",
                name=L("Sanallaştırma ana makinesi", "Virtualization host"),
                summary=L(
                    "libvirt/QEMU host: virsh / qemu-img (konteyner ile eşitlenmez).",
                    "libvirt/QEMU host: virsh / qemu-img (not equated with containers).",
                ),
                operating_systems=["linux"],
                server_platforms=["kvm", "qemu", "libvirt", "proxmox-ve"],
                related_commands=["virsh", "qemu-img", "systemctl", "ip", "ss", "df"],
                related_tasks=["list-running-services", "check-disk-space", "show-local-ip", "connect-ssh"],
                tags=["virtualization", "kvm"],
                sources=["https://libvirt.org/manpages/virsh.html"],
            ),
        )
    )

    return items


def main() -> None:
    # Verify referenced command ids exist
    cmd_ids: set[str] = set()
    for path in (ROOT / "commands").rglob("*.yaml"):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(raw, dict) and "id" in raw:
            cmd_ids.add(raw["id"])

    missing: list[str] = []
    for fname, data in build_tasks() + build_profiles():
        for cid in data.get("related_commands") or []:
            if cid not in cmd_ids:
                missing.append(f"{fname}: related_commands missing {cid}")
        for impl_row in data.get("implementations") or []:
            for cid in impl_row.get("commands") or []:
                if cid not in cmd_ids:
                    missing.append(f"{fname}: impl {impl_row.get('id')} missing {cid}")

    if missing:
        print("FAIL: missing command ids:")
        for m in missing:
            print(f"  - {m}")
        raise SystemExit(1)

    TASKS.mkdir(parents=True, exist_ok=True)
    PROFILES.mkdir(parents=True, exist_ok=True)
    for fname, data in build_tasks():
        dump(TASKS / fname, data)
    for fname, data in build_profiles():
        dump(PROFILES / fname, data)

    print(
        f"OK: wrote {len(list(TASKS.glob('*.yaml')))} tasks, "
        f"{len(list(PROFILES.glob('*.yaml')))} profiles"
    )


if __name__ == "__main__":
    main()
