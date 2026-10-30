#!/usr/bin/env python3
"""Stage 4.9: regression tests for numeric P3D bounds and paper-space pilot."""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path

from assess_stage4_9_visual_envelopes import ROOT,OUT,build,visual_radius,dist_to_segment,BUFFER

def test()->None:
    m=json.loads((ROOT/"config/stage4_9_p3d_bbox_evidence.json").read_text(encoding="utf-8"))
    assert len(m["models"])==13
    for record in m["models"]:
        assert record["source_model_url"]==f'https://www.dzp3dexplorer.com/v1/models/{record["p3d_explorer_id"]}'
        assert record["p3d_path"].endswith(".p3d")
        assert record["odolv"]==56
        assert record["physics_collision_verified"] is False
        assert record["console_runtime_verified"] is False
        assert visual_radius(record)>0
    # Deliberately asymmetric bounding box: radius must be measured from the
    # model origin, not (max-min)/2.
    asym={
        "bbox_min":{"x":-1,"y":-1,"z":-2},
        "bbox_max":{"x":7,"y":2,"z":3}
    }
    assert abs(visual_radius(asym)-math.hypot(7,3))<1e-8
    assert abs(dist_to_segment((6,5),(0,0),(10,0))-5)<1e-8
    assert abs(dist_to_segment((12,4),(0,0),(10,0))-math.hypot(2,4))<1e-8
    assert abs(dist_to_segment((0,0),(0,0),(10,0)))<1e-8
    report=build()
    assert report["stage"]=="4.9" and report["model_count"]==13
    assert report["status"]=="MODEL_BBOX_PAPER_CLEARANCE_NOT_PHYSICAL_COLLISION"
    assert report["deployment_allowed"] is False
    assert report["all_height_y_unknown"] is True
    assert report["all_p3d_collision_shapes_unknown"] is True
    assert report["playstation_model_classes_verified"] is False
    assert report["third_party_model_name_mapping_is_unverified"] is True
    assert report["provisional_site_world_center"]==[9000,7800]
    assert len(report["visual_model_size_catalog"])==13
    assert len(report["pilot_provisional_geometry_adjustments"])==5
    assert report["initial_heuristic_fail_count"]>=2,"Expected original route-overlap risk"
    assert report["proposed_heuristic_fail_count"]==0
    changed=[]
    for p in report["pilot_provisional_geometry_adjustments"]:
        x=p["suggestion"]
        assert x["has_heuristic_solution"] is True
        assert p["suggested_world_y"] is None
        assert p["ready_to_install"] is False
        assert p["p3d_to_console_class_compatibility_verified"] is False
        assert p["real_collision_clearance_confirmed"] is False
        assert x["distance_to_nearest_paper_link_m"]+0.001>=p["visual_envelope_radius_m"]+BUFFER-0.003
        assert x["suggested_displacement_m"]<=20.001
        assert 0<p["suggested_world_x"]<12800 and 0<p["suggested_world_z"]<12800
        if x["suggested_displacement_m"]>0:changed.append(p["symbolic_placement_id"])
    assert len(changed)>=2, "No pilot corridor adjustments recorded"
    with zipfile.ZipFile(OUT/"beileys47-visual-clearance-not-deployable.zip") as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={"DO_NOT_DEPLOY.txt","pilot_visual_clearance_report.json","SHA256.json"}
        assert b"DO NOT DEPLOY" in archive.read("DO_NOT_DEPLOY.txt")
        sha=json.loads(archive.read("SHA256.json"))
        for name,value in sha.items():assert hashlib.sha256(archive.read(name)).hexdigest()==value
        assert json.loads(archive.read("pilot_visual_clearance_report.json"))==report
        assert "zone47_objects.json" not in archive.namelist()
    print("PASS: independent numeric visual-envelope math, pilot corridor mitigations and no-deploy archive.")
    print("NOT VERIFIED: model collision hulls, real roads, Y, spawnable console classes, PS4/PS5 performance.")

if __name__=="__main__":test()
