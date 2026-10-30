#!/usr/bin/env python3
"""Stage 4.10: full 26-symbol visual clearance risk audit, NEVER deployable.

13 P3D records are third-party VISUAL bounding boxes, not collision hulls.
9 of 26 conceptual markers have role-matched hypothetical model options; the
remaining 17 have UNKNOWN size (not radius zero). Audit all 325 marker pairs.
Distances to graph links are illustrative only; graph edges end at SECTOR
CENTERS, so a structure on a node can appear to 'block' a fictitious path.
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

from zip_deterministic import add_bytes

from assess_stage4_9_visual_envelopes import visual_radius, dist_to_segment
from build_stage4_terrain_survey_grid import local_to_world

ROOT=Path(__file__).resolve().parents[1]
BP=ROOT/"config/stage4_zone47_blueprint.json"
MICRO=ROOT/"config/stage4_zone47_micro_layout.json"
META=ROOT/"config/stage4_9_p3d_bbox_evidence.json"
POLICY=ROOT/"config/stage4_10_placement_roles.json"
OUT=ROOT/"dist/stage4_10_full_layout"

def need(ok:bool,reason:str)->None:
    if not ok:raise AssertionError(reason)

def proximity(a:dict,b:dict,buffer:float)->dict:
    """Classify center distance without treating unknown visual sizes as zero."""
    distance=math.dist((a["local_x"],a["local_z"]),(b["local_x"],b["local_z"]))
    ra,rb=a["visual_radius_m"],b["visual_radius_m"]
    base={
        "a":a["id"],"b":b["id"],"a_zone":a["zone"],"b_zone":b["zone"],
        "local_center_separation_m":round(distance,3),
        "radius_a_m":round(ra,3) if ra is not None else None,
        "radius_b_m":round(rb,3) if rb is not None else None,
        "visual_disk_edge_gap_m":None,
        "review_priority":"NEEDS_UNKNOWN_MODEL_FOOTPRINT",
        "classification":"BOTH_SIZES_UNKNOWN" if ra is None and rb is None else "ONE_SIZE_UNKNOWN",
        "reference_visual_overlap_claim":False,
        "never_claim_real_collisions":True,
        "may_be_intentional_indoor":False
    }
    if ra is not None and rb is not None:
        gap=distance-ra-rb
        base["visual_disk_edge_gap_m"]=round(gap,3)
        base["reference_visual_overlap_claim"]=gap<0
        if gap<0:
            base["classification"]="REFERENCE_VISUAL_DISKS_OVERLAP"
            base["review_priority"]="HIGH_REVIEW_MODEL_AND_POSITION"
        elif gap<buffer:
            base["classification"]="REFERENCE_VISUAL_DISKS_WITHIN_DESIGN_BUFFER"
            base["review_priority"]="MEDIUM_REVIEW_PROXIMITY"
        else:
            base["classification"]="REFERENCE_VISUAL_DISKS_ABOVE_DESIGN_BUFFER"
            base["review_priority"]="LOW_STILL_NOT_COLLISION_VERIFIED"
    elif ra is not None or rb is not None:
        identified=a if ra is not None else b
        unknown=b if ra is not None else a
        radius=ra if ra is not None else rb
        known_edge_gap=distance-radius
        base["known_model_edge_to_unknown_marker_center_m"]=round(known_edge_gap,3)
        if known_edge_gap<0:
            base["classification"]="UNKNOWN_MARKER_CENTER_INSIDE_KNOWN_VISUAL_DISK"
            base["review_priority"]="HIGH_REVIEW_INTENDED_INTERIOR_OR_GEOMETRY"
        elif known_edge_gap<buffer:
            base["classification"]="UNKNOWN_MARKER_CENTER_NEAR_KNOWN_VISUAL_DISK"
            base["review_priority"]="MEDIUM_GET_UNKNOWN_MODEL_SIZE"
        base["may_be_intentional_indoor"]=(
            unknown["placement_intent"]=="POSSIBLE_INTERIOR" and known_edge_gap<buffer
        )
        base["known_model_reference"]=identified["provisional_model"]
    return base

def gather(bp:dict,micro:dict,meta:dict,policy:dict)->dict:
    need(bp["status"]=="DESIGN_ONLY_NOT_INSTALLABLE"
         and micro["status"]=="SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON",
         "Missing original design-only safety status")
    need(policy["stage"]=="4.10"
         and policy["status"]=="HYPOTHETICAL_ROLE_MATCHED_MODEL_OPTIONS_NO_RUNTIME_VERIFICATION"
         and policy["deploy_allowed"] is False,"Unsafe role policy")
    need(meta["status"]=="THIRD_PARTY_P3D_VISUAL_BBOX_METADATA_NOT_COLLISION_PROOF",
         "Unexpected model evidence")
    need(bp["coordinate_system"]["terrain_surveyed"] is False
         and micro["ground_elevations_known"] is False,"Ground survey must remain unverified")
    need(len(bp["zones"])==8 and len(bp["links"])==16,"Schematic route/sector source changed")
    props=micro["asset_placements"]
    need(len(props)==26 and len(policy["placement_options"])==26,"All 26 symbols required")
    need(set(p["id"] for p in props)==set(policy["placement_options"]),"Missing symbol policy entries")
    need(all(p["class_name"] is None and p["world_pos"] is None
             and p["verified_model"] is False and p["placement_checked_on_console"] is False
             for p in props),"Unexpected class or live placement claims")
    world_center=policy["reference_center_m"]
    need(world_center==[9000,7800],"Site candidate changed")
    model_by_name={m["candidate_dayz_terrain_classname"]:m for m in meta["models"]}
    need(len(model_by_name)==13,"Expected 13 source P3D records")
    source_nodes={p["id"]:(p["x"],p["z"]) for p in bp["entrances"]+bp["zones"]}
    zone_counts=Counter(p["zone"] for p in props)
    need(all(zone_counts[z["id"]]==z["prototype_count"] for z in bp["zones"]),"Zone budget mismatch")
    links=bp["links"]
    need(all(a in source_nodes and b in source_nodes for a,b in links),"Unknown link node")
    buffer=policy["visual_pair_gap_heuristic_m"]
    corridor=policy["corridor_buffer_internal_design_only_m"]
    need(buffer==corridor==4,"Internal paper buffer changed; review needed")
    assessed=[]
    summary=[]
    for p in props:
        option=policy["placement_options"][p["id"]]
        need(option["status"]=="UNVERIFIED_NON_DEPLOYABLE_OPTION"
             and option["needs_in_game_validation"] is True,"Policy bypass")
        need(option["original_role"]==p["visual_role"],"Stale role mapping")
        model=option["proposed_visual_model_classname"]
        need(model is None or model in model_by_name,"Reference model missing")
        radius=visual_radius(model_by_name[model]) if model is not None else None
        wx,wz=local_to_world(p["local_x"],p["local_z"],9000,7800,240,220,120)
        need(0<=wx<=12800 and 0<=wz<=12800,"Out of map bounds")
        status={
            "id":p["id"],"zone":p["zone"],"visual_role":p["visual_role"],
            "local_x":p["local_x"],"local_z":p["local_z"],
            "world_x_provisional":round(wx,3),"world_z_provisional":round(wz,3),
            "world_y_measured":None,
            "placement_intent":option["placement_intent"],
            "provisional_model":model,
            "model_status":"UNVERIFIED_VISUAL_REFERENCE_ONLY" if model else "NO_SIZE_EVIDENCE",
            "visual_radius_m":radius,
            "physical_collision_verified":False,
            "ps5_object_spawner_verified":False,
            "terrain_survey_verified":False,
            "deployment_allowed":False
        }
        assessed.append(status)

        distances=[{"link":a+"__"+b,"incident_to_own_sector":p["zone"] in (a,b),
                    "paper_centerline_distance_m":dist_to_segment(
                        (p["local_x"],p["local_z"]),source_nodes[a],source_nodes[b]
                    )} for a,b in links]
        all_nearest=min(distances,key=lambda item:(item["paper_centerline_distance_m"],item["link"]))
        unrelated=[x for x in distances if not x["incident_to_own_sector"]]
        other_nearest=min(unrelated,key=lambda item:(item["paper_centerline_distance_m"],item["link"]))
        summary.append({
            "symbol_id":p["id"],"zone":p["zone"],
            "provisional_model":model,"visual_radius_m":round(radius,3) if radius is not None else None,
            "known_visual_envelope":radius is not None,
            "nearest_paper_link":all_nearest["link"],
            "nearest_any_link_centerline_distance_m":round(all_nearest["paper_centerline_distance_m"],3),
            "nearest_link_incident_to_own_sector":all_nearest["incident_to_own_sector"],
            "nearest_other_zone_paper_link":other_nearest["link"],
            "nearest_other_zone_link_distance_m":round(other_nearest["paper_centerline_distance_m"],3),
            "hypothetical_unrelated_link_margin_m":round(other_nearest["paper_centerline_distance_m"]-radius,3) if radius is not None else None,
            "unrelated_link_review_flag":(
                "PAPER_LINK_VISUAL_ENVELOPE_WITHIN_BUFFER"
                if radius is not None and other_nearest["paper_centerline_distance_m"]<radius+corridor
                else "NO_ASSIGNED_MODEL_SIZE" if radius is None
                else "MARGIN_PASSED_PAPER_ONLY"
            ),
            "sector_center_link_geometry_critical_caveat":
                 "Paper links terminate at sector CENTERS, not verified building doors.",
            "possible_interior":p["id"] in {"barracks_04","hq_04","hq_05"},
            "site_and_collision_still_unverified":True
        })
    known=sum(p["visual_radius_m"] is not None for p in assessed)
    need(known==policy["selected_role_matched_options"]==9,"Unexpected known visual candidates")
    need(len(assessed)-known==policy["unassigned_role_visual_sizes"]==17,"Unknown size count changed")
    pairs=[proximity(a,b,buffer) for a,b in itertools.combinations(assessed,2)]
    need(len(pairs)==325,"Expected all 26 choose 2 placements")
    class_count=Counter(p["classification"] for p in pairs)
    near_unknown=[
        p for p in pairs
        if p["classification"] in (
            "UNKNOWN_MARKER_CENTER_INSIDE_KNOWN_VISUAL_DISK",
            "UNKNOWN_MARKER_CENTER_NEAR_KNOWN_VISUAL_DISK"
        )
    ]
    important={
        "stage":"4.10",
        "status":"FULL_26_PLACEMENT_RISK_AUDIT_SOME_MODEL_SIZES_UNKNOWN",
        "map":"Livonia",
        "candidate_center_world_xz":world_center,
        "surveyed_game_terrain":False,
        "total_placement_markers":len(props),
        "reference_model_assigned_count":known,
        "model_size_unknown_count":len(props)-known,
        "pairwise_marker_tests":len(pairs),
        "pairs_both_reference_sizes_known":known*(known-1)//2,
        "pairs_one_or_more_unknown_size":len(pairs)-known*(known-1)//2,
        "pair_classification_counts":dict(sorted(class_count.items())),
        "known_model_to_unknown_origin_within_buffer":len(near_unknown),
        "reference_visual_disk_overlaps":class_count["REFERENCE_VISUAL_DISKS_OVERLAP"],
        "paper_route_centerline_checks_per_marker":len(links),
        "route_line_is_not_physical_trail":True,
        "design_link_endpoints_are_sector_centers":True,
        "unknown_size_does_not_equal_zero_radius":True,
        "interior_markers_may_be_deliberate":True,
        "placement_reports":summary,
        "near_unknown_marker_review_cases":near_unknown,
        "all_pairs":pairs,
        "recommended_next_actions":[
           "Do not infer safety for the 17 props with no suitable size evidence.",
           "Inspect barracks_03 and barracks_04 against barracks_01 visual disk, including intentional indoor placement.",
           "Inspect HQ narrative and interior markers against hq_01 visual disk, including actual door/floor and collision.",
           "Revisit the five-object Stage 4.9 advisory choices: some map to a full-size object despite a symbolic barrier or entry-marker role.",
           "Model real walkway waypoints/doors before claiming corridor clearance. All graph links currently join zone centers.",
           "Acquire trusted DayZ SurfaceY and PS4/PS5 Nitrado live checks before selecting actual objects."
        ],
        "any_real_collision_confirmed":False,
        "any_console_model_verified":False,
        "any_world_y_measured":False,
        "object_spawner_generated":False,
        "deployment_allowed":False
    }
    return important

def build()->dict:
    bp=json.loads(BP.read_text(encoding="utf-8"))
    micro=json.loads(MICRO.read_text(encoding="utf-8"))
    meta=json.loads(META.read_text(encoding="utf-8"))
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    data=gather(bp,micro,meta,policy)
    OUT.mkdir(parents=True,exist_ok=True)
    report=OUT/"full_26_layout_risk_report.json"
    report.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    csvplacements=OUT/"all_26_placement_review.csv"
    keys=["symbol_id","zone","provisional_model","visual_radius_m","known_visual_envelope",
          "nearest_paper_link","nearest_any_link_centerline_distance_m",
          "nearest_link_incident_to_own_sector","nearest_other_zone_paper_link",
          "nearest_other_zone_link_distance_m","hypothetical_unrelated_link_margin_m",
          "unrelated_link_review_flag","possible_interior"]
    with csvplacements.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
        writer.writeheader();writer.writerows(data["placement_reports"])
    csvpairs=OUT/"all_325_pair_review.csv"
    keys=["a","b","a_zone","b_zone","local_center_separation_m",
          "radius_a_m","radius_b_m","visual_disk_edge_gap_m","classification",
          "review_priority","may_be_intentional_indoor",
          "known_model_edge_to_unknown_marker_center_m"]
    with csvpairs.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
        writer.writeheader();writer.writerows(data["all_pairs"])
    files={
        "DO_NOT_DEPLOY.txt":(
            "STAGE 4.10. 26 conceptual markers, 17 UNKNOWN visual sizes. P3D visuals NOT collision.\n"
            "Graph centerlines are NOT walkable paths. NO world Y. No PS5 tests. DO NOT UPLOAD TO NITRADO.\n"
        ).encode(),
        "full_26_layout_risk_report.json":report.read_bytes(),
        "all_26_placement_review.csv":csvplacements.read_bytes(),
        "all_325_pair_review.csv":csvpairs.read_bytes()
    }
    manifest={name:hashlib.sha256(content).hexdigest() for name,content in sorted(files.items())}
    files["SHA256_MANIFEST.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    zpath=OUT/"beileys47-full-layout-paper-audit-only.zip"
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as archive:
        for name,contents in sorted(files.items()):add_bytes(archive,name,contents)
    with zipfile.ZipFile(zpath) as archive:
        need(archive.testzip() is None and set(archive.namelist())==set(files),"Invalid ZIP")
        for name,digest in manifest.items():
            need(hashlib.sha256(archive.read(name)).hexdigest()==digest,"Invalid ZIP member hash")
        need(not any(n.endswith("cfggameplay.json") or "zone47_objects" in n for n in archive.namelist()),
             "Installable game objects forbidden")
    print("PASS: Stage 4.10: 26 symbolic props, 325 pairs, 9 P3D visual references, 17 UNKNOWN footprints.")
    print(f"REVIEW: {len(data['near_unknown_marker_review_cases'])} known-to-unknown origin risks; "
          f"{data['reference_visual_disk_overlaps']} visual disk overlaps among fully specified pairs.")
    print("NO DayZ Y, collision, walkable trails or PlayStation runtime checks. DO NOT DEPLOY.")
    return data

if __name__=="__main__":build()
