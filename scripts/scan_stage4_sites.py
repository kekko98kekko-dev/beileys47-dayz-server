#!/usr/bin/env python3
"""Screen Livonia coordinates using official PINNED mission files.

This is a spatial pre-screen, NOT terrain-slope, object collision, road,
vegetation, DayZ pathfinding, or PlayStation/Nitrado testing. It cannot
select/approve a deployable ZONA 47 site and never edits a game mission.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
RULES=ROOT/"config/stage4_site_screening_rules.json"
OUT=ROOT/"dist/stage4_site_screening"
SOURCE_FILES=("mapgrouppos.xml","cfgplayerspawnpoints.xml","cfgeventspawns.xml")
BASE="https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/"
ALLOWED_MAX_BYTES={"mapgrouppos.xml":1_200_000,"cfgplayerspawnpoints.xml":100_000,"cfgeventspawns.xml":200_000}


def require(condition:bool, reason:str)->None:
    if not condition:raise AssertionError(reason)


def fetch_source(path:str,commit:str,source_dir:Path|None)->bytes:
    require(path in SOURCE_FILES,"Unapproved upstream file")
    if source_dir is not None:
        raw=(source_dir/path).read_bytes()
    else:
        url=BASE+commit+"/dayzOffline.enoch/"+path
        req=urllib.request.Request(url,headers={"User-Agent":"BEILEYS47-ZONA47-SiteScreen/1.0"})
        with urllib.request.urlopen(req,timeout=45) as resp:
            raw=resp.read(ALLOWED_MAX_BYTES[path]+1)
    require(len(raw)<=ALLOWED_MAX_BYTES[path] and len(raw)>100,"Unexpected source size")
    up=raw.upper()
    require(b"<!ENTITY" not in up and b"<!DOCTYPE" not in up,"DTD/entities forbidden")
    return raw


def read_positions(roots:dict[str,ET.Element],fresh_groups:list[str],prefixes:list[str])->tuple[list[tuple],list[tuple],list[tuple],dict]:
    groups=[]
    root=roots["mapgrouppos.xml"]
    require(root.tag=="map","Map group root mismatch")
    for el in root.findall("group"):
        nums=el.get("pos","").split()
        require(len(nums)==3,"Malformed map group")
        x,y,z=map(float,nums)
        require(all(math.isfinite(v) for v in (x,y,z)),"Nonfinite map coord")
        groups.append((x,z,el.get("name","")))
    require(len(groups)>3000,"Official map group list unexpectedly small")
    military=[(x,z,name) for x,z,name in groups if name.startswith("Land_Mil_")]
    require(len(military)>20,"Military group sample too small")

    root=roots["cfgplayerspawnpoints.xml"]
    require(root.tag=="playerspawnpoints","Spawn root mismatch")
    parent=root.find("./fresh/generator_posbubbles")
    require(parent is not None,"Fresh spawn bubbles missing")
    spawn=[]
    available={el.get("name"):el for el in parent.findall("group")}
    require(set(fresh_groups)<=set(available),"Stage1 fresh-spawn group names changed")
    for name in fresh_groups:
        for pos in available[name].findall("pos"):
            spawn.append((float(pos.get("x")),float(pos.get("z")),name))
    require(len(spawn)>=8,"Too few Stage 1 spawn positions")

    root=roots["cfgeventspawns.xml"]
    require(root.tag=="eventposdef","Event spawn root mismatch")
    event=[]
    counts=Counter()
    for item in root.findall("event"):
        name=item.get("name","")
        if not any(name.startswith(p) for p in prefixes):
            continue
        for pos in item.findall("pos"):
            x=float(pos.get("x"));z=float(pos.get("z"))
            require(math.isfinite(x) and math.isfinite(z),"Invalid event coordinate")
            event.append((x,z,name))
            counts[name]+=1
    require(len(event)>=100,"Too few official event points")
    return groups,military,spawn,event,{"event_types":dict(sorted(counts.items()))}


def dist_nearest(x:int,z:int,points:list[tuple])->float:
    return math.sqrt(min((x-p[0])**2+(z-p[1])**2 for p in points))


def candidate(x:int,z:int,world:tuple,rules:dict)->dict|None:
    groups,military,spawn,event=world
    nearest_spawn=dist_nearest(x,z,spawn)
    if nearest_spawn<rules["minimum_nearest_fresh_spawn_metres"]:return None
    nearest_event=dist_nearest(x,z,event)
    if nearest_event<rules["minimum_nearest_active_event_position_metres"]:return None
    nearest_terrain=dist_nearest(x,z,groups)
    if nearest_terrain<rules["minimum_nearest_terrain_group_metres"]:return None
    nearest_military=dist_nearest(x,z,military)
    if not (rules["minimum_nearest_military_group_metres"]<=nearest_military<=rules["maximum_nearest_military_group_metres"]):
        return None
    near_terrain_230=sum((x-gx)**2+(z-gz)**2<=230**2 for gx,gz,_ in groups)
    if near_terrain_230>rules["max_terrain_groups_within_230m"]:return None
    near_terrain_500=sum((x-gx)**2+(z-gz)**2<=500**2 for gx,gz,_ in groups)
    near_military_1800=sum((x-mx)**2+(z-mz)**2<=1800**2 for mx,mz,_ in military)
    if near_military_1800<rules["minimum_military_groups_within_1800m"]:return None
    # Heuristic rewards medium travel from north, existing military interest,
    # lower nearby static anchors and not being directly on an event position.
    score=(110-abs(nearest_military-850)/30
           -abs(nearest_spawn-3500)/900
           -near_terrain_500*1.2
           -max(0,650-nearest_event)/25)
    return {
      "x":x,"z":z,"screen_score":round(score,2),
      "nearest_selected_fresh_spawn_m":round(nearest_spawn),
      "nearest_included_event_point_m":round(nearest_event),
      "nearest_terrain_group_anchor_m":round(nearest_terrain),
      "nearest_military_terrain_anchor_m":round(nearest_military),
      "terrain_anchors_within_500m":near_terrain_500,
      "military_terrain_anchors_within_1800m":near_military_1800,
      "height_y":None,"slope_degrees":None,"road_access_verified":False,
      "vegetation_or_collision_checked":False,"object_spawner_approved":False,
      "status":"CANDIDATE_COORDINATE_ONLY_REQUIRES_IN_GAME_SURVEY"
    }


def shortlist(rules:dict,world:tuple)->list[dict]:
    selections=[]
    for window in rules["windows"]:
        x0,x1,z0,z1=window["bounds_xz"]
        step=rules["stride_metres"]
        require(all(isinstance(v,int) for v in (x0,x1,z0,z1,step)) and 0<x0<x1<=20000 and 0<z0<z1<=20000 and 50<=step<=500,"Invalid search grid")
        accepted=[]
        for x in range(x0,x1+1,step):
            for z in range(z0,z1+1,step):
                item=candidate(x,z,world,rules)
                if item is not None:accepted.append(item)
        accepted.sort(key=lambda c:(-c["screen_score"],c["x"],c["z"]))
        chosen=[]
        for item in accepted:
            if all(math.hypot(item["x"]-other["x"],item["z"]-other["z"])>=rules["minimum_separation_between_selected_centers_metres"] for other in chosen):
                chosen.append(item)
            if len(chosen)==rules["per_region_top_n"]:break
        require(len(chosen)==rules["per_region_top_n"],f"Too few candidates in region: {window['id']}")
        selections.append({
            "id":window["id"],"name":window["name"],"design_priority":window["design_priority"],
            "screened_grid_centers":(1+(x1-x0)//step)*(1+(z1-z0)//step),
            "passes_static_filters":len(accepted),
            "top_candidates":chosen,
            "decision":"SURVEY_REQUIRED_NO_SITE_APPROVED"
        })
    return selections


def render_svg(results:list[dict],spawn:list[tuple],military:list[tuple],events:list[tuple])->str:
    # Coordinate scatter plot: only selected risk proxies, not a terrain map.
    sx=lambda x:round(82+x*0.065,1)
    sz=lambda z:round(895-z*0.061,1)
    p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1030">',
       '<rect width="1100" height="1030" fill="#121a20"/>',
       '<text x="82" y="48" font-family="sans-serif" font-size="28" font-weight="bold" fill="#eae5dc">ZONA 47 — LIVONIA SITE SCREEN (STAGE 4)</text>',
       '<text x="82" y="75" font-family="sans-serif" font-size="15" fill="#aeb8c0">PINNED MISSION COORDINATES • NOT TERRAIN SURVEY • NO HEIGHT OR ROADS</text>',
       '<rect x="80" y="95" width="850" height="800" rx="14" stroke="#536977" stroke-width="2" fill="#1c2930"/>']
    for k in range(0,14001,2000):
        x=sx(k)
        z=sz(k)
        p.append(f'<path d="M{x} 95V895 M80 {z}H930" stroke="#334851" stroke-width="1"/>')
    # Only visual indication of named event spawn points & military terrain group anchors.
    for x,z,_ in events:p.append(f'<circle cx="{sx(x)}" cy="{sz(z)}" r="2.5" fill="#ba6b5c" opacity="0.55"/>')
    for x,z,_ in military:p.append(f'<circle cx="{sx(x)}" cy="{sz(z)}" r="2.5" fill="#6bb1ac" opacity="0.65"/>')
    for x,z,_ in spawn:p.append(f'<circle cx="{sx(x)}" cy="{sz(z)}" r="5" stroke="#fff1bd" stroke-width="1.2" fill="#e0bd70"/>')
    palettes={"central":"#f4e29d","southern_west":"#6ec8ef","southern_east":"#b1a4eb"}
    for region in results:
        for idx,item in enumerate(region["top_candidates"],1):
            x,z=sx(item["x"]),sz(item["z"])
            clr=palettes[region["id"]]
            p.append(f'<circle cx="{x}" cy="{z}" r="{11 if idx==1 else 7}" fill="{clr}" stroke="#f6faf8" stroke-width="1.5"/>')
            if idx==1:
                label=f'{escape(region["id"])} ({item["x"]}, {item["z"]})'
                p.append(f'<text x="{x+14}" y="{z-12}" font-family="sans-serif" font-size="13" fill="{clr}">{label}</text>')
    p.extend([
     '<text x="82" y="939" fill="#e0bd70" font-family="sans-serif" font-size="13">● selected Stage 2 fresh spawn points</text>',
     '<text x="82" y="962" fill="#ba6b5c" font-family="sans-serif" font-size="13">● included dynamic event points</text>',
     '<text x="480" y="939" fill="#6bb1ac" font-family="sans-serif" font-size="13">● official military terrain group anchors</text>',
     '<text x="480" y="962" fill="#e4e6e5" font-family="sans-serif" font-size="13">Large outlined circles: candidates to physically inspect</text>',
     '<text x="82" y="1002" fill="#f4bb80" font-family="sans-serif" font-size="15">WARNING: NO TOPOGRAPHY, VEGETATION, ROAD OR COLLISION DATA. DO NOT DEPLOY.</text>',
     '</svg>'])
    return "\n".join(p)+"\n"


def run(source_dir:Path|None=None)->dict:
    rules=json.loads(RULES.read_text(encoding="utf-8"))
    fresh_rules=json.loads((ROOT/"config/stage1_rules.json").read_text(encoding="utf-8"))
    require(rules["status"]=="SITE_SCREENING_ONLY_NO_TERRAIN_SURVEY" and rules["stage"]==4,"Unsafe screening status")
    require(len(rules["windows"])==3 and len({x["id"] for x in rules["windows"]})==3,"Three unique regions required")
    commit=rules["upstream_commit"]
    require(commit=="f220b2918b1d79a5055b1ee9be70c0ec1516e876","Baseline SHA changed without review")
    raw={name:fetch_source(name,commit,source_dir) for name in SOURCE_FILES}
    roots={name:ET.fromstring(data) for name,data in raw.items()}
    groups,military,spawn,event,counts=read_positions(roots,fresh_rules["fresh_spawn_groups"],rules["event_prefixes"])
    regions=shortlist(rules,(groups,military,spawn,event))
    report={
      "stage":4,
      "status":"PROVISIONAL_SITE_SCREENING_NOT_SITE_APPROVAL",
      "source_commit":commit,
      "source_sha256":{name:hashlib.sha256(data).hexdigest() for name,data in raw.items()},
      "evidence_counts":{"terrain_group_anchors":len(groups),"military_terrain_group_anchors":len(military),
                         "selected_fresh_spawn_points":len(spawn),"included_event_positions":len(event),**counts},
      "search_rules":rules,
      "regions":regions,
      "recommended_first_survey_region":"central",
      "reason":"Prioritize reasonable potential access from concentrated spawn groups on an initial 10-slot server; not proof of traffic, roads or fun.",
      "critical_omissions":["No terrain heights/slope","No trees or vegetation","No road geometry",
                           "No static object footprints or interiors","No line-of-sight evidence",
                           "No real gameplay/PvP measurements","No PS4/PS5 or Nitrado tests"],
      "ready_to_export_object_spawner":False,
      "ready_for_live_deployment":False
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"site_screen_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"site_screen_scatter.svg").write_text(render_svg(regions,spawn,military,event),encoding="utf-8")
    warning="BEILEYS47 ZONA 47 SITE SCREEN ONLY. Coordinates are candidates from official static XML positions, NOT terrain surveyed or approved. NO Y elevations, road geometry, vegetation, gameplay or console tests. Never upload this archive to Nitrado.\n"
    sources={
      "DO_NOT_DEPLOY.txt":warning.encode(),
      "site_screen_report.json":(OUT/"site_screen_report.json").read_bytes(),
      "site_screen_scatter.svg":(OUT/"site_screen_scatter.svg").read_bytes()
    }
    sums={name:hashlib.sha256(payload).hexdigest() for name,payload in sources.items()}
    sources["sha256.json"]=(json.dumps(sums,indent=2)+"\n").encode()
    archive=OUT/"beileys47-zone47-site-screen-only.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(sources.items()):z.writestr(name,data)
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None and set(z.namelist())==set(sources),"Bad screening archive")
        for name,h in sums.items():require(hashlib.sha256(z.read(name)).hexdigest()==h,"Archive hash failure")
    print("PASS: screened 3 Livonia regions with pinned map, Stage 2 spawn and event data.")
    for r in regions:print(r["id"],r["top_candidates"][0]["x"],r["top_candidates"][0]["z"],"passes",r["passes_static_filters"])
    print("NO terrain validation, PS5 testing, asset spawning, or Nitrado deployment.")
    return report

if __name__=="__main__":
    run()
