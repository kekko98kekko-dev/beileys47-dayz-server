#!/usr/bin/env python3
"""Basic regression checks for generated DayZ Stage 2 preview, no game launch."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "dist/stage2/dayzOffline.enoch"
REPORT = ROOT / "dist/stage2/change_report.json"


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    types = ET.parse(STAGE / "db/types.xml").getroot()
    loot = {n.get("name"): n for n in types.findall("type")}
    assert len(loot) == len(set(loot)), "Duplicate CE class"
    for name in ("M4A1", "AKM", "UndergroundStash", "WoodenCrate", "SKS", "MP5K"):
        assert name in loot, f"Missing type {name}"
    assert int(loot["M4A1"].findtext("nominal")) == 1, "Rare M4 should remain rare"
    assert int(loot["AKM"].findtext("nominal")) == 2, "Rare AKM should remain unchanged"
    assert int(loot["UndergroundStash"].findtext("lifetime")) == 21 * 86400
    assert int(loot["WoodenCrate"].findtext("lifetime")) == 45 * 86400
    assert int(loot["SKS"].findtext("nominal")) == 8
    assert int(loot["MP5K"].findtext("nominal")) == 15
    assert int(loot["BandageDressing"].findtext("nominal")) == 21

    spawns = ET.parse(STAGE / "cfgplayerspawnpoints.xml").getroot()
    groups = [g.get("name") for g in spawns.findall("./fresh/generator_posbubbles/group")]
    assert groups == ["Brena", "Kolembrody", "Sobotka"], groups
    assert len(spawns.findall("./fresh/generator_posbubbles/group/pos")) >= 8

    vehicles = ET.parse(STAGE / "cfgspawnabletypes.xml").getroot()
    configs = {t.get("name"): t for t in vehicles.findall("type")}
    for car in ("Hatchback_02", "OffroadHatchback"):
        assert car in configs
        wheels = [
            item for group in configs[car].findall("attachments")
            for item in group.findall("item")
            if "Wheel" in item.get("name", "")
        ]
        assert len(wheels) >= 4
        assert all(float(w.get("chance", 0)) >= 0.9 for w in wheels[:4])

    gameplay = json.loads((STAGE / "cfggameplay.json").read_text(encoding="utf-8"))
    assert gameplay["PlayerData"]["StaminaData"]["staminaMax"] == 110
    assert gameplay["GeneralData"]["disableBaseDamage"] is False
    assert gameplay["GeneralData"]["disableContainerDamage"] is False
    assert report["status"].startswith("PREVIEW ONLY")
    assert len(report["vehicle_part_changes"]) == 2
    assert len(report["additional_loot_and_stash_changes"]) == 12

    print("PASS: Stage 2 static regression checks.")
    print("NOTE: This does NOT test DayZ PS5 runtime, Nitrado upload, vehicle physics or persistence.")


if __name__ == "__main__":
    main()
