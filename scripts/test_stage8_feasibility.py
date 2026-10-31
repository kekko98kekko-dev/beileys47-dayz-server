#!/usr/bin/env python3
"""Synthetic tampering tests for real-vs-unverified bunker evidence Stage 8."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from build_stage8_feasibility import (
    CONFIG, MAP, P3D, STAGE7, PILOT, build, load, validate
)


def reject(design, map_inventory, p3d_inventory, stage7, pilot, contains):
    try:
        validate(design, map_inventory, p3d_inventory, stage7, pilot)
    except ValueError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError("Stage 8 wrongly accepted changed evidence: " + contains)


def test() -> None:
    d, maps, p3ds, seven, pilot = (
        load(CONFIG), load(MAP), load(P3D), load(STAGE7), load(PILOT))
    with tempfile.TemporaryDirectory(prefix="beileys-stage8-") as folder:
        dest = Path(folder) / "feasibility.json"
        report = build(dest)
        assert json.loads(dest.read_text(encoding="utf-8")) == report
        assert report["deployment_allowed"] is False
        assert report["any_reliable_PS5_bunker_class_verified"] is False
        assert report["real_reachable_exits_verified"] == 0
        assert report["historical_bunker_reused"] is False
        assert report["existing_pilot_counts_unchanged"] == [1, 3, 5]
        assert report["selected_first_rental_strategy"] == "surface_command"
        assert report["p3d_visual_metadata_only_model_count"] >= 10
        assert report["map_group_only_land_candidate_count"] >= 10
        assert report["deployable_object_spawner_emitted"] is False

    case = copy.deepcopy(d)
    case["deployment_allowed"] = True
    reject(case, maps, p3ds, seven, pilot, "no-deploy protections")

    case = copy.deepcopy(d)
    case["source_review"]["example_limitation"] = "SAFE_EXIT"
    reject(case, maps, p3ds, seven, pilot, "unverified third-party bunker")

    case = copy.deepcopy(d)
    case["source_review"]["example_is_verified_for_current_ps5"] = True
    reject(case, maps, p3ds, seven, pilot, "unverified third-party bunker")

    case = copy.deepcopy(d)
    case["source_review"]["example_content_copied"] = True
    reject(case, maps, p3ds, seven, pilot, "unverified third-party bunker")

    case = copy.deepcopy(d)
    case["release_gates"]["runtime_exits_tested"] = True
    reject(case, maps, p3ds, seven, pilot, "unverified safety claim")

    case = copy.deepcopy(d)
    case["release_gates"]["verify_normal_exit_without_logout"] = False
    reject(case, maps, p3ds, seven, pilot, "missing mandatory real-world test")

    case = copy.deepcopy(d)
    case["release_gates"]["planned_first_pilot_counts"] = [1, 20, 60]
    reject(case, maps, p3ds, seven, pilot, "unsafe accelerated")

    case = copy.deepcopy(d)
    case["release_gates"]["minimum_real_exits_walked_per_selected_bunker"] = 1
    reject(case, maps, p3ds, seven, pilot, "at least two tested exits")

    case = copy.deepcopy(d)
    case["options"][2]["bunker_underground_guaranteed"] = True
    reject(case, maps, p3ds, seven, pilot, "false underground promise")

    case = copy.deepcopy(d)
    case["options"][1]["needs"].remove("walk_all_real_exits")
    reject(case, maps, p3ds, seven, pilot, "missing real-world route")

    case = copy.deepcopy(d)
    case["surface_classname_review_candidates"].append("Land_InventedBunker")
    reject(case, maps, p3ds, seven, pilot, "new or mislocated")

    case = copy.deepcopy(maps)
    case["models"][0]["object_spawner_confirmed"] = True
    reject(d, case, p3ds, seven, pilot, "guessed or approved")

    case = copy.deepcopy(p3ds)
    case["reference_model_catalog"][0]["can_use_direct_p3d_path_in_object_spawner"] = True
    reject(d, maps, case, seven, pilot, "unverified 3D metadata")

    case = copy.deepcopy(p3ds)
    case["reference_model_catalog"][0]["runtime_object_spawner_classname"] = "Land_Fiction"
    reject(d, maps, case, seven, pilot, "unverified 3D metadata")

    case = copy.deepcopy(seven)
    case["rooms"][0]["ground_y"] = 250.5
    reject(d, maps, p3ds, case, pilot, "Stage 7 contains claimed real geometry")

    case = copy.deepcopy(pilot)
    case["rollout"][-1]["object_count"] = 26
    reject(d, maps, p3ds, seven, case, "unsafe accelerated")

    print("PASS: Stage 8 source safety, trap-case rejection, false console/geometry proof rejected.")
    print("No actual DayZ runtime tests conducted.")


if __name__ == "__main__":
    test()
