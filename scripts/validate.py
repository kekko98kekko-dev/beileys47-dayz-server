#!/usr/bin/env python3
"""Preflight checks only: no Nitrado access, no server restarts, no dependencies."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)
    print(f"ERROR: {message}")


def check_profile() -> None:
    path = ROOT / "config" / "profile.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: {exc}")
        return

    if data.get("map") != "livonia":
        error("config/profile.json: map must be 'livonia' for this project")
    if data.get("platform") != "PlayStation 4 / PlayStation 5":
        error("config/profile.json: unexpected platform")
    if type(data.get("slots")) is not int or not 2 <= data["slots"] <= 100:
        error("config/profile.json: slots must be an integer between 2 and 100")
    if data.get("status") != "planning_only_not_deployable":
        error("config/profile.json: status must indicate planning-only until deploy is verified")
    gameplay = data.get("gameplay")
    if not isinstance(gameplay, dict):
        error("config/profile.json: missing gameplay object")
        return
    loot = gameplay.get("loot")
    if not isinstance(loot, dict):
        error("config/profile.json: missing gameplay.loot object")
        return
    for key in ("general_target_multiplier", "food_medicine_target_multiplier"):
        val = loot.get(key)
        if type(val) not in (float, int) or not 0.1 <= val <= 5:
            error(f"config/profile.json: invalid gameplay.loot.{key}")
    hotspots = gameplay.get("hotspots")
    if not isinstance(hotspots, list) or not hotspots or not all(
        isinstance(p, str) and p.strip() for p in hotspots
    ):
        error("config/profile.json: gameplay.hotspots must be a nonempty list of places")
    print("OK: project profile syntax and basic constraints")


def check_mission() -> None:
    path = ROOT / "mission"
    if not path.exists():
        print("INFO: mission/ not created yet; no official DayZ mission files to validate")
        return
    files = sorted(
        p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in {".xml", ".json"}
    )
    if not files:
        print("INFO: mission/ has no DayZ XML/JSON files yet; no in-game validation performed")
        return

    for file in files:
        relative = file.relative_to(ROOT)
        try:
            raw = file.read_text(encoding="utf-8-sig")
            if file.suffix.lower() == ".json":
                json.loads(raw)
            else:
                if "<!DOCTYPE" in raw.upper() or "<!ENTITY" in raw.upper():
                    raise ValueError("XML document types/entities are not permitted")
                tree = ET.fromstring(raw)
                if file.name.lower() == "types.xml":
                    names = [
                        el.attrib["name"]
                        for el in tree.findall("type")
                        if el.attrib.get("name")
                    ]
                    duplicates = sorted({n for n in names if names.count(n) > 1})
                    if duplicates:
                        raise ValueError(f"duplicate item type names: {duplicates[:10]}")
            print(f"OK: {relative}")
        except (OSError, UnicodeError, ValueError, ET.ParseError, json.JSONDecodeError) as exc:
            error(f"{relative}: {exc}")
    print(f"INFO: checked {len(files)} mission XML/JSON file(s); game compatibility untested")


def main() -> int:
    check_profile()
    check_mission()
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} issue(s) found")
        return 1
    print("PASS: static checks only; no PS5 or Nitrado gameplay tests executed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
