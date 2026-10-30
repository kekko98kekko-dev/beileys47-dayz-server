#!/usr/bin/env python3
"""Stage 5: reproducible OFFLINE balancing scorecard from real generated CE XML.

This is not a loot simulator: CE nominal is a configuration target, not a
per-hour spawn promise. No access to Nitrado, no PlayStation testing, no deploy.
"""
from __future__ import annotations

import copy
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from build_mission import UPSTREAM_COMMIT

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = DIST / "stage5_gameplay/ce_balance_scorecard.json"


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("STAGE5_BLOCKED: " + reason)


def load_types(path: Path) -> dict[str, ET.Element]:
    raw = path.read_bytes()
    need(b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(),
         "Disallowed XML DTD")
    root = ET.fromstring(raw)
    need(root.tag == "types", "Unexpected CE root")
    items: dict[str, ET.Element] = {}
    for node in root.findall("type"):
        name = node.get("name")
        need(bool(name) and name not in items, "Unidentified or duplicate CE class")
        for field in ("nominal", "min"):
            child = node.find(field)
            need(child is not None and child.text is not None, f"Missing {name}.{field}")
            try:
                number = int(child.text)
            except ValueError as exc:
                raise ValueError(f"STAGE5_BLOCKED: Noninteger {name}.{field}") from exc
            need(number >= 0, f"Negative {name}.{field}")
        need(int(node.findtext("min")) <= int(node.findtext("nominal")),
             f"Invalid minimum for {name}")
        items[name] = node
    need(len(items) >= 100, "CE item inventory suspiciously short")
    return items


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    need(isinstance(result, dict), f"Not a JSON object: {path.name}")
    return result


