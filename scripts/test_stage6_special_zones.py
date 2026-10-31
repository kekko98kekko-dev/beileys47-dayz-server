#!/usr/bin/env python3
"""Adversarial regression for Stage 6 nondeployable special-zone design."""
from __future__ import annotations

import copy
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build_stage6_special_zones import (
    BLUEPRINT, CONFIG, PILOT, STAGE3, build, read, validate,
)


def refuse(data: dict, blueprint: dict, pilot: dict, messages: bytes, expected: str) -> None:
    try:
        validate(data, blueprint, pilot, messages)
    except ValueError as exc:
        assert expected in str(exc), (expected, str(exc))
    else:
        raise AssertionError("Unsafe Stage 6 configuration was accepted: " + expected)


def run() -> None:
    design, blueprint, pilot = read(CONFIG), read(BLUEPRINT), read(PILOT)
    msg = STAGE3.read_bytes()
    with tempfile.TemporaryDirectory(prefix="stage6-concepts-only-") as temp:
        out = Path(temp) / "stage6_review.json"
        report = build(out)
        assert json.loads(out.read_text(encoding="utf-8")) == report
        assert report["reviewed_concept_count"] == 4
        assert report["staged_object_pilot_counts"] == [1, 3, 5]
        assert report["deployment_allowed"] is False
        assert report["may_generate_live_dayz_files"] is False
        assert report["existing_stage3_shutdown_active"] is False
        assert report["real_zombie_territory_positions_confirmed"] is False
        assert report["loot_positions_confirmed"] is False

    changed = copy.deepcopy(design)
    changed["deployment_allowed"] = True
    refuse(changed, blueprint, pilot, msg, "unsafe deployment declarations")

    changed = copy.deepcopy(design)
    changed["constraints"]["real_terrain_Y_known"] = True
    refuse(changed, blueprint, pilot, msg, "safety gate reversed")

    changed = copy.deepcopy(design)
    changed["proposed_zones"][0]["class_name"] = "Land_UnknownBunker"
    refuse(changed, blueprint, pilot, msg, "extra fields could hide executable configuration")

    changed = copy.deepcopy(design)
    changed["proposed_zones"][1]["needed"].remove("verify_current_zombie_territories_xml")
    refuse(changed, blueprint, pilot, msg, "official env/zombie_territories.xml")

    changed = copy.deepcopy(design)
    changed["proposed_zones"][2]["loot_status"] = "READY"
    refuse(changed, blueprint, pilot, msg, "loot cannot be claimed installed")

    changed = copy.deepcopy(design)
    changed["incremental_trial"]["props_planned"] = [1, 3, 26]
    refuse(changed, blueprint, pilot, msg, "unsafe pilot progression")

    changed = copy.deepcopy(design)
    changed["restart_design"]["restart_implemented"] = True
    refuse(changed, blueprint, pilot, msg, "restart status not safe")

    changed = copy.deepcopy(design)
    changed["restart_design"]["trial_uptime_minutes"] = 0
    refuse(changed, blueprint, pilot, msg, "restart status not safe")

    tree = ET.fromstring(msg)
    tree.find("message/shutdown").text = "1"
    tree.find("message/deadline").text = "360"
    refuse(design, blueprint, pilot, ET.tostring(tree), "Stage 3 must not already shutdown")

    bp = copy.deepcopy(blueprint)
    bp["coordinate_system"]["terrain_surveyed"] = True
    refuse(design, bp, pilot, msg, "blueprint no longer safely conceptual")

    pt = copy.deepcopy(pilot)
    pt["rollout"][2]["object_count"] = 26
    refuse(design, blueprint, pt, msg, "pilot conflicts")

    print("PASS: Stage 6 concepts, pilot, zombie territory and restarter guards.")
    print("NO DayZ event, Object Spawner or messages.xml is emitted/deployed.")


if __name__ == "__main__":
    run()
