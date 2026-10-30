#!/usr/bin/env python3
"""Stage 4.10: exact 26/325 regression, missing sizes and indoor caveat."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import zipfile

from audit_stage4_10_all_placements import ROOT,OUT,build,gather,proximity

def test()->None:
    bp=json.loads((ROOT/"config/stage4_zone47_blueprint.json").read_text(encoding="utf-8"))
    micro=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text(encoding="utf-8"))
    meta=json.loads((ROOT/"config/stage4_9_p3d_bbox_evidence.json").read_text(encoding="utf-8"))
    policy=json.loads((ROOT/"config/stage4_10_placement_roles.json").read_text(encoding="utf-8"))

    result=build()
    assert result["status"]=="FULL_26_PLACEMENT_RISK_AUDIT_SOME_MODEL_SIZES_UNKNOWN"
    assert result["total_placement_markers"]==26
    assert result["reference_model_assigned_count"]==9
    assert result["model_size_unknown_count"]==17
    assert result["pairwise_marker_tests"]==325
    assert result["pairs_both_reference_sizes_known"]==36
    assert result["pairs_one_or_more_unknown_size"]==289
    assert len(result["all_pairs"])==325
    assert len({frozenset((x["a"],x["b"])) for x in result["all_pairs"]})==325
    assert result["route_line_is_not_physical_trail"] is True
    assert result["design_link_endpoints_are_sector_centers"] is True
    assert result["unknown_size_does_not_equal_zero_radius"] is True
    assert result["deployment_allowed"] is False
    assert result["any_real_collision_confirmed"] is False
    assert result["any_console_model_verified"] is False
    assert result["any_world_y_measured"] is False
    assert result["object_spawner_generated"] is False

    records={x["symbol_id"]:x for x in result["placement_reports"]}
    assert len(records)==26
    assert all(records[x]["visual_radius_m"] is None for x in ("barracks_03","hq_04","secret_02"))
    assert records["barracks_01"]["visual_radius_m"]>19
    assert records["hq_01"]["visual_radius_m"]>8
    assert len([x for x in records.values() if x["known_visual_envelope"]])==9
    assert all(x["site_and_collision_still_unverified"] is True for x in records.values())
    assert all(x["sector_center_link_geometry_critical_caveat"] for x in records.values())
    assert all(x["nearest_any_link_centerline_distance_m"]>=0 for x in records.values())

    near={(x["a"],x["b"]):x for x in result["near_unknown_marker_review_cases"]}
    def has_pair(x:str,y:str)->dict:
        return near.get((x,y)) or near[(y,x)]
    assert has_pair("barracks_01","barracks_03")["classification"]=="UNKNOWN_MARKER_CENTER_INSIDE_KNOWN_VISUAL_DISK"
    assert has_pair("barracks_01","barracks_04")["classification"]=="UNKNOWN_MARKER_CENTER_INSIDE_KNOWN_VISUAL_DISK"
    assert has_pair("barracks_01","barracks_02")["classification"]=="UNKNOWN_MARKER_CENTER_NEAR_KNOWN_VISUAL_DISK"
    assert has_pair("hq_01","hq_04")["may_be_intentional_indoor"] is True
    assert has_pair("hq_01","hq_05")["may_be_intentional_indoor"] is True
    assert has_pair("barracks_01","barracks_04")["may_be_intentional_indoor"] is True
    assert has_pair("barracks_01","barracks_03")["may_be_intentional_indoor"] is False

    for row in result["all_pairs"]:
        if row["radius_a_m"] is None or row["radius_b_m"] is None:
            assert row["visual_disk_edge_gap_m"] is None
        assert row["never_claim_real_collisions"] is True
    assert result["reference_visual_disk_overlaps"]==0

    # Synthetic only: a measured model radius of 5 m against another
    # measured radius of 5 m at 8 m center spacing overlaps in paper space.
    a={"id":"synthetic_a","zone":"X","local_x":0,"local_z":0,
       "visual_radius_m":5,"placement_intent":"EXTERIOR","provisional_model":"synthetic"}
    b={"id":"synthetic_b","zone":"X","local_x":8,"local_z":0,
       "visual_radius_m":5,"placement_intent":"EXTERIOR","provisional_model":"synthetic"}
    pair=proximity(a,b,4)
    assert pair["classification"]=="REFERENCE_VISUAL_DISKS_OVERLAP"
    assert pair["reference_visual_overlap_claim"] is True
    unknown=copy.deepcopy(b)
    unknown["visual_radius_m"]=None
    unknown["placement_intent"]="POSSIBLE_INTERIOR"
    p=proximity(a,unknown,4)
    assert p["visual_disk_edge_gap_m"] is None
    assert p["may_be_intentional_indoor"] is True
    assert p["classification"]=="UNKNOWN_MARKER_CENTER_NEAR_KNOWN_VISUAL_DISK"

    # Missing size must not silently become 0, including role-policy changes.
    broken=copy.deepcopy(policy)
    broken["placement_options"].pop("hq_05")
    try:gather(bp,micro,meta,broken)
    except AssertionError as ex: assert "All 26" in str(ex)
    else:raise AssertionError("Unassessed symbol accepted")
    broken=copy.deepcopy(policy)
    broken["placement_options"]["hq_05"]["proposed_visual_model_classname"]="Land_FabricatedHouse"
    broken["selected_role_matched_options"]=10
    broken["unassigned_role_visual_sizes"]=16
    try:gather(bp,micro,meta,broken)
    except AssertionError as ex: assert "Reference model missing" in str(ex)
    else:raise AssertionError("Fabricated class accepted")

    with (OUT/"all_26_placement_review.csv").open(encoding="utf-8",newline="") as f:
        assert len(list(csv.DictReader(f)))==26
    with (OUT/"all_325_pair_review.csv").open(encoding="utf-8",newline="") as f:
        assert len(list(csv.DictReader(f)))==325
    with zipfile.ZipFile(OUT/"beileys47-full-layout-paper-audit-only.zip") as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={
            "DO_NOT_DEPLOY.txt","full_26_layout_risk_report.json",
            "all_26_placement_review.csv","all_325_pair_review.csv","SHA256_MANIFEST.json"}
        hashes=json.loads(archive.read("SHA256_MANIFEST.json"))
        for name,hashsum in hashes.items(): assert hashlib.sha256(archive.read(name)).hexdigest()==hashsum
        assert b"DO NOT UPLOAD" in archive.read("DO_NOT_DEPLOY.txt")
        assert json.loads(archive.read("full_26_layout_risk_report.json"))==result
    print("PASS: 26/325 exact pairs and intentional indoor-design interpretation.")
    print("FAIL-CLOSED: 17 unmeasured P3D sizes, unverified source/runtime, zero deploy.")

if __name__=="__main__":test()
