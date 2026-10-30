#!/usr/bin/env python3
"""Stage 4.2: rotated 240x220m rectangles against pinned DayZ XML anchors.

This is a screening proxy only, NOT a terrain survey or collision analysis.
NO object placement, map/mission modification, Nitrado or DayZ deployment.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from scan_stage4_sites import SOURCE_FILES, fetch_source, read_positions

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/stage4_footprint"
RULES=ROOT/"config/stage4_footprint_rules.json"
SITE_REPORT=ROOT/"dist/stage4_site_screening/site_screen_report.json"


def ensure(ok:bool,why:str)->None:
    if not ok: raise AssertionError(why)


def distance_to_rotated_rectangle(
        px:float,pz:float,cx:float,cz:float,width:float,depth:float,angle_degrees:float
) -> float:
    """0 inside rectangle; Euclidean distance to nearest outside edge."""
    theta=math.radians(angle_degrees)
    c,s=math.cos(theta),math.sin(theta)
    dx,dz=px-cx,pz-cz
    u=c*dx+s*dz
    v=-s*dx+c*dz
    return math.hypot(max(abs(u)-width/2,0),max(abs(v)-depth/2,0))


def metrics(cx:float,cz:float,angle:float,world:tuple,settings:dict)->dict:
    groups,military,spawns,events=world
    width,depth=settings["width_m"],settings["depth_m"]
    dgroup=min(distance_to_rotated_rectangle(x,z,cx,cz,width,depth,angle) for x,z,_ in groups)
    devent=min(distance_to_rotated_rectangle(x,z,cx,cz,width,depth,angle) for x,z,_ in events)
    dspawn=min(distance_to_rotated_rectangle(x,z,cx,cz,width,depth,angle) for x,z,_ in spawns)
    counts={
      "terrain_anchor_points_inside_rectangle":sum(distance_to_rotated_rectangle(x,z,cx,cz,width,depth,angle)<1e-8 for x,z,_ in groups),
      "event_anchor_points_inside_rectangle":sum(distance_to_rotated_rectangle(x,z,cx,cz,width,depth,angle)<1e-8 for x,z,_ in events),
    }
    limits={
      "terrain_group_anchor":settings["minimum_static_group_anchor_clearance_to_footprint_m"],
      "active_event_point":settings["minimum_active_event_point_clearance_to_footprint_m"],
      "fresh_spawn_point":settings["minimum_fresh_spawn_point_clearance_to_footprint_m"],
    }
    pass_proxy=(dgroup>=limits["terrain_group_anchor"] and devent>=limits["active_event_point"] and dspawn>=limits["fresh_spawn_point"])
    # This is just a heuristic ranking among those that pass. It deliberately
    # does not infer actual roads, hill shapes, trees or travel times.
    margin=(
      min((dgroup-limits["terrain_group_anchor"])/25,5)
      +min((devent-limits["active_event_point"])/100,5)
      +min((dspawn-limits["fresh_spawn_point"])/700,5)
    )
    return {
      "rotation_deg":angle,
      "status":"STATIC_ANCHOR_MARGIN_PASSED_SURVEY_NEEDED" if pass_proxy else "STATIC_ANCHOR_MARGIN_FAILED",
      "proxy_passed":pass_proxy,
      "nearest_terrain_group_anchor_from_rectangle_m":round(dgroup,1),
      "nearest_event_point_from_rectangle_m":round(devent,1),
      "nearest_stage1_fresh_spawn_from_rectangle_m":round(dspawn,1),
      "anchors_inside_rectangle":counts,
      "heuristic_margin_score":round(margin,3)
    }


def corners(cx:float,cz:float,width:float,depth:float,angle:float)->list[tuple[float,float]]:
    t=math.radians(angle);co,si=math.cos(t),math.sin(t)
    return [(cx+co*dx-si*dz,cz+si*dx+co*dz)
            for dx,dz in ((-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2))]


def render_svg(output:list[dict],settings:dict)->str:
    sx=lambda x:round(80+x*.065,1)
    sy=lambda z:round(910-z*.06,1)
    parts=[
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1030">',
      '<rect width="1120" height="1030" fill="#101b22"/>',
      '<text x="80" y="45" fill="#f3e8d3" font-family="sans-serif" font-size="27" font-weight="bold">ZONA 47 • RECTANGULAR FOOTPRINT PRE-SCREEN</text>',
      '<text x="80" y="70" fill="#b4c0c7" font-family="sans-serif" font-size="14">240×220m idealized rectangles; source anchors only, NOT a terrain or satellite map</text>',
      '<rect x="75" y="97" width="900" height="815" fill="#182930" stroke="#4d6b79" stroke-width="2"/>'
    ]
    colors={"central":"#f4d692","southern_west":"#6cbcdc","southern_east":"#be9de4"}
    for region in output:
      for idx,c in enumerate(region["candidates"],1):
        best=c["best_rotation"]
        if best is None:angle=0;pass_proxy=False
        else:angle=best["rotation_deg"];pass_proxy=best["proxy_passed"]
        pts=corners(c["x"],c["z"],settings["width_m"],settings["depth_m"],angle)
        poly=" ".join(f"{sx(x)},{sy(z)}" for x,z in pts)
        col=colors[region["id"]]
        parts.append(f'<polygon points="{poly}" stroke="{col}" stroke-width="{3 if idx==1 else 1.7}" fill="{col}" fill-opacity="0.15" stroke-dasharray="{ "none" if pass_proxy else "4 4"}"/>')
        parts.append(f'<circle cx="{sx(c["x"])}" cy="{sy(c["z"])}" r="3.5" fill="{col}"/>')
        if idx==1:parts.append(f'<text x="{sx(c["x"])+13}" y="{sy(c["z"])-9}" fill="{col}" font-family="sans-serif" font-size="14">{region["id"]} {c["x"]}/{c["z"]}</text>')
    parts.extend([
      '<text x="80" y="950" fill="#e8e2d2" font-family="sans-serif" font-size="14">Filled rectangles: bounding-box proxy only. No trees, height, streets, physics or model footprint data.</text>',
      '<text x="80" y="978" fill="#f2b978" font-family="sans-serif" font-size="15">UNVERIFIED LOCATION • DO NOT DEPLOY ON PLAYSTATION OR NITRADO</text>',
      '</svg>'
    ])
    return "\n".join(parts)+"\n"


def run(source_dir:Path|None=None)->dict:
    settings=json.loads(RULES.read_text(encoding="utf-8"))
    site=json.loads(SITE_REPORT.read_text(encoding="utf-8"))
    ensure(settings["status"]=="PROXY_FOOTPRINT_EVALUATION_NOT_TERRAIN_APPROVAL","Unsafe rules status")
    ensure(site["status"]=="PROVISIONAL_SITE_SCREENING_NOT_SITE_APPROVAL","Upstream shortlist isn't a preview")
    ensure(site["source_commit"]==settings["compatible_upstream_commit"],"Source baseline mismatch")
    ensure((settings["width_m"],settings["depth_m"])==(240,220),"Layout size mismatch")
    ensure(len(settings["rotation_angles_degrees"])>=4,"At least four orientations needed")
    ensure(all(type(x) in (int,float) and 0<=x<180 for x in settings["rotation_angles_degrees"]),"Invalid angles")
    fresh=json.loads((ROOT/"config/stage1_rules.json").read_text(encoding="utf-8"))["fresh_spawn_groups"]
    sources={name:fetch_source(name,site["source_commit"],source_dir) for name in SOURCE_FILES}
    roots={name:ET.fromstring(data) for name,data in sources.items()}
    groups,military,spawns,events,counts=read_positions(roots,fresh,site["search_rules"]["event_prefixes"])
    regions=[]
    for region in site["regions"]:
      vals=[]
      for point in region["top_candidates"][:settings["max_top_candidates_per_region"]]:
        cx,cz=point["x"],point["z"]
        values=[metrics(cx,cz,angle,(groups,military,spawns,events),settings) for angle in settings["rotation_angles_degrees"]]
        passed=sorted((x for x in values if x["proxy_passed"]),key=lambda x:(-x["heuristic_margin_score"],x["rotation_deg"]))
        best=passed[0] if passed else None
        vals.append({
            "x":cx,"z":cz,"selected_for_real_world_build":False,
            "Y_height_measured":False,"rotations_tested":values,
            "best_rotation":best,
            "recommendation":"CONSIDER_GROUND_SURVEY" if best else "REJECT_BY_STATIC_ANCHORS",
            "limitations":"Terrain slopes, vegetation, roads, true model collision volumes, object class and gameplay are still unknown"
        })
      regions.append({"id":region["id"],"candidates":vals})
    report={
      "stage":4,"status":"RECTANGLE_PROXY_SCREENING_NOT_IN_GAME_VERIFIED",
      "source_commit":site["source_commit"],
      "source_sha256":{n:hashlib.sha256(p).hexdigest() for n,p in sources.items()},
      "footprint_rules":settings,"regions":regions,
      "any_site_approved":False,
      "real_object_placement_ready":False,
      "limitations":["XML anchors are points not 3D polygons","No terrain height/slope, trees, roads, water or object collision",
                     "No true player travel/accessibility, sightlines, traffic, PS4/PS5 FPS or DayZ runtime",
                     "Successful static clearance cannot establish a playable location"]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    rp=OUT/"footprint_report.json"
    rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"footprint_rectangles.svg").write_text(render_svg(regions,settings),encoding="utf-8")
    archive=OUT/"beileys47-zone47-footprint-screen-only.zip"
    notes=b"STATIC ANCHOR RECTANGLE SCREENING ONLY. NOT A TERRAIN SURVEY. NO REAL GAME DEPLOYMENT. DO NOT UPLOAD TO NITRADO.\n"
    files={
       "DO_NOT_UPLOAD.txt":notes,
       "footprint_report.json":rp.read_bytes(),
       "footprint_rectangles.svg":(OUT/"footprint_rectangles.svg").read_bytes()
    }
    hashes={name:hashlib.sha256(payload).hexdigest() for name,payload in files.items()}
    files["sha256.json"]=(json.dumps(hashes,indent=2)+"\n").encode("utf-8")
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
      for name,payload in sorted(files.items()):z.writestr(name,payload)
    with zipfile.ZipFile(archive) as z:
      ensure(z.testzip() is None and set(z.namelist())==set(files),"Archive integrity failure")
      for name,h in hashes.items():ensure(hashlib.sha256(z.read(name)).hexdigest()==h,"Hash mismatch")
    for region in regions:
      x=region["candidates"][0]
      print(f"Proxy footprint {region['id']} center=({x['x']},{x['z']}) rotations_pass={sum(y['proxy_passed'] for y in x['rotations_tested'])}/{len(x['rotations_tested'])}")
    print("PASS: Stage 4.2 rectangle screening ZIP & report. NO Y, vegetation, road or live console survey.")
    return report

if __name__=="__main__":run()
