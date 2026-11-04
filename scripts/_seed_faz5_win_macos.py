#!/usr/bin/env python3
"""One-shot Faz 5 seeder: Windows + macOS command YAML (schema v2).

Not for re-run after content is curated — edits go in commands/ directly.
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "commands"

# Keep YAML stable / readable like existing bank files.
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


def draft_sources(*urls: str, note: str = "Agent-authored Faz 5 draft from official docs; not human-verified.") -> dict:
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
    shell: str | None = None,
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
    if shell:
        e["shell"] = shell
    if platforms:
        e["platforms"] = platforms
    if privilege:
        e["privilege"] = privilege
    return e


def ps_cmd(
    *,
    id_: str,
    name: str,
    category: str,
    summary: dict,
    description: dict,
    tags: list[str],
    risk: str,
    elevated: bool,
    sources: list[str],
    examples: list[dict],
    flags: list[dict] | None = None,
    related: list[str] | None = None,
    intent: dict | None = None,
    security: dict | None = None,
    aliases: list[str] | None = None,
    shells: list[str] | None = None,
    concepts: list[str] | None = None,
) -> dict:
    shells = shells or ["powershell", "windows-powershell"]
    data: dict = {
        "schema_version": 2,
        "id": id_,
        "name": name,
        "kind": "powershell_cmdlet",
        "category": category,
        "summary": summary,
        "description": description,
        "tags": tags,
        "risk": risk,
        "requires_elevated": elevated,
        "platforms": ["windows"],
        "operating_systems": ["windows"],
        "shells": shells,
        "flags": flags or [],
        "examples": examples,
        "intent": intent
        or {
            "tr": [name.lower(), f"powershell {id_.replace('-', ' ')}"],
            "en": [name, f"powershell {id_.replace('-', ' ')}"],
        },
        "verification": draft_sources(*sources),
    }
    if aliases:
        data["aliases"] = aliases
    if related:
        data["related"] = related
    if security:
        data["security"] = security
    if concepts:
        data["nova"] = {"concepts": concepts}
    return data


def win_exe(
    *,
    id_: str,
    name: str,
    category: str,
    summary: dict,
    description: dict,
    tags: list[str],
    risk: str,
    elevated: bool,
    sources: list[str],
    examples: list[dict],
    kind: str = "executable",
    flags: list[dict] | None = None,
    related: list[str] | None = None,
    intent: dict | None = None,
    security: dict | None = None,
    shells: list[str] | None = None,
    package_refs: list[dict] | None = None,
    concepts: list[str] | None = None,
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
        "platforms": ["windows"],
        "operating_systems": ["windows"],
        "flags": flags or [],
        "examples": examples,
        "intent": intent
        or {
            "tr": [name.lower(), id_.replace("-", " ")],
            "en": [name, id_.replace("-", " ")],
        },
        "verification": draft_sources(*sources),
    }
    if shells:
        data["shells"] = shells
    if related:
        data["related"] = related
    if security:
        data["security"] = security
    if package_refs:
        data["package_refs"] = package_refs
    if concepts:
        data["nova"] = {"concepts": concepts}
    return data


def mac_cmd(
    *,
    id_: str,
    name: str,
    category: str,
    summary: dict,
    description: dict,
    tags: list[str],
    risk: str,
    elevated: bool,
    sources: list[str],
    examples: list[dict],
    kind: str = "executable",
    flags: list[dict] | None = None,
    related: list[str] | None = None,
    intent: dict | None = None,
    package_refs: list[dict] | None = None,
    concepts: list[str] | None = None,
    shells: list[str] | None = None,
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
        "platforms": ["macos"],
        "operating_systems": ["macos"],
        "flags": flags or [],
        "examples": examples,
        "intent": intent
        or {
            "tr": [name, id_.replace("-", " ")],
            "en": [name, id_.replace("-", " ")],
        },
        "verification": draft_sources(*sources),
    }
    if shells:
        data["shells"] = shells
    if related:
        data["related"] = related
    if package_refs:
        data["package_refs"] = package_refs
    if concepts:
        data["nova"] = {"concepts": concepts}
    return data


WINDOWS: list[tuple[str, dict]] = []
MACOS: list[tuple[str, dict]] = []

# --- PowerShell cmdlets (separate from CMD / executables) ---

WINDOWS.append(
    (
        "system/get-command.yaml",
        ps_cmd(
            id_="get-command",
            name="Get-Command",
            category="system",
            summary=L(
                "PowerShell’de komut, cmdlet, fonksiyon veya alias bulur.",
                "Finds a cmdlet, function, alias, or executable in PowerShell.",
            ),
            description=L(
                "Get-Command, PowerShell oturumunda hangi komutların yüklü/erişilebilir "
                "olduğunu listeler. Linux `which`/`type` karşılığı değildir — ayrı kayıt. "
                "PowerShell 7+ (`pwsh`) ve Windows PowerShell 5.1’de çalışır; bazı modüller "
                "yalnızca Windows’ta bulunur.",
                "Get-Command lists which commands are available in the PowerShell session. "
                "It is not a Linux which/type alias — separate record. Works on PowerShell 7+ "
                "(pwsh) and Windows PowerShell 5.1; some modules are Windows-only.",
            ),
            tags=["powershell", "windows", "discovery"],
            risk="safe",
            elevated=False,
            aliases=["gcm"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-command"],
            flags=[
                flag("-Name", "Komut adı / joker.", "Command name / wildcard.", takes_value=True, value_name="Name"),
                flag("-Module", "Belirli modülden listele.", "List from a module.", takes_value=True, value_name="Module"),
                flag("-CommandType", "Cmdlet/Function/Alias/Application süz.", "Filter by CommandType.", takes_value=True),
            ],
            examples=[
                ex(
                    "Cmdlet ara",
                    "Find cmdlet",
                    "Get-Command Get-Process",
                    "Get-Process cmdlet bilgisini gösterir.",
                    "Shows metadata for Get-Process.",
                    shell="powershell",
                    platforms=["windows"],
                    privilege="none",
                ),
                ex(
                    "Joker",
                    "Wildcard",
                    "Get-Command Get-Net*",
                    "Get-Net* ile başlayan komutları listeler.",
                    "Lists commands matching Get-Net*.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-help", "get-process"],
            concepts=["path"],
        ),
    )
)

WINDOWS.append(
    (
        "system/get-help.yaml",
        ps_cmd(
            id_="get-help",
            name="Get-Help",
            category="system",
            summary=L(
                "PowerShell yardım konularını gösterir.",
                "Displays PowerShell help topics.",
            ),
            description=L(
                "Get-Help, cmdlet ve kavramlar için yardım metnini getirir. İlk kullanımda "
                "`Update-Help` gerekebilir. man/—help ile karıştırılmamalı; PowerShell’e özgüdür. "
                "PowerShell 7+ ve Windows PowerShell 5.1’de mevcuttur.",
                "Get-Help shows help for cmdlets and conceptual topics. Update-Help may be "
                "needed first. Not the same as man/--help — PowerShell-specific. Available in "
                "PowerShell 7+ and Windows PowerShell 5.1.",
            ),
            tags=["powershell", "windows", "help"],
            risk="safe",
            elevated=False,
            aliases=["help", "man"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-help"],
            flags=[
                flag("-Full", "Tam yardım.", "Full help."),
                flag("-Examples", "Yalnız örnekler.", "Examples only."),
                flag("-Online", "Çevrimiçi yardıma git.", "Open online help."),
            ],
            examples=[
                ex(
                    "Örnekler",
                    "Examples",
                    "Get-Help Get-Service -Examples",
                    "Get-Service için örnekleri listeler.",
                    "Lists examples for Get-Service.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-command"],
        ),
    )
)

WINDOWS.append(
    (
        "processes/get-process.yaml",
        ps_cmd(
            id_="get-process",
            name="Get-Process",
            category="processes",
            summary=L(
                "Yerel süreçleri listeler (PowerShell).",
                "Lists local processes (PowerShell).",
            ),
            description=L(
                "Get-Process, çalışan süreçleri nesne olarak döndürür. Linux `ps` karşılığı "
                "değildir — ayrı kayıt. Windows’ta Task Manager / tasklist ile benzer amaç. "
                "PowerShell 7+ ve Windows PowerShell 5.1.",
                "Get-Process returns running processes as objects. Not a Linux ps alias — "
                "separate record. Similar intent to Task Manager / tasklist on Windows. "
                "PowerShell 7+ and Windows PowerShell 5.1.",
            ),
            tags=["powershell", "windows", "processes"],
            risk="safe",
            elevated=False,
            aliases=["gps", "ps"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-process"],
            flags=[
                flag("-Name", "Süreç adı.", "Process name.", takes_value=True, value_name="Name"),
                flag("-Id", "PID.", "Process id.", takes_value=True, value_name="Id"),
            ],
            examples=[
                ex(
                    "Ada göre",
                    "By name",
                    "Get-Process -Name explorer",
                    "explorer süreçlerini listeler.",
                    "Lists explorer processes.",
                    shell="powershell",
                    platforms=["windows"],
                ),
                ex(
                    "CPU sıralı",
                    "Sort by CPU",
                    "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
                    "CPU’ya göre ilk 10 süreç.",
                    "Top 10 processes by CPU.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-service", "stop-service"],
            intent={
                "tr": ["powershell süreç", "get-process", "çalışan process"],
                "en": ["powershell processes", "get-process", "list processes windows"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "system/get-service.yaml",
        ps_cmd(
            id_="get-service",
            name="Get-Service",
            category="system",
            summary=L(
                "Windows servislerini listeler / sorgular.",
                "Lists or queries Windows services.",
            ),
            description=L(
                "Get-Service, Service Control Manager üzerinden Windows servis durumunu "
                "gösterir. Linux systemctl karşılığı değildir. Servis değiştirmek için "
                "Start/Stop/Restart/Set-Service kullanılır; çoğu yazma işlemi yönetici (UAC) ister.",
                "Get-Service reports Windows service status via SCM. Not a systemctl alias. "
                "Use Start/Stop/Restart/Set-Service to change state; most write ops need "
                "Administrator (UAC).",
            ),
            tags=["powershell", "windows", "services"],
            risk="safe",
            elevated=False,
            aliases=["gsv"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-service"],
            flags=[
                flag("-Name", "Servis adı / joker.", "Service name / wildcard.", takes_value=True),
                flag("-DisplayName", "Görünen ad.", "Display name.", takes_value=True),
            ],
            examples=[
                ex(
                    "Tüm servisler",
                    "All services",
                    "Get-Service",
                    "Yerel servisleri listeler.",
                    "Lists local services.",
                    shell="powershell",
                    platforms=["windows"],
                ),
                ex(
                    "Ada göre",
                    "By name",
                    "Get-Service -Name wuauserv",
                    "Windows Update servis durumunu gösterir.",
                    "Shows Windows Update service status.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["start-service", "stop-service", "restart-service", "set-service", "sc"],
            intent={
                "tr": ["windows servis listele", "get-service", "servis durumu"],
                "en": ["list windows services", "get-service", "service status"],
            },
            concepts=["systemd"],
        ),
    )
)

WINDOWS.append(
    (
        "network/get-netipconfiguration.yaml",
        ps_cmd(
            id_="get-netipconfiguration",
            name="Get-NetIPConfiguration",
            category="network",
            summary=L(
                "Windows ağ IP yapılandırmasını gösterir.",
                "Show Windows network IP configuration.",
            ),
            description=L(
                "PowerShell NetTCPIP modülü cmdlet’i; Linux ip/ifconfig veya CMD ipconfig "
                "karşılığı değildir — ayrı kayıtlar. Tipik olarak Windows PowerShell 5.1 ve "
                "Windows üzerinde PowerShell 7+ ile kullanılır (NetTCPIP Windows’a özgüdür).",
                "PowerShell NetTCPIP cmdlet; not a Linux ip/ifconfig or CMD ipconfig alias — "
                "separate records. Typically used with Windows PowerShell 5.1 and PowerShell 7+ "
                "on Windows (NetTCPIP is Windows-specific).",
            ),
            tags=["powershell", "windows", "network"],
            risk="safe",
            elevated=False,
            aliases=["gip"],
            sources=["https://learn.microsoft.com/powershell/module/nettcpip/get-netipconfiguration"],
            examples=[
                ex(
                    "IP yapılandırması",
                    "IP configuration",
                    "Get-NetIPConfiguration",
                    "Yerel arabirim IP/DNS/gateway özetini listeler.",
                    "Lists local interface IP/DNS/gateway summary.",
                    shell="powershell",
                    platforms=["windows"],
                    privilege="none",
                ),
            ],
            related=["ipconfig", "get-nettcpconnection", "netsh"],
            intent={
                "tr": ["windows ip adresi", "ağ yapılandırması powershell"],
                "en": ["windows show ip", "powershell network configuration"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "network/get-nettcpconnection.yaml",
        ps_cmd(
            id_="get-nettcpconnection",
            name="Get-NetTCPConnection",
            category="network",
            summary=L(
                "Windows TCP bağlantılarını listeler.",
                "Lists Windows TCP connections.",
            ),
            description=L(
                "NetTCPIP Get-NetTCPConnection, yerel TCP dinleyicileri ve bağlantıları "
                "gösterir. Linux `ss`/`netstat` veya CMD `netstat` ile aynı komut değildir. "
                "Windows’a özgü NetTCPIP modülü gerektirir.",
                "Get-NetTCPConnection shows local TCP listeners and connections. Not the same "
                "command as Linux ss/netstat or CMD netstat. Requires the Windows NetTCPIP module.",
            ),
            tags=["powershell", "windows", "network", "tcp"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/nettcpip/get-nettcpconnection"],
            flags=[
                flag("-LocalPort", "Yerel port süz.", "Filter local port.", takes_value=True),
                flag("-State", "Listen/Established vb.", "Filter by state.", takes_value=True),
            ],
            examples=[
                ex(
                    "Dinleyen portlar",
                    "Listening ports",
                    "Get-NetTCPConnection -State Listen",
                    "Dinleme durumundaki TCP soketleri listeler.",
                    "Lists TCP sockets in Listen state.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-netipconfiguration", "netstat"],
            intent={
                "tr": ["windows tcp bağlantı", "dinleyen port powershell"],
                "en": ["windows tcp connections", "listening ports powershell"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "disks/get-disk.yaml",
        ps_cmd(
            id_="get-disk",
            name="Get-Disk",
            category="disks",
            summary=L(
                "Fiziksel diskleri listeler (Storage cmdlet).",
                "Lists physical disks (Storage cmdlet).",
            ),
            description=L(
                "Get-Disk, Windows Storage modülü ile fiziksel diskleri gösterir. Linux "
                "`lsblk` karşılığı değildir. Disk numarası ile Get-Partition/Get-Volume "
                "birlikte kullanılır. Yazma işlemleri yönetici ister; bu kayıt salt okuma odaklıdır.",
                "Get-Disk lists physical disks via the Windows Storage module. Not an lsblk "
                "alias. Often paired with Get-Partition/Get-Volume by disk number. Write ops "
                "need admin; this record focuses on read-only queries.",
            ),
            tags=["powershell", "windows", "disks", "storage"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/storage/get-disk"],
            examples=[
                ex(
                    "Diskleri listele",
                    "List disks",
                    "Get-Disk",
                    "Fiziksel disk numarası, boyutu ve sağlık bilgisini gösterir.",
                    "Shows physical disk number, size, and health.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-volume", "diskpart", "get-partition"],
            intent={
                "tr": ["windows disk listele", "get-disk"],
                "en": ["list windows disks", "get-disk"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "disks/get-volume.yaml",
        ps_cmd(
            id_="get-volume",
            name="Get-Volume",
            category="disks",
            summary=L(
                "Birimleri (volume) listeler — sürücü harfi / FS.",
                "Lists volumes — drive letter / filesystem.",
            ),
            description=L(
                "Get-Volume, Windows birimlerini (NTFS/ReFS vb.) gösterir. Linux `df` "
                "karşılığı değildir. Get-Disk ile birlikte depolama envanteri için kullanılır.",
                "Get-Volume lists Windows volumes (NTFS/ReFS, etc.). Not a df alias. Used with "
                "Get-Disk for storage inventory.",
            ),
            tags=["powershell", "windows", "disks", "volume"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/storage/get-volume"],
            examples=[
                ex(
                    "Birimleri listele",
                    "List volumes",
                    "Get-Volume",
                    "Sürücü harfi, dosya sistemi ve boş alanı listeler.",
                    "Lists drive letter, filesystem, and free space.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-disk", "chkdsk"],
        ),
    )
)

WINDOWS.append(
    (
        "system/get-computerinfo.yaml",
        ps_cmd(
            id_="get-computerinfo",
            name="Get-ComputerInfo",
            category="system",
            summary=L(
                "Windows sistem / donanım özet bilgisi.",
                "Windows system / hardware summary info.",
            ),
            description=L(
                "Get-ComputerInfo, işletim sistemi, BIOS ve donanım özetini bir nesnede "
                "toplar. Windows Server ve istemci sürümlerinde yönetim keşfi için kullanışlıdır. "
                "Linux `uname`/`hostnamectl` karşılığı değildir.",
                "Get-ComputerInfo aggregates OS, BIOS, and hardware summary into one object. "
                "Useful on Windows Server and client for inventory. Not a uname/hostnamectl alias.",
            ),
            tags=["powershell", "windows", "system", "inventory"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-computerinfo"],
            examples=[
                ex(
                    "Özet",
                    "Summary",
                    "Get-ComputerInfo | Select-Object WindowsProductName, OsVersion, CsProcessors",
                    "Ürün adı, OS sürümü ve işlemci özetini seçer.",
                    "Selects product name, OS version, and CPU summary.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["system-profiler", "get-winevent"],
            intent={
                "tr": ["windows sistem bilgisi", "get-computerinfo"],
                "en": ["windows system info", "get-computerinfo"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "monitoring/get-winevent.yaml",
        ps_cmd(
            id_="get-winevent",
            name="Get-WinEvent",
            category="monitoring",
            summary=L(
                "Windows Olay Günlüğü kayıtlarını sorgular.",
                "Queries Windows Event Log records.",
            ),
            description=L(
                "Get-WinEvent, Event Viewer / Windows Event Log kanallarını PowerShell ile "
                "okur. Linux journalctl karşılığı değildir. Geniş sorgular yavaş olabilir; "
                "FilterHashtable tercih edin. Bazı kanallar yönetici hakkı ister.",
                "Get-WinEvent reads Event Viewer / Windows Event Log channels from PowerShell. "
                "Not a journalctl alias. Prefer FilterHashtable for performance. Some channels "
                "require Administrator.",
            ),
            tags=["powershell", "windows", "logs", "events"],
            risk="caution",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.diagnostics/get-winevent"],
            security={
                "notes": L(
                    "Güvenlik günlüğü gibi kanallar için yükseltilmiş kabuk (UAC) gerekebilir.",
                    "Elevated shell (UAC) may be required for channels such as Security.",
                ),
                "requires_admin": False,
                "uac_prompt": False,
            },
            flags=[
                flag("-LogName", "Kanal adı (System, Application…).", "Log channel name.", takes_value=True),
                flag("-MaxEvents", "En fazla olay sayısı.", "Maximum events.", takes_value=True),
                flag("-FilterHashtable", "Süzgeç hash tablosu.", "Filter hashtable.", takes_value=True),
            ],
            examples=[
                ex(
                    "Son System olayları",
                    "Recent System events",
                    "Get-WinEvent -LogName System -MaxEvents 20",
                    "System kanalından son 20 olayı getirir.",
                    "Fetches the latest 20 System-channel events.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["wevtutil", "journalctl"],
            intent={
                "tr": ["windows olay günlüğü", "get-winevent", "event viewer"],
                "en": ["windows event log", "get-winevent", "event viewer powershell"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "filesystem/get-childitem.yaml",
        ps_cmd(
            id_="get-childitem",
            name="Get-ChildItem",
            category="filesystem",
            summary=L(
                "Dizin içeriğini listeler (PowerShell).",
                "Lists directory contents (PowerShell).",
            ),
            description=L(
                "Get-ChildItem dosya/klasör listeler; `dir`/`ls` alias’ları PowerShell içindedir. "
                "CMD `dir` ve Linux `ls` ayrı kayıtlardır — bayraklar birebir değildir. "
                "Gizli/sistem öğeleri için -Force.",
                "Get-ChildItem lists files/folders; dir/ls are PowerShell aliases. CMD dir and "
                "Linux ls are separate records — flags are not 1:1. Use -Force for hidden/system items.",
            ),
            tags=["powershell", "windows", "filesystem"],
            risk="safe",
            elevated=False,
            aliases=["gci", "ls", "dir"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-childitem"],
            flags=[
                flag("-Recurse", "Alt dizinlere in.", "Recurse into children."),
                flag("-Force", "Gizli öğeleri de göster.", "Include hidden items."),
                flag("-Filter", "Sağlayıcı süzgeci.", "Provider filter.", takes_value=True),
            ],
            examples=[
                ex(
                    "Listele",
                    "List",
                    "Get-ChildItem -Path C:\\Windows -Filter *.exe",
                    "Belirtilen yolda exe süzgeçli liste.",
                    "Lists matching exe files under the path.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-item", "get-content", "get-itemproperty"],
        ),
    )
)

WINDOWS.append(
    (
        "filesystem/get-content.yaml",
        ps_cmd(
            id_="get-content",
            name="Get-Content",
            category="filesystem",
            summary=L(
                "Dosya içeriğini okur (PowerShell).",
                "Reads file content (PowerShell).",
            ),
            description=L(
                "Get-Content satır satır veya ham içerik okur (`cat`/`type` alias). Linux "
                "`cat` ve CMD `type` ayrı kayıtlardır. Büyük dosyalarda -TotalCount / -Tail kullanın.",
                "Get-Content reads line-oriented or raw content (cat/type aliases). Linux cat "
                "and CMD type are separate records. Prefer -TotalCount / -Tail for large files.",
            ),
            tags=["powershell", "windows", "filesystem", "text"],
            risk="safe",
            elevated=False,
            aliases=["gc", "cat", "type"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-content"],
            flags=[
                flag("-TotalCount", "İlk N satır.", "First N lines.", takes_value=True),
                flag("-Tail", "Son N satır.", "Last N lines.", takes_value=True),
                flag("-Raw", "Tek dize olarak oku.", "Read as a single string."),
            ],
            examples=[
                ex(
                    "Son satırlar",
                    "Tail lines",
                    "Get-Content -Path C:\\log.txt -Tail 50",
                    "Dosyanın son 50 satırını basar.",
                    "Prints the last 50 lines of the file.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-childitem", "get-item", "cat"],
        ),
    )
)

WINDOWS.append(
    (
        "filesystem/get-item.yaml",
        ps_cmd(
            id_="get-item",
            name="Get-Item",
            category="filesystem",
            summary=L(
                "Belirtilen yolu (dosya/klasör) nesne olarak alır.",
                "Gets the item at a path as an object.",
            ),
            description=L(
                "Get-Item tek bir öğeyi (dosya, dizin, kayıt defteri anahtarı vb. sağlayıcı "
                "yolu) döndürür. Get-ChildItem alt öğeleri listeler; karıştırmayın.",
                "Get-Item returns a single item (file, directory, registry key, etc.). "
                "Get-ChildItem lists children — do not confuse them.",
            ),
            tags=["powershell", "windows", "filesystem"],
            risk="safe",
            elevated=False,
            aliases=["gi"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-item"],
            examples=[
                ex(
                    "Dosya nesnesi",
                    "File object",
                    "Get-Item -Path C:\\Windows\\System32\\notepad.exe",
                    "Dosya meta verisini nesne olarak döndürür.",
                    "Returns file metadata as an object.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["get-childitem", "get-itemproperty"],
        ),
    )
)

WINDOWS.append(
    (
        "filesystem/get-itemproperty.yaml",
        ps_cmd(
            id_="get-itemproperty",
            name="Get-ItemProperty",
            category="filesystem",
            summary=L(
                "Öğe özelliklerini (kayıt defteri değerleri vb.) okur.",
                "Gets item properties (e.g. registry values).",
            ),
            description=L(
                "Get-ItemProperty sağlayıcı özelliklerini okur; Windows’ta sıkça kayıt "
                "defteri değerleri için kullanılır. Yazma için Set-ItemProperty (ayrı kayıt "
                "olabilir) — yanlış anahtar sistem davranışını bozar.",
                "Get-ItemProperty reads provider properties; on Windows often used for registry "
                "values. Writing uses Set-ItemProperty — wrong keys can break the system.",
            ),
            tags=["powershell", "windows", "registry"],
            risk="caution",
            elevated=False,
            aliases=["gp"],
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-itemproperty"],
            examples=[
                ex(
                    "Kayıt değeri oku",
                    "Read registry value",
                    "Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' | Select-Object ProductName",
                    "Ürün adını kayıt defterinden okur (salt okuma).",
                    "Reads product name from the registry (read-only).",
                    shell="powershell",
                    platforms=["windows"],
                    risk="caution",
                ),
            ],
            related=["get-item", "get-childitem"],
            security={
                "notes": L(
                    "HKLM okuma çoğu durumda normal kullanıcıyla çalışır; yazma işlemleri UAC ister.",
                    "HKLM reads often work as a normal user; writes require UAC elevation.",
                ),
            },
        ),
    )
)

WINDOWS.append(
    (
        "security/get-executionpolicy.yaml",
        ps_cmd(
            id_="get-executionpolicy",
            name="Get-ExecutionPolicy",
            category="security",
            summary=L(
                "PowerShell betik yürütme ilkesini gösterir.",
                "Shows the PowerShell script execution policy.",
            ),
            description=L(
                "Get-ExecutionPolicy, betiklerin nasıl çalıştırılacağını kontrol eden "
                "ExecutionPolicy değerini gösterir. Set-ExecutionPolicy değiştirir ve "
                "yönetici / grup ilkesi etkisi olabilir — bu kayıt salt okuma odaklıdır. "
                "PowerShell 7+ ile Windows PowerShell 5.1 kapsamları farklı olabilir "
                "(CurrentUser vs MachinePolicy).",
                "Get-ExecutionPolicy reports how scripts may run. Set-ExecutionPolicy changes "
                "it and may need admin / be overridden by Group Policy — this record is "
                "read-focused. PowerShell 7+ vs Windows PowerShell 5.1 scopes can differ "
                "(CurrentUser vs MachinePolicy).",
            ),
            tags=["powershell", "windows", "security", "policy"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/microsoft.powershell.security/get-executionpolicy"],
            flags=[
                flag("-List", "Tüm kapsamları listele.", "List all scopes."),
            ],
            examples=[
                ex(
                    "İlke listesi",
                    "List policies",
                    "Get-ExecutionPolicy -List",
                    "Kapsam bazında ExecutionPolicy değerlerini gösterir.",
                    "Shows ExecutionPolicy values by scope.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            intent={
                "tr": ["execution policy", "powershell betik izni"],
                "en": ["execution policy", "powershell script policy"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "system/get-scheduledtask.yaml",
        ps_cmd(
            id_="get-scheduledtask",
            name="Get-ScheduledTask",
            category="system",
            summary=L(
                "Zamanlanmış görevleri listeler (Task Scheduler).",
                "Lists scheduled tasks (Task Scheduler).",
            ),
            description=L(
                "Get-ScheduledTask, Windows Görev Zamanlayıcı görevlerini listeler. "
                "`schtasks.exe` ayrı bir executable kaydıdır. Görev oluşturma/silme yönetici "
                "gerektirebilir; bu kayıt sorgu odaklıdır.",
                "Get-ScheduledTask lists Windows Task Scheduler tasks. schtasks.exe is a "
                "separate executable record. Creating/deleting tasks may need admin; this "
                "record is query-focused.",
            ),
            tags=["powershell", "windows", "scheduler"],
            risk="safe",
            elevated=False,
            sources=["https://learn.microsoft.com/powershell/module/scheduledtasks/get-scheduledtask"],
            examples=[
                ex(
                    "Görevleri listele",
                    "List tasks",
                    "Get-ScheduledTask | Select-Object TaskName, State",
                    "Görev adı ve durumunu listeler.",
                    "Lists task name and state.",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["schtasks"],
        ),
    )
)

for id_, name, summary_tr, summary_en, risk, desc_extra_tr, desc_extra_en, src in [
    (
        "start-service",
        "Start-Service",
        "Windows servisini başlatır.",
        "Starts a Windows service.",
        "caution",
        "Yönetici (UAC) gerekir. Get-Service ile durumu doğrulayın.",
        "Requires Administrator (UAC). Verify state with Get-Service.",
        "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/start-service",
    ),
    (
        "stop-service",
        "Stop-Service",
        "Windows servisini durdurur.",
        "Stops a Windows service.",
        "dangerous",
        "Kritik servisleri durdurmak oturumu veya rolleri bozabilir. UAC gerekir.",
        "Stopping critical services can break sessions or roles. UAC required.",
        "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/stop-service",
    ),
    (
        "restart-service",
        "Restart-Service",
        "Windows servisini yeniden başlatır.",
        "Restarts a Windows service.",
        "dangerous",
        "Kısa kesinti yaratır. Yönetici (UAC) gerekir.",
        "Causes a brief outage. Requires Administrator (UAC).",
        "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/restart-service",
    ),
    (
        "set-service",
        "Set-Service",
        "Windows servis özelliklerini değiştirir.",
        "Changes Windows service properties.",
        "dangerous",
        "Başlangıç türü vb. değiştirir; yanlış yapılandırma kalıcı etki yapar. UAC gerekir.",
        "Changes startup type etc.; misconfiguration persists. UAC required.",
        "https://learn.microsoft.com/powershell/module/microsoft.powershell.management/set-service",
    ),
]:
    WINDOWS.append(
        (
            f"system/{id_}.yaml",
            ps_cmd(
                id_=id_,
                name=name,
                category="system",
                summary=L(summary_tr, summary_en),
                description=L(
                    f"{name}, Service Control Manager üzerinden servis durumunu/özelliklerini "
                    f"değiştirir. Linux systemctl karşılığı değildir. {desc_extra_tr}",
                    f"{name} changes service state/properties via SCM. Not a systemctl alias. "
                    f"{desc_extra_en}",
                ),
                tags=["powershell", "windows", "services", "admin"],
                risk=risk,
                elevated=True,
                sources=[src],
                security={
                    "notes": L(
                        "Yükseltilmiş PowerShell oturumu (UAC onayı) gerekir.",
                        "Requires an elevated PowerShell session (UAC prompt).",
                    ),
                    "requires_admin": True,
                    "uac_prompt": True,
                },
                examples=[
                    ex(
                        "Güvenli örnek (ad değiştirin)",
                        "Safe example (change name)",
                        f"{name} -Name Spooler -WhatIf"
                        if name != "Set-Service"
                        else "Set-Service -Name Spooler -StartupType Manual -WhatIf",
                        "WhatIf ile etkiyi simüle eder; gerçek değişiklik yapmaz.",
                        "Simulates the effect with -WhatIf; makes no real change.",
                        risk="safe",
                        elevated=True,
                        shell="powershell",
                        platforms=["windows"],
                        privilege="admin",
                    ),
                ],
                related=["get-service", "sc"],
                concepts=["systemd"],
            ),
        )
    )

# --- Windows executables / CMD-oriented tools (separate from cmdlets) ---

WINDOWS.append(
    (
        "network/ipconfig.yaml",
        win_exe(
            id_="ipconfig",
            name="ipconfig",
            category="network",
            kind="executable",
            summary=L(
                "CMD/Windows IP yapılandırmasını gösterir.",
                "Shows CMD/Windows IP configuration.",
            ),
            description=L(
                "ipconfig.exe, cmd.exe ve PowerShell’den çağrılabilen klasik Windows "
                "ağ yapılandırma aracısıdır. PowerShell `Get-NetIPConfiguration` ve Linux "
                "`ip` ayrı kayıtlardır — bayraklar eşdeğer değildir. `/release` `/renew` "
                "DHCP’yi etkiler.",
                "ipconfig.exe is the classic Windows IP config tool callable from cmd.exe "
                "and PowerShell. PowerShell Get-NetIPConfiguration and Linux ip are separate "
                "records — flags are not equivalent. /release and /renew affect DHCP.",
            ),
            tags=["windows", "cmd", "network"],
            risk="caution",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/ipconfig"],
            flags=[
                flag("/all", "Ayrıntılı yapılandırma.", "Detailed configuration."),
                flag("/flushdns", "DNS çözümleyici önbelleğini temizle.", "Flush DNS resolver cache."),
                flag("/release", "DHCP adresini bırak (etki).", "Release DHCP address (side effect)."),
                flag("/renew", "DHCP yenile (etki).", "Renew DHCP (side effect)."),
            ],
            examples=[
                ex(
                    "Ayrıntılı bilgi",
                    "Detailed info",
                    "ipconfig /all",
                    "Tüm arabirimler için ayrıntılı IP/DNS bilgisini basar.",
                    "Prints detailed IP/DNS info for all interfaces.",
                    shell="cmd",
                    platforms=["windows"],
                    privilege="none",
                ),
            ],
            related=["get-netipconfiguration", "netsh", "route"],
            intent={
                "tr": ["ipconfig", "windows ip", "cmd ip adresi"],
                "en": ["ipconfig", "windows ip", "cmd show ip"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "network/netstat.yaml",
        win_exe(
            id_="netstat",
            name="netstat",
            category="network",
            summary=L(
                "Windows TCP/UDP bağlantı ve dinleme tablosu.",
                "Windows TCP/UDP connection and listening table.",
            ),
            description=L(
                "netstat.exe bağlantı istatistiklerini listeler. Linux netstat/ss ve "
                "PowerShell Get-NetTCPConnection ayrı kayıtlardır. `-b` yönetici ister.",
                "netstat.exe lists connection statistics. Linux netstat/ss and PowerShell "
                "Get-NetTCPConnection are separate records. -b requires elevation.",
            ),
            tags=["windows", "network", "tcp"],
            risk="safe",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/netstat"],
            flags=[
                flag("-an", "Sayısal adres/port, tüm bağlantılar.", "Numeric addresses/ports, all connections."),
                flag("-b", "Yürütülebilir adı (yönetici).", "Owning executable (admin).", ),
            ],
            examples=[
                ex(
                    "Dinleyen portlar",
                    "Listening ports",
                    "netstat -an | findstr LISTENING",
                    "Dinleme durumundaki soketleri süzgeçler (CMD).",
                    "Filters sockets in LISTENING state (CMD).",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["get-nettcpconnection", "netsh"],
            security={
                "notes": L(
                    "`netstat -b` için yükseltilmiş kabuk (UAC) gerekir.",
                    "`netstat -b` requires an elevated shell (UAC).",
                ),
                "requires_admin": False,
                "uac_prompt": True,
            },
        ),
    )
)

WINDOWS.append(
    (
        "network/netsh.yaml",
        win_exe(
            id_="netsh",
            name="netsh",
            category="network",
            kind="administrative_tool",
            summary=L(
                "Windows ağ yığını yapılandırma kabuğu.",
                "Windows networking stack configuration shell.",
            ),
            description=L(
                "netsh, arabirim, güvenlik duvarı, WLAN ve diğer ağ bağlamlarını yönetir. "
                "Yazma komutları yönetici (UAC) ister. Salt okuma örnekleri tercih edilir; "
                "yanlış bağlam sistemi ağdan düşürebilir.",
                "netsh manages interface, firewall, WLAN, and other networking contexts. "
                "Write commands need Administrator (UAC). Prefer read-only examples; wrong "
                "context can drop connectivity.",
            ),
            tags=["windows", "network", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/netsh"],
            security={
                "notes": L(
                    "Yapılandırma değişiklikleri UAC yükseltmesi ister; üretimde dikkat.",
                    "Configuration changes require UAC elevation; use care in production.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Arabirimleri göster",
                    "Show interfaces",
                    "netsh interface show interface",
                    "Ağ arabirimlerini salt okuma listeler.",
                    "Lists network interfaces read-only.",
                    risk="safe",
                    elevated=False,
                    shell="cmd",
                    platforms=["windows"],
                    privilege="none",
                ),
            ],
            related=["ipconfig", "route", "get-netipconfiguration"],
        ),
    )
)

WINDOWS.append(
    (
        "network/route.yaml",
        win_exe(
            id_="route",
            name="route",
            category="network",
            summary=L(
                "Windows IPv4 yönlendirme tablosu aracı.",
                "Windows IPv4 routing table tool.",
            ),
            description=L(
                "route.exe yönlendirme tablosunu gösterir veya değiştirir. `route print` "
                "salt okumadır; add/delete yönetici ister. Linux `ip route` ayrı kayıttır.",
                "route.exe displays or modifies the routing table. route print is read-only; "
                "add/delete need admin. Linux ip route is a separate record.",
            ),
            tags=["windows", "network", "routing"],
            risk="dangerous",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/route"],
            flags=[
                flag("print", "Tabloyu yazdır (alt komut).", "Print table (subcommand)."),
                flag("add", "Rota ekle (yönetici).", "Add route (admin)."),
                flag("delete", "Rota sil (yönetici).", "Delete route (admin)."),
            ],
            examples=[
                ex(
                    "Tabloyu yazdır",
                    "Print table",
                    "route print",
                    "IPv4/IPv6 yönlendirme tablosunu basar.",
                    "Prints the IPv4/IPv6 routing table.",
                    risk="safe",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["netsh", "ipconfig"],
            security={
                "notes": L(
                    "Rota ekleme/silme UAC yükseltmesi ister.",
                    "Adding/deleting routes requires UAC elevation.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
        ),
    )
)

WINDOWS.append(
    (
        "system/sc.yaml",
        win_exe(
            id_="sc",
            name="sc.exe",
            category="system",
            kind="administrative_tool",
            summary=L(
                "Service Control — Windows servis yönetimi (executable).",
                "Service Control — Windows service management (executable).",
            ),
            description=L(
                "sc.exe, cmd.exe’den servis sorgu/denetimi yapar. PowerShell Get-Service / "
                "Start-Service ayrı kayıtlardır. PowerShell’de `sc` alias’ı Set-Content’tir — "
                "mutlaka `sc.exe` çağırın. Yazma işlemleri yönetici (UAC) ister.",
                "sc.exe queries/controls services from cmd.exe. PowerShell Get-Service / "
                "Start-Service are separate records. In PowerShell, sc aliases Set-Content — "
                "always invoke sc.exe. Write ops need Administrator (UAC).",
            ),
            tags=["windows", "services", "cmd", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/sc-query"],
            security={
                "notes": L(
                    "Servis değiştirme UAC ister. PowerShell’de sc ≠ sc.exe.",
                    "Changing services needs UAC. In PowerShell sc ≠ sc.exe.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Servis sorgula",
                    "Query service",
                    "sc.exe query wuauserv",
                    "Windows Update servis durumunu sorgular (salt okuma).",
                    "Queries Windows Update service status (read-only).",
                    risk="safe",
                    elevated=False,
                    shell="cmd",
                    platforms=["windows"],
                    privilege="none",
                ),
            ],
            related=["get-service", "start-service", "stop-service"],
            intent={
                "tr": ["sc.exe", "windows servis cmd", "servis sorgula"],
                "en": ["sc.exe", "windows service cmd", "query service"],
            },
        ),
    )
)

WINDOWS.append(
    (
        "filesystem/robocopy.yaml",
        win_exe(
            id_="robocopy",
            name="robocopy",
            category="filesystem",
            summary=L(
                "Sağlam Windows dosya kopyalama aracı.",
                "Robust Windows file copy utility.",
            ),
            description=L(
                "robocopy, büyük/özellikli kopyalar için tasarlanmıştır. Linux rsync "
                "karşılığı değildir. Yanlış /MIR hedefi dosya silebilir — dikkat.",
                "robocopy is built for large/attribute-aware copies. Not an rsync alias. "
                "Wrong /MIR targets can delete files — use care.",
            ),
            tags=["windows", "filesystem", "copy"],
            risk="dangerous",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/robocopy"],
            flags=[
                flag("/E", "Boş dahil alt dizinler.", "Subdirs including empty."),
                flag("/MIR", "Ayna (fazla dosyaları siler — tehlikeli).", "Mirror (deletes extras — dangerous)."),
                flag("/L", "Listele, kopyalama (kuru koşu).", "List only, no copy (dry run)."),
            ],
            examples=[
                ex(
                    "Kuru koşu",
                    "Dry run",
                    "robocopy C:\\src D:\\dst /E /L",
                    "Ne kopyalanacağını listeler; yazmaz.",
                    "Lists what would be copied; writes nothing.",
                    risk="safe",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["rsync", "icacls"],
        ),
    )
)

WINDOWS.append(
    (
        "users/icacls.yaml",
        win_exe(
            id_="icacls",
            name="icacls",
            category="users",
            summary=L(
                "NTFS ACL görüntüleme ve düzenleme.",
                "Display and edit NTFS ACLs.",
            ),
            description=L(
                "icacls, Windows NTFS izinlerini gösterir/değiştirir. Linux chmod/chown "
                "modeli değildir. Yanlış /grant veya /reset erişimi kilitleyebilir; "
                "yönetici gerekebilir.",
                "icacls displays/changes Windows NTFS permissions. Not the Linux chmod/chown "
                "model. Wrong /grant or /reset can lock you out; admin may be required.",
            ),
            tags=["windows", "acl", "ntfs", "permissions"],
            risk="dangerous",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/icacls"],
            security={
                "notes": L(
                    "Sistem yollarında değişiklik UAC ister; yedek ACL alın.",
                    "Changing ACLs on system paths needs UAC; back up ACLs first.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "ACL göster",
                    "Show ACL",
                    "icacls C:\\Users\\Public",
                    "Dizin ACL’sini salt okuma listeler.",
                    "Lists the directory ACL read-only.",
                    risk="safe",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["takeown", "chmod"],
        ),
    )
)

WINDOWS.append(
    (
        "users/takeown.yaml",
        win_exe(
            id_="takeown",
            name="takeown",
            category="users",
            summary=L(
                "Dosya/klasör sahipliğini alır.",
                "Takes ownership of a file or folder.",
            ),
            description=L(
                "takeown, nesne sahipliğini mevcut kullanıcıya geçirir; ardından icacls "
                "gerekebilir. Sistem dosyalarında tehlikelidir — yönetici (UAC) ister.",
                "takeown assigns ownership to the current user; icacls may still be needed. "
                "Dangerous on system files — requires Administrator (UAC).",
            ),
            tags=["windows", "acl", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/takeown"],
            security={
                "notes": L(
                    "Sahiplik değişimi UAC ister; OS dosyalarında kullanmayın.",
                    "Ownership changes need UAC; avoid on OS files.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Yardım",
                    "Help",
                    "takeown /?",
                    "Sözdizimini gösterir; sahiplik değiştirmez.",
                    "Shows syntax; does not change ownership.",
                    risk="safe",
                    elevated=False,
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["icacls"],
        ),
    )
)

WINDOWS.append(
    (
        "system/schtasks.yaml",
        win_exe(
            id_="schtasks",
            name="schtasks",
            category="system",
            summary=L(
                "Görev Zamanlayıcı komut satırı (executable).",
                "Task Scheduler command line (executable).",
            ),
            description=L(
                "schtasks.exe görev oluşturur/sorgular/siler. PowerShell Get-ScheduledTask "
                "ayrı kayıttır. Değişiklikler çoğu ortamda yönetici ister.",
                "schtasks.exe creates/queries/deletes tasks. PowerShell Get-ScheduledTask is "
                "a separate record. Changes usually need admin.",
            ),
            tags=["windows", "scheduler", "cmd"],
            risk="dangerous",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/schtasks"],
            examples=[
                ex(
                    "Görevleri listele",
                    "List tasks",
                    "schtasks /Query /FO LIST",
                    "Zamanlanmış görevleri listeler (salt okuma).",
                    "Lists scheduled tasks (read-only).",
                    risk="safe",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["get-scheduledtask"],
            security={
                "notes": L(
                    "Görev oluşturma/silme UAC gerektirebilir.",
                    "Creating/deleting tasks may require UAC.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
        ),
    )
)

WINDOWS.append(
    (
        "monitoring/wevtutil.yaml",
        win_exe(
            id_="wevtutil",
            name="wevtutil",
            category="monitoring",
            summary=L(
                "Windows Event Log komut satırı aracı.",
                "Windows Event Log command-line tool.",
            ),
            description=L(
                "wevtutil.exe olay günlüklerini sorgular/dışa aktarır. PowerShell "
                "Get-WinEvent ayrı kayıttır. cl (clear) yıkıcıdır — örneklerde yok.",
                "wevtutil.exe queries/exports event logs. PowerShell Get-WinEvent is separate. "
                "cl (clear) is destructive — omitted from examples.",
            ),
            tags=["windows", "logs", "events"],
            risk="caution",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/wevtutil"],
            examples=[
                ex(
                    "Kanalları listele",
                    "List channels",
                    "wevtutil el",
                    "Olay günlüğü kanal adlarını listeler.",
                    "Lists event log channel names.",
                    risk="safe",
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["get-winevent"],
        ),
    )
)

WINDOWS.append(
    (
        "disks/chkdsk.yaml",
        win_exe(
            id_="chkdsk",
            name="chkdsk",
            category="disks",
            kind="administrative_tool",
            summary=L(
                "NTFS/FAT birim bütünlüğü denetimi.",
                "NTFS/FAT volume integrity check.",
            ),
            description=L(
                "chkdsk dosya sistemi hatalarını tarar; `/f` onarım yapar ve birimi "
                "kilitleyebilir. Linux fsck karşılığı değildir. Üretimde yedek ve bakım penceresi.",
                "chkdsk scans filesystem errors; /f repairs and may lock the volume. Not an "
                "fsck alias. Use backups and a maintenance window in production.",
            ),
            tags=["windows", "disks", "ntfs", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/chkdsk"],
            security={
                "notes": L(
                    "Onarım için yönetici ve çoğu zaman yeniden başlatma gerekir.",
                    "Repair needs admin and often a reboot.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Salt okuma tarama",
                    "Read-only scan",
                    "chkdsk C:",
                    "C: birimini onarmadan tarar (yine de yük bindirir).",
                    "Scans C: without fixing (still I/O heavy).",
                    risk="caution",
                    elevated=True,
                    shell="cmd",
                    platforms=["windows"],
                    privilege="admin",
                ),
            ],
            related=["sfc", "dism", "get-volume"],
        ),
    )
)

WINDOWS.append(
    (
        "system/sfc.yaml",
        win_exe(
            id_="sfc",
            name="sfc",
            category="system",
            kind="administrative_tool",
            summary=L(
                "Sistem Dosyası Denetleyicisi (Windows).",
                "System File Checker (Windows).",
            ),
            description=L(
                "sfc.exe korunan sistem dosyalarını tarar/onarır. `/scannow` uzun sürer ve "
                "yönetici ister. DISM ile birlikte kullanılır; diskpart ile karıştırmayın.",
                "sfc.exe scans/repairs protected system files. /scannow is long-running and "
                "needs admin. Often paired with DISM; do not confuse with diskpart.",
            ),
            tags=["windows", "system", "repair", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/sfc"],
            security={
                "notes": L(
                    "Yükseltilmiş CMD/PowerShell (UAC) zorunlu.",
                    "Elevated CMD/PowerShell (UAC) required.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            flags=[
                flag("/scannow", "Tara ve onarmaya çalış.", "Scan and attempt repairs."),
                flag("/verifyonly", "Onarmadan doğrula.", "Verify without repairing."),
            ],
            examples=[
                ex(
                    "Yardım",
                    "Help",
                    "sfc /?",
                    "Sözdizimini gösterir.",
                    "Shows syntax.",
                    risk="safe",
                    elevated=False,
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["dism", "chkdsk"],
        ),
    )
)

WINDOWS.append(
    (
        "system/dism.yaml",
        win_exe(
            id_="dism",
            name="DISM",
            category="system",
            kind="administrative_tool",
            summary=L(
                "Deployment Image Servicing and Management.",
                "Deployment Image Servicing and Management.",
            ),
            description=L(
                "DISM, Windows imajlarını ve çevrimiçi bileşen deposunu yönetir. "
                "`/Cleanup-Image /RestoreHealth` onarım için yaygındır; yönetici ister. "
                "Yanlış imaj yolu sistemi bozabilir.",
                "DISM services Windows images and the online component store. "
                "/Cleanup-Image /RestoreHealth is a common repair path; needs admin. "
                "Wrong image paths can damage the system.",
            ),
            tags=["windows", "system", "image", "admin"],
            risk="dangerous",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-hardware/manufacture/desktop/what-is-dism"],
            security={
                "notes": L(
                    "UAC yükseltmesi zorunlu; online onarım uzun sürer.",
                    "UAC elevation required; online repair takes time.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Bileşen deposu sağlığı (bilgi)",
                    "Component store health (info)",
                    "DISM /Online /Cleanup-Image /CheckHealth",
                    "Depo bozulma işaretini kontrol eder (düşük etkili).",
                    "Checks for component-store corruption flags (low impact).",
                    risk="caution",
                    elevated=True,
                    shell="cmd",
                    platforms=["windows"],
                    privilege="admin",
                ),
            ],
            related=["sfc", "chkdsk"],
        ),
    )
)

WINDOWS.append(
    (
        "disks/diskpart.yaml",
        win_exe(
            id_="diskpart",
            name="diskpart",
            category="disks",
            kind="administrative_tool",
            summary=L(
                "Etkileşimli disk bölümleme aracı (yıkıcı olabilir).",
                "Interactive disk partitioning tool (can be destructive).",
            ),
            description=L(
                "diskpart.exe bölüm/disk yönetir. `clean` / yanlış disk numarası veri "
                "kaybına yol açar. PowerShell Get-Disk ayrı kayıttır. Bu bankada yıkıcı "
                "örnek yok — yalnız list.",
                "diskpart.exe manages disks/partitions. clean / wrong disk numbers cause data "
                "loss. PowerShell Get-Disk is separate. No destructive examples here — list only.",
            ),
            tags=["windows", "disks", "partition", "admin"],
            risk="destructive",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/diskpart"],
            security={
                "notes": L(
                    "Yönetici gerekir. Yanlış disk seçimi yıkıcıdır — list disk ile doğrulayın.",
                    "Admin required. Wrong disk selection is destructive — verify with list disk.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "Yardım (etkileşimsiz)",
                    "Help (non-interactive)",
                    "diskpart /?",
                    "Kullanım bilgisini gösterir; diske yazmaz.",
                    "Shows usage; does not write to disks.",
                    risk="safe",
                    elevated=False,
                    shell="cmd",
                    platforms=["windows"],
                ),
            ],
            related=["get-disk", "get-volume", "bcdedit"],
        ),
    )
)

WINDOWS.append(
    (
        "system/bcdedit.yaml",
        win_exe(
            id_="bcdedit",
            name="bcdedit",
            category="system",
            kind="administrative_tool",
            summary=L(
                "Önyükleme Yapılandırma Verisi (BCD) düzenleyicisi.",
                "Boot Configuration Data (BCD) editor.",
            ),
            description=L(
                "bcdedit önyükleme girdilerini görüntüler/değiştirir. Yanlış değişiklik "
                "sistemi açılmaz hale getirebilir. Yönetici gerekir; bu kayıtta salt "
                "görüntüleme örneği vardır.",
                "bcdedit displays/modifies boot entries. Wrong edits can make the system "
                "unbootable. Admin required; this record only shows a display example.",
            ),
            tags=["windows", "boot", "admin"],
            risk="destructive",
            elevated=True,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=["https://learn.microsoft.com/windows-server/administration/windows-commands/bcdedit"],
            security={
                "notes": L(
                    "BCD yazma UAC ister; değişiklik öncesi `bcdedit /export` yedeği alın.",
                    "BCD writes need UAC; take a bcdedit /export backup first.",
                ),
                "requires_admin": True,
                "uac_prompt": True,
            },
            examples=[
                ex(
                    "BCD özeti",
                    "BCD summary",
                    "bcdedit /enum",
                    "Önyükleme girdilerini listeler (yazmaz).",
                    "Lists boot entries (does not write).",
                    risk="caution",
                    elevated=True,
                    shell="cmd",
                    platforms=["windows"],
                    privilege="admin",
                ),
            ],
            related=["diskpart", "bootctl"],
        ),
    )
)

WINDOWS.append(
    (
        "packages/winget.yaml",
        win_exe(
            id_="winget",
            name="winget",
            category="packages",
            kind="package_manager",
            summary=L(
                "Windows Paket Yöneticisi (WinGet) CLI.",
                "Windows Package Manager (WinGet) CLI.",
            ),
            description=L(
                "winget, Microsoft’un Windows paket yöneticisidir. Chocolatey/Scoop ayrı "
                "kayıtlardır (henüz bankada olmayabilir). Kurulum/upgrade yönetici veya "
                "kullanıcı kapsamına göre değişir. Arch/pacman ile ilişkisi yoktur.",
                "winget is Microsoft’s Windows package manager. Chocolatey/Scoop are separate "
                "records (may not be in the bank yet). Install/upgrade elevation depends on "
                "scope. Unrelated to Arch/pacman.",
            ),
            tags=["windows", "packages", "winget"],
            risk="caution",
            elevated=False,
            shells=["cmd", "powershell", "windows-powershell"],
            sources=[
                "https://learn.microsoft.com/windows/package-manager/winget/",
                "https://learn.microsoft.com/windows/package-manager/winget/install",
            ],
            package_refs=[
                {
                    "manager": "winget",
                    "package": "Microsoft.AppInstaller",
                    "distributions": ["windows-10", "windows-11", "windows-server"],
                    "notes": L(
                        "App Installer / WinGet ile gelir; sürümler Windows’a göre değişir.",
                        "Ships via App Installer / WinGet; versions vary by Windows edition.",
                    ),
                }
            ],
            flags=[
                flag("search", "Depoda ara (alt komut).", "Search repository (subcommand)."),
                flag("install", "Paket kur (alt komut).", "Install package (subcommand)."),
                flag("upgrade", "Paket yükselt.", "Upgrade package."),
                flag("list", "Kurulu paketleri listele.", "List installed packages."),
                flag("show", "Paket ayrıntısı.", "Show package details."),
            ],
            examples=[
                ex(
                    "Ara",
                    "Search",
                    "winget search vscode",
                    "vscode ile eşleşen paketleri arar.",
                    "Searches packages matching vscode.",
                    risk="safe",
                    shell="powershell",
                    platforms=["windows"],
                ),
                ex(
                    "Listele",
                    "List",
                    "winget list",
                    "Kurulu WinGet paketlerini listeler.",
                    "Lists installed WinGet packages.",
                    risk="safe",
                    shell="powershell",
                    platforms=["windows"],
                ),
                ex(
                    "Göster",
                    "Show",
                    "winget show Microsoft.PowerShell",
                    "PowerShell paket manifesto özetini gösterir.",
                    "Shows the PowerShell package manifest summary.",
                    risk="safe",
                    shell="powershell",
                    platforms=["windows"],
                ),
            ],
            related=["brew", "pacman", "choco"],
            concepts=["packages", "package-managers", "package-managers-comparison"],
            intent={
                "tr": ["winget kur", "windows paket", "winget ara"],
                "en": ["winget install", "windows package", "winget search"],
            },
        ),
    )
)

# --- macOS commands ---

MACOS.append(
    (
        "packages/brew.yaml",
        mac_cmd(
            id_="brew",
            name="brew",
            category="packages",
            kind="package_manager",
            summary=L(
                "Homebrew paket yöneticisi (macOS).",
                "Homebrew package manager (macOS).",
            ),
            description=L(
                "Homebrew (`brew`), macOS (ve Linuxbrew) için kullanıcı alanı paket "
                "yöneticisidir. MacPorts `port` ayrı kayıttır. formül/cask ayrımına dikkat; "
                "sistem güncellemesi `softwareupdate` ile karıştırılmamalı. Arch host’ta "
                "sistem PM olarak pacman tercih edilir.",
                "Homebrew (brew) is a user-space package manager for macOS (and Linuxbrew). "
                "MacPorts port is a separate record. Mind formula vs cask; do not confuse with "
                "OS updates via softwareupdate. On Arch hosts prefer pacman as the system PM.",
            ),
            tags=["macos", "packages", "homebrew"],
            risk="caution",
            elevated=False,
            sources=["https://docs.brew.sh/", "https://docs.brew.sh/Manpage"],
            package_refs=[
                {
                    "manager": "homebrew",
                    "package": "homebrew",
                    "distributions": ["macos-desktop"],
                    "notes": L(
                        "Resmi kurulum betiği docs.brew.sh; Linuxbrew ayrı ortam.",
                        "Official install script at docs.brew.sh; Linuxbrew is a separate env.",
                    ),
                }
            ],
            flags=[
                flag("install", "Formül/cask kur.", "Install formula/cask."),
                flag("uninstall", "Kaldır.", "Uninstall."),
                flag("update", "brew’i ve formül indekslerini güncelle.", "Update brew and formula indexes."),
                flag("upgrade", "Kurulu formülleri yükselt.", "Upgrade installed formulae."),
                flag("search", "Ara.", "Search."),
                flag("info", "Paket bilgisi.", "Package info."),
            ],
            examples=[
                ex(
                    "Ara",
                    "Search",
                    "brew search ripgrep",
                    "ripgrep formül/cask arar.",
                    "Searches formulae/casks for ripgrep.",
                    risk="safe",
                    platforms=["macos"],
                ),
                ex(
                    "Bilgi",
                    "Info",
                    "brew info git",
                    "git formül ayrıntısını gösterir.",
                    "Shows git formula details.",
                    risk="safe",
                    platforms=["macos"],
                ),
                ex(
                    "Güncelle indeksler",
                    "Update indexes",
                    "brew update",
                    "Homebrew ve formül tanımlarını yeniler (paket yükseltmez).",
                    "Refreshes Homebrew and formula definitions (does not upgrade packages).",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["port", "softwareupdate", "winget", "pacman"],
            concepts=["packages", "package-managers", "package-managers-comparison"],
            intent={
                "tr": ["brew kur", "homebrew", "macos paket"],
                "en": ["brew install", "homebrew", "macos package"],
            },
        ),
    )
)

MACOS.append(
    (
        "packages/port.yaml",
        mac_cmd(
            id_="port",
            name="port",
            category="packages",
            kind="package_manager",
            summary=L(
                "MacPorts paket yöneticisi CLI.",
                "MacPorts package manager CLI.",
            ),
            description=L(
                "MacPorts (`port`), macOS için ports-tree tabanlı paket yöneticisidir. "
                "Homebrew `brew` ile aynı değildir — ayrı kayıt. Çoğu işlem `sudo` ister.",
                "MacPorts (port) is a ports-tree package manager for macOS. It is not "
                "Homebrew brew — separate record. Most operations need sudo.",
            ),
            tags=["macos", "packages", "macports"],
            risk="caution",
            elevated=True,
            sources=["https://guide.macports.org/", "https://www.macports.org/"],
            package_refs=[
                {
                    "manager": "macports",
                    "package": "MacPorts",
                    "distributions": ["macos-desktop"],
                    "notes": L(
                        "Resmi kurulum pkg/guide.macports.org.",
                        "Official install via pkg / guide.macports.org.",
                    ),
                }
            ],
            examples=[
                ex(
                    "Ara",
                    "Search",
                    "port search ripgrep",
                    "Ports ağacında arar.",
                    "Searches the ports tree.",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
                ex(
                    "Bilgi",
                    "Info",
                    "port info git",
                    "Port meta verisini gösterir.",
                    "Shows port metadata.",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["brew", "softwareupdate"],
            concepts=["packages", "package-managers-comparison"],
        ),
    )
)

MACOS.append(
    (
        "system/softwareupdate.yaml",
        mac_cmd(
            id_="softwareupdate",
            name="softwareupdate",
            category="system",
            kind="administrative_tool",
            summary=L(
                "macOS yazılım / sistem güncelleme CLI.",
                "macOS software / system update CLI.",
            ),
            description=L(
                "softwareupdate, Apple sistem ve güvenlik güncellemelerini listeler/kurar. "
                "Homebrew `brew upgrade` OS güncellemesi değildir. Kurulum yeniden başlatma "
                "gerektirebilir; üretimde bakım penceresi kullanın.",
                "softwareupdate lists/installs Apple system and security updates. Homebrew "
                "brew upgrade is not an OS update. Installs may require reboot; use a "
                "maintenance window in production.",
            ),
            tags=["macos", "system", "updates"],
            risk="dangerous",
            elevated=True,
            sources=["https://support.apple.com/guide/terminal/update-software-apd3c5f3772/mac"],
            flags=[
                flag("-l", "Kullanılabilir güncellemeleri listele.", "List available updates."),
                flag("-i", "Güncelleme kur.", "Install updates."),
                flag("--all", "Tüm uygun güncellemeler.", "All applicable updates."),
            ],
            examples=[
                ex(
                    "Listele",
                    "List",
                    "softwareupdate -l",
                    "Bekleyen güncellemeleri listeler (kurmaz).",
                    "Lists pending updates (does not install).",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["brew", "launchctl"],
            intent={
                "tr": ["macos güncelle", "softwareupdate"],
                "en": ["macos update", "softwareupdate"],
            },
        ),
    )
)

MACOS.append(
    (
        "system/launchctl.yaml",
        mac_cmd(
            id_="launchctl",
            name="launchctl",
            category="system",
            kind="administrative_tool",
            summary=L(
                "launchd iş yükü denetimi (macOS servisleri).",
                "launchd job control (macOS services).",
            ),
            description=L(
                "launchctl, macOS launchd ajanlarını yükler/başlatır/durdurur. Linux "
                "systemctl karşılığı değildir. `bootout`/`enable` yanlış kullanıldığında "
                "oturum ajanlarını bozar; sorgu örnekleri tercih edilir.",
                "launchctl loads/starts/stops macOS launchd agents. Not a systemctl alias. "
                "Misused bootout/enable can break session agents; prefer query examples.",
            ),
            tags=["macos", "services", "launchd"],
            risk="dangerous",
            elevated=False,
            sources=[
                "https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html",
                "man 1 launchctl",
            ],
            examples=[
                ex(
                    "Kullanıcı etki alanı listesi",
                    "List user domain",
                    "launchctl print gui/$(id -u) 2>/dev/null | head",
                    "GUI etki alanı özetini basmaya çalışır (ortama göre değişir).",
                    "Attempts to print GUI domain summary (varies by environment).",
                    risk="safe",
                    platforms=["macos"],
                ),
                ex(
                    "Yardım",
                    "Help",
                    "launchctl help",
                    "Alt komut yardımını gösterir.",
                    "Shows subcommand help.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["systemctl", "softwareupdate"],
            concepts=["systemd"],
            intent={
                "tr": ["launchctl", "macos servis", "launchd"],
                "en": ["launchctl", "macos services", "launchd"],
            },
        ),
    )
)

MACOS.append(
    (
        "disks/diskutil.yaml",
        mac_cmd(
            id_="diskutil",
            name="diskutil",
            category="disks",
            kind="administrative_tool",
            summary=L(
                "macOS disk / APFS yönetim aracı.",
                "macOS disk / APFS management utility.",
            ),
            description=L(
                "diskutil birimleri listeler, bağlar/ayarlar ve APFS işlemleri yapar. "
                "`eraseDisk` yıkıcıdır — örneklerde yok. Linux lsblk/fdisk karşılığı değildir. "
                "macOS diskleri listelemek için `diskutil list` kullanın.",
                "diskutil lists volumes, mounts/manages, and performs APFS ops. eraseDisk is "
                "destructive — omitted from examples. Not an lsblk/fdisk alias. Use "
                "diskutil list to list macOS disks.",
            ),
            tags=["macos", "disks", "apfs"],
            risk="destructive",
            elevated=False,
            sources=["man 8 diskutil", "https://ss64.com/mac/diskutil.html"],
            flags=[
                flag("list", "Diskleri listele.", "List disks."),
                flag("info", "Birim bilgisi.", "Volume info."),
            ],
            examples=[
                ex(
                    "Diskleri listele",
                    "List disks",
                    "diskutil list",
                    "Bağlı disk ve bölümleri listeler (yazmaz).",
                    "Lists attached disks and partitions (no writes).",
                    risk="safe",
                    platforms=["macos"],
                ),
                ex(
                    "Birim bilgisi",
                    "Volume info",
                    "diskutil info /",
                    "Kök birim hakkında bilgi basar.",
                    "Prints info about the root volume.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["get-disk", "lsblk", "df"],
            intent={
                "tr": ["macos disk listele", "diskutil", "apfs"],
                "en": ["list macos disks", "diskutil", "apfs"],
            },
        ),
    )
)

MACOS.append(
    (
        "network/networksetup.yaml",
        mac_cmd(
            id_="networksetup",
            name="networksetup",
            category="network",
            kind="administrative_tool",
            summary=L(
                "macOS ağ servisleri yapılandırması (System Settings CLI).",
                "macOS network service configuration (System Settings CLI).",
            ),
            description=L(
                "networksetup, ağ konumları, DNS ve proxy ayarlarını yönetir. Linux `ip` "
                "veya `ifconfig` ile aynı değildir; BSD `ifconfig` macOS’ta da vardır ama "
                "farklı model. Yazma işlemleri yönetici ister.",
                "networksetup manages network locations, DNS, and proxies. Not the same as "
                "Linux ip or ifconfig; BSD ifconfig also exists on macOS under a different "
                "model. Writes need admin.",
            ),
            tags=["macos", "network"],
            risk="dangerous",
            elevated=True,
            sources=["man 8 networksetup", "https://ss64.com/mac/networksetup.html"],
            examples=[
                ex(
                    "Donanım portları",
                    "Hardware ports",
                    "networksetup -listallhardwareports",
                    "Donanım portlarını listeler (salt okuma).",
                    "Lists hardware ports (read-only).",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
                ex(
                    "Ağ servisleri",
                    "Network services",
                    "networksetup -listallnetworkservices",
                    "Yapılandırılmış ağ servislerini listeler.",
                    "Lists configured network services.",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["scutil", "ifconfig", "ip"],
            intent={
                "tr": ["macos ağ", "networksetup", "dns ayarla"],
                "en": ["macos network", "networksetup", "set dns"],
            },
        ),
    )
)

MACOS.append(
    (
        "hardware/system-profiler.yaml",
        mac_cmd(
            id_="system-profiler",
            name="system_profiler",
            category="hardware",
            summary=L(
                "macOS sistem / donanım envanter raporu.",
                "macOS system / hardware inventory report.",
            ),
            description=L(
                "system_profiler, System Information uygulamasının CLI karşılığıdır. "
                "Belirli veri türleri (SPHardwareDataType vb.) ile süzülür. Linux lshw/lscpu "
                "karşılığı değildir.",
                "system_profiler is the CLI counterpart of System Information. Filter with "
                "data types (SPHardwareDataType, etc.). Not an lshw/lscpu alias.",
            ),
            tags=["macos", "hardware", "inventory"],
            risk="safe",
            elevated=False,
            sources=["man 8 system_profiler"],
            examples=[
                ex(
                    "Donanım özeti",
                    "Hardware overview",
                    "system_profiler SPHardwareDataType",
                    "Model, çip ve bellek özetini basar.",
                    "Prints model, chip, and memory overview.",
                    platforms=["macos"],
                ),
            ],
            related=["get-computerinfo", "lscpu"],
        ),
    )
)

MACOS.append(
    (
        "system/pmset.yaml",
        mac_cmd(
            id_="pmset",
            name="pmset",
            category="system",
            summary=L(
                "macOS güç yönetimi ayarları.",
                "macOS power management settings.",
            ),
            description=L(
                "pmset uyku, hibernation ve güç profillerini yönetir. Yazma `sudo` ister; "
                "yanlış ayar dizüstü pili ve sunucu erişimini etkiler.",
                "pmset manages sleep, hibernation, and power profiles. Writes need sudo; "
                "wrong settings affect laptop battery and server reachability.",
            ),
            tags=["macos", "power"],
            risk="caution",
            elevated=False,
            sources=["man 1 pmset"],
            examples=[
                ex(
                    "Güç ayarlarını göster",
                    "Show power settings",
                    "pmset -g",
                    "Geçerli güç yönetimi ayarlarını basar.",
                    "Prints current power management settings.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["system-profiler"],
        ),
    )
)

MACOS.append(
    (
        "monitoring/log.yaml",
        mac_cmd(
            id_="log",
            name="log",
            category="monitoring",
            summary=L(
                "macOS birleşik günlük (unified logging) CLI.",
                "macOS unified logging CLI.",
            ),
            description=L(
                "`log` aracı unified logging akışını gösterir/toplar. Linux journalctl "
                "karşılığı değildir. `log show` yoğun olabilir; predicate süzgeçleri kullanın.",
                "The log tool shows/collects the unified logging stream. Not a journalctl "
                "alias. log show can be heavy; use predicate filters.",
            ),
            tags=["macos", "logs"],
            risk="caution",
            elevated=False,
            sources=["man 1 log", "https://developer.apple.com/documentation/os/logging"],
            examples=[
                ex(
                    "Son satırlar (kısa)",
                    "Recent lines (short)",
                    "log show --last 2m --style compact | tail",
                    "Son 2 dakikalık kompakt günlükten kuyruk alır.",
                    "Tails a compact log from the last 2 minutes.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["get-winevent", "journalctl"],
        ),
    )
)

MACOS.append(
    (
        "users/dscl.yaml",
        mac_cmd(
            id_="dscl",
            name="dscl",
            category="users",
            kind="administrative_tool",
            summary=L(
                "Directory Service komut satırı (kullanıcı/düğüm).",
                "Directory Service command line (users/nodes).",
            ),
            description=L(
                "dscl, Open Directory / yerel dizin düğümlerini okur/yazar. Kullanıcı "
                "oluşturma/silme yıkıcı olabilir. Linux getent/useradd modeli değildir.",
                "dscl reads/writes Open Directory / local directory nodes. Creating/deleting "
                "users can be destructive. Not the Linux getent/useradd model.",
            ),
            tags=["macos", "directory", "users"],
            risk="dangerous",
            elevated=True,
            sources=["man 1 dscl"],
            examples=[
                ex(
                    "Yerel kullanıcıları listele",
                    "List local users",
                    "dscl . -list /Users",
                    "Yerel dizin kullanıcı adlarını listeler (salt okuma).",
                    "Lists local directory usernames (read-only).",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["id", "whoami"],
        ),
    )
)

MACOS.append(
    (
        "system/defaults.yaml",
        mac_cmd(
            id_="defaults",
            name="defaults",
            category="system",
            summary=L(
                "macOS kullanıcı tercihlerine (plist) okuma/yazma.",
                "Read/write macOS user preferences (plists).",
            ),
            description=L(
                "defaults, uygulama domain tercihlerini okur/yazar. Yanlış yazma uygulama "
                "ayarlarını bozar. `plutil` plist doğrulama için ayrı kayıttır.",
                "defaults reads/writes app domain preferences. Wrong writes break app settings. "
                "plutil is a separate record for plist validation.",
            ),
            tags=["macos", "preferences", "plist"],
            risk="caution",
            elevated=False,
            sources=["man 1 defaults"],
            examples=[
                ex(
                    "Domain oku",
                    "Read domain",
                    "defaults read com.apple.dock tilesize",
                    "Dock simge boyutunu okur (varsa).",
                    "Reads Dock icon size if present.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["plutil"],
        ),
    )
)

MACOS.append(
    (
        "development/plutil.yaml",
        mac_cmd(
            id_="plutil",
            name="plutil",
            category="development",
            summary=L(
                "Property list (plist) doğrulama ve dönüştürme.",
                "Validate and convert property list (plist) files.",
            ),
            description=L(
                "plutil plist dosyalarını lint’ler ve xml1/binary1/json arasında dönüştürür. "
                "`defaults` tercih yazma aracıdır — karıştırmayın.",
                "plutil lints plists and converts among xml1/binary1/json. defaults is for "
                "preference writes — do not confuse them.",
            ),
            tags=["macos", "plist", "development"],
            risk="caution",
            elevated=False,
            sources=["man 1 plutil"],
            examples=[
                ex(
                    "Lint",
                    "Lint",
                    "plutil -lint ~/Library/Preferences/com.apple.dock.plist",
                    "Plist sözdizimini doğrular.",
                    "Validates plist syntax.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["defaults"],
        ),
    )
)

MACOS.append(
    (
        "security/security.yaml",
        mac_cmd(
            id_="security",
            name="security",
            category="security",
            kind="administrative_tool",
            summary=L(
                "macOS Anahtarlık (Keychain) komut satırı.",
                "macOS Keychain command-line tool.",
            ),
            description=L(
                "security, anahtarlık öğelerini listeler/yönetir. Gizli anahtar işlemleri "
                "dikkat ister; örnekler salt listeleme odaklıdır.",
                "security lists/manages keychain items. Secret-key operations need care; "
                "examples focus on listing only.",
            ),
            tags=["macos", "keychain", "security"],
            risk="dangerous",
            elevated=False,
            sources=["man 1 security"],
            examples=[
                ex(
                    "Anahtarlıkları listele",
                    "List keychains",
                    "security list-keychains",
                    "Arama listesindeki anahtarlıkları basar.",
                    "Prints keychains on the search list.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["openssl", "gpg"],
        ),
    )
)

MACOS.append(
    (
        "security/profiles.yaml",
        mac_cmd(
            id_="profiles",
            name="profiles",
            category="security",
            kind="administrative_tool",
            summary=L(
                "Yapılandırma profilleri (MDM) yönetimi.",
                "Configuration profiles (MDM) management.",
            ),
            description=L(
                "profiles, cihaz/kullanıcı yapılandırma profillerini listeler/yükler. "
                "Kurumsal MDM ortamlarında kritiktir; kaldırma politikaya bağlıdır.",
                "profiles lists/installs device/user configuration profiles. Critical in "
                "enterprise MDM; removal depends on policy.",
            ),
            tags=["macos", "mdm", "profiles"],
            risk="dangerous",
            elevated=True,
            sources=["man 1 profiles"],
            examples=[
                ex(
                    "Profilleri listele",
                    "List profiles",
                    "profiles list",
                    "Yüklü yapılandırma profillerini listeler.",
                    "Lists installed configuration profiles.",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["softwareupdate"],
        ),
    )
)

MACOS.append(
    (
        "network/scutil.yaml",
        mac_cmd(
            id_="scutil",
            name="scutil",
            category="network",
            summary=L(
                "Sistem yapılandırma çerçevesi aracı (DNS/proxy vb.).",
                "System configuration framework tool (DNS/proxy, etc.).",
            ),
            description=L(
                "scutil, dynamic store ve DNS yapılandırmasını inceler. networksetup yüksek "
                "seviye ağ servisi CLI’sidir — birlikte kullanılır, aynı değildir.",
                "scutil inspects the dynamic store and DNS configuration. networksetup is the "
                "higher-level network-service CLI — complementary, not identical.",
            ),
            tags=["macos", "network", "dns"],
            risk="caution",
            elevated=False,
            sources=["man 8 scutil"],
            examples=[
                ex(
                    "DNS göster",
                    "Show DNS",
                    "scutil --dns | head",
                    "Çözümleyici yapılandırmasının başını basar.",
                    "Prints the head of resolver configuration.",
                    risk="safe",
                    platforms=["macos"],
                ),
            ],
            related=["networksetup"],
        ),
    )
)

MACOS.append(
    (
        "development/xcode-select.yaml",
        mac_cmd(
            id_="xcode-select",
            name="xcode-select",
            category="development",
            summary=L(
                "Aktif Xcode / CLT geliştirici dizinini seçer.",
                "Selects the active Xcode / CLT developer directory.",
            ),
            description=L(
                "xcode-select, derleyici araçlarının hangi Developer dizinini kullanacağını "
                "ayarlar. `xcrun` araçları bu seçime göre yollar. Yanlış yol derlemeyi bozar.",
                "xcode-select sets which Developer directory compiler tools use. xcrun "
                "resolves tools from that selection. A wrong path breaks builds.",
            ),
            tags=["macos", "xcode", "development"],
            risk="caution",
            elevated=True,
            sources=["man 1 xcode-select"],
            examples=[
                ex(
                    "Yolu yazdır",
                    "Print path",
                    "xcode-select -p",
                    "Aktif geliştirici dizinini basar.",
                    "Prints the active developer directory.",
                    risk="safe",
                    elevated=False,
                    platforms=["macos"],
                ),
            ],
            related=["xcrun"],
        ),
    )
)

MACOS.append(
    (
        "development/xcrun.yaml",
        mac_cmd(
            id_="xcrun",
            name="xcrun",
            category="development",
            summary=L(
                "Xcode araç zincirinden komut çalıştırır / yol bulur.",
                "Runs / locates tools from the Xcode toolchain.",
            ),
            description=L(
                "xcrun, seçili Developer dizini içindeki araçları bulur veya çalıştırır "
                "(ör. `xcrun simctl`). xcode-select ile birlikte kullanılır.",
                "xcrun finds or runs tools inside the selected Developer directory "
                "(e.g. xcrun simctl). Used together with xcode-select.",
            ),
            tags=["macos", "xcode", "development"],
            risk="safe",
            elevated=False,
            sources=["man 1 xcrun"],
            examples=[
                ex(
                    "clang yolunu bul",
                    "Find clang path",
                    "xcrun --find clang",
                    "Aktif toolchain’deki clang yolunu basar.",
                    "Prints the clang path from the active toolchain.",
                    platforms=["macos"],
                ),
            ],
            related=["xcode-select"],
        ),
    )
)


def patch_bsd_gnu_notes() -> None:
    """Annotate existing cross-platform Unix tools with BSD vs GNU notes for macOS."""
    notes = {
        "text/sed.yaml": (
            " macOS/BSD `sed` GNU sed’den farklıdır (ör. yerinde düzenleme: BSD `sed -i ''`; "
            "GNU `sed -i`). Platforma özgü seçenekleri ayrı doğrulayın.",
            " macOS/BSD sed differs from GNU sed (e.g. in-place: BSD `sed -i ''` vs GNU "
            "`sed -i`). Verify platform-specific options separately.",
        ),
        "archives/tar.yaml": (
            " macOS/BSD `tar` ile GNU tar seçenekleri birebir değildir (ör. `--selinux` yok; "
            "bazı uzun seçenekler farklı).",
            " macOS/BSD tar options are not 1:1 with GNU tar (e.g. no --selinux; some long "
            "options differ).",
        ),
        "search/find.yaml": (
            " macOS/BSD `find` GNU findutils’ten farklıdır (ör. `-printf` yok; `-exec` sonlandırma "
            "alışkanlıkları kontrol edin).",
            " macOS/BSD find differs from GNU findutils (e.g. no -printf; check -exec termination).",
        ),
        "filesystem/stat.yaml": (
            " macOS/BSD `stat` biçim dizgileri GNU `stat -c` ile uyumlu değildir (`-f` vs `-c`).",
            " macOS/BSD stat format strings are not compatible with GNU `stat -c` (`-f` vs `-c`).",
        ),
        "system/date.yaml": (
            " macOS/BSD `date` GNU date’ten farklıdır (ör. `-d` yok; `-v` / `-r` kullanın).",
            " macOS/BSD date differs from GNU date (e.g. no -d; use -v / -r).",
        ),
    }
    for rel, (tr_extra, en_extra) in notes.items():
        path = COMMANDS / rel
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        desc = data.get("description") or {}
        if "BSD" in desc.get("en", "") or "macOS/BSD" in desc.get("en", ""):
            continue
        desc["tr"] = desc.get("tr", "").rstrip() + tr_extra
        desc["en"] = desc.get("en", "").rstrip() + en_extra
        # localizedLong max 2000
        if len(desc["tr"]) > 2000 or len(desc["en"]) > 2000:
            raise SystemExit(f"description too long after BSD note: {rel}")
        data["description"] = desc
        # Add a draft platform note flag marker via verification notes? Keep verification intact.
        dump(path, data)
        print(f"patched {rel}")


def main() -> None:
    for rel, data in WINDOWS + MACOS:
        # Drop related entries that do not exist yet (except within this batch)
        known = {p.stem for p in COMMANDS.rglob("*.yaml")}
        batch_ids = {d["id"] for _, d in WINDOWS + MACOS}
        related = data.get("related") or []
        data["related"] = [r for r in related if r in known or r in batch_ids]
        if not data["related"]:
            data.pop("related", None)
        # Drop nova.concepts that are unknown — validator checks them
        dump(COMMANDS / rel, data)
        print(f"wrote {rel}")
    patch_bsd_gnu_notes()
    print(f"total new: {len(WINDOWS) + len(MACOS)} (windows={len(WINDOWS)} macos={len(MACOS)})")


if __name__ == "__main__":
    main()
