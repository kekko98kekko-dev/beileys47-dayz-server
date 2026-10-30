#!/usr/bin/env python3
"""Stage 4.2 geometry, archive and proxy-status regression tests."""
from __future__ import annotations
import hashlib
import json
import math
import zipfile
from pathlib import Path

from assess_stage4_footprints import distance_to_rotated_rectangle, corners, OUT

ROOT=Path(__file__).resolve().parents[1]

def near(a:float,b:float)->None:
    assert abs(a-b)<1e-8,(a,b)

def test()->None:
    # Geometry unit tests: unrotated / rotated rectangle, center, edges.
    near(distance_to_rotated_rectangle(0,0,0,0,20,10,0),0)
    near(distance_to_rotated_rectangle(10,5,0,0,20,10,0),0)
    near(distance_to_rotated_rectangle(13,0,0,0,20,10,0),3)
    near(distance_to_rotated_rectangle(13,9,0,0,20,10,0),5)
    near(distance_to_rotated_rectangle(0,13,0,0,20,10,90),3)
    vertices=corners(100,200,20,10,0)
    assert vertices==[(90.0,195.0),(110.0,195.0),(110.0,205.0),(90.0,205.0)]
    assert len(corners(100,200,20,10,30))==4

    report=json.loads((OUT/"footprint_report.json").read_text(encoding="utf-8"))
    rules=json.loads((ROOT/"config/stage4_footprint_rules.json").read_text(encoding="utf-8"))
    shortlist=json.loads((ROOT/"dist/stage4_site_screening/site_screen_report.json").read_text(encoding="utf-8"))
    assert report["status"]=="RECTANGLE_PROXY_SCREENING_NOT_IN_GAME_VERIFIED"
    assert report["any_site_approved"] is False and report["real_object_placement_ready"] is False
    assert report["source_commit"]==shortlist["source_commit"]
    assert report["footprint_rules"]==rules
    assert len(report["regions"])==len(shortlist["regions"])==3
    for region,old in zip(report["regions"],shortlist["regions"]):
        assert region["id"]==old["id"]
        assert len(region["candidates"])==rules["max_top_candidates_per_region"]
        for now,original in zip(region["candidates"],old["top_candidates"]):
            assert (now["x"],now["z"])==(original["x"],original["z"])
            assert now["selected_for_real_world_build"] is False and now["Y_height_measured"] is False
            assert len(now["rotations_tested"])==len(rules["rotation_angles_degrees"])
            for orient in now["rotations_tested"]:
                assert orient["rotation_deg"] in rules["rotation_angles_degrees"]
                assert orient["status"] in ("STATIC_ANCHOR_MARGIN_PASSED_SURVEY_NEEDED","STATIC_ANCHOR_MARGIN_FAILED")
                assert orient["anchors_inside_rectangle"]["terrain_anchor_points_inside_rectangle"]>=0
                expected=(
                    orient["nearest_terrain_group_anchor_from_rectangle_m"]+0.05>=rules["minimum_static_group_anchor_clearance_to_footprint_m"] and
                    orient["nearest_event_point_from_rectangle_m"]+0.05>=rules["minimum_active_event_point_clearance_to_footprint_m"] and
                    orient["nearest_stage1_fresh_spawn_from_rectangle_m"]+0.05>=rules["minimum_fresh_spawn_point_clearance_to_footprint_m"]
                )
                assert orient["proxy_passed"] is expected
            if now["best_rotation"]:
                assert now["recommendation"]=="CONSIDER_GROUND_SURVEY"
                assert now["best_rotation"]["proxy_passed"] is True
            else:
                assert now["recommendation"]=="REJECT_BY_STATIC_ANCHORS"
    archive=OUT/"beileys47-zone47-footprint-screen-only.zip"
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"DO_NOT_UPLOAD.txt","footprint_report.json","footprint_rectangles.svg","sha256.json"}
        assert b"DO NOT UPLOAD" in z.read("DO_NOT_UPLOAD.txt")
        checks=json.loads(z.read("sha256.json"))
        for name,digest in checks.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
        assert json.loads(z.read("footprint_report.json"))==report
    print("PASS: Stage 4.2 rectangle geometry, reported constraints and non-deployable archive.")
    print("NOT TESTED: height, slope, roads, tree coverage, actual building footprints or game runtime.")

if __name__=="__main__":test()
