#!/usr/bin/env python3
"""Stage 4.4: exact REAL X/Z survey coordinates, but NO surveyed world Y values.

Safe conversion of Stage 4 local layout into the world at the *center* of a
candidate 240x220m rectangle. Makes a ground-measurement worksheet only.
A terrain-group anchor's Y is not a measurement at our proposed coordinates.
No Nitrado use, Object Spawner output, gameplay modifications or deployment.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from scan_stage4_sites import fetch_source

ROOT=Path(__file__).resolve().parents[1]
BP=ROOT/"config/stage4_zone47_blueprint.json"
MICRO=ROOT/"config/stage4_zone47_micro_layout.json"
FOOTPRINT=ROOT/"dist/stage4_footprint/footprint_report.json"
OUT=ROOT/"dist/stage4_terrain_survey"
MAX_MAP=12800

def checked(ok:bool,what:str)->None:
    if not ok:raise AssertionError(what)

def local_to_world(
    local_x:float,local_z:float,cx:float,cz:float,
    width:float,depth:float,yaw_degrees:float
)->tuple[float,float]:
    """Place the local rectangle center onto the world candidate center."""
    angle=math.radians(yaw_degrees)
    dx,dz=local_x-width/2,local_z-depth/2
    return (cx+math.cos(angle)*dx-math.sin(angle)*dz,
            cz+math.sin(angle)*dx+math.cos(angle)*dz)

def world_origin_from_center(cx:float,cz:float,width:float,depth:float,yaw:float)->tuple[float,float]:
    return local_to_world(0,0,cx,cz,width,depth,yaw)

def nearby_anchors(xml_bytes:bytes,cx:float,cz:float)->list[dict]:
    if b"<!DOCTYPE" in xml_bytes.upper() or b"<!ENTITY" in xml_bytes.upper():
        raise ValueError("Unsafe XML entity")
    root=ET.fromstring(xml_bytes)
    checked(root.tag=="map","Pinned CE map data format changed")
    candidates=[]
    for el in root.findall("group"):
        raw=el.get("pos","").split()
        checked(len(raw)==3,"Broken map group coordinate")
        x,y,z=map(float,raw)
        d=math.hypot(cx-x,cz-z)
        if d<=1500:
            candidates.append({
              "name":el.get("name"),"source_anchor_x":round(x,2),
              "source_anchor_y":round(y,2),"source_anchor_z":round(z,2),
              "horizontal_distance_to_candidate_center_m":round(d,1),
              "IMPORTANT":"This Y is the source map group's anchor height at its own X/Z, NOT the proposed site's height."
            })
    return sorted(candidates,key=lambda p:(p["horizontal_distance_to_candidate_center_m"],p["name"]))[:12]

def make_csv(rows:list[dict],path:Path)->bytes:
    fields=["sample_id","world_x","world_z","terrain_y_measured","surface_type_observed","slope_notes","evidence_reference"]
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k:row.get(k) for k in fields})
    return path.read_bytes()

def schematic(regions:list[dict])->str:
    w=regions[0]
    cx,cz=w["center_x"],w["center_z"]
    sx=lambda x:round(460+(x-cx)*1.55,1)
    sy=lambda z:round(490-(z-cz)*1.55,1)
    angle=w["orientation_degrees"]
    bp=json.loads(BP.read_text(encoding="utf-8"))
    micro=json.loads(MICRO.read_text(encoding="utf-8"))
    points=lambda lx,lz:local_to_world(lx,lz,cx,cz,bp["coordinate_system"]["width"],bp["coordinate_system"]["height"],angle)
    corners=[points(x,z) for x,z in ((0,0),(240,0),(240,220),(0,220))]
    coords=" ".join(f"{sx(x)},{sy(z)}" for x,z in corners)
    parts=[
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 930">',
      '<rect width="1000" height="930" fill="#111c24"/>',
      '<text x="65" y="46" fill="#eee6d8" font-family="sans-serif" font-size="29" font-weight="bold">BEILEYS47 • ZONA 47 / SITE SURVEY GRID</text>',
      '<text x="65" y="74" fill="#bfcdd1" font-family="sans-serif" font-size="14">COORDINATE TRANSFORM ONLY • NO REAL TERRAIN HEIGHTS • NOT DEPLOYABLE</text>',
      '<rect x="85" y="112" width="750" height="690" fill="#182a32" stroke="#647b86" stroke-width="2"/>',
      f'<polygon points="{coords}" fill="#234239" fill-opacity=".5" stroke="#e7c385" stroke-width="4"/>'
    ]
    for row in w["terrain_samples"]:
        parts.append(f'<circle cx="{sx(row["world_x"])}" cy="{sy(row["world_z"])}" r="2.1" fill="#7c948d" opacity=".70"/>')
    for p in w["prototype_locations"]:
        parts.append(f'<circle cx="{sx(p["world_x"])}" cy="{sy(p["world_z"])}" r="5.2" fill="#e7ad7a" stroke="#f9e9ba" stroke-width=".8"/>')
    parts+= [
      f'<circle cx="{sx(cx)}" cy="{sy(cz)}" r="9" fill="#f2db7e" stroke="#fff" stroke-width="2"/>',
      f'<text x="{sx(cx)+14}" y="{sy(cz)-12}" fill="#fff1cb" font-family="sans-serif" font-size="15">Center X {cx} / Z {cz}</text>',
      f'<text x="65" y="843" fill="#e8e6d6" font-family="sans-serif" font-size="15">26 symbolic props • {len(w["terrain_samples"])} empty Y-height samples • rotation {angle}° from static source screening</text>',
      '<text x="65" y="875" fill="#eabf8b" font-family="sans-serif" font-size="15">HEIGHTMAP NOT PRESENT. NO CONFIRMED TREES, ROADS, WATER, COLLISIONS OR PS5 FPS.</text>',
      '</svg>'
    ]
    return "\n".join(parts)+"\n"

def build()->dict:
    bp=json.loads(BP.read_text(encoding="utf-8"))
    micro=json.loads(MICRO.read_text(encoding="utf-8"))
    screen=json.loads(FOOTPRINT.read_text(encoding="utf-8"))
    checked(screen["status"]=="RECTANGLE_PROXY_SCREENING_NOT_IN_GAME_VERIFIED","Unapproved footprint input")
    checked(screen["any_site_approved"] is False,"Ground site already approved unexpectedly")
    checked(bp["coordinate_system"]["unit"]=="local_metres_xz","Local layout changed")
    width=bp["coordinate_system"]["width"]
    depth=bp["coordinate_system"]["height"]
    checked((width,depth)==(240,220),"Unexpected layout size")
    checked(micro["status"]=="SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON","Wrong source layout")
    checked(len(micro["asset_placements"])==26,"Prototype count mismatch")
    source=fetch_source("mapgrouppos.xml",screen["source_commit"],None)
    regions=[]
    for region in screen["regions"]:
        first=region["candidates"][0]
        best=first["best_rotation"]
        checked(best is not None and best["proxy_passed"] is True, f"No safe proxy rotation in {region['id']}")
        cx,cz=first["x"],first["z"]
        angle=best["rotation_deg"]
        ox,oz=world_origin_from_center(cx,cz,width,depth,angle)
        samples=[]
        for j,z in enumerate(range(0,depth+1,20)):
            for i,x in enumerate(range(0,width+1,20)):
                wx,wz=local_to_world(x,z,cx,cz,width,depth,angle)
                checked(0<=wx<=MAX_MAP and 0<=wz<=MAX_MAP,"Generated outside 12800m Livonia bounds")
                samples.append({
                   "sample_id":f"GRID-{i:02d}-{j:02d}",
                   "world_x":round(wx,3),"world_z":round(wz,3),
                   "terrain_y_measured":None,"surface_type_observed":None,
                   "slope_notes":None,"evidence_reference":None
                })
        prototype=[]
        for prop in micro["asset_placements"]:
            wx,wz=local_to_world(prop["local_x"],prop["local_z"],cx,cz,width,depth,angle)
            checked(0<=wx<=MAX_MAP and 0<=wz<=MAX_MAP,"Invalid world prop coordinate")
            prototype.append({
                "id":prop["id"],"zone":prop["zone"],"role":prop["visual_role"],
                "world_x":round(wx,3),"world_z":round(wz,3),
                "terrain_y_measured":None,"classname_verified_on_console":False,
                "collision_free_verified":False,"gameplay_access_verified":False,
                "do_not_use_as_object_spawner_position":True
            })
        checked(len(samples)==156 and len(prototype)==26,"Wrong sample counts")
        # The local layout is centered on (120,110), NOT at (0,0).
        mid=local_to_world(width/2,depth/2,cx,cz,width,depth,angle)
        checked(math.dist(mid,(cx,cz))<1e-9,"World center calculation mismatch")
        regions.append({
            "region":region["id"],
            "status":"WORLD_XZ_SURVEY_COORDINATES_ONLY_NO_REAL_Y",
            "center_x":cx,"center_z":cz,
            "orientation_degrees":angle,
            "local_southwest_origin_world_x":round(ox,4),
            "local_southwest_origin_world_z":round(oz,4),
            "center_definition":"center of the 240×220 local rectangle (local x=120,z=110)",
            "rotation_is_not_terrain_verified":True,
            "terrain_samples":samples,
            "prototype_locations":prototype,
            "nearby_official_terrain_group_anchors":nearby_anchors(source,cx,cz),
            "real_world_site_approved":False
        })
    checked(len(regions)==3,"Expected 3 regions")
    report={
        "stage":"4.4",
        "status":"SURVEY_COORDINATES_ONLY_NOT_TERRAIN_MEASURED",
        "official_baseline_commit":screen["source_commit"],
        "official_map_groups_sha256":hashlib.sha256(source).hexdigest(),
        "preferred_region_for_first_survey":"central",
        "important_convention":"The site candidate X/Z is the WORLD CENTER. It is NOT the old exporter's local-southwest-origin X/Z.",
        "vertical_height_source_available":False,
        "heightmap_surface_queried":False,
        "site_ready_for_object_spawner":False,
        "estimated_slope":None,
        "any_in_game_survey_performed":False,
        "regions":regions,
        "limitations":[
           "World X/Z are a geometric transformation from static candidates; NO real ground Y or slopes.",
           "Heights of official nearby terrain-group anchors describe THOSE objects at THEIR positions; no interpolation or substitution allowed.",
           "No tree/vegetation, rivers, roads, water, collision, line-of-sight or player routes surveyed.",
           "A static rotation score is not a valid building orientation for a terrain parcel.",
           "The custom placement survey remains incomplete and the exporter must fail closed."
        ]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    rp=OUT/"terrain_survey_grid.json"
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files={"terrain_survey_grid.json":rp.read_bytes()}
    for region in regions:
        name=f"{region['region']}_empty_Y_grid.csv"
        files[name]=make_csv(region["terrain_samples"],OUT/name)
    svg=schematic(regions)
    (OUT/"central_xz_survey.svg").write_text(svg,encoding="utf-8")
    files["central_xz_survey.svg"]=svg.encode()
    warning=(
        "BEILEYS47 ZONA 47 / STAGE 4.4. X/Z points, NOT surveyed terrain.\n"
        "All Y heights are EMPTY. No trusted terrain heightmap or verified in-game measurements.\n"
        "Do not upload to Nitrado; no installed object spawner data.\n"
    ).encode()
    files["DO_NOT_DEPLOY.txt"]=warning
    manifest={n:hashlib.sha256(data).hexdigest() for n,data in sorted(files.items())}
    files["sha256_manifest.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    package=OUT/"beileys47-zone47-terrain-survey-worksheet-only.zip"
    with zipfile.ZipFile(package,"w",zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(name,data)
    with zipfile.ZipFile(package) as z:
        checked(z.testzip() is None and set(z.namelist())==set(files),"Bad survey archive")
        for name,digest in manifest.items():
            checked(hashlib.sha256(z.read(name)).hexdigest()==digest,"Archive digest mismatch")
        checked("zone47_objects.json" not in z.namelist(),"Installable objects forbidden")
    print("PASS: centered X/Z survey worksheet: 3 provisional sites × 156 EMPTY Y samples, 26 proposed XY-map anchors each.")
    print("NOT surveyed: real Y, slope, trees, roads, water, runtime assets, collisions, PS4/PS5 FPS, Nitrado.")
    return report

if __name__=="__main__":build()
