#!/usr/bin/env python3
"""Build a reversible Livonia Stage-1 patch from pinned Bohemia originals.

NO Nitrado network operations or credentials. Output is for manual testing only.
"""
from __future__ import annotations

import argparse
import json
import math
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from zip_deterministic import add_bytes

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "f220b2918b1d79a5055b1ee9be70c0ec1516e876"
UPSTREAM_BASE = (
    "https://raw.githubusercontent.com/BohemiaInteractive/"
    f"DayZ-Central-Economy/{UPSTREAM_COMMIT}/dayzOffline.enoch/"
)
FILES = ("db/types.xml", "cfgplayerspawnpoints.xml")


def read_upstream(path: str, source_dir: Path | None) -> bytes:
    if path not in FILES:
        raise ValueError(f"Unexpected upstream file {path}")
    if source_dir:
        return (source_dir / path).read_bytes()
    request = urllib.request.Request(UPSTREAM_BASE + path, headers={
        "User-Agent": "BEILEYS47-DayZ-Stage1/1.0", "Accept": "application/xml"
    })
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(3 * 1024 * 1024 + 1)
    if len(content) > 3 * 1024 * 1024:
        raise ValueError("Unexpectedly large upstream file")
    return content


def parse_xml(data: bytes, name: str) -> ET.Element:
    # Prevent DTD/entity use in downloaded input.
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError(f"Disallowed XML entities in {name}")
    return ET.fromstring(data)


def modify_types(root: ET.Element, rules: dict) -> list[dict]:
    if root.tag != "types":
        raise ValueError("Unexpected types.xml root")
    lookup = {}
    for item in root.findall("type"):
        name = item.get("name")
        if name in lookup:
            raise ValueError(f"Duplicate DayZ item {name}")
        lookup[name] = item
    changes = []
    required = set(rules["required_items"])
    missing_required = sorted(required - set(lookup))
    if missing_required:
        raise ValueError(f"Essential item classes no longer exist: {missing_required}")
    for name, multiplier in rules["loot_multipliers"].items():
        if not isinstance(multiplier, (int, float)) or not 1.0 <= multiplier <= 2.0:
            raise ValueError(f"Invalid multiplier for {name}")
        item = lookup.get(name)
        if item is None:
            changes.append({"name": name, "status": "not_found_skipped"})
            continue
        nominal = item.find("nominal")
        minimum = item.find("min")
        if nominal is None or minimum is None:
            raise ValueError(f"Missing CE nominal/min for {name}")
        old_nominal, old_min = int(nominal.text), int(minimum.text)
        if old_nominal < 0 or old_min < 0 or old_min > old_nominal:
            raise ValueError(f"Invalid vanilla CE limits for {name}")
        # Never activate intentionally disabled or limited loot types.
        if old_nominal == 0:
            changes.append({"name": name, "status": "zero_nominal_skipped"})
            continue
        new_nominal = max(old_nominal, math.ceil(old_nominal * multiplier))
        new_min = min(new_nominal, math.ceil(old_min * multiplier)) if old_min else 0
        nominal.text, minimum.text = str(new_nominal), str(new_min)
        changes.append({"name": name, "status": "modified",
                        "old": [old_nominal, old_min], "new": [new_nominal, new_min]})
    if len([r for r in changes if r["status"] == "modified"]) < 3:
        raise ValueError("Too few actual loot changes: upstream may be incompatible")
    return changes


def modify_spawns(root: ET.Element, rules: dict) -> dict:
    if root.tag != "playerspawnpoints":
        raise ValueError("Unexpected player spawn points root")
    fresh = root.find("fresh")
    if fresh is None:
        raise ValueError("Missing fresh spawn section")
    bubbles = fresh.find("generator_posbubbles")
    if bubbles is None:
        raise ValueError("Missing fresh spawn bubbles")
    group_nodes = bubbles.findall("group")
    group_names = [node.get("name") for node in group_nodes]
    if not group_names or None in group_names or len(group_names) != len(set(group_names)):
        raise ValueError("Duplicate, unnamed or missing official fresh spawn group")
    groups = dict(zip(group_names, group_nodes))
    selected = rules["fresh_spawn_groups"]
    if not isinstance(selected, list) or len(selected) < 2 or len(selected) != len(set(selected)):
        raise ValueError("Choose at least two unique spawn groups")
    missing = set(selected) - set(groups)
    if missing:
        raise ValueError(f"Requested Livonia fresh spawn groups missing: {sorted(missing)}")
    for name, node in groups.items():
        if name not in selected:
            bubbles.remove(node)
    surviving = bubbles.findall("group")
    if sum(len(g.findall("pos")) for g in surviving) < 8:
        raise ValueError("Too few existing official spawn positions remain")
    # Leave fresh spawn safety distances, hop spawns, and all coordinates untouched.
    return {"vanilla_groups": list(groups), "active_groups": selected,
            "positions": sum(len(g.findall("pos")) for g in surviving),
            "hop_spawns_untouched": True}


def run(output: Path, source_dir: Path | None) -> None:
    rules = json.loads((ROOT / "config" / "stage1_rules.json").read_text(encoding="utf-8"))
    out_mission = output / "dayzOffline.enoch"
    report = {"origin": "BohemiaInteractive/DayZ-Central-Economy",
              "commit": UPSTREAM_COMMIT,
              "status": "NOT TESTED ON PLAYSTATION / DO NOT AUTO-DEPLOY",
              "files": list(FILES)}
    for path in FILES:
        xml = parse_xml(read_upstream(path, source_dir), path)
        if path == "db/types.xml":
            report["loot_changes"] = modify_types(xml, rules)
        else:
            report["fresh_spawns"] = modify_spawns(xml, rules)
        dest = out_mission / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Preserve the original XML element order and all non-target values.
        ET.ElementTree(xml).write(dest, encoding="utf-8", xml_declaration=True)
        ET.parse(dest)
    output.mkdir(parents=True, exist_ok=True)
    (output / "change_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    archive = output / "beileys47-livonia-stage1.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipout:
        for path in FILES:
            dest = out_mission / path
            add_bytes(zipout, f"dayzOffline.enoch/{path}", dest.read_bytes())
        add_bytes(zipout, "change_report.json", (output / "change_report.json").read_bytes())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Stage-1 preview ready: {archive}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--source-dir", type=Path,
                        help="Optional folder of official XMLs for offline tests")
    args = parser.parse_args()
    run(args.output, args.source_dir)
