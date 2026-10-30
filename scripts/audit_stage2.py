#!/usr/bin/env python3
"""Independent change-scope audit for the generated Livonia Stage 2 preview.

Rebuilds an expected tree from the pinned *official* input without invoking
the Stage 1/Stage 2 modification functions. Any unexpected XML/JSON change
fails the pipeline. This is NOT a PlayStation runtime or Nitrado test.
"""
from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from build_mission import FILES as STAGE1_FILES, UPSTREAM_COMMIT, read_upstream
from build_stage2 import EXTRA_ORIGINALS, STAGE2_FILES, fetch_original

ROOT = Path(__file__).resolve().parents[1]


def assert_equal(expected: object, actual: object, label: str) -> None:
    if expected != actual:
        raise AssertionError(
            f"{label}: unauthorized/unexpected difference versus the "
            "pinned official baseline + approved rules"
        )


def canonical(root: ET.Element) -> str:
    """Normalize attributes, while preserving meaningful element text."""
    return ET.canonicalize(ET.tostring(root, encoding="unicode"))


def official(path: str, source_dir: Path | None) -> bytes:
    if path in STAGE1_FILES:
        raw = read_upstream(path, source_dir)
    elif path in EXTRA_ORIGINALS:
        raw = fetch_original(path, source_dir)
    else:
        raise ValueError(f"Unapproved upstream path: {path}")
    if path.endswith(".xml") and (
        b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper()
    ):
        raise ValueError(f"Disallowed official XML DTD/entity: {path}")
    return raw


def index_types(root: ET.Element) -> dict[str, ET.Element]:
    assert_equal("types", root.tag, "Official types root")
    result = {}
    for node in root.findall("type"):
        name = node.get("name")
        if not name or name in result:
            raise AssertionError(f"Missing/duplicated CE type name: {name}")
        result[name] = node
    return result


def expected_types(raw: bytes, one: dict, two: dict) -> ET.Element:
    root = ET.fromstring(raw)
    items = index_types(root)
    for name in one["required_items"] + two["required_item_types"]:
        if name not in items:
            raise AssertionError(f"Official baseline lacks required type: {name}")

    # First stage: the original zero-nominal classes must stay disabled.
    for name, factor in one["loot_multipliers"].items():
        if name not in items:
            continue
        item = items[name]
        nominal, minimum = item.find("nominal"), item.find("min")
        if nominal is None or minimum is None:
            raise AssertionError(f"Invalid official type {name}")
        n, m = int(nominal.text), int(minimum.text)
        if not (0 <= m <= n):
            raise AssertionError(f"Invalid official nominal/min: {name}")
        if n:
            nominal.text = str(max(n, math.ceil(n * factor)))
            minimum.text = str(min(int(nominal.text), math.ceil(m * factor)) if m else 0)

    # Second stage: only the specified active classes may be adjusted.
    for name, factor in two["type_multipliers"].items():
        if name not in items:
            raise AssertionError(f"Stage 2 type not found: {name}")
        item = items[name]
        nominal, minimum = item.find("nominal"), item.find("min")
        if nominal is None or minimum is None:
            raise AssertionError(f"Missing nominal/min on {name}")
        n, m = int(nominal.text), int(minimum.text)
        if n <= 0 or not 0 <= m <= n:
            raise AssertionError(f"Stage 2 type disabled/invalid: {name}")
        nominal.text = str(math.ceil(n * factor))
        minimum.text = str(min(int(nominal.text), math.ceil(m * factor)))

    lifetime = items["UndergroundStash"].find("lifetime")
    if lifetime is None:
        raise AssertionError("UndergroundStash has no lifetime")
    lifetime.text = str(int(two["buried_stash_lifetime_days"]) * 86400)
    return root


