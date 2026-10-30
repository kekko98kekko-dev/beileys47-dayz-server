#!/usr/bin/env python3
"""Stage 4.11 negative/positive catalog tests without PS5 model validation."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import zipfile

from assess_stage4_11_role_model_options import ROOT, OUT, build, examine

def reject(fn,reason:str)->None:
    try:fn()
    except AssertionError as ex:assert reason in str(ex),(reason,str(ex))
    else:raise AssertionError("Unsafe mutation accepted: "+reason)

def test()->None:
    source=json.loads((ROOT/"config/stage4_11_p3d_role_candidates.json").read_text(encoding="utf-8"))
    earlier=json.loads((ROOT/"config/stage4_9_p3d_bbox_evidence.json").read_text(encoding="utf-8"))
    roles=json.loads((ROOT/"config/stage4_10_placement_roles.json").read_text(encoding="utf-8"))
    layout=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text(encoding="utf-8"))
    results=build()
    assert results["status"]=="26_MODEL_VISUAL_REFERENCES_ONLY_ZERO_RUNTIME_VERIFICATION"
    assert results["new_role_matched_visual_suggestions"]==17
    assert results["new_distinct_p3d_reference_models"]==14
    assert results["old_visual_reference_placements"]==9
    assert results["total_symbolic_markers"]==26
    assert results["total_visual_reference_markers"]==26
    assert results["design_2d_marker_pair_count"]==325
    assert len(results["all_325_hypothetical_pairs"])==325
    assert len(results["newly_suggested_model_roles"])==17
    assert len(results["all_26_hypothetical_visual_placements"])==26
    assert results["p3d_direct_path_for_structure_models_supported"] is False
    assert results["confirmed_spawner_classnames_on_ps4_ps5"]==0
    assert results["physical_collision_hulls_verified"]==0
    assert results["actual_terrain_or_floor_Y_heights"]==0
    assert results["fully_verified_actual_placement_count"]==0
    assert results["deployment_allowed"] is False
    assert results["no_game_files_generated"] is True
    assert results["ps4_ps5_tested"] is False
    assert all(p["world_y"] is None and p["verified_playstation_spawner_classname"] is None
               and p["deployment_allowed"] is False for p in results["all_26_hypothetical_visual_placements"])
    assert all(p["visual_radius_m"]>0 for p in results["all_26_hypothetical_visual_placements"])
    assert {p["id"] for p in results["newly_suggested_model_roles"]}==set(source["suggestions"])
    assert all(p["verified_console_classname"] is None and p["real_ground_or_floor_Y"] is None
               for p in results["newly_suggested_model_roles"])
    assert len({frozenset((p["a"],p["b"])) for p in results["all_325_hypothetical_pairs"]})==325
    assert all(p["never_claim_real_collisions"] is True for p in results["all_325_hypothetical_pairs"])
    assert len(results["overlapping_visual_reference_disks"])+len(results["near_visual_reference_disks"])<=325
    assert results["hypothetical_visual_reference_disk_overlap_count"]==len(results["overlapping_visual_reference_disks"])
    assert all(p["visual_disk_edge_gap_m"] is not None for p in results["all_325_hypothetical_pairs"])

    # Catch a common and dangerous false assumption: spawner support for
    # arbitrary structural P3D model paths.
    modified=copy.deepcopy(source)
    modified["reference_model_catalog"][0]["can_use_direct_p3d_path_in_object_spawner"]=True
    reject(lambda:examine(modified,earlier,roles,layout),"Unsafe direct P3D spawn claim")
    modified=copy.deepcopy(source)
    modified["reference_model_catalog"][0]["runtime_object_spawner_classname"]="Land_Fictitious"
    reject(lambda:examine(modified,earlier,roles,layout),"Fabricated console classname")
    modified=copy.deepcopy(source)
    modified["suggestions"]["hq_05"]["real_Y"]=800.0
    reject(lambda:examine(modified,earlier,roles,layout),"Fabricated ground/indoor height")
    modified=copy.deepcopy(source)
    modified["suggestions"].pop("hq_05")
    reject(lambda:examine(modified,earlier,roles,layout),"Unresolved / extra marker suggestions")
    modified=copy.deepcopy(source)
    modified["approval"]["deployment_allowed"]=True
    reject(lambda:examine(modified,earlier,roles,layout),"Release approval bypass")
    modified=copy.deepcopy(source)
    modified["reference_model_catalog"][0]["bbox_min"]["x"]=float("nan")
    reject(lambda:examine(modified,earlier,roles,layout),"Invalid P3D bounds")

    with (OUT/"all_26_visual_candidate_sizes.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==26 and all(p["world_y"]=="" and p["verified_playstation_spawner_classname"]=="" for p in rows)
    with zipfile.ZipFile(OUT/"beileys47-stage411-visual-role-options-not-deployable.zip") as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={"DO_NOT_DEPLOY.txt","candidate_26_visual_fit_report.json","all_26_visual_candidate_sizes.csv","reference_pair_warnings.csv","SHA256.json"}
        hashes=json.loads(archive.read("SHA256.json"))
        for name,sha in hashes.items():assert hashlib.sha256(archive.read(name)).hexdigest()==sha
        assert b"DO NOT DEPLOY" in archive.read("DO_NOT_DEPLOY.txt")
        assert json.loads(archive.read("candidate_26_visual_fit_report.json"))==results
    print("PASS: Stage 4.11 all 17 new model roles, 26 visual references, 325 combos; no fabricated console classes.")

if __name__=="__main__":test()
