#!/usr/bin/env python3
"""Stage 4.9: static P3D visual-envelope clearance around conceptual route lines.

All dimensions originate from indexed P3D *visual* bbox metadata, not collision
geometries. Routes are GRAPH STRAIGHT-LINE CONCEPTS, not actual accessible roads.
No Y, no PlayStation class compatibility, no game file, no Nitrado deployment.
"""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path

from zip_deterministic import add_bytes

from build_stage4_terrain_survey_grid import local_to_world

ROOT=Path(__file__).resolve().parents[1]
META=ROOT/"config/stage4_9_p3d_bbox_evidence.json"
CANDIDATES=ROOT/"config/stage4_asset_candidates.json"
BP=ROOT/"config/stage4_zone47_blueprint.json"
LAYOUT=ROOT/"config/stage4_zone47_micro_layout.json"
PILOT=ROOT/"dist/stage4_6_preflight/zone47_micro_pilot_plan.json"
OUT=ROOT/"dist/stage4_9_visual_envelopes"
BUFFER=4.0  # internal buffer from PAPER route centerline, not true path clearance
STEP=2
SEARCH_RADIUS=20
ZONE_RADIUS=25

# Advisory candidates for 5-prop low-structure trial, no console spawn approval.
# These are NOT automatically assigned to the real object spawner.
PILOT_MODELS={
    "checkpoint_01":"Land_Mil_GuardBox_Green",
    "woods_01":"Land_Mil_Fortified_Nest_Small",
    "service_01":"Land_Guardhouse",
    "logistics_02":"Land_Container_1Bo",
    "hq_02":"Land_Mil_Guardhouse1"
}

def check(ok:bool,why:str)->None:
    if not ok:raise AssertionError(why)

def visual_radius(record:dict)->float:
    lo,hi=record["bbox_min"],record["bbox_max"]
    for axis in ("x","y","z"):
        check(isinstance(lo[axis],(float,int)) and isinstance(hi[axis],(float,int)),
              "Invalid P3D bounds")
        check(math.isfinite(lo[axis]) and math.isfinite(hi[axis]) and lo[axis]<hi[axis],
              "Impossible P3D bounds")
    # A circle centered at the original model origin, containing every corner
    # of its reported VISUAL X/Z bbox regardless of its unknown yaw.
    return max(math.hypot(x,z) for x in (lo["x"],hi["x"]) for z in (lo["z"],hi["z"]))

def dist_to_segment(p:tuple[float,float],a:tuple[float,float],b:tuple[float,float])->float:
    dx,dz=b[0]-a[0],b[1]-a[1]
    norm=dx*dx+dz*dz
    check(norm>0,"Degenerate route edge")
    t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/norm))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz)

def min_route_distance(p:tuple[float,float],nodes:dict,links:list)->float:
    return min(dist_to_segment(p,nodes[a],nodes[b]) for a,b in links)

def optimize(original:tuple[int,int],sector:tuple[int,int],radius:float,nodes:dict,
             links:list,selected:list[dict])->dict:
    scored=[]
    for x in range(original[0]-SEARCH_RADIUS,original[0]+SEARCH_RADIUS+1,STEP):
        for z in range(original[1]-SEARCH_RADIUS,original[1]+SEARCH_RADIUS+1,STEP):
            if not (0<=x<=240 and 0<=z<=220):continue
            if math.dist((x,z),sector)>ZONE_RADIUS:continue
            distance=min_route_distance((x,z),nodes,links)
            min_gap=min((math.dist((x,z),(s["local_x"],s["local_z"]))-radius-s["visual_radius_m"]
                         for s in selected),default=float("inf"))
            shift=math.dist((x,z),original)
            accepted=distance+1e-9>=radius+BUFFER and min_gap+1e-9>=BUFFER
            if accepted:scored.append((round(shift,7),-round(distance,7),x,z,distance,min_gap))
    if not scored:
        return {"has_heuristic_solution":False,"suggested_local_x":None,
                "suggested_local_z":None,"distance_to_nearest_paper_link_m":None,
                "suggested_displacement_m":None,"risk":"NO_SOLUTION_UNDER_VISUAL_ENVELOPE_HEURISTIC"}
    scored.sort()
    _,__,x,z,distance,min_gap=scored[0]
    return {
       "has_heuristic_solution":True,
       "suggested_local_x":x,"suggested_local_z":z,
       "distance_to_nearest_paper_link_m":round(distance,3),
       "model_visual_radius_m":round(radius,3),
       "buffer_from_route_centerline_m":BUFFER,
       "suggested_displacement_m":round(math.dist((x,z),original),3),
       "min_separation_from_other_pilot_visual_envelopes_m":
          round(min_gap,3) if math.isfinite(min_gap) else None,
       "risk":"GEOMETRY_ONLY_NOT_WALKABILITY_OR_COLLISION_VERIFIED"
    }