def expected_spawns(raw: bytes, one: dict) -> ET.Element:
    root = ET.fromstring(raw)
    assert_equal("playerspawnpoints", root.tag, "Official spawn root")
    bubbles = root.find("./fresh/generator_posbubbles")
    if bubbles is None:
        raise AssertionError("Official fresh spawn group container absent")
    active = set(one["fresh_spawn_groups"])
    existing = [node.get("name") for node in bubbles.findall("group")]
    if len(existing) != len(set(existing)) or not active.issubset(existing):
        raise AssertionError("Unexpected official spawn group list")
    for node in list(bubbles.findall("group")):
        if node.get("name") not in active:
            bubbles.remove(node)
    return root


def expected_vehicles(raw: bytes, two: dict) -> ET.Element:
    root = ET.fromstring(raw)
    assert_equal("spawnabletypes", root.tag, "Official vehicle root")
    vehicles = {node.get("name"): node for node in root.findall("type")}
    for name, rule in two["vehicle_attachment_rules"].items():
        if name not in vehicles:
            raise AssertionError(f"Official vehicle missing: {name}")
        wheels = 0
        repair = 0
        for group in vehicles[name].findall("attachments"):
            for item in group.findall("item"):
                part = item.get("name", "")
                if "Wheel" in part and wheels < 4:
                    floor = float(rule["wheel_chance_first_four"])
                    wheels += 1
                elif part in {"SparkPlug", "CarBattery", "CarRadiator"}:
                    floor = float(rule["repair_part_chance_floor"])
                    repair += 1
                else:
                    continue
                before = float(item.attrib["chance"])
                target = max(before, floor)
                if not 0 <= target <= 1:
                    raise AssertionError(f"Invalid chance in official vehicle: {name}")
                item.set("chance", f"{target:.2f}")
        if wheels != 4 or repair < 1:
            raise AssertionError(f"Vehicle parts changed upstream: {name}")
    return root


def expected_gameplay(raw: bytes, two: dict) -> dict:
    original = json.loads(raw.decode("utf-8-sig"))
    data = original["PlayerData"]["StaminaData"]
    for key in ("staminaMax", "staminaKgToStaminaPercentPenalty"):
        data[key] = two["gameplay"][key]
    return original


def audit(stage: Path, source_dir: Path | None) -> None:
    one = json.loads((ROOT / "config/stage1_rules.json").read_text(encoding="utf-8"))
    two = json.loads((ROOT / "config/stage2_rules.json").read_text(encoding="utf-8"))
    expected = {
        "db/types.xml": expected_types(official("db/types.xml", source_dir), one, two),
        "cfgplayerspawnpoints.xml": expected_spawns(
            official("cfgplayerspawnpoints.xml", source_dir), one
        ),
        "cfgspawnabletypes.xml": expected_vehicles(
            official("cfgspawnabletypes.xml", source_dir), two
        ),
    }
    for path, tree in expected.items():
        actual = ET.parse(stage / path).getroot()
        assert_equal(canonical(tree), canonical(actual), path)
        print(f"PASS: complete independent XML change-scope comparison: {path}")

    gameplay = expected_gameplay(official("cfggameplay.json", source_dir), two)
    actual_gameplay = json.loads((stage / "cfggameplay.json").read_text(encoding="utf-8"))
    assert_equal(gameplay, actual_gameplay, "cfggameplay.json")
    print("PASS: complete independent JSON change-scope comparison: cfggameplay.json")

    report = json.loads((stage.parent / "change_report.json").read_text(encoding="utf-8"))
    assert_equal(UPSTREAM_COMMIT, report.get("pinned_commit"), "Report upstream commit")
    assert_equal(2, report.get("stage"), "Report stage")
    assert_equal(
        "PREVIEW ONLY - NO NITRADO DEPLOY / NO PLAYSTATION TEST",
        report.get("status"),
        "Report deployment safety status",
    )
    print("PASS: approved-rule-only Stage 2 preview. NO console or server tested.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, default=ROOT / "dist/stage2/dayzOffline.enoch")
    parser.add_argument("--source-dir", type=Path, default=None)
    args = parser.parse_args()
    audit(args.stage, args.source_dir)
