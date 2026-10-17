#!/usr/bin/env python3
"""Static XenForo 2.3.13 gate across public Warext XenForo add-on repos.

Never reports runtime compatibility: XF source requires a licensed test install.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

OWNER = "benjamin1734"
TARGET_XF = 2030130
REPOSITORIES = {
    "Davet / Referans": ("Warext-Studios-Xenfero-Davet-Referans-Sistemi", "upload/src/addons/WarextStudios/ReferralSystem"),
    "Konu Güncellik": ("Warext-Studios---Konu-Guncellik-Sistemi", "upload/src/addons/WarextStudios/ThreadFreshness"),
    "Klan / Grup": ("Warext-Studios-XenForo-Klan-Grup-Sistemi", "upload/src/addons/Warext/Clans"),
    "GitHub Otomasyonu": ("Warext-Studios-Xenfero-GitHub-Integration-Add-on", "src/addons/Warext/GitHubSync"),
    "İçerik AI Denetimi": ("Warext-Studios-Xenfero-Icerik-AI-Denetim-Sistemi", "upload/src/addons/Warext/AIContentInspector"),
    "Hata Bildirim": ("Warext-Studios-Xenfero-Hata-Bildirim-Sistemi", "upload/src/addons/Warext/HataBildirimi"),
    "S.S.S.": ("Warext-Studios-XenForo-S.S.S.-Sistemi", "upload/src/addons/Warext/SSS"),
    "Moderasyon Denetimi": ("Warext-Studios-XenForo-Moderasyon-Denetim-Sistemi", "upload/src/addons/Warext/ModerationAudit"),
    "Kullanıcı İçerik Yöneticisi": ("Warext-Studios-Kullanici-Icerik-Yoneticisi", "upload/src/addons/WarextStudios/UserContentManager"),
    "Portfolyo": ("Warext-Studios-Xenfero-Portfolyo-Sistemi", "upload/src/addons/Warext/Portfolio"),
    "Özel Mesaj Moderasyonu": ("Warext-Studios-Xenfero-Private-Messages-Moderation-Add-on", "src/addons/Warext/PrivateModeration"),
    "Türkçe Yazım": ("Warext-Studios-Xenfero-Turkce-Yazim-Denetim-Eklentisi", "upload/src/addons/Warext/TurkishSpellCheck"),
    "Minecraft Vote": ("Warext-Studios-XenForo-Minecraft-Sunucu-Vote-Sistemi", "src/addons/Warext/MinecraftVote"),
}
CORE_CHANGED_2313 = {
    "bb_code_tag_url_unfurl", "featured_content_item",
    "lightbox_macros", "trending_content_item_thread",
    "featured_content_item_resource", "trending_content_item_resource",
    "xfrm_resource_rate", "xfrm_resource_reviews", "xfrm_resource_updates",
}

def process(repo: str, path: Path, dst: Path):
    errors, manual = [], []
    remote = f"https://github.com/{OWNER}/{repo}.git"
    fetched = subprocess.run(["git", "clone", "--depth", "1", "--quiet", remote, str(dst)],
                             capture_output=True, text=True, timeout=180)
    if fetched.returncode:
        return ["Git clone failed: " + fetched.stderr.strip()[:250]], [], "-", 0, 0
    addon_dir = dst / path
    try:
        addon = json.loads((addon_dir / "addon.json").read_text(encoding="utf-8"))
        version = str(addon["version_string"])
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append("Invalid version_string")
        if not isinstance(addon.get("version_id"), int) or addon["version_id"] <= 0:
            errors.append("Invalid version_id")
        numeric, label = addon["require"]["XF"]
        numeric = int(numeric)
        if numeric > TARGET_XF:
            errors.append(f"Requires XF {numeric}, newer than 2.3.13")
        if 2030000 <= numeric <= TARGET_XF and (numeric - 2030000) % 10 == 0:
            expected = f"2.3.{(numeric - 2030000) // 10}"
            if expected not in str(label):
                errors.append(f"Requirement label {label!r} does not match {expected}")
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return ["Invalid addon.json: " + str(exc)[:180]], [], "-", 0, 0

    xml_count = 0
    data_dir = addon_dir / "_data"
    if data_dir.is_dir():
        for f in sorted(data_dir.glob("*.xml")):
            xml_count += 1
            try:
                ET.parse(f)
            except ET.ParseError as exc:
                errors.append(f"Invalid XML: {f.name}: {exc}")
        ext = data_dir / "class_extensions.xml"
        if ext.exists():
            try:
                for element in ET.parse(ext).getroot().findall("extension"):
                    cls = element.attrib.get("to_class", "")
                    parts = cls.split("\\")
                    if len(parts) >= 3:
                        rel = Path(*parts[2:]).with_suffix(".php")
                        if not (addon_dir / rel).is_file():
                            errors.append(f"Missing class-extension file: {cls}")
                    manual.append(f"Class extension {element.attrib.get('from_class', '?')}")
            except ET.ParseError:
                pass
        mods = data_dir / "template_modifications.xml"
        if mods.exists():
            try:
                for element in ET.parse(mods).getroot().findall("modification"):
                    template = element.attrib.get("template", "")
                    if template in CORE_CHANGED_2313:
                        manual.append("2.3.13 changed template: " + template)
                    if template in {"PAGE_CONTAINER", "editor", "thread_view", "post_macros"}:
                        manual.append("Core template anchor: " + template)
            except ET.ParseError:
                pass
    elif (addon_dir / "_output").is_dir():
        manual.append("_data is generated at packaging time; verify release ZIP export")
    else:
        errors.append("No XenForo _data or _output found")
    php_count = 0
    for php_file in sorted(addon_dir.rglob("*.php")):
        php_count += 1
        check = subprocess.run(["php", "-l", str(php_file)], capture_output=True, text=True)
        if check.returncode:
            errors.append("PHP syntax: " + str(php_file.relative_to(addon_dir)))
            if len(errors) >= 30:
                break
    return errors, sorted(set(manual)), version, php_count, xml_count

def main():
    lines = [
        "# Warext XenForo 2.3.13 — Static compatibility report",
        "",
        "**Scope:** manifest constraints, metadata consistency, XML parsing, PHP 8.4 syntax and risk flags.",
        "**Not verified:** licensed XenForo 2.3.13 install/upgrade, template-anchor matches against core source, runtime interactions, browser tests and official add-on integrations.",
        "",
        "| Add-on | Version | PHP files | XML files | Static status | Manual follow-up |",
        "|---|---:|---:|---:|---|---:|",
    ]
    findings = []
    failed = 0
    with tempfile.TemporaryDirectory(prefix="warext-xf-audit-") as tmp:
        for index, (title, (repo, subpath)) in enumerate(REPOSITORIES.items()):
            try:
                errors, manual, version, php_count, xml_count = process(repo, Path(subpath), Path(tmp) / str(index))
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors, manual, version, php_count, xml_count = [str(exc)], [], "-", 0, 0
            failed += bool(errors)
            lines.append(f"| {title} | {version} | {php_count} | {xml_count} | {'FAIL' if errors else 'PASS (static)'} | {len(manual)} |")
            if errors or manual:
                findings.append(f"### {title}\n\n" + "\n".join("- **Error:** " + x for x in errors)
                    + ("\n" if errors and manual else "") + "\n".join("- **Needs live test:** " + x for x in manual))
    lines.extend(["", "## Findings and unverified integration points", ""])
    lines.extend(findings or ["No issues detected in the static checks. Live integration is still required."])
    lines.extend(["", f"**Static failures: {failed}/{len(REPOSITORIES)}**. A static PASS must never be presented as verified XenForo runtime compatibility.", ""])
    report = "\n".join(lines)
    Path("xenforo-audit-report.md").write_text(report, encoding="utf-8")
    print(report)
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
