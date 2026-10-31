#!/usr/bin/env python3
"""Stage 8: grounded DayZ PS5 bunker feasibility, NOT an Object Spawner.

Cross-check official Livonia map group candidate names, third-party P3D
visual metadata, and the abstract Stage 7 graph. Fail closed for fake
console approval or unsafe legacy bunker reuse. No provider operations.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/stage8_bunker_feasibility.json"
MAP = ROOT / "config/stage4_asset_candidates.json"
P3D = ROOT / "config/stage4_11_p3d_role_candidates.json"
STAGE7 = ROOT / "config/stage7_bunker_layout.json"
PILOT = ROOT / "config/stage4_13_pilot_protocol.json"
OUT = ROOT / "dist/stage8_bunker_feasibility/feasibility_review.json"

REFERENCE_FILES = {
    "stage7": "config/stage7_bunker_layout.json",
    "official_map_candidates": "config/stage4_asset_candidates.json",
    "third_party_p3d_catalog": "config/stage4_11_p3d_role_candidates.json",
    "stage4_pilot": "config/stage4_13_pilot_protocol.json",
}
OPTIONS = {
    "vanilla_site_reuse": ("USE_EXISTING_ACCESSIBLE_VANILLA_WORLD_GEOMETRY", False),
    "surface_command": ("SMALL_VANILLA_CLASS_CANDIDATE_COMPOUND", True),
    "underground_assembled": ("UNVERIFIED_COMPLEX_BUNKER_EXPERIMENT", False),
}
REQUIRED_OPTION_GATES = {
    "vanilla_site_reuse": {"actual_entrance_and_exit_walkthrough", "verify_no_player_traps"},
    "surface_command": {"prove_console_spawnability_per_class", "walk_all_real_exits"},
    "underground_assembled": {"two_independent_exits_playtested", "test_item_floor_behavior",
                              "test_persistence_and_FPS"},
}
REQUIRED_TRUE = {
    "verify_normal_exit_without_logout",
    "verify_dropped_items_remain_accessible",
    "verify_server_restart_and_persistence",
    "verify_PS5_and_PS4_separately",
    "verify_collision_terrain_water_and_vegetation",
}
REQUIRED_FALSE = {
    "verify_visual_model_classname_is_spawnable", "current_server_exists", "Y_measured",
    "runtime_classnames_confirmed", "runtime_exits_tested",
    "dropped_item_persistence_tested", "runtime_FPS_tested",
    "addon_workshop_mods_installed", "deploy_allowed",
}


def must(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("STAGE8_BLOCKED: " + reason)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    must(type(value) is dict, "expected an object")
    return value


def validate(data: dict, map_inventory: dict, p3d_inventory: dict,
             stage7: dict, pilot: dict) -> dict:
    must(data.get("stage") == 8 and data.get("codename") == "ZONA 47 — bunker feasibility"
         and data.get("status") == "SOURCE_SCREENING_ONLY_NOT_CONSOLE_PROVEN",
         "stage identity")
    must(data.get("reference_files") == REFERENCE_FILES, "provenance references")
    must(data.get("no_installable_json") is True and data.get("no_nitrado_requests") is True
         and data.get("no_live_tests") is True and data.get("deployment_allowed") is False,
         "no-deploy protections")
    must(stage7.get("stage") == 7 and stage7.get("deployment_allowed") is False
         and stage7.get("artifacts", {}).get("object_spawner_json_generated") is False,
         "Stage 7 schema/physical evidence not as expected")
    must(stage7.get("status") == "SCHEMATIC_TOPOLOGY_NOT_OBJECT_SPAWNER"
         and len(stage7.get("entrances", [])) == 3
         and all(x.get("ground_y") is None and x.get("object_classname") is None
                 and x.get("console_verified") is False for x in stage7.get("rooms", [])),
         "Stage 7 contains claimed real geometry")
    must(pilot.get("status") == "CONSOLE_PILOT_PROTOCOL_ONLY_NO_RUNTIME_TRIAL"
         and pilot["site"]["terrain_not_yet_verified"] is True
         and pilot["safety"]["automatic_deployment_allowed"] is False,
         "old approved runtime gate changed")
    gates = data.get("release_gates")
    must(type(gates) is dict and set(gates) ==
         REQUIRED_TRUE | REQUIRED_FALSE |
         {"planned_first_pilot_counts", "minimum_real_exits_walked_per_selected_bunker"},
         "wrong test-gate inventory")
    must(gates["planned_first_pilot_counts"] == [1, 3, 5]
         and [x["object_count"] for x in pilot["rollout"]] == [1, 3, 5],
         "unsafe accelerated object deployment")
    must(type(gates["minimum_real_exits_walked_per_selected_bunker"]) is int
         and gates["minimum_real_exits_walked_per_selected_bunker"] == 2,
         "a real bunker requires at least two tested exits by design")
    for name in REQUIRED_TRUE:
        must(gates[name] is True, "missing mandatory real-world test: " + name)
    for name in REQUIRED_FALSE:
        must(gates[name] is False, "unverified safety claim enabled: " + name)

    evidence = data.get("source_review", {})
    must(type(evidence) is dict
         and evidence.get("bohemia_object_spawner") ==
         "https://community.bistudio.com/wiki/DayZ:Object_Spawner"
         and evidence.get("console_bunker_historical_example") ==
         "https://github.com/scalespeeder/DayZ-LIVONIA-Yugovostok-Underground-Bunker-Custom-Json-File-For-PC-and-Console",
         "unsafe or missing source citations")
    must(evidence.get("example_test_platform") == "PC Livonia local server"
         and evidence.get("example_tested_game_version") == "1.16"
         and evidence.get("example_limitation") == "EXIT_REQUIRES_LOGOUT_LOGIN"
         and evidence.get("example_secondary_limitation") ==
         "DROPPED_ITEMS_MAY_REAPPEAR_ON_SURFACE"
         and evidence.get("example_is_verified_for_current_ps5") is False
         and evidence.get("example_content_copied") is False
         and evidence.get("official_direct_structure_p3d_paths_allowed") is False
         and evidence.get("third_party_model_paths_spawnable_directly") is False,
         "unverified third-party bunker or direct P3D path considered safe")

    must(map_inventory.get("status") == "CANDIDATE_CLASS_NAMES_ONLY_NOT_RUNTIME_VERIFIED"
         and map_inventory.get("pinned_commit") ==
         "f220b2918b1d79a5055b1ee9be70c0ec1516e876",
         "map group inventory provenance")
    models = map_inventory.get("models")
    must(type(models) is list and len(models) >= 10, "map class catalog incomplete")
    classnames = {}
    for model in models:
        name = model.get("name")
        must(type(name) is str and name.startswith("Land_") and name not in classnames
             and model.get("object_spawner_confirmed") is False
             and model.get("ps4_ps5_runtime_confirmed") is False
             and model.get("ground_elevation_known") is False,
             "guessed or approved map object class")
        classnames[name] = model

    must(p3d_inventory.get("status") ==
         "ROLE_MATCHED_VISUAL_SIZE_CANDIDATES_NO_CONSOLE_CLASS_PROOF",
         "P3D provenance changed")
    visual = p3d_inventory.get("reference_model_catalog")
    must(type(visual) is list and len(visual) >= 10, "visual catalog incomplete")
    p3d_classes = {}
    for model in visual:
        label = model.get("model_class")
        path = model.get("p3d_path")
        must(type(label) is str and label not in p3d_classes
             and type(path) is str and path.startswith(("structures/", "structures_bliss/"))
             and path.lower().endswith(".p3d")
             and model.get("runtime_object_spawner_classname") is None
             and model.get("can_use_direct_p3d_path_in_object_spawner") is False
             and model.get("ps4_ps5_spawning_tested") is False
             and model.get("collision_verified") is False,
             "unverified 3D metadata claimed as spawnable")
        p3d_classes[label] = model

    cls = data.get("surface_classname_review_candidates")
    must(type(cls) is list and cls == ["Land_Mil_GuardHouse3", "Land_Mil_Guardhouse1"]
         and all(name in classnames and classnames[name]["zone"] == "hq" for name in cls),
         "new or mislocated surface class candidates")
    visual_ref = data.get("interior_model_visual_references")
    must(type(visual_ref) is list and visual_ref == ["Desk_Office", "Desk_Globe"]
         and all(name in p3d_classes for name in visual_ref),
         "false interior model evidence")

    plans = data.get("options")
    must(type(plans) is list and len(plans) == len(OPTIONS), "three distinct strategies needed")
    found = set()
    for opt in plans:
        must(type(opt) is dict and set(opt) ==
             {"id", "method", "bunker_underground_guaranteed",
              "suggested_for_first_rental", "needs"}, "unexpected strategy parameters")
        ident = opt.get("id")
        must(type(ident) is str and ident in OPTIONS and ident not in found,
             "missing/duplicate strategy")
        found.add(ident)
        method, suggested = OPTIONS[ident]
        must(opt["method"] == method and opt["suggested_for_first_rental"] is suggested
             and opt["bunker_underground_guaranteed"] is False,
             "false underground promise")
        needs = opt["needs"]
        must(type(needs) is list and len(needs) >= 4
             and all(type(s) is str and s for s in needs)
             and len(needs) == len(set(needs))
             and REQUIRED_OPTION_GATES[ident].issubset(needs),
             "missing real-world route or class tests")
    must(found == set(OPTIONS), "not all feasibility strategies reviewed")

    return {
        "stage": 8, "status": "SOURCE_AUDIT_READY_PHYSICAL_BUNKER_UNPROVEN",
        "selected_first_rental_strategy": "surface_command",
        "strategy_count": len(plans),
        "map_group_only_land_candidate_count": len(classnames),
        "p3d_visual_metadata_only_model_count": len(p3d_classes),
        "surface_classnames_to_test_not_install": [
            {"name": name, "provenance": "OFFICIAL_LIVONIA_MAP_GROUP_NAME_ONLY",
             "console_spawner_tested": False, "terrain_Y_measured": False,
             "collision_tested": False} for name in cls
        ],
        "interior_p3d_visuals_not_directly_spawnable": [
            {"visual_name": label, "model_path": p3d_classes[label]["p3d_path"],
             "spawnable_classname": None,
             "direct_p3d_spawn_allowed": False} for label in visual_ref
        ],
        "existing_stage7_room_count": len(stage7["rooms"]),
        "stage7_entries_on_paper": len(stage7["entrances"]),
        "existing_pilot_counts_unchanged": [1, 3, 5],
        "historical_bunker_example_risk": "TESTED_OLD_PC_VERSION_AND_EXIT_REQUIRES_LOGOUT",
        "historical_bunker_reused": False,
        "any_reliable_PS5_bunker_class_verified": False,
        "real_reachable_exits_verified": 0,
        "terrain_Y_verified": False,
        "real_loot_and_item_persistence_verified": False,
        "deployable_object_spawner_emitted": False,
        "deployment_allowed": False,
        "next_action": "Private Nitrado PS5 vanilla test, real field survey and a single low-risk class pilot with rollback; no underground import",
        "limitations": [
            "Names found in Livonia mapgrouppos.xml are not proof the Object Spawner can create them on PS5.",
            "Third-party visual P3D paths under structures/ cannot be pasted directly as Object Spawner model paths.",
            "Old third-party underground bunker has documented normal-exit and dropped-item problems; do not reuse blindly.",
            "Stage 7's ten rooms and three entrances are abstract graph nodes, not verified physical rooms.",
            "If no safe console geometry works underground, prefer an above-ground command compound.",
        ],
    }


def build(output: Path = OUT) -> dict:
    report = validate(load(CONFIG), load(MAP), load(P3D), load(STAGE7), load(PILOT))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: stage 8 verified evidence provenance and no unsafe bunker approval.")
    print("NOT TESTED: exits, PS5 object classes, terrain, collision, item drops and Nitrado.")
    return report


if __name__ == "__main__":
    build()
