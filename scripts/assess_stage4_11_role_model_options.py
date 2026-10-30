#!/usr/bin/env python3
"""Stage 4.11: cross-check 17 NEW role-appropriate P3D *visual candidates*.

P3D existence is not a valid DayZ Object Spawner object classname. The
official spawner restricts direct P3D path usage to plants and rocks.
ALL placements remain UNVERIFIED and deployment stays blocked.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import zipfile
from collections import Counter
from pathlib import Path

from assess_stage4_9_visual_envelopes import visual_radius
from audit_stage4_10_all_placements import ROOT as ROOT_410, proximity
from build_stage4_terrain_survey_grid import local_to_world

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"config/stage4_11_p3d_role_candidates.json"
EARLIER=ROOT/"config/stage4_9_p3d_bbox_evidence.json"
ROLES=ROOT/"config/stage4_10_placement_roles.json"
LAYOUT=ROOT/"config/stage4_zone47_micro_layout.json"
OUT=ROOT/"dist/stage4_11_role_catalog"

def expect(ok:bool,msg:str)->None:
    if not ok:raise AssertionError(msg)

def examine(data:dict,earlier:dict,roles:dict,layout:dict)->dict:
    expect(ROOT==ROOT_410,"Stage 4.10 root changed")
    expect(data["stage"]=="4.11" and data["status"]=="ROLE_MATCHED_VISUAL_SIZE_CANDIDATES_NO_CONSOLE_CLASS_PROOF","Unsafe candidate status")
    expect(data["suggested_count"]==17 and data["unique_new_p3d_models"]==14,"Catalog scope changed")
    expect(len(data["reference_model_catalog"])==14,"14 new P3D records expected")
    expect(earlier["status"]=="THIRD_PARTY_P3D_VISUAL_BBOX_METADATA_NOT_COLLISION_PROOF","Legacy model evidence changed")
    expect(roles["status"]=="HYPOTHETICAL_ROLE_MATCHED_MODEL_OPTIONS_NO_RUNTIME_VERIFICATION","Stage 4.10 role policy changed")
    expect(layout["status"]=="SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON","Unsafe layout status")
    expect(all(p["class_name"] is None and p["world_pos"] is None and
               p["placement_checked_on_console"] is False for p in layout["asset_placements"]),"Layout was deployed")
    model_by_id={}
    for m in data["reference_model_catalog"]:
        mid=m["id"]
        expect(type(mid)==int and mid>100 and mid not in model_by_id,"Duplicate model ID")
        expect(m["source_url"]==f"https://www.dzp3dexplorer.com/v1/models/{mid}","Source URL mismatch")
        expect(m["p3d_path"].endswith("/"+m["model_class"]+".p3d"),"Unmatched P3D model basename")
        expect(not m["p3d_path"].startswith(("DZ/plants","DZ/rocks")),"Unexpected directly spawnable foliage path")
        expect(m["p3d_path"].startswith(("structures/","structures_bliss/")),"Unexpected model-pack family")
        expect(m["odol_version"]==56,"Unknown P3D index version")
        expect(m["runtime_object_spawner_classname"] is None,"Fabricated console classname")
        expect(m["can_use_direct_p3d_path_in_object_spawner"] is False,"Unsafe direct P3D spawn claim")
        expect(m["collision_verified"] is False and m["ps4_ps5_spawning_tested"] is False,"Unsafe runtime claim")
        expect(0<visual_radius(m)<8,"Noncompact new model unexpectedly approved for role candidate")
        model_by_id[mid]=m
    old_by_cls={m["candidate_dayz_terrain_classname"]:m for m in earlier["models"]}
    expect(len(old_by_cls)==13,"Existing model count changed")
    markers=layout["asset_placements"]
    marker_ids={p["id"] for p in markers}
    missing={key for key,p in roles["placement_options"].items() if p["proposed_visual_model_classname"] is None}
    expect(len(markers)==len(marker_ids)==26 and len(missing)==17,"Expected 17 missing old sizes")
    expect(set(data["suggestions"])==missing,"Unresolved / extra marker suggestions")
    if data["approval"].get("deployment_allowed") is not False:
        raise AssertionError("Release approval bypass")

    catalog=[]
    suggested=[]
    for p in markers:
        original=roles["placement_options"][p["id"]]
        old=original["proposed_visual_model_classname"]
        new=data["suggestions"].get(p["id"])
        if old is not None:
            expect(new is None and old in old_by_cls,"Old candidate changed or overwritten")
            model=old_by_cls[old]
            size_kind="PRIOR_ROLE_MATCHED_VISUAL_P3D"
            p3d=model["p3d_model_class"]
            url=model["source_model_url"]
        else:
            expect(new is not None and new["model_id"] in model_by_id,"Missing source model for new role")
            expect(new["suggested_only"] is True and new["verified_console_object_classname"] is None,"Unsafe class claim")
            expect(new["real_Y"] is None and new["ground_or_floor_checked"] is False,"Fabricated ground/indoor height")
            expect(new["requires_height_and_collision_test"] is True,"Missing gameplay gate")
            expect(new["placement_intent"]==original["placement_intent"] or
                   original["placement_intent"]=="UNSPECIFIED_OR_EXTERIOR" and new["placement_intent"]=="EXTERIOR",
                   "Unexpected indoor/outdoor role override")
            model=model_by_id[new["model_id"]]
            p3d=model["model_class"]
            url=model["source_url"]
            size_kind="NEW_UNVERIFIED_MODEL_VISUAL_P3D"
        radius=visual_radius(model)
        wx,wz=local_to_world(p["local_x"],p["local_z"],9000,7800,240,220,120)
        expect(0<=wx<=12800 and 0<=wz<=12800,"Out of world bounds")
        proposed_class=old if old is not None else None
        item={
            "id":p["id"],"zone":p["zone"],"local_x":p["local_x"],"local_z":p["local_z"],
            "world_x":round(wx,3),"world_z":round(wz,3),"world_y":None,
            "visual_role":p["visual_role"],"visual_p3d_reference":p3d,
            "p3d_source_url":url,"visual_radius_m":radius,
            "visual_reference_kind":size_kind,
            "existing_paper_candidate_classname":proposed_class,
            "verified_playstation_spawner_classname":None,
            "selected_for_final_layout":False,
            "real_ground_or_floor_Y_measured":False,
            "real_collision_confirmed":False,
            "dayz_runtime_spawn_tested":False,
            "placement_intent":new["placement_intent"] if new is not None else original["placement_intent"],
            "deployment_allowed":False
        }
        catalog.append(item)
        if new is not None:
            suggested.append({
                "id":p["id"],"role":p["visual_role"],"proposed_p3d":p3d,
                "source_url":url,"visual_radius_m":round(radius,3),
                "proposed_role_fit":new["visual_role_fit"],
                "rationale":new["rationale"],"orientation_unknown":True,
                "real_ground_or_floor_Y":None,
                "verified_console_classname":None,
                "technical_review_status":"VISUAL_MODEL_MATCH_ONLY"
            })
    expect(len(catalog)==26 and len(suggested)==17,"Failed complete coverage")

    # Even with all 26 *reference* radii, observed physical hull sizes remain
    # unknown until class matching and console collision tests.
    pairs=[proximity(a,b,4.0) for a,b in itertools.combinations(catalog,2)]
    expect(len(pairs)==325,"Unexpected pair count")
    kinds=Counter(pair["classification"] for pair in pairs)
    overlapping=[p for p in pairs if p["classification"]=="REFERENCE_VISUAL_DISKS_OVERLAP"]
    near=[p for p in pairs if p["classification"]=="REFERENCE_VISUAL_DISKS_WITHIN_DESIGN_BUFFER"]
    report={
        "stage":"4.11",
        "status":"26_MODEL_VISUAL_REFERENCES_ONLY_ZERO_RUNTIME_VERIFICATION",
        "source":"DayZ P3D Explorer public 1.30 model metadata (not authoritative PS4/PS5 class registry)",
        "authoritative_spawner_doc":"https://community.bistudio.com/wiki/DayZ:Object_Spawner",
        "p3d_direct_path_for_structure_models_supported":False,
        "new_role_matched_visual_suggestions":17,
        "new_distinct_p3d_reference_models":14,
        "old_visual_reference_placements":9,
        "total_symbolic_markers":26,
        "total_visual_reference_markers":26,
        "confirmed_spawner_classnames_on_ps4_ps5":0,
        "physical_collision_hulls_verified":0,
        "actual_terrain_or_floor_Y_heights":0,
        "fully_verified_actual_placement_count":0,
        "design_2d_marker_pair_count":325,
        "pair_classifications":dict(sorted(kinds.items())),
        "hypothetical_visual_reference_disk_overlap_count":len(overlapping),
        "hypothetical_visual_reference_disk_under_4m_buffer_count":len(near),
        "overlapping_visual_reference_disks":overlapping,
        "near_visual_reference_disks":near,
        "newly_suggested_model_roles":suggested,
        "all_26_hypothetical_visual_placements":catalog,
        "all_325_hypothetical_pairs":pairs,
        "remaining_real_risks":[
           "Class_name and object-spawner compatibility cannot be inferred from the P3D basename.",
           "Official Object Spawner only supports direct P3D paths under DZ/plants* and DZ/rocks*, not these furniture/military structures.",
           "A visual radius is NOT a collision shape; paper disk overlap can be intentional interior detail.",
           "P3D local Y bbox does not supply ground/floor placement Y at site X/Z.",
           "Schematic zone-to-zone links do not represent real footpaths, doors or vehicle clearances.",
           "Furniture-sized models might not be valid noninteractive Land_ objects in Nitrado PlayStation.",
           "Never use these proposed models as approved assets, spawn instructions, or game files."
        ],
        "real_world_site_approved":False,
        "ps4_ps5_tested":False,
        "no_game_files_generated":True,
        "deployment_allowed":False
    }
    return report

def build()->dict:
    paths=(SOURCE,EARLIER,ROLES,LAYOUT)
    source,earlier,roles,layout=[json.loads(p.read_text(encoding="utf-8")) for p in paths]
    report=examine(source,earlier,roles,layout)
    OUT.mkdir(parents=True,exist_ok=True)
    result=OUT/"candidate_26_visual_fit_report.json"
    result.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    markers=OUT/"all_26_visual_candidate_sizes.csv"
    cols=["id","zone","visual_role","visual_p3d_reference","visual_radius_m","visual_reference_kind",
          "world_x","world_z","world_y","verified_playstation_spawner_classname","selected_for_final_layout"]
    with markers.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        w.writeheader();w.writerows(report["all_26_hypothetical_visual_placements"])
    warnings=OUT/"reference_pair_warnings.csv"
    paircols=["a","b","a_zone","b_zone","visual_disk_edge_gap_m","classification","may_be_intentional_indoor"]
    with warnings.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=paircols,extrasaction="ignore")
        w.writeheader();w.writerows(report["overlapping_visual_reference_disks"]+report["near_visual_reference_disks"])
    files={
        "DO_NOT_DEPLOY.txt":(
          "Stage 4.11: source-backed model VISUAL metadata only. 17 suggestions, ZERO validated PlayStation classes.\n"
          "P3D structural model paths cannot be used directly in DayZ Object Spawner. No actual Y, no collisions.\n"
          "NO game installable files. DO NOT DEPLOY TO NITRADO.\n"
        ).encode(),
        "candidate_26_visual_fit_report.json":result.read_bytes(),
        "all_26_visual_candidate_sizes.csv":markers.read_bytes(),
        "reference_pair_warnings.csv":warnings.read_bytes()
    }
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(hashes,indent=2)+"\n").encode()
    with zipfile.ZipFile(OUT/"beileys47-stage411-visual-role-options-not-deployable.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,contents in sorted(files.items()):z.writestr(name,contents)
    with zipfile.ZipFile(OUT/"beileys47-stage411-visual-role-options-not-deployable.zip") as z:
        expect(z.testzip() is None and set(z.namelist())==set(files),"Archive failed")
        for name,digest in hashes.items():expect(hashlib.sha256(z.read(name)).hexdigest()==digest,"Bad hash")
        expect(not any(x.endswith("cfggameplay.json") or "zone47_objects" in x for x in z.namelist()),"Unsafe file in archive")
    print("PASS: Stage 4.11: 17 new role-matched VISUAL P3D suggestions, 26 visual references, 325 paper pair comparisons.")
    print(f"WARNING: {report['hypothetical_visual_reference_disk_overlap_count']} hypothetical P3D disk overlaps; {report['hypothetical_visual_reference_disk_under_4m_buffer_count']} small paper visual gaps.")
    print("ZERO verified PlayStation object classes, zero real terrain Y or collisions. DO NOT DEPLOY.")
    return report

if __name__=="__main__":build()
