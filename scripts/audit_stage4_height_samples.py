#!/usr/bin/env python3
"""Stage 4.5: validate actual X/Z-indexed DayZ surface height observations.

Fail closed: incomplete/uncorroborated metadata and fabricated coordinates
never count as terrain-ready. Even complete data is ONLY DATA ACCEPTED FOR
MANUAL SURVEY REVIEW, not a PS5-validated or deployable object spawner.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GRID=ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json"
EXPECTED_METHODS={"DayZ_CGame_SurfaceY","DayZ_terrain_data_verified"}
OUT=ROOT/"dist/stage4_height_capture/terrain_height_audit.json"
ANGLE_LIMIT=10.0   # internal review heuristic, not an engine-verified grade limit
HEIGHT_SPAN_LIMIT=18.0  # internal comfort threshold across 240x220m

def require(ok:bool,msg:str)->None:
    if not ok:raise ValueError("INVALID HEIGHT DATASET: "+msg)

def finite(value:object,name:str,lower:float=-200,upper:float=1500)->float:
    require(type(value) in (float,int) and math.isfinite(value) and lower<=value<=upper,
            name+" must be a finite measured number within declared sanity bounds")
    return float(value)

def valid_captured_utc(value: object) -> bool:
    """Require a real ISO-8601 UTC instant, not an arbitrary 16-char string."""
    if not isinstance(value, str) or re.fullmatch(
        r"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?Z", value
    ) is None:
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def analyze(data:dict,reference:dict,region_name:str)->dict:
    region=next((x for x in reference["regions"] if x["region"]==region_name),None)
    require(region is not None,"unknown region")
    require(data.get("stage")=="4.5" and data.get("schema_version")=="1.0","wrong schema version")
    require(data.get("map")=="Livonia" and data.get("region")==region_name,"wrong map or region")
    require(data.get("official_mission_baseline")==reference["official_baseline_commit"],"baseline mismatch")
    require(data.get("candidate_center_x")==region["center_x"] and
            data.get("candidate_center_z")==region["center_z"],"center mismatch")
    require(data.get("candidate_rotation_degrees")==region["orientation_degrees"],"rotation mismatch")
    expected={("GRID",x["sample_id"]):(x["world_x"],x["world_z"]) for x in region["terrain_samples"]}
    expected.update({("PROP",x["id"]):(x["world_x"],x["world_z"]) for x in region["prototype_locations"]})
    points=data.get("points")
    require(isinstance(points,list) and len(points)==182,"exactly 182 sample records required")
    seen=set()
    missing=[]
    yvalues={}
    for p in points:
        require(isinstance(p,dict),"point must be JSON object")
        key=(p.get("kind"),p.get("id"))
        require(key in expected and key not in seen,"unknown or duplicate grid/prop ID")
        seen.add(key)
        x,z=expected[key]
        # Tolerance covers the three-decimal place geometry rounding, but
        # prevents accidental X/Z swapping, wrong origin and stale site data.
        require(type(p.get("x")) in (float,int) and
                type(p.get("z")) in (float,int) and
                abs(p["x"]-x)<0.01 and abs(p["z"]-z)<0.01,
                "coordinate mismatch at "+str(key))
        y=p.get("ground_y")
        if y is None:
            missing.append(key)
        else:
            yvalues[key]=finite(y,str(key))
    require(seen==set(expected),"missing point IDs")
    meta=data.get("measurement",{})
    require(isinstance(meta,dict),"missing provenance object")
    method=meta.get("method")
    game=meta.get("dayz_game_build")
    captured=meta.get("captured_utc")
    ref=meta.get("evidence_reference")
    provenance_complete=(isinstance(method,str) and method in EXPECTED_METHODS and
                         isinstance(game,str) and len(game.strip())>=5 and
                         valid_captured_utc(captured) and
                         isinstance(ref,str) and len(ref.strip())>=12)
    complete=(len(missing)==0 and provenance_complete)
    grades=[]
    if complete:
        assert len(yvalues)==182
        for j in range(12):
            for i in range(13):
                key=("GRID",f"GRID-{i:02d}-{j:02d}")
                if i+1<13:
                    nextkey=("GRID",f"GRID-{i+1:02d}-{j:02d}")
                    p1,p2=expected[key],expected[nextkey]
                    dist=math.dist(p1,p2)
                    grades.append(math.degrees(math.atan(abs(yvalues[key]-yvalues[nextkey])/dist)))
                if j+1<12:
                    nextkey=("GRID",f"GRID-{i:02d}-{j+1:02d}")
                    p1,p2=expected[key],expected[nextkey]
                    dist=math.dist(p1,p2)
                    grades.append(math.degrees(math.atan(abs(yvalues[key]-yvalues[nextkey])/dist)))
    ordered=sorted(grades)
    height_range=(max(yvalues.values())-min(yvalues.values())) if complete else None
    max_angle=max(ordered) if ordered else None
    p95=ordered[int((len(ordered)-1)*.95)] if ordered else None
    review_flags=[]
    if complete:
        if max_angle>ANGLE_LIMIT:review_flags.append("LOCAL_GRADE_EXCEEDS_INTERNAL_10_DEG_HEURISTIC")
        if height_range>HEIGHT_SPAN_LIMIT:review_flags.append("TOTAL_HEIGHT_SPAN_EXCEEDS_INTERNAL_18_M_HEURISTIC")
        # Do not claim accepted terrain is collision-free; even a flat
        # topographic mesh can be covered by trees, water or roads.
        status=("REVIEW_REQUIRED_STEEP_GRADE" if review_flags
                else "MEASUREMENTS_COMPLETE_REQUIRE_MANUAL_VERIFICATION")
    else:
        status="BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE"
        review_flags.append("INCOMPLETE_Y_OR_EVIDENCE")
    return {
        "stage":"4.5","status":status,
        "region":region_name,"center_x":region["center_x"],"center_z":region["center_z"],
        "candidate_orientation_degrees":region["orientation_degrees"],
        "provided_y_count":len(yvalues),"expected_y_count":182,
        "missing_ids":[kind+":"+id for kind,id in missing][:182],
        "provenance_complete":provenance_complete,
        "observed_surface_method":method if isinstance(method,str) and method in EXPECTED_METHODS else None,
        "observed_game_build":game if provenance_complete else None,
        "grade_sample_pairs":len(grades),
        "max_local_grid_grade_degrees":round(max_angle,3) if max_angle is not None else None,
        "p95_local_grid_grade_degrees":round(p95,3) if p95 is not None else None,
        "max_minus_min_ground_y_m":round(height_range,3) if height_range is not None else None,
        "review_flags":review_flags,
        "source_not_independently_authenticated":True,
        "terrain_approval":False,
        "physical_obstacles_checked":False,
        "object_spawner_ready":False,
        "playstation_runtime_tested":False,
        "deployment_allowed":False,
        "limitations":[
            "Even complete data needs independent confirmation against a real DayZ terrain runtime or a calibrated official terrain source.",
            "20m-grid gradients miss boulders, trenches, cliffs and local microgeometry between samples.",
            "SurfaceY is raw terrain: roads, bridges and building floors may have different walkable heights.",
            "The grade threshold is an internal pre-review heuristic, not a safe-base or DayZ requirement.",
            "No Object Spawner files are emitted by this auditor."
        ]
    }

def run(input_path:Path,output_path:Path=OUT)->dict:
    data=json.loads(input_path.read_text(encoding="utf-8"))
    baseline=json.loads(GRID.read_text(encoding="utf-8"))
    report=analyze(data,baseline,data.get("region",""))
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Stage 4.5: {report['status']}; real Y values={report['provided_y_count']}/182; PS4/PS5 ready? NO.")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=ROOT/"dist/stage4_height_capture/central_surfaceY_empty.json")
    parser.add_argument("--output",type=Path,default=OUT)
    args=parser.parse_args()
    run(args.input,args.output)
