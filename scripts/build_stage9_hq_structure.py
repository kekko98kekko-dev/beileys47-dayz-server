#!/usr/bin/env python3
"""Stage 9: offline, source-backed first HQ structure feasibility comparison.

No world Y, no approved console class, no physical collision/FPS evidence,
no Object Spawner or Nitrado operations. Bounding spheres are VISUAL only.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/stage9_hq_structure_pilot.json"
STAGE8 = ROOT / "config/stage8_bunker_feasibility.json"
CLASS_NAMES = ROOT / "config/stage4_asset_candidates.json"
VISUAL = ROOT / "config/stage4_9_p3d_bbox_evidence.json"
MICRO = ROOT / "config/stage4_zone47_micro_layout.json"
PILOT = ROOT / "config/stage4_13_pilot_protocol.json"
OUTPUT = ROOT / "dist/stage9_hq_structure"
CHOICES = ("Land_Mil_GuardHouse3", "Land_Mil_Guardhouse1")
NEIGHBORS = ("hq_02", "hq_03", "hq_04", "hq_05")
REQUIRED_TESTS = (
    ("01_provider_baseline", "Livonia PS4/PS5 server reachable and matching DayZ version"),
    ("02_vanilla", "Vanilla start and spawn observed on PS5"),
    ("03_originals", "Download real mission files and inspect actual backup/restore options"),
    ("04_stage1", "Stage 1 verified live with original-file rollback"),
    ("05_stage2", "Stage 2 verified live including cfggameplay and persistence"),
    ("06_stage3", "Stage 3 messages and events verified live with rollback"),
    ("07_site", "HQ physical site surveyed; world ground Y and obstructions recorded privately"),
    ("08_pilot", "Stage 4.13 one-three-five low-impact pilot passed separately"),
    ("09_class", "One selected Land_ classname recognized in PS5 server Object Spawner/RPT"),
    ("10_visibility", "Visual prop visible and grounded after normal restart"),
    ("11_exit_a", "Normal first exit traversed without relog or glitches"),
    ("12_exit_b", "Independent second exit traversed without relog or glitches"),
    ("13_collision", "Collision, approach, stairs, equipment and dropped items checked"),
    ("14_performance", "PS5 measured gameplay stability and stutter vs vanilla baseline"),
    ("15_restore", "Rollback executed safely on test instance and persistence rechecked"),
    ("16_owner", "Owner approval for any later structural deployment"),
)
SAFE_FLAGS = {
    "live_nitrado_connected": False, "playstation_classname_tested": False,
    "site_ground_y_measured": False, "actual_vanilla_object_collision_tested": False,
    "backups_verified": False, "owner_approved_hq_trial": False,
    "installable_objects_generated": False,
}
SAFETY_POLICY = {
    "try_one_alternative_at_a_time": True,
    "keep_original_stage4_pilot_1_3_5": True,
    "hq_structural_trial_is_separate_later_gate": True,
    "stage1_to_3_required_first": True,
    "vanilla_access_verified_first": True,
    "owner_approval_required": True,
    "real_ground_y_required": True,
    "verified_console_class_required": True,
    "collision_and_exit_walkthrough_required": True,
    "private_backup_before_edit_required": True,
    "at_least_two_normal_walkable_exits_required": True,
    "zero_persistent_fps_regression_required": True,
    "restore_trial_must_be_proven": True,
}


def check(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("STAGE9_BLOCKED: " + msg)


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    check(type(data) is dict, "input must be an object")
    return data


def evaluate(cfg: dict, stage8: dict, names: dict, visuals: dict,
             micro: dict, pilot: dict) -> dict:
    check(cfg.get("stage") == 9 and
          cfg.get("status") == "STRUCTURAL_PILOT_REVIEW_ONLY_NOT_INSTALLABLE"
          and cfg.get("map") == "Livonia" and cfg.get("mission") == "dayzOffline.enoch"
          and cfg.get("platform") == "PlayStation 4/5", "stage identity")
    check(cfg.get("references") == {
        "stage8": "config/stage8_bunker_feasibility.json",
        "terrain_names": "config/stage4_asset_candidates.json",
        "third_party_bbox": "config/stage4_9_p3d_bbox_evidence.json",
        "micro_layout": "config/stage4_zone47_micro_layout.json",
        "pilot": "config/stage4_13_pilot_protocol.json",
    }, "untrusted data provenance")
    check(cfg.get("deployment_allowed") is False and
          cfg.get("allowed_output_files") == ["hq_structure_review.json", "hq_structure_checklist.csv"]
          and cfg.get("evidence_status") == SAFE_FLAGS and
          cfg.get("trial_policy") == SAFETY_POLICY, "unsafe deploy/owner/runtime claims")
    check(stage8.get("stage") == 8 and stage8.get("deployment_allowed") is False and
          stage8.get("status") == "SOURCE_SCREENING_ONLY_NOT_CONSOLE_PROVEN" and
          stage8.get("surface_classname_review_candidates") == list(CHOICES),
          "Stage 8 source gate")
    check(names.get("status") == "CANDIDATE_CLASS_NAMES_ONLY_NOT_RUNTIME_VERIFIED",
          "map class provenance")
    check(visuals.get("status") ==
          "THIRD_PARTY_P3D_VISUAL_BBOX_METADATA_NOT_COLLISION_PROOF" and
          visuals.get("kind") == "P3D MODEL_VISUAL_ENVELOPE_ONLY",
          "third-party model dimensions not physical proof")
    check(micro.get("status") == "SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON" and
          micro.get("ground_elevations_known") is False and
          micro.get("selected_map_anchor") is None and
          micro.get("global_rotation") is None,
          "micro-layout falsely located on real terrain")
    check(pilot.get("status") == "CONSOLE_PILOT_PROTOCOL_ONLY_NO_RUNTIME_TRIAL" and
          pilot.get("site", {}).get("terrain_not_yet_verified") is True and
          pilot.get("safety", {}).get("automatic_deployment_allowed") is False and
          [p["object_count"] for p in pilot["rollout"]] == [1, 3, 5],
          "Stage 4.13 progressive pilot changed")
    check(cfg.get("candidate_classnames") == list(CHOICES) and
          cfg.get("focus_marker") == "hq_01" and
          cfg.get("inspect_local_markers") == list(NEIGHBORS) and
          type(cfg.get("concept_clearance_buffer_m")) in (float, int) and
          cfg["concept_clearance_buffer_m"] == 4, "unexpected choices or buffer")
    valid_names = {}
    for item in names.get("models", []):
        n = item.get("name")
        check(type(n) is str and n not in valid_names and
              item.get("object_spawner_confirmed") is False and
              item.get("ps4_ps5_runtime_confirmed") is False and
              item.get("ground_elevation_known") is False,
              "invented console class evidence")
        valid_names[n] = item
    valid_visual = {}
    for item in visuals.get("models", []):
        n = item.get("candidate_dayz_terrain_classname")
        check(type(n) is str and n not in valid_visual
              and item.get("console_runtime_verified") is False
              and item.get("physics_collision_verified") is False,
              "invented P3D collision evidence")
        valid_visual[n] = item
    markers = {}
    for item in micro.get("asset_placements", []):
        marker = item.get("id")
        check(type(marker) is str and marker not in markers and
              item.get("class_name") is None and item.get("world_pos") is None and
              item.get("verified_model") is False and
              item.get("placement_checked_on_console") is False,
              "unverified micro placement/console proof")
        markers[marker] = item
    check(all(x in markers and markers[x]["zone"] == "hq" for x in ("hq_01",) + NEIGHBORS),
          "missing HQ neighborhood")
    focus = markers["hq_01"]
    check(focus["local_x"] == 119 and focus["local_z"] == 175 and
          focus["visual_role"] == "command_shell", "unexpected reference HQ center")

    options = []
    for name in CHOICES:
        check(name in valid_names and name in valid_visual and
              valid_names[name]["zone"] == "hq", "missing actual source-backed candidate")
        asset = valid_visual[name]
        check(asset.get("p3d_path", "").startswith(("structures/", "structures_bliss/"))
              and asset["p3d_path"].endswith(".p3d")
              and asset.get("odolv") == 56, "P3D source mismatch")
        low, high = asset["bbox_min"], asset["bbox_max"]
        check(all(type(low.get(a)) in (int, float) and type(high.get(a)) in (int, float)
                  and math.isfinite(low[a]) and math.isfinite(high[a]) and low[a] < high[a]
                  for a in ("x", "y", "z")), "invalid visual bounds")
        # This is a conservative full radial visual envelope around P3D origin.
        # It does NOT show a real footprint or collision, door position or path.
        radius = math.hypot(max(abs(low["x"]), abs(high["x"])),
                            max(abs(low["z"]), abs(high["z"])))
        vicinity = []
        for pid in NEIGHBORS:
            pt = markers[pid]
            separation = math.hypot(pt["local_x"] - focus["local_x"],
                                    pt["local_z"] - focus["local_z"])
            clearance = separation - radius
            vicinity.append({
                "marker": pid,
                "neighbor_role": pt["visual_role"],
                "center_separation_local_m": round(separation, 3),
                "center_to_visual_envelope_estimate_m": round(clearance, 3),
                "inside_visual_envelope_possible": clearance <= 0,
                "below_design_buffer": clearance < cfg["concept_clearance_buffer_m"],
                "neighbor_dimensions_known": False,
                "physical_collision_tested": False,
            })
        options.append({
            "class_name_source_lead": name,
            "model_class_third_party_visual": asset["p3d_model_class"],
            "visual_model_path_DO_NOT_USE_IN_OBJECT_SPAWNER": asset["p3d_path"],
            "p3d_index_record": asset["p3d_explorer_id"],
            "visual_bbox_extent_m": [round(high[a] - low[a], 3) for a in ("x", "y", "z")],
            "conservative_visual_envelope_radius_m": round(radius, 3),
            "schematic_center_xz": [focus["local_x"], focus["local_z"]],
            "neighbor_checks": vicinity,
            "runtime_spawnable_on_PS5": False,
            "actual_collision_verified": False,
            "real_ground_y": None,
            "ready_to_install": False,
        })
    options.sort(key=lambda x: x["conservative_visual_envelope_radius_m"])
    # Sort is visual compactness only, NOT a recommendation about quality or
    # actual spawner success. Other considerations have zero in-game data.
    check(len(options) == 2 and options[0]["conservative_visual_envelope_radius_m"]
          < options[1]["conservative_visual_envelope_radius_m"],
          "visual candidate comparison ambiguous")
    return {
        "stage": 9, "status": "TWO_OFFLINE_HQ_OPTIONS_ONLY",
        "scope": "DayZ Livonia PS4/PS5 ZONA 47 hq_01 schematic center",
        "reviewed_candidates": options,
        "sort_basis": "ONLY small-to-large third-party P3D visual radius, not overall suitability",
        "first_test_option_source_lead": options[0]["class_name_source_lead"],
        "candidate_count": len(options),
        "ground_y_measurements": 0,
        "player_collision_tests": 0,
        "independent_exit_tests": 0,
        "console_object_spawner_classnames_confirmed": 0,
        "existing_stage4_13_pilot_counts_unchanged": [1, 3, 5],
        "hq_building_test_must_wait_until_original_pilot_passes": True,
        "nitrado_backups_verified": False,
        "owner_approval_received": False,
        "safe_to_install": False,
        "deployment_allowed": False,
        "warnings": [
            "P3D visual bounding boxes are not object physics or door layouts.",
            "Distances subtract only the inspected model radius; neighbors have unknown dimensions.",
            "A neighbor inside a visual envelope may be intentionally inside a building, not an invalid overlap.",
            "Land_ names from Livonia map group do not prove current PS5 Object Spawner support.",
            "Never paste arbitrary structures/ P3D model paths into the Object Spawner.",
            "HQ structure experiment is AFTER the existing 1→3→5 pilot, not a substitute for it.",
        ]
    }


def build(output: Path = OUTPUT) -> dict:
    report = evaluate(load(CONFIG), load(STAGE8), load(CLASS_NAMES),
                      load(VISUAL), load(MICRO), load(PILOT))
    output.mkdir(parents=True, exist_ok=True)
    (output / "hq_structure_review.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "hq_structure_checklist.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["step", "evidence_required", "status", "deployment_permission"])
        for step, evidence in REQUIRED_TESTS:
            writer.writerow([step, evidence, "NOT_TESTED", "BLOCKED"])
    print("PASS: Stage 9 compares two source-backed visual models and emits a blocked checklist.")
    print("No playable building, real Y, RPT, PS5 runtime or Nitrado server access confirmed.")
    return report


if __name__ == "__main__":
    build()
