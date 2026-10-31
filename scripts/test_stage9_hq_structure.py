#!/usr/bin/env python3
"""Stage 9 adversarial tests against early unsafe HQ structure approval."""
from __future__ import annotations

import copy
import csv
import json
import tempfile
from pathlib import Path

from build_stage9_hq_structure import (
    CLASS_NAMES, CONFIG, MICRO, PILOT, STAGE8, VISUAL,
    REQUIRED_TESTS, build, evaluate, load,
)


def reject(c, s8, names, visuals, micro, pilot, phrase):
    try:
        evaluate(c, s8, names, visuals, micro, pilot)
    except ValueError as exc:
        assert phrase in str(exc), (phrase, str(exc))
    else:
        raise AssertionError("Unsafe test fixture was accepted: " + phrase)


def main() -> None:
    cfg, s8, names, visuals, micro, pilot = (
        load(CONFIG), load(STAGE8), load(CLASS_NAMES), load(VISUAL),
        load(MICRO), load(PILOT)
    )
    with tempfile.TemporaryDirectory(prefix="stage9-hq-trial-") as root:
        dest = Path(root)
        report = build(dest)
        assert report == json.loads((dest / "hq_structure_review.json").read_text("utf-8"))
        assert report["candidate_count"] == 2
        assert report["first_test_option_source_lead"] == "Land_Mil_Guardhouse1"
        assert report["existing_stage4_13_pilot_counts_unchanged"] == [1, 3, 5]
        assert report["hq_building_test_must_wait_until_original_pilot_passes"] is True
        assert report["deployment_allowed"] is False
        assert report["ground_y_measurements"] == 0
        assert report["console_object_spawner_classnames_confirmed"] == 0
        assert all(x["real_ground_y"] is None and x["ready_to_install"] is False
                   and x["runtime_spawnable_on_PS5"] is False for x in report["reviewed_candidates"])
        assert all(x["visual_model_path_DO_NOT_USE_IN_OBJECT_SPAWNER"]
                   .startswith(("structures/", "structures_bliss/"))
                   for x in report["reviewed_candidates"])
        assert all(len(x["neighbor_checks"]) == 4 for x in report["reviewed_candidates"])
        assert report["reviewed_candidates"][0]["conservative_visual_envelope_radius_m"] < \
               report["reviewed_candidates"][1]["conservative_visual_envelope_radius_m"]

        with (dest / "hq_structure_checklist.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == len(REQUIRED_TESTS)
        assert {x["step"] for x in rows} == {step for step, _ in REQUIRED_TESTS}
        assert all(x["status"] == "NOT_TESTED" and
                   x["deployment_permission"] == "BLOCKED" for x in rows)

    mutation = copy.deepcopy(cfg)
    mutation["deployment_allowed"] = True
    reject(mutation, s8, names, visuals, micro, pilot, "unsafe deploy")
    mutation = copy.deepcopy(cfg)
    mutation["evidence_status"]["playstation_classname_tested"] = True
    reject(mutation, s8, names, visuals, micro, pilot, "unsafe deploy")
    mutation = copy.deepcopy(cfg)
    mutation["trial_policy"]["hq_structural_trial_is_separate_later_gate"] = False
    reject(mutation, s8, names, visuals, micro, pilot, "unsafe deploy")
    mutation = copy.deepcopy(cfg)
    mutation["candidate_classnames"].append("Land_FantasyBunker")
    reject(mutation, s8, names, visuals, micro, pilot, "unexpected choices")
    mutation = copy.deepcopy(cfg)
    mutation["allowed_output_files"].append("objects.json")
    reject(mutation, s8, names, visuals, micro, pilot, "unsafe deploy")
    mutation = copy.deepcopy(cfg)
    mutation["concept_clearance_buffer_m"] = 0
    reject(mutation, s8, names, visuals, micro, pilot, "unexpected choices")

    mutation = copy.deepcopy(micro)
    mutation["asset_placements"][0]["world_pos"] = [9000, 200, 7800]
    reject(cfg, s8, names, visuals, mutation, pilot, "unverified micro")
    mutation = copy.deepcopy(names)
    mutation["models"][0]["ps4_ps5_runtime_confirmed"] = True
    reject(cfg, s8, mutation, visuals, micro, pilot, "invented console")
    mutation = copy.deepcopy(visuals)
    mutation["models"][0]["physics_collision_verified"] = True
    reject(cfg, s8, names, mutation, micro, pilot, "invented P3D")
    mutation = copy.deepcopy(visuals)
    record = next(x for x in mutation["models"] if x["candidate_dayz_terrain_classname"] == "Land_Mil_Guardhouse1")
    record["bbox_max"]["x"] = float("nan")
    reject(cfg, s8, names, mutation, micro, pilot, "invalid visual bounds")
    mutation = copy.deepcopy(pilot)
    mutation["rollout"][2]["object_count"] = 26
    reject(cfg, s8, names, visuals, micro, mutation, "Stage 4.13 progressive pilot changed")
    mutation = copy.deepcopy(s8)
    mutation["deployment_allowed"] = True
    reject(cfg, mutation, names, visuals, micro, pilot, "Stage 8 source gate")
    print("PASS: Stage 9 source cross-check, exact trial list, fake proof and drift guards.")
    print("NO real DayZ objects installed.")


if __name__ == "__main__":
    main()
