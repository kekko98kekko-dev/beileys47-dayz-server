#!/usr/bin/env python3
"""Fail-closed OFFLINE Object Spawner preview exporter.

Requires a REAL completed terrain+asset survey. It is impossible to export
from the project's default template. It NEVER connects to Nitrado.
Exported files would still be EXPERIMENTAL, NOT PS4/PS5 certified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SURVEY=ROOT/"dist/stage4/zone47_survey_template.json"
STAGE3_GAMEPLAY=ROOT/"dist/stage3/dayzOffline.enoch/cfggameplay.json"
DEFAULT_OUT=ROOT/"dist/stage4/experimental_object_spawner"
OUTPUT_NAME="zone47_objects.json"

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("EXPORT BLOCKED: "+message)

def numeric(x: object, label: str, low: float, high: float) -> float:
    require(type(x) in (int,float) and math.isfinite(x) and low<=x<=high,f"{label} missing/outside safety bounds")
    return float(x)

def export(survey_path:Path, gameplay_path:Path, output_dir:Path) -> dict:
    survey=json.loads(survey_path.read_text(encoding="utf-8"))
    blueprint=json.loads((ROOT/"config/stage4_zone47_blueprint.json").read_text(encoding="utf-8"))
    micro=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text(encoding="utf-8"))
    candidates=json.loads((ROOT/"config/stage4_asset_candidates.json").read_text(encoding="utf-8"))
    require(survey.get("status")=="SURVEY_DATA_REVIEWED_FOR_OFFLINE_EXPORT",
            "reviewed survey status required; initial template is NOT exportable")
    flags=survey.get("confirmations",{})
    for key in ("actual_livonia_site_surveyed","terrain_heights_recorded_for_each_prop",
                "game_asset_classes_checked_against_current_playstation_version",
                "exact_current_game_version_matched"):
        require(flags.get(key) is True,f"survey evidence/confirmation missing: {key}")
    require(survey.get("map")=="Livonia", "map mismatch")
    site=survey.get("site",{})
    x0=numeric(site.get("world_origin_x"),"world origin X",0,20000)
    z0=numeric(site.get("world_origin_z"),"world origin Z",0,20000)
    a=numeric(site.get("rotation_degrees"),"rotation", -360,360)
    require(isinstance(site.get("game_version"),str) and len(site["game_version"].strip())>=2,"record exact DayZ build")
    require(isinstance(site.get("survey_notes"),str) and len(site["survey_notes"].strip())>=20,"terrain survey notes required")
    require(blueprint["coordinate_system"]["world_x"] is None and not blueprint["coordinate_system"]["terrain_surveyed"],
            "project's paper blueprint must remain unsigned/unanchored")
    layout={x["id"]:x for x in micro["asset_placements"]}
    require(len(layout)==len(micro["asset_placements"])==26,"wrong micro placement set")
    placements=survey.get("placements")
    require(isinstance(placements,list) and len(placements)==len(layout),"all 26 placements must be surveyed")
    allowed={x["name"] for x in candidates["models"]}
    ids=[x.get("id") for x in placements]
    require(len(set(ids))==len(ids) and set(ids)==set(layout),"placement IDs mismatch")
    theta=math.radians(a)
    ct,st=math.cos(theta),math.sin(theta)
    objects=[]
    positions=[]
    for p in placements:
        label=p["id"]
        require(p.get("asset_verified_in_target_version") is True,f"asset unverified: {label}")
        require(p.get("terrain_height_measured") is True,f"height unmeasured: {label}")
        name=p.get("classname")
        require(isinstance(name,str) and name in allowed,f"class not on official-candidate shortlist: {label}")
        y=numeric(p.get("height_y"),f"Y height {label}",-200,1500)
        yaw=numeric(p.get("yaw_degrees"),f"yaw {label}",-360,360)
        pitch=numeric(p.get("pitch_degrees"),f"pitch {label}",-90,90)
        roll=numeric(p.get("roll_degrees"),f"roll {label}",-90,90)
        scale=numeric(p.get("scale"),f"scale {label}",0.85,1.15)
        local=layout[label]
        lx,lz=local["local_x"],local["local_z"]
        x=x0+ct*lx-st*lz
        z=z0+st*lx+ct*lz
        numeric(x,f"derived X {label}",0,20000)
        numeric(z,f"derived Z {label}",0,20000)
        require(all(math.hypot(x-old_x,z-old_z)>=2.5 for old_x,old_z in positions),
                f"too-close placements may collide: {label}")
        positions.append((x,z))
        objects.append({
            "name":name,"pos":[round(x,4),round(y,4),round(z,4)],
            "ypr":[round(yaw,4),round(pitch,4),round(roll,4)],
            "scale":round(scale,3),"enableCEPersistency":False
        })
    require(len(objects)==26,"missing placements")

    game=json.loads(gameplay_path.read_text(encoding="utf-8-sig"))
    require(isinstance(game.get("WorldsData",{}).get("objectSpawnersArr"),list),
            "current gameplay lacks compatible objectSpawnersArr")
    old=game["WorldsData"]["objectSpawnersArr"]
    require(all(isinstance(x,str) for x in old),"invalid existing Object Spawner references")
    require(OUTPUT_NAME not in old, "a ZONA 47 spawner is already referenced")
    game["WorldsData"]["objectSpawnersArr"]=old+[OUTPUT_NAME]

    warn={
        "status":"EXPERIMENTAL_OFFLINE_EXPORT_NOT_PLAYSTATION_VERIFIED",
        "site_build_reported":site["game_version"],
        "world_positions_count":len(objects),
        "no_provider_connection":True,
        "no_live_deployment":True,
        "still_required":["owner authorization","Nitrado-compatible file path","original mission backup",
                          "PS4/PS5 object collision tests","PS4/PS5 performance and sightline tests",
                          "rollback plan"],
        "source_gameplay_sha256":hashlib.sha256(gameplay_path.read_bytes()).hexdigest(),
        "warning":"DO NOT AUTOMATICALLY DEPLOY. This is an OFFLINE test asset. All confirmations are user-supplied, not independently certified."
    }
    # Produce no output until all fail-closed checks have passed.
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/OUTPUT_NAME).write_text(json.dumps({"Objects":objects},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (output_dir/"cfggameplay.json").write_text(json.dumps(game,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (output_dir/"DO_NOT_DEPLOY_REPORT.json").write_text(json.dumps(warn,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PASS: EXPERIMENTAL local Object Spawner preview exported, no Nitrado network connection.")
    print("NOT VERIFIED: actual runtime rendering, collisions, FPS, correctness of survey assertions.")
    return warn

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--survey",type=Path,default=SURVEY)
    parser.add_argument("--gameplay",type=Path,default=STAGE3_GAMEPLAY)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    export(args.survey,args.gameplay,args.output)
