#!/usr/bin/env python3
"""Stage 6: fail-closed NON-DEPLOYABLE special-zone/restart planning report.

Checks the staged creative design against ZONA 47 schema, Stage 4.13 progressive
pilot and actual Stage 3 messages. Never emits object spawner, event XML,
scheduled restart, login material or any ready-to-install payload.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/stage6_special_zones.json"
BLUEPRINT = ROOT / "config/stage4_zone47_blueprint.json"
PILOT = ROOT / "config/stage4_13_pilot_protocol.json"
STAGE3 = ROOT / "dist/stage3/dayzOffline.enoch/db/messages.xml"
OUT = ROOT / "dist/stage6_special_zones/concept_review.json"

REQUIRED_ZONE_IDS = {
    "hidden_bunker": ("hq", "scenery_and_exploration"),
    "infected_cordon": ("checkpoint", "zombie_pressure"),
    "logistics_hotspot": ("logistics", "pvp_risk_reward"),
    "hidden_cache": ("secret", "exploration"),
}
REQUIRED_GATES = {
    "real_terrain_Y_known": False,
    "classnames_verified_on_console": False,
    "zombie_event_positions_verified": False,
    "loot_spawn_points_verified": False,
    "server_restarter_available_verified": False,
    "all_proposed_special_content_disabled": True,
    "no_scripted_horde_ai": True,
    "game_mods_supported": False,
    "no_new_models": True,
    "automatic_deployment_allowed": False,
}
ZONE_KEYS = {"id", "type", "blueprint_zone", "concept", "needed", "mechanic", "loot_status"}


def ensure(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError("STAGE6_BLOCKED: " + label)


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    ensure(type(value) is dict, "JSON must be an object")
    return value


def validate(data: dict, blueprint: dict, pilot: dict, messages: bytes) -> dict:
    ensure(data.get("stage") == 6 and data.get("map") == "Livonia" and
           data.get("target_platform") == "PlayStation 4 / PlayStation 5" and
           data.get("status") == "DESIGN_ONLY_NO_CONSOLE_OR_NITRADO_TEST",
           "project identity or safe status")
    ensure(data.get("source_blueprint") == "config/stage4_zone47_blueprint.json"
           and data.get("source_pilot") == "config/stage4_13_pilot_protocol.json",
           "unexpected source reference")
    ensure(data.get("deployment_allowed") is False and
           data.get("no_installable_files") is True and
           data.get("no_runtime_test") is True, "unsafe deployment declarations")
    ensure(type(data.get("constraints")) is dict and
           set(data["constraints"]) == set(REQUIRED_GATES),
           "unexpected/missing safety gate")
    for key, value in REQUIRED_GATES.items():
        ensure(data["constraints"][key] is value, "safety gate reversed: " + key)

    ensure(blueprint.get("codename") == "ZONA 47" and
           blueprint.get("map") == "Livonia" and
           blueprint.get("status") == "DESIGN_ONLY_NOT_INSTALLABLE" and
           blueprint["coordinate_system"]["terrain_surveyed"] is False and
           blueprint["balance"]["objects_spawner_implemented"] is False and
           blueprint["balance"]["spawned_loot_implemented"] is False,
           "blueprint no longer safely conceptual")
    zones = {x["id"]: x for x in blueprint["zones"]}
    ensure(len(zones) == len(blueprint["zones"]), "duplicate blueprint zones")
    specs = data.get("proposed_zones")
    ensure(type(specs) is list and len(specs) == len(REQUIRED_ZONE_IDS),
           "exactly four concepts required")
    seen = set()
    for spec in specs:
        ensure(type(spec) is dict and set(spec) == ZONE_KEYS,
               "extra fields could hide executable configuration")
        zid = spec.get("id")
        ensure(type(zid) is str and zid in REQUIRED_ZONE_IDS and zid not in seen,
               "unexpected/duplicate concept")
        seen.add(zid)
        blueprint_id, typ = REQUIRED_ZONE_IDS[zid]
        ensure(spec["blueprint_zone"] == blueprint_id and spec["type"] == typ and
               blueprint_id in zones, "concept references wrong sector")
        ensure(spec["loot_status"] == "NOT_CONFIGURED", "loot cannot be claimed installed")
        ensure(type(spec["concept"]) is str and 25 <= len(spec["concept"]) <= 240,
               "missing concept design")
        required = spec["needed"]
        ensure(type(required) is list and len(required) >= 2 and
               len(set(required)) == len(required) and
               all(type(x) is str and x for x in required),
               "missing/duplicate real-world gates")
        ensure(type(spec["mechanic"]) is str and
               spec["mechanic"] in {
                   "environmental_story_only",
                   "VANILLA_INFECTED_EVENT_REVIEW_REQUIRED",
                   "SCENERY_PLUS_CE_REVIEW_REQUIRED",
                   "SCENERY_ONLY",
               }, "unreviewed gameplay mechanic")
    ensure(seen == set(REQUIRED_ZONE_IDS), "missing special-zone scenario")
    ensure("verify_current_zombie_territories_xml" in next(
           x for x in specs if x["id"] == "infected_cordon")["needed"],
           "infected territory plan missing official env/zombie_territories.xml check")
    ensure("confirm_vanilla_CE_spawnable_positions" in next(
           x for x in specs if x["id"] == "logistics_hotspot")["needed"],
           "loot plan cannot promise new loot spawning without CE positions")

    ensure(pilot.get("status") == "CONSOLE_PILOT_PROTOCOL_ONLY_NO_RUNTIME_TRIAL" and
           pilot["site"]["terrain_not_yet_verified"] is True and
           pilot["safety"]["automatic_deployment_allowed"] is False,
           "Stage 4.13 evidence gate changed")
    phases = data.get("incremental_trial", {})
    ensure(type(phases) is dict and
           set(phases) == {"source", "agreed_phases", "props_planned",
                           "counts_are_schematic",
                           "require_console_terrain_and_asset_tests_before_any_spawner"}
           and phases["source"] == "config/stage4_13_pilot_protocol.json" and
           phases["agreed_phases"] == ["P1", "P3", "P5"] and
           phases["props_planned"] == [1, 3, 5] and
           phases["counts_are_schematic"] is True and
           phases["require_console_terrain_and_asset_tests_before_any_spawner"] is True,
           "unsafe pilot progression")
    ensure([x["phase"] for x in pilot["rollout"]] == phases["agreed_phases"] and
           [x["object_count"] for x in pilot["rollout"]] == phases["props_planned"],
           "pilot conflicts with approved Stage 4.13")

    restart = data.get("restart_design")
    ensure(type(restart) is dict and
           set(restart) == {
               "method", "trial_uptime_minutes",
               "trial_interval_is_relative_to_server_start_not_a_local_clock_time",
               "shutdown_messages_in_existing_stage3", "restart_implemented",
               "scheduled_start_confirmed", "must_confirm_provider_start_task_availability",
               "must_check_actual_server_timezone",
               "must_backup_mission_and_persistence_before_test", "source"},
           "unexpected/missing restart planning field")
    ensure(restart["method"] == "GRACEFUL_XML_SHUTDOWN_PLUS_PROVIDER_SCHEDULED_START_REVIEW" and
           type(restart["trial_uptime_minutes"]) is int and
           240 <= restart["trial_uptime_minutes"] <= 480 and
           restart["trial_interval_is_relative_to_server_start_not_a_local_clock_time"] is True and
           restart["shutdown_messages_in_existing_stage3"] is False and
           restart["restart_implemented"] is False and
           restart["scheduled_start_confirmed"] is False and
           restart["must_confirm_provider_start_task_availability"] is True and
           restart["must_check_actual_server_timezone"] is True and
           restart["must_backup_mission_and_persistence_before_test"] is True and
           restart["source"] == "https://server.nitrado.net/en-GB/guides/server-messages-for-dayz/",
           "restart status not safe")

    ensure(b"<!DOCTYPE" not in messages.upper() and b"<!ENTITY" not in messages.upper(),
           "messages XML DTD forbidden")
    message_root = ET.fromstring(messages)
    ensure(message_root.tag == "messages", "messages XML root mismatch")
    items = message_root.findall("message")
    ensure(len(items) == 3, "Stage 3 messages expected exactly 3")
    ensure(all(msg.findtext("shutdown") == "0" and
               msg.findtext("deadline") == "0" for msg in items),
           "Stage 3 must not already shutdown the server")
    return {
        "stage": 6,
        "status": "SPECIAL_ZONES_CONCEPT_ACCEPTED_NOT_INSTALLABLE",
        "map": "Livonia",
        "concepts": [{"id": x["id"], "blueprint_zone": x["blueprint_zone"],
                      "type": x["type"], "loot_implemented": False,
                      "zombie_behavior_implemented": False,
                      "console_placement_verified": False} for x in specs],
        "reviewed_concept_count": len(specs),
        "staged_object_pilot_counts": phases["props_planned"],
        "restart_method_reviewed": restart["method"],
        "restart_uptime_minutes_is_only_a_proposal": restart["trial_uptime_minutes"],
        "existing_stage3_shutdown_active": False,
        "real_zombie_territory_positions_confirmed": False,
        "loot_positions_confirmed": False,
        "terrain_and_building_classes_confirmed": False,
        "live_PS5_gameplay_tested": False,
        "live_Nitrado_accessed": False,
        "may_generate_live_dayz_files": False,
        "deployment_allowed": False,
        "next_gate": "Nitrado trial + PS5 field evidence; verify classnames, real Y, CE infected event spawns, loot positions, backups and safe startup task",
    }


def build(output: Path = OUT) -> dict:
    report = validate(read(CONFIG), read(BLUEPRINT), read(PILOT), STAGE3.read_bytes())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: 4 reviewed concept zones, approved 1→3→5 pilot, three safe Stage 3 messages.")
    print("NO bunker, horde, special loot or scheduled restart is deployed or verified.")
    return report


if __name__ == "__main__":
    build()