def build()->dict:
    meta=json.loads(META.read_text(encoding="utf-8"))
    source=json.loads(CANDIDATES.read_text(encoding="utf-8"))
    bp=json.loads(BP.read_text(encoding="utf-8"))
    micro=json.loads(LAYOUT.read_text(encoding="utf-8"))
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    check(meta["status"]=="THIRD_PARTY_P3D_VISUAL_BBOX_METADATA_NOT_COLLISION_PROOF",
          "Model metadata status changed")
    check(bp["status"]=="DESIGN_ONLY_NOT_INSTALLABLE"
          and pilot["status"]=="PILOT_PLANNING_ONLY_NOT_NITRADO_INSTALLABLE",
          "Unsafe input status")
    check(pilot["real_height_measurements"]==0 and pilot["deployment_allowed"] is False,
          "Unexpected height/source approval")
    available={r["candidate_dayz_terrain_classname"]:r for r in meta["models"]}
    approved={r["name"] for r in source["models"]}
    check(len(available)==len(approved)==13 and set(available)==approved,"Unexpected P3D audit coverage")
    # Model classname match is only a NAME HEURISTIC, not a proven runtime
    # DayZ class->P3D mapping.
    for cls,model in available.items():
        check(model["p3d_model_class"].casefold()==cls.removeprefix("Land_").casefold(),
              "Unmatched terrain classname and P3D filename")
        check(model["odolv"]==56,"Unexpected index version")
        check(model["console_runtime_verified"] is False
              and model["physics_collision_verified"] is False,"Unsafe model metadata claim")
        check(0.1<visual_radius(model)<45,"Unreasonable visual envelope")
    nodes={z["id"]:(z["x"],z["z"]) for z in bp["zones"]}
    nodes.update({e["id"]:(e["x"],e["z"]) for e in bp["entrances"]})
    check(len(bp["links"])==16,"Stage 4.7 bypass missing")
    positions={x["id"]:(x["local_x"],x["local_z"],x["zone"]) for x in micro["asset_placements"]}
    check(set(PILOT_MODELS)=={p["placement_id"] for p in pilot["pilot_props"]},"Pilot IDs changed")
    chosen=[]
    records=[]
    for pid,cls in PILOT_MODELS.items():
        lx,lz,sector=positions[pid]
        radius=visual_radius(available[cls])
        old_dist=min_route_distance((lx,lz),nodes,bp["links"])
        candidate=optimize((lx,lz),nodes[sector],radius,nodes,bp["links"],chosen)
        check(candidate["has_heuristic_solution"],f"No conservative pilot-space alternative: {pid}")
        wx,wz=local_to_world(candidate["suggested_local_x"],candidate["suggested_local_z"],
                            pilot["center_x"],pilot["center_z"],240,220,
                            pilot["orientation_degrees"])
        check(0<=wx<=12800 and 0<=wz<=12800,"Out of world bounds")
        records.append({
          "symbolic_placement_id":pid,"sector":sector,"conceptual_p3d_class_candidate":cls,
          "p3d_model_source_url":available[cls]["source_model_url"],
          "visual_envelope_radius_m":round(radius,3),
          "visual_bbox_span_x_m":round(available[cls]["bbox_max"]["x"]-available[cls]["bbox_min"]["x"],3),
          "visual_bbox_span_z_m":round(available[cls]["bbox_max"]["z"]-available[cls]["bbox_min"]["z"],3),
          "initial_local_x":lx,"initial_local_z":lz,
          "initial_distance_to_nearest_paper_path_m":round(old_dist,3),
          "initial_paper_corridor_margin_m":round(old_dist-radius,3),
          "initial_fails_4m_heuristic":old_dist<radius+BUFFER,
          "suggestion":candidate,
          "suggested_world_x":round(wx,3),"suggested_world_z":round(wz,3),
          "suggested_world_y":None,
          "p3d_to_console_class_compatibility_verified":False,
          "real_collision_clearance_confirmed":False,
          "ready_to_install":False
        })
        chosen.append({"local_x":candidate["suggested_local_x"],
                       "local_z":candidate["suggested_local_z"],
                       "visual_radius_m":radius})
    maxvisual=max(visual_radius(r) for r in available.values())
    sorted_models=sorted([
       {"candidate_class":cls,"model_name":rec["p3d_model_class"],
        "p3d_index_record":rec["p3d_explorer_id"],
        "visual_bbox_width_m":round(rec["bbox_max"]["x"]-rec["bbox_min"]["x"],3),
        "visual_bbox_length_m":round(rec["bbox_max"]["z"]-rec["bbox_min"]["z"],3),
        "visual_envelope_radius_m":round(visual_radius(rec),3),
        "collision_and_playstation_spawner_validated":False}
       for cls,rec in available.items()
    ],key=lambda x:(-x["visual_envelope_radius_m"],x["candidate_class"]))
    report={
      "stage":"4.9","status":"MODEL_BBOX_PAPER_CLEARANCE_NOT_PHYSICAL_COLLISION",
      "model_metadata_source":meta["source"],"indexed_game_version":"DayZ 1.30 ODOL v56",
      "third_party_model_name_mapping_is_unverified":True,
      "model_count":13,"largest_visual_envelope_radius_m":round(maxvisual,3),
      "visual_model_size_catalog":sorted_models,
      "provisional_site_world_center":[pilot["center_x"],pilot["center_z"]],
      "pilot_heuristic_candidate_count":len(records),
      "pilot_visual_clearance_rules":{"paper_path_centerline_buffer_m":BUFFER,
          "max_offset_from_original_local_marker_m":SEARCH_RADIUS,
          "max_distance_from_sector_center_m":ZONE_RADIUS,
          "candidate_search_grid_step_m":STEP},
      "initial_heuristic_fail_count":sum(r["initial_fails_4m_heuristic"] for r in records),
      "proposed_heuristic_fail_count":sum(not r["suggestion"]["has_heuristic_solution"] for r in records),
      "pilot_provisional_geometry_adjustments":records,
      "all_height_y_unknown":True,
      "all_p3d_collision_shapes_unknown":True,
      "all_proposed_paper_paths_terrain_unverified":True,
      "playstation_model_classes_verified":False,
      "no_live_objects_spawned":True,
      "any_site_approved":False,
      "deployment_allowed":False,
      "critical_warnings":[
        "P3D visual bounds are NOT DayZ collision hulls; this is a conservative 2D disk enclosing reported metadata bbox corners.",
        "P3D Explorer is third-party; name matching does not certify the Land_ object class or version against the console.",
        "Four-metre corridor buffer is an internal DESIGN heuristic against a theoretical straight line, not a measured playable path.",
        "Small local X/Z moves can hit roads, trees, slopes or vanilla objects; the suggested positions remain UNAPPROVED.",
        "No actual Y, playable route, DayZ object-spawn performance, player trapping or vehicle clearance verified."
      ]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"pilot_visual_clearance_report.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    no=b"STAGE 4.9: THIRD-PARTY P3D VISUAL BOUNDS ONLY. NO REAL COLLISIONS, Y, CONSOLE OR ROUTES. DO NOT DEPLOY TO NITRADO.\n"
    files={"DO_NOT_DEPLOY.txt":no,"pilot_visual_clearance_report.json":path.read_bytes()}
    digest={n:hashlib.sha256(v).hexdigest() for n,v in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(digest,indent=2)+"\n").encode("utf-8")
    with zipfile.ZipFile(OUT/"beileys47-visual-clearance-not-deployable.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):add_bytes(z,name,data)
    with zipfile.ZipFile(OUT/"beileys47-visual-clearance-not-deployable.zip") as z:
        check(z.testzip() is None and set(z.namelist())==set(files),"ZIP integrity")
        for name,sha in digest.items():check(hashlib.sha256(z.read(name)).hexdigest()==sha,"ZIP checksum mismatch")
    print(f"PASS: 13 third-party P3D visual bounds; pilot baseline {report['initial_heuristic_fail_count']}/5 near PAPER routes.")
    print("PASS: proposed alternatives remain non-deployable, all real Y/collision/PS5 checks missing.")
    return report

if __name__=="__main__":build()
