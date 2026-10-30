#!/usr/bin/env python3
"""Stage 4.4: prevent southwest-origin mistakes and unmeasured Y release."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path

from build_stage4_terrain_survey_grid import (
    ROOT, OUT, local_to_world, world_origin_from_center
)

def near(a:float,b:float)->None:
    assert abs(a-b)<1e-7,(a,b)

def test()->None:
    # Center and origin transformations must be consistent even after rotation.
    for a in (0,30,60,90,120,150):
        cx,cz=9000,7800
        wx,wz=local_to_world(120,110,cx,cz,240,220,a)
        near(wx,cx); near(wz,cz)
        ox,oz=world_origin_from_center(cx,cz,240,220,a)
        x0,z0=local_to_world(0,0,cx,cz,240,220,a)
        near(ox,x0);near(oz,z0)
        assert math.dist((ox,oz),(cx,cz))>100,"Would confuse southwest origin with center"

    data=json.loads((OUT/"terrain_survey_grid.json").read_text(encoding="utf-8"))
    assert data["stage"]=="4.4"
    assert data["status"]=="SURVEY_COORDINATES_ONLY_NOT_TERRAIN_MEASURED"
    assert data["heightmap_surface_queried"] is False
    assert data["vertical_height_source_available"] is False
    assert data["estimated_slope"] is None
    assert data["any_in_game_survey_performed"] is False
    assert data["site_ready_for_object_spawner"] is False
    assert len(data["regions"])==3

    raw=json.loads((ROOT/"dist/stage4_footprint/footprint_report.json").read_text(encoding="utf-8"))
    assert data["official_baseline_commit"]==raw["source_commit"]
    zone_def=json.loads((ROOT/"config/stage4_zone47_blueprint.json").read_text(encoding="utf-8"))
    assert zone_def["coordinate_system"]["world_x"] is None
    assert zone_def["coordinate_system"]["terrain_surveyed"] is False

    for current, old in zip(data["regions"],raw["regions"]):
        assert current["region"]==old["id"]
        assert current["status"]=="WORLD_XZ_SURVEY_COORDINATES_ONLY_NO_REAL_Y"
        assert current["real_world_site_approved"] is False
        first=old["candidates"][0]
        assert current["center_x"]==first["x"] and current["center_z"]==first["z"]
        assert current["orientation_degrees"]==first["best_rotation"]["rotation_deg"]
        ox,oz=world_origin_from_center(first["x"],first["z"],240,220,current["orientation_degrees"])
        near(current["local_southwest_origin_world_x"],round(ox,4))
        near(current["local_southwest_origin_world_z"],round(oz,4))
        samples=current["terrain_samples"]
        props=current["prototype_locations"]
        assert len(samples)==156 and len(props)==26
        assert len({s["sample_id"] for s in samples})==156
        assert len({p["id"] for p in props})==26
        assert all(s["terrain_y_measured"] is None for s in samples)
        assert all(s["evidence_reference"] is None for s in samples)
        assert all(p["terrain_y_measured"] is None for p in props)
        assert all(p["classname_verified_on_console"] is False for p in props)
        assert all(p["do_not_use_as_object_spawner_position"] is True for p in props)
        assert all(0<=p["world_x"]<=12800 and 0<=p["world_z"]<=12800 for p in props)
        with (OUT/f"{current['region']}_empty_Y_grid.csv").open(encoding="utf-8",newline="") as inp:
            reader=list(csv.DictReader(inp))
        assert len(reader)==156
        assert all(s["terrain_y_measured"]=="" and s["evidence_reference"]=="" for s in reader)
        anchors=current["nearby_official_terrain_group_anchors"]
        assert all("NOT the proposed site's height" in a["IMPORTANT"] for a in anchors)

    with zipfile.ZipFile(OUT/"beileys47-zone47-terrain-survey-worksheet-only.zip") as z:
        assert z.testzip() is None
        assert "DO_NOT_DEPLOY.txt" in z.namelist()
        assert "terrain_survey_grid.json" in z.namelist()
        assert "central_xz_survey.svg" in z.namelist()
        assert all("zone47_objects" not in n and "cfggameplay.json" not in n for n in z.namelist())
        checks=json.loads(z.read("sha256_manifest.json"))
        for name,digest in checks.items():
            assert hashlib.sha256(z.read(name)).hexdigest()==digest
        assert b"All Y heights are EMPTY" in z.read("DO_NOT_DEPLOY.txt")
    print("PASS: centered X/Z transforms, 468 blank terrain Y fields, 78 non-installable prop coordinates, SHA-256 archive.")
    print("NOT done: terrain survey, world heights, PS5 test, real-site approval.")

if __name__=="__main__":test()
