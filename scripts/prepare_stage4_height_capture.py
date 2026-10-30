#!/usr/bin/env python3
"""Stage 4.5: produce structured EMPTY terrain-height capture sheets.

Each 4.4 provisional site has 156 GRID and 26 PROP locations. These are X/Z
coordinates only. Measured terrain Y must come from a separately documented
DayZ engine SurfaceY acquisition or a provenance-checked equivalent.
No DayZ API execution, no Nitrado access, no generated object-spawner.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from zip_deterministic import add_bytes

ROOT=Path(__file__).resolve().parents[1]
GRID=ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json"
OUT=ROOT/"dist/stage4_height_capture"

def template(region:dict,baseline:str)->dict:
    points=[]
    for item in region["terrain_samples"]:
        points.append({
            "id":item["sample_id"],"kind":"GRID",
            "x":item["world_x"],"z":item["world_z"],
            "ground_y":None,"surface_material":None
        })
    for item in region["prototype_locations"]:
        points.append({
            "id":item["id"],"kind":"PROP",
            "x":item["world_x"],"z":item["world_z"],
            "ground_y":None,"surface_material":None
        })
    assert len(points)==182 and len({(x["kind"],x["id"]) for x in points})==182
    return {
        "schema_version":"1.0",
        "stage":"4.5",
        "status":"UNMEASURED_CAPTURE_TEMPLATE",
        "map":"Livonia",
        "official_mission_baseline":baseline,
        "region":region["region"],
        "candidate_center_x":region["center_x"],
        "candidate_center_z":region["center_z"],
        "candidate_rotation_degrees":region["orientation_degrees"],
        "measurement":{
            "method":None,
            "dayz_game_build":None,
            "captured_utc":None,
            "evidence_reference":None,
            "remarks":None
        },
        "points":points,
        "warning":"All Y values are null. This is a capture request only; no actual terrain elevations, buildings, collisions or PlayStation tests."
    }

def build()->list[dict]:
    existing=json.loads(GRID.read_text(encoding="utf-8"))
    assert existing["stage"]=="4.4" and existing["status"]=="SURVEY_COORDINATES_ONLY_NOT_TERRAIN_MEASURED"
    assert existing["site_ready_for_object_spawner"] is False
    OUT.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for region in existing["regions"]:
        data=template(region,existing["official_baseline_commit"])
        path=OUT/f"{region['region']}_surfaceY_empty.json"
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        outputs.append(data)
    filename=OUT/"beileys47-zone47-height-capture-templates-only.zip"
    note=(
      "BEILEYS47 STAGE 4.5 - UNMEASURED Y templates.\n"
      "DO NOT DEPLOY. No actual Livonia terrain samples were collected.\n"
      "Run the independent terrain-height audit only on an actual measured dataset\n"
      "with source, build/date and evidence. The audit never creates DayZ game files.\n"
    ).encode()
    files={"NO_REAL_HEIGHTS_DO_NOT_DEPLOY.txt":note}
    for path in OUT.glob("*_surfaceY_empty.json"):files[path.name]=path.read_bytes()
    manifest={k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    with zipfile.ZipFile(filename,"w",zipfile.ZIP_DEFLATED) as z:
        for k,v in sorted(files.items()):add_bytes(z,k,v)
    with zipfile.ZipFile(filename) as z:
        assert z.testzip() is None
        for k,h in manifest.items():assert hashlib.sha256(z.read(k)).hexdigest()==h
        assert all("zone47_objects.json" not in n for n in z.namelist())
    print("PASS: 3 capture templates × 182 ground-Y entries, all deliberately null, SHA-256 ZIP.")
    print("NOT DONE: in-game SurfaceY acquisition, physical terrain/road survey, PS4/PS5 tests.")
    return outputs

if __name__=="__main__":build()
