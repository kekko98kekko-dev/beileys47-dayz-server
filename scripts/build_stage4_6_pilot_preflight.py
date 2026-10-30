#!/usr/bin/env python3
"""Stage 4.6 preflight: compare reviewed centers to generated Stage 4.2 results.

Generate only a non-installable five-prop pilot plan at X/Z without model
class names or Y heights. Not a DayZ object-spawner, not terrain verified.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from build_stage4_terrain_survey_grid import local_to_world

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"config/stage4_centered_export_contract.json"
GRID=ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json"
SCREEN=ROOT/"dist/stage4_footprint/footprint_report.json"
MICRO=ROOT/"config/stage4_zone47_micro_layout.json"
OUT=ROOT/"dist/stage4_6_preflight"
PILOT_IDS=("checkpoint_01","woods_01","service_01","logistics_02","hq_02")

def require(ok:bool,msg:str)->None:
    if not ok:raise AssertionError(msg)

def run()->dict:
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    grid=json.loads(GRID.read_text(encoding="utf-8"))
    screen=json.loads(SCREEN.read_text(encoding="utf-8"))
    micro=json.loads(MICRO.read_text(encoding="utf-8"))
    require(c["status"]=="STATIC_SCREENED_CENTERS_ONLY_NEVER_TERRAIN_APPROVED"
            and c["deployment_allowed"] is False,"Unsafe configuration")
    require(c["site_coordinate_convention"]=="WORLD_CENTER_OF_BLUEPRINT","Unexpected coordinate reference")
    require(c["blueprint_width_m"]==240 and c["blueprint_depth_m"]==220,"Changed blueprint dimensions")
    require(len(c["candidates"])==len(grid["regions"])==len(screen["regions"])==3,"Three candidates required")
    reference={p["region"]:p for p in c["candidates"]}
    for src in grid["regions"]:
        region=src["region"]
        require(region in reference,"Missing candidate")
        fixed=reference[region]
        require((fixed["world_center_x"],fixed["world_center_z"],fixed["screened_orientation_degrees"])==
                (src["center_x"],src["center_z"],src["orientation_degrees"]),
                f"Outdated site anchor: {region}")
        original=next(v for v in screen["regions"] if v["id"]==region)
        require((original["candidates"][0]["x"],original["candidates"][0]["z"],
                 original["candidates"][0]["best_rotation"]["rotation_deg"])==
                (fixed["world_center_x"],fixed["world_center_z"],fixed["screened_orientation_degrees"]),
                f"Changed Stage 4.2 screening: {region}")
    selected=reference["central"]
    props={p["id"]:p for p in micro["asset_placements"]}
    require(len(props)==26 and all(k in props for k in PILOT_IDS),"Missing pilot placements")
    plan=[]
    for pid in PILOT_IDS:
        p=props[pid]
        x,z=local_to_world(p["local_x"],p["local_z"],
                           selected["world_center_x"],selected["world_center_z"],
                           c["blueprint_width_m"],c["blueprint_depth_m"],
                           selected["screened_orientation_degrees"])
        plan.append({
          "placement_id":pid,"sector":p["zone"],"visual_role":p["visual_role"],
          "candidate_world_x":round(x,3),"candidate_world_z":round(z,3),
          "ground_y":None,"selected_model_classname":None,
          "actual_collision_clearance_verified":False,
          "physical_terrain_survey_verified":False,
          "console_asset_verified":False,
          "ready_to_install":False
        })
    data={
      "stage":"4.6","status":"PILOT_PLANNING_ONLY_NOT_NITRADO_INSTALLABLE",
      "center_x":selected["world_center_x"],"center_z":selected["world_center_z"],
      "source_region":"central","orientation_degrees":selected["screened_orientation_degrees"],
      "coordinate_reference":"WORLD_CENTER_OF_BLUEPRINT",
      "pilot_prop_count":len(plan),"pilot_props":plan,
      "official_object_spawner_schema_keys":["Objects","name","pos","ypr","scale","enableCEPersistency"],
      "reference_documentation":"https://community.bohemia.net/wiki/DayZ:Object_Spawner",
      "official_schema_meaning":"The official JSON shape is checked in SYNTHETIC exporter tests; runtime object compatibility remains unproven.",
      "real_height_measurements":0,
      "any_real_site_approved":False,
      "any_runtime_objects_spawned":False,
      "ps4_ps5_tested":False,
      "deployment_allowed":False,
      "next_mandatory_gate":"real DayZ SurfaceY measurements plus terrain, roads, collisions and PS4/5 verification"
    }
    OUT.mkdir(parents=True,exist_ok=True)
    rp=OUT/"zone47_micro_pilot_plan.json"
    rp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    note=b"ZONA 47 STAGE 4.6 IS A PLANNING TEMPLATE ONLY. ALL HEIGHTS AND MODEL CLASSES UNKNOWN. DO NOT DEPLOY TO NITRADO.\n"
    files={"README_DO_NOT_DEPLOY.txt":note,"zone47_micro_pilot_plan.json":rp.read_bytes()}
    manifest={name:hashlib.sha256(v).hexdigest() for name,v in files.items()}
    files["sha256.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    with zipfile.ZipFile(OUT/"beileys47-micro-pilot-plan-only.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):z.writestr(name,value)
    with zipfile.ZipFile(OUT/"beileys47-micro-pilot-plan-only.zip") as z:
        require(z.testzip() is None,"Bad ZIP")
        require(set(z.namelist())==set(files),"Unexpected ZIP file")
        for name,digest in manifest.items():
            require(hashlib.sha256(z.read(name)).hexdigest()==digest,"Checksum mismatch")
        require("zone47_objects.json" not in z.namelist(),"Object spawner cannot ship")
    print("PASS: reviewed centers cross-check Stage 4.2/4.4; five-prop CENTRAL world-XZ plan.")
    print("NO measured Y, no model classes, no collision or PS4/5 claims, no Nitrado modification.")
    return data

if __name__=="__main__":run()
