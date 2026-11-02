#!/usr/bin/env python3
"""BEILEYS47 V48: OFFLINE-ONLY preview of selective DayZ building placement changes.

No network, Nitrado API, server restart, world storage or persistence writes.
It deliberately does not alter item stacking or container behaviour.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

BALANCED = {
    ("HologramData", "disableIsCollidingBBoxCheck"),
    ("HologramData", "disableIsBaseViableCheck"),
    ("HologramData", "disableIsCollidingAngleCheck"),
    ("HologramData", "disableHeightPlacementCheck"),
    ("ConstructionData", "disableIsCollidingCheck"),
}
# These additional checks are more invasive; require explicit profile opt-in.
EXTENDED = BALANCED | {
    ("HologramData", "disableIsClippingRoofCheck"),
    ("HologramData", "disableIsPlacementPermittedCheck"),
    ("ConstructionData", "disablePerformRoofCheck"),
}

def apply_preview(original: bytes, profile: str = "balanced") -> tuple[bytes, list[str]]:
    if profile not in ("balanced", "extended"):
        raise ValueError("Unknown profile")
    data = json.loads(original)
    if not isinstance(data, dict) or not isinstance(data.get("BaseBuildingData"), dict):
        raise ValueError("Expected DayZ cfggameplay.json BaseBuildingData")
    before = copy.deepcopy(data)
    target = BALANCED if profile == "balanced" else EXTENDED
    changes = []
    for section, key in sorted(target):
        group = data["BaseBuildingData"].get(section)
        if not isinstance(group, dict) or type(group.get(key)) is not bool:
            raise ValueError(f"Unsupported/missing boolean field: {section}.{key}")
        if not group[key]:
            changes.append(f"BaseBuildingData.{section}.{key}")
        group[key] = True
    expected = copy.deepcopy(before)
    for section, key in target:
        expected["BaseBuildingData"][section][key] = True
    if data != expected:
        raise AssertionError("Unexpected non-target config change")
    output = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    assert json.loads(output) == expected
    return output, changes

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Locally downloaded current cfggameplay.json")
    parser.add_argument("output", type=Path, help="NEW output path (never overwrites)")
    parser.add_argument("--profile", choices=("balanced", "extended"), default="balanced")
    args = parser.parse_args()
    src, dst = args.input.resolve(), args.output.resolve()
    if src == dst:
        parser.error("Original input must not be modified")
    if dst.exists():
        parser.error("Output exists; refusing to overwrite")
    updated, changes = apply_preview(src.read_bytes(), args.profile)
    with dst.open("xb") as fp:
        fp.write(updated)
    print(f"OFFLINE ONLY; profile={args.profile}; fields changed={len(changes)}")
    for c in changes:
        print("  " + c)
    print("NOT INSTALLED ON NITRADO. PS5 TEST REQUIRED. NO ITEM STACKING GUARANTEE.")

if __name__ == "__main__":
    main()