def build(dist: Path = DIST, output: Path = OUT) -> dict:
    one = dist / "stage1"
    two = dist / "stage2"
    three = dist / "stage3"
    t1 = load_types(one / "dayzOffline.enoch/db/types.xml")
    t2 = load_types(two / "dayzOffline.enoch/db/types.xml")
    t3_path = three / "dayzOffline.enoch/db/types.xml"
    t3 = load_types(t3_path)
    need(set(t1) == set(t2) == set(t3), "CE class inventory changed across stages")
    need(list(t1) == list(t2) == list(t3), "CE class ordering changed")
    need(t3_path.read_bytes() == (two / "dayzOffline.enoch/db/types.xml").read_bytes(),
         "Stage 3 must inherit Stage 2 types.xml byte-for-byte")

    report1 = read_json(one / "change_report.json")
    report2 = read_json(two / "change_report.json")
    report3 = read_json(three / "change_report.json")
    rules1 = read_json(ROOT / "config/stage1_rules.json")
    rules2 = read_json(ROOT / "config/stage2_rules.json")
    rules3 = read_json(ROOT / "config/stage3_rules.json")
    need(report1.get("commit") == report2.get("pinned_commit") ==
         report3.get("pinned_commit") == UPSTREAM_COMMIT, "Pinned baseline mismatch")
    need(report2.get("stage") == 2 and report3.get("stage") == 3,
         "Unexpected report stages")
    need(report3.get("inherited_from") == "STAGE2_BYTE_FOR_BYTE",
         "Stage 3 inheritance not documented")
    need(report2.get("stage1_report") == report1, "Stage 2 embedded Stage 1 report mismatch")

    stage1_changes = report1.get("loot_changes")
    need(isinstance(stage1_changes, list), "Missing Stage 1 change ledger")
    stage1_by_name = {}
    for change in stage1_changes:
        need(isinstance(change, dict) and isinstance(change.get("name"), str) and
             change["name"] not in stage1_by_name, "Invalid Stage 1 change ledger")
        stage1_by_name[change["name"]] = change
    need(set(stage1_by_name) == set(rules1["loot_multipliers"]),
         "Stage 1 change ledger differs from chosen loot rules")
    actual_stage1 = []
    for name, change in stage1_by_name.items():
        if change["status"] == "modified":
            need(name in t1 and
                 [int(t1[name].findtext("nominal")), int(t1[name].findtext("min"))]
                 == change["new"], f"Stage 1 report mismatch: {name}")
            actual_stage1.append({"class": name, "vanilla": change["old"],
                                  "stage1": change["new"]})
        else:
            need(change["status"] in ("not_found_skipped", "zero_nominal_skipped"),
                 f"Unexpected Stage 1 status: {name}")

    ledger = report2.get("additional_loot_and_stash_changes")
    need(isinstance(ledger, list), "Stage 2 report lacks CE ledger")
    by_name = {}
    for change in ledger:
        need(isinstance(change, dict) and isinstance(change.get("name"), str)
             and change["name"] not in by_name, "Duplicate or invalid Stage 2 CE ledger")
        by_name[change["name"]] = change
    target_names = set(rules2["type_multipliers"])
    need(set(by_name) == target_names | {"UndergroundStash"},
         "Unexpected Stage 2 CE change list")

    changed = []
    for name in t1:
        before, after = t1[name], t2[name]
        previous = copy.deepcopy(after)
        if name in target_names:
            multiplier = rules2["type_multipliers"][name]
            need(type(multiplier) in (int, float) and math.isfinite(multiplier) and
                 1 <= multiplier <= 1.5, f"Invalid multiplier {name}")
            old_nominal, old_min = int(before.findtext("nominal")), int(before.findtext("min"))
            new_nominal, new_min = int(after.findtext("nominal")), int(after.findtext("min"))
            expected_nominal = math.ceil(old_nominal * multiplier)
            expected_min = min(expected_nominal, math.ceil(old_min * multiplier))
            need(old_nominal > 0 and new_nominal == expected_nominal and
                 new_min == expected_min, f"Stage 2 CE boost differs from rules: {name}")
            entry = by_name[name]
            need(entry.get("nominal") == [old_nominal, new_nominal] and
                 entry.get("min") == [old_min, new_min] and
                 entry.get("factor") == multiplier,
                 f"Stage 2 ledger does not match XML: {name}")
            previous.find("nominal").text = str(old_nominal)
            previous.find("min").text = str(old_min)
            changed.append({
                "class": name,
                "nominal": [old_nominal, new_nominal],
                "minimum": [old_min, new_min],
                "configured_factor": multiplier,
                "nominal_delta": new_nominal - old_nominal,
            })
        elif name == "UndergroundStash":
            original_life = int(before.findtext("lifetime"))
            updated_life = int(after.findtext("lifetime"))
            expected_life = int(rules2["buried_stash_lifetime_days"]) * 86400
            need(expected_life >= original_life and updated_life == expected_life and
                 by_name[name].get("lifetime_seconds") == [original_life, updated_life],
                 "UndergroundStash lifetime mismatch")
            previous.find("lifetime").text = str(original_life)
        # Validate ALL other CE child fields/attributes, not just target fields.
        need(ET.tostring(previous) == ET.tostring(before),
             f"Unauthorized Stage 2 CE change: {name}")

    stage3_events = report3.get("event_changes")
    need(isinstance(stage3_events, list) and len(stage3_events) == 2,
         "Stage 3 event report missing")
    event_index = {x.get("event"): x for x in stage3_events}
    need(len(event_index) == 2 and set(event_index) == set(rules3["events"]),
         "Stage 3 unexpected event changes")
    event_delta = 0
    for name, rule in rules3["events"].items():
        detail = event_index[name]
        need(detail["vanilla_nominal"] == rule["vanilla_nominal"] and
             detail["target_nominal"] == rule["target_nominal"],
             f"Event mismatch: {name}")
        event_delta += detail["target_nominal"] - detail["vanilla_nominal"]

    nominal1 = sum(int(node.findtext("nominal")) for node in t1.values())
    nominal2 = sum(int(node.findtext("nominal")) for node in t2.values())
    delta = sum(x["nominal_delta"] for x in changed)
    need(nominal2 - nominal1 == delta and delta >= 0,
         "Aggregate CE nominal mismatch")
    result = {
        "stage": 5,
        "status": "OFFLINE_BALANCE_SCORECARD_NOT_RUNTIME_VALIDATED",
        "source_baseline_commit": UPSTREAM_COMMIT,
        "active_ce_classes_stage1": sum(int(n.findtext("nominal")) > 0 for n in t1.values()),
        "total_ce_class_records": len(t1),
        "stage1_changed_classes": sorted(actual_stage1, key=lambda x: x["class"]),
        "stage2_changed_classes": sorted(changed, key=lambda x: x["class"]),
        "stage2_change_count": len(changed),
        "stage1_all_class_nominal_sum": nominal1,
        "stage2_all_class_nominal_sum": nominal2,
        "stage2_nominal_sum_delta": delta,
        "stage2_nominal_sum_delta_pct": round(100 * delta / nominal1, 3) if nominal1 else None,
        "stage3_event_nominal_delta": event_delta,
        "stage3_event_changes": stage3_events,
        "stage3_types_byte_equal_stage2": True,
        "every_unselected_ce_class_unchanged_stage1_to_stage2": True,
        "in_game_spawn_rates_verified": False,
        "playstation_compatibility_verified": False,
        "nitrado_server_accessed": False,
        "object_spawner_included": False,
        "deployment_allowed": False,
        "interpretation": [
            "CE nominal is a configured target for individual types, NOT items/hour or a guarantee of visible world loot.",
            "A sum across CE classes is a static configuration checksum-like indicator, NOT a world item count.",
            "Dynamic event nominal values are configuration requests, NOT guaranteed simultaneous crash/convoy events.",
            "Players online, economy categories, zone usage, lifetime, restock, storage and engine limits affect actual experience.",
            "The design remains subject to incremental Nitrado and PS5 playtesting before any public release.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PASS: Stage 5 static scorecard: {len(changed)} CE boosts; delta nominal={delta}")
    print("IMPORTANT: nominal counts are NOT observed loot rates; NO console test or deployment.")
    return result


if __name__ == "__main__":
    build()
