#!/usr/bin/env python3
"""Stage 2 DayZ Livonia preview: build from official pinned upstream + Stage 1.

Safety: preview ZIP only; NEVER calls Nitrado, never modifies a running server.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from build_mission import UPSTREAM_BASE, UPSTREAM_COMMIT, run as run_stage1

ROOT = Path(__file__).resolve().parents[1]
STAGE2_FILES = ("db/types.xml", "cfgplayerspawnpoints.xml",
                "cfgspawnabletypes.xml", "cfggameplay.json")
EXTRA_ORIGINALS = ("cfgspawnabletypes.xml", "cfggameplay.json")


def fetch_original(relpath: str, source_dir: Path | None) -> bytes:
    if relpath not in EXTRA_ORIGINALS:
        raise ValueError(f"Unexpected extra official file: {relpath}")
    if source_dir is not None:
        return (source_dir / relpath).read_bytes()
    request = urllib.request.Request(
        UPSTREAM_BASE + relpath,
        headers={"User-Agent": "BEILEYS47-DayZ-Preview/1.0"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read(3 * 1024 * 1024 + 1)
    if len(payload) > 3 * 1024 * 1024:
        raise ValueError("Official file exceeds safety size limit")
    return payload


def parse_xml(raw: bytes, label: str) -> ET.Element:
    upper = raw.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError(f"DTD/entity rejected in {label}")
    return ET.fromstring(raw)


def update_type_values(root: ET.Element, rules: dict) -> list[dict]:
    if root.tag != "types":
        raise ValueError("Unexpected types.xml root")
    items = {node.get("name"): node for node in root.findall("type")}
    missing = set(rules["required_item_types"]) - set(items)
    if missing:
        raise ValueError(f"Official types missing: {sorted(missing)}")
    changes = []
    for name, factor in rules["type_multipliers"].items():
        if name not in items or not 1.0 <= float(factor) <= 1.5:
            raise ValueError(f"Missing or invalid item multiplier: {name}")
        node = items[name]
        nominal, minimum = node.find("nominal"), node.find("min")
        if nominal is None or minimum is None:
            raise ValueError(f"Malformed CE type: {name}")
        old_n, old_m = int(nominal.text), int(minimum.text)
        if old_n <= 0 or old_m < 0 or old_m > old_n:
            raise ValueError(f"Refusing to alter disabled/invalid CE class: {name}")
        flags = node.find("flags")
        if flags is None:
            raise ValueError(f"No flags for {name}")
        new_n = math.ceil(old_n * factor)
        new_m = min(new_n, math.ceil(old_m * factor))
        nominal.text, minimum.text = str(new_n), str(new_m)
        changes.append({"name": name, "nominal": [old_n, new_n],
                        "min": [old_m, new_m], "factor": factor})

    stash = items["UndergroundStash"]
    lifetime = stash.find("lifetime")
    if lifetime is None:
        raise ValueError("No lifetime on UndergroundStash")
    old_seconds = int(lifetime.text)
    new_seconds = int(rules["buried_stash_lifetime_days"]) * 86400
    if not 14 * 86400 <= new_seconds <= 30 * 86400:
        raise ValueError("Buried stash lifetime outside conservative limits")
    if old_seconds > new_seconds:
        raise ValueError("Refusing to shorten existing vanilla stash lifetime")
    lifetime.text = str(new_seconds)
    changes.append({"name": "UndergroundStash", "lifetime_seconds": [
        old_seconds, new_seconds]})
    return changes


def update_vehicles(root: ET.Element, rules: dict) -> list[dict]:
    if root.tag != "spawnabletypes":
        raise ValueError("Unexpected cfgspawnabletypes.xml root")
    vehicles = {node.get("name"): node for node in root.findall("type")}
    report = []
    for name, options in rules["vehicle_attachment_rules"].items():
        if name not in vehicles:
            raise ValueError(f"Official vehicle cfg missing: {name}")
        vehicle = vehicles[name]
        changed = []
        wheel_count = 0
        repair_part_count = 0
        for group in vehicle.findall("attachments"):
            for item in group.findall("item"):
                partname = item.get("name", "")
                if "Wheel" in partname and wheel_count < 4:
                    # Modify only four main wheels; keep spare wheel probability untouched.
                    old = float(item.attrib["chance"])
                    new = max(old, float(options["wheel_chance_first_four"]))
                    if new > 1:
                        raise ValueError("Invalid wheel probability")
                    item.set("chance", f"{new:.2f}")
                    changed.append({"part": partname, "chance": [old, new]})
                    wheel_count += 1
                elif partname in {"SparkPlug", "CarBattery", "CarRadiator"}:
                    old = float(item.attrib["chance"])
                    new = max(old, float(options["repair_part_chance_floor"]))
                    if new > 1:
                        raise ValueError("Invalid repair part probability")
                    item.set("chance", f"{new:.2f}")
                    changed.append({"part": partname, "chance": [old, new]})
                    repair_part_count += 1
        if wheel_count != 4 or repair_part_count < 1:
            raise ValueError(f"Unexpected original vehicle attachments for {name}: {wheel_count} wheels, {repair_part_count} repair parts")
        report.append({"vehicle": name, "parts": changed,
                       "note": "No vehicle event counts or spawn locations changed"})
    return report


def update_gameplay(gameplay: dict, rules: dict) -> list[dict]:
    if not isinstance(gameplay, dict):
        raise ValueError("Original cfggameplay.json is not an object")
    general = gameplay["GeneralData"]
    stamina = gameplay["PlayerData"]["StaminaData"]
    report = []
    for key in ("staminaMax", "staminaKgToStaminaPercentPenalty"):
        old = stamina[key]
        target = rules["gameplay"][key]
        if not isinstance(old, (float, int)) or not 0.5 <= target <= 150:
            raise ValueError(f"Invalid gameplay setting {key}")
        stamina[key] = target
        report.append({"setting": "PlayerData.StaminaData." + key,
                       "old": old, "new": target})
    for key in ("disableBaseDamage", "disableContainerDamage"):
        if rules["gameplay"][key] is not False:
            raise ValueError("Stage 2 must not globally disable raid/base damage")
        if general[key] is not False:
            raise ValueError(f"Unexpected official default for {key}")
    return report


def build(output_dir: Path, source_dir: Path | None) -> None:
    stage1dir = output_dir / "stage1"
    run_stage1(stage1dir, source_dir)
    result_root = output_dir / "stage2" / "dayzOffline.enoch"
    rules = json.loads(
        (ROOT / "config" / "stage2_rules.json").read_text(encoding="utf-8"))
    report = {
        "stage": 2,
        "source": "BohemiaInteractive/DayZ-Central-Economy",
        "pinned_commit": UPSTREAM_COMMIT,
        "status": "PREVIEW ONLY - NO NITRADO DEPLOY / NO PLAYSTATION TEST",
        "stage1_report": json.loads(
            (stage1dir / "change_report.json").read_text(encoding="utf-8")),
    }

    for path in ("db/types.xml", "cfgplayerspawnpoints.xml"):
        source = stage1dir / "dayzOffline.enoch" / path
        dest = result_root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

    types_path = result_root / "db/types.xml"
    tree = ET.parse(types_path)
    report["additional_loot_and_stash_changes"] = update_type_values(tree.getroot(), rules)
    tree.write(types_path, encoding="utf-8", xml_declaration=True)

    vehicle_tree = ET.ElementTree(
        parse_xml(fetch_original("cfgspawnabletypes.xml", source_dir),
                  "cfgspawnabletypes.xml"))
    report["vehicle_part_changes"] = update_vehicles(vehicle_tree.getroot(), rules)
    vehicle_path = result_root / "cfgspawnabletypes.xml"
    vehicle_tree.write(vehicle_path, encoding="utf-8", xml_declaration=True)

    gameplay = json.loads(
        fetch_original("cfggameplay.json", source_dir).decode("utf-8-sig"))
    report["gameplay_changes"] = update_gameplay(gameplay, rules)
    gameplay_path = result_root / "cfggameplay.json"
    gameplay_path.write_text(
        json.dumps(gameplay, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for path in STAGE2_FILES:
        dest = result_root / path
        if path.endswith(".xml"):
            ET.parse(dest)
        else:
            json.loads(dest.read_text(encoding="utf-8"))

    outdir = output_dir / "stage2"
    report_path = outdir / "change_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    zip_path = outdir / "beileys47-livonia-stage2-preview.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in STAGE2_FILES:
            archive.write(result_root / path, arcname=f"dayzOffline.enoch/{path}")
        archive.write(report_path, arcname="change_report.json")
    print("Stage 2 built and syntax validated.")
    print("Important: no server compatibility, gameplay or persistence testing performed.")
    print("Preview ZIP:", zip_path)
    print("Changed CE items:", len(report["additional_loot_and_stash_changes"]))
    print("Changed car configurations:", len(report["vehicle_part_changes"]))
    print("Changed gameplay parameters:", len(report["gameplay_changes"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--source-dir", type=Path, default=None)
    args = parser.parse_args()
    build(args.output, args.source_dir)
