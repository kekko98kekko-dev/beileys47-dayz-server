#!/usr/bin/env python3
"""Stage 4.8: non-deployable PS4/PS5 field reconnaissance waypoint kit.

Convert conceptual local route nodes and links into provisional world X/Z
using the Stage 4.4 centered transform, without EVER inventing terrain Y.
Important: 'north/west/east' legacy IDs are NAMES, not real world compass.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path

from build_stage4_terrain_survey_grid import local_to_world

ROOT=Path(__file__).resolve().parents[1]
BP=ROOT/"config/stage4_zone47_blueprint.json"
GRID=ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json"
GRAPH=ROOT/"dist/stage4_7_route_balance/pvp_route_stress_report.json"
PILOT=ROOT/"dist/stage4_6_preflight/zone47_micro_pilot_plan.json"
OUT=ROOT/"dist/stage4_8_field_recon"

def require(ok:bool,what:str)->None:
    if not ok:raise AssertionError(what)

def bearing(x:float,z:float,cx:float,cz:float)->float:
    """Compass degrees from world +Z = North, +X = East."""
    return (math.degrees(math.atan2(x-cx,z-cz))+360)%360

def cardinal(degrees:float)->str:
    dirs=("N","NE","E","SE","S","SW","W","NW")
    return dirs[int((degrees+22.5)%360//45)]

def entry_checklist(name:str)->dict:
    return {
      "route_id":name,
      "actual_ground_walk_attempted":False,
      "actual_ground_walkable":None,
      "water_or_bog_barrier_seen":None,
      "terrain_grade_inspected":None,
      "road_track_crossing_verified":None,
      "trees_rocks_and_vanilla_collision_checked":None,
      "visual_cover_and_pvp_sightlines_checked":None,
      "player_stuck_or_trapped":None,
      "test_platform":None,
      "current_game_build":None,
      "photo_or_video_evidence":None,
      "notes":None,
      "evaluation":"UNTESTED_NO_REAL_TERRAIN_EVIDENCE"
    }

def build()->dict:
    bp=json.loads(BP.read_text(encoding="utf-8"))
    grid=json.loads(GRID.read_text(encoding="utf-8"))
    graph=json.loads(GRAPH.read_text(encoding="utf-8"))
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    require(bp["status"]=="DESIGN_ONLY_NOT_INSTALLABLE","Unsafe blueprint")
    require(graph["stage"]=="4.7" and graph["deployment_allowed"] is False,"Graph gate not passed")
    require(len(graph["two_sector_lockout_failures"])==0 and graph["route_edges"]==16,
            "Concept graph regression")
    require(grid["status"]=="SURVEY_COORDINATES_ONLY_NOT_TERRAIN_MEASURED","Site survey state changed")
    region=next(x for x in grid["regions"] if x["region"]=="central")
    cx,cz=region["center_x"],region["center_z"]
    yaw=region["orientation_degrees"]
    require((cx,cz,yaw)==(9000,7800,120),"Unreviewed site location")
    require((pilot["center_x"],pilot["center_z"],pilot["orientation_degrees"])==(cx,cz,yaw),
            "Pilot and field routes disagree")
    width,depth=bp["coordinate_system"]["width"],bp["coordinate_system"]["height"]
    require((width,depth)==(240,220),"Wrong blueprint size")
    items=[(x["id"],x["x"],x["z"],"ENTRANCE",x["name"])
           for x in bp["entrances"]]+[
           (x["id"],x["x"],x["z"],"SECTOR",x["name"]) for x in bp["zones"]]
    waypoints=[]
    byid={}
    for name,lx,lz,kind,label in items:
        wx,wz=local_to_world(lx,lz,cx,cz,width,depth,yaw)
        require(0<=wx<=12800 and 0<=wz<=12800,"Out of Livonia map")
        az=bearing(wx,wz,cx,cz)
        p={
          "waypoint_id":name,"schematic_label":label,
          "kind":kind,"local_x":lx,"local_z":lz,
          "provisional_world_x":round(wx,3),"provisional_world_z":round(wz,3),
          "terrain_y":None,
          "bearing_from_site_center_deg":round(az,1),
          "compass_direction_from_site_center":cardinal(az),
          "actual_pathfinding_verified":False,
          "actual_collisions_verified":False,
          "world_coordinate_status":"MATHEMATICAL_TRANSFORM_NOT_SURVEYED"
        }
        byid[name]=p;waypoints.append(p)
    require(len(waypoints)==11,"Wrong waypoint count")
    segments=[]
    for n,(start,end) in enumerate(bp["links"],1):
        a,b=byid[start],byid[end]
        distance=math.dist((a["provisional_world_x"],a["provisional_world_z"]),
                           (b["provisional_world_x"],b["provisional_world_z"]))
        segments.append({
          "segment_id":f"LINK-{n:02d}",
          "start_waypoint":start,"end_waypoint":end,
          "start_x":a["provisional_world_x"],"start_z":a["provisional_world_z"],
          "end_x":b["provisional_world_x"],"end_z":b["provisional_world_z"],
          "schematic_straight_line_m":round(distance,2),
          "ground_walkable":None,
          "water_rock_tree_barriers":None,
          "line_of_sight_verified":None,
          "real_ground_y_available":False,
          "requires_real_in_game_inspection":True
        })
    require(len(segments)==16,"Wrong segment count")
    routes=[]
    for entry in graph["entrance_paths"]:
        for i,variant in enumerate(entry["independent_routes"],1):
            labels=[entry["entry"]]+variant["zones"]
            # A route starts at the entrance then follows its one designated sector.
            # These paths are conceptual graph links, not walkable tracks.
            coords=[byid[name] for name in labels]
            routes.append({
              "test_id":f"{entry['entry'].upper()}-{i}",
              "waypoint_ids":labels,
              "provisional_world_xz":[[p["provisional_world_x"],p["provisional_world_z"]] for p in coords],
              "terrain_heights_known":False,
              "route_confirmation":entry_checklist(f"{entry['entry'].upper()}-{i}")
            })
    require(len(routes)==6,"Expected 2 alternative paper routes per entrance")
    actual_compass={p["waypoint_id"]:p["compass_direction_from_site_center"]
                    for p in waypoints if p["kind"]=="ENTRANCE"}
    report={
      "stage":"4.8","status":"FIELD_RECON_COORDINATES_READY_NOT_PLAYABLE_OR_VERIFIED",
      "map":"Livonia","source_baseline":grid["official_baseline_commit"],
      "candidate_world_center":[cx,cz],
      "candidate_yaw_degrees":yaw,
      "selected_location_not_approved":True,
      "real_terrain_y_samples":0,
      "all_waypoints_Y_null":True,
      "console_gameplay_tests_completed":0,
      "deployment_allowed":False,
      "legacy_entrance_ids_not_true_compass_directions":True,
      "actual_compass_for_entrances_from_provisional_coordinate_transform":actual_compass,
      "waypoints":waypoints,
      "route_segments":segments,
      "two_independent_routes_per_entrance_to_inspect":routes,
      "high_priority_survey_links":[
        {"from":"service","to":"secret",
         "reason":"New east bypass; ensures no two-sector camping lockout in paper graph; unknown on terrain"}
      ],
      "survey_procedure":[
        "Confirm target world and exact DayZ build on in-game map before going to the proposed site",
        "Visit waypoint coordinates; verify whether each is on walkable ground or water/inside a vanilla building",
        "Walk every segment in both directions, check slopes, trees, rocks, fences and roads",
        "Compare checkpoint and ridge sightlines, potential one-way peeking and forced chokepoints",
        "Record all Y values via valid terrain measurement source and visual evidence",
        "Only after real survey review and authorization, test 3–5 actual objects on a private console server"
      ],
      "non_claims":[
        "Legacy labels north/west/east are narrative waypoint IDs, not world compass bearings after rotation.",
        "Schematic straight-line links do not prove actual trails or safe passage.",
        "The newly proposed service-secret connection has NOT been surveyed and might be impossible.",
        "The source geometry transformation does not certify an equivalent yaw convention in the DayZ object engine.",
        "No user, moderator or server owner has confirmed any in-game location, screenshot, game object or performance."
      ]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    rp=OUT/"central_field_recon.json"
    rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    points=OUT/"central_waypoints.csv"
    with points.open("w",encoding="utf-8",newline="") as stream:
        cols=["waypoint_id","kind","schematic_label","provisional_world_x","provisional_world_z",
              "terrain_y","bearing_from_site_center_deg","compass_direction_from_site_center"]
        writer=csv.DictWriter(stream,fieldnames=cols,extrasaction="ignore")
        writer.writeheader();writer.writerows(waypoints)
    links=OUT/"central_route_links.csv"
    with links.open("w",encoding="utf-8",newline="") as stream:
        cols=["segment_id","start_waypoint","end_waypoint","start_x","start_z","end_x","end_z",
              "schematic_straight_line_m","ground_walkable","water_rock_tree_barriers","line_of_sight_verified"]
        writer=csv.DictWriter(stream,fieldnames=cols,extrasaction="ignore")
        writer.writeheader();writer.writerows(segments)
    warning=(
      "BEILEYS47 Stage 4.8. THIS IS A MATHEMATICAL X/Z FIELD GUIDE, NOT A VERIFIED IN-GAME TRAIL.\n"
      "All terrain heights Y are missing. Compass directions are computed from provisional rotation.\n"
      "DO NOT INSTALL OR UPLOAD THESE FILES TO NITRADO. No DayZ gameplay data in this archive.\n"
    ).encode()
    files={
      "DO_NOT_DEPLOY.txt":warning,"central_field_recon.json":rp.read_bytes(),
      "central_waypoints.csv":points.read_bytes(),"central_route_links.csv":links.read_bytes()
    }
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(hashes,indent=2)+"\n").encode()
    with zipfile.ZipFile(OUT/"beileys47-world-xz-field-guide-only.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(name,data)
    with zipfile.ZipFile(OUT/"beileys47-world-xz-field-guide-only.zip") as z:
        require(z.testzip() is None and set(z.namelist())==set(files),"Bad archive")
        for name,digest in hashes.items():
            require(hashlib.sha256(z.read(name)).hexdigest()==digest,"Checksum mismatch")
        require("zone47_objects.json" not in z.namelist(),"No installable files allowed")
    print("PASS: ZONA 47 X/Z field guide: 11 waypoints, 16 segments, 6 paper routes, ZERO measured Y.")
    print(f"Legacy compass IDs after rotation: {actual_compass}. No in-game compass/site survey performed.")
    return report

if __name__=="__main__":build()
