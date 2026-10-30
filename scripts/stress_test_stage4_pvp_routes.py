#!/usr/bin/env python3
"""Stage 4.7: deterministic conceptual PvP route resilience audit.

Graph edges are DRAWN LINKS, not verified roads/paths. Distances are local
2D Euclidean schematic lengths: NOT actual walking times or traveled metres.
No Y, obstacles, line-of-sight, AI, player movement or game runtime.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import zipfile
from pathlib import Path

from zip_deterministic import add_bytes

ROOT=Path(__file__).resolve().parents[1]
BP=ROOT/"config/stage4_zone47_blueprint.json"
MICRO=ROOT/"config/stage4_zone47_micro_layout.json"
OUT=ROOT/"dist/stage4_7_route_balance"

def graph_of(bp:dict)->tuple[dict[str,set[str]],dict[str,tuple[float,float]]]:
    zones={z["id"] for z in bp["zones"]}
    entries={e["id"] for e in bp["entrances"]}
    assert len(zones)==8 and len(entries)==3 and not zones.intersection(entries)
    nodes={n:set() for n in zones.union(entries)}
    coords={z["id"]:(z["x"],z["z"]) for z in bp["zones"]}
    coords.update({e["id"]:(e["x"],e["z"]) for e in bp["entrances"]})
    links=set()
    for a,b in bp["links"]:
        assert a in nodes and b in nodes and a!=b
        edge=tuple(sorted((a,b)))
        assert edge not in links
        links.add(edge)
        nodes[a].add(b);nodes[b].add(a)
    assert all(len(nodes[e])==1 for e in entries)
    assert "hq" in zones and "ridge" in zones
    return nodes,coords

def distinct_paths(graph:dict[str,set[str]],start:str,target:str,blocked:set[str]|None=None)->list[list[str]]:
    banned=blocked or set()
    if start in banned or target in banned:return []
    routes=[]
    def walk(cur:str,path:list[str])->None:
        if cur==target:
            routes.append(path)
            return
        for nxt in sorted(graph[cur]):
            if nxt not in banned and nxt not in path:
                walk(nxt,path+[nxt])
    walk(start,[start])
    return routes

def length(route:list[str],coords:dict[str,tuple[float,float]])->float:
    return sum(math.dist(coords[a],coords[b]) for a,b in zip(route,route[1:]))

def two_independent_routes(routes:list[list[str]],coords:dict)->tuple[list[str],list[str]]|None:
    """Different intermediate zone nodes, same start and HQ permitted."""
    options=[]
    for a,b in itertools.combinations(routes,2):
        if set(a[1:-1]).isdisjoint(b[1:-1]):
            options.append((a,b))
    if not options:return None
    return min(options,key=lambda pair:(round(length(pair[0],coords)+length(pair[1],coords),8),
                                        len(pair[0])+len(pair[1]),tuple(pair[0]),tuple(pair[1])))

def summarize(bp:dict)->dict:
    assert bp["codename"]=="ZONA 47" and bp["status"]=="DESIGN_ONLY_NOT_INSTALLABLE"
    assert bp["coordinate_system"]["terrain_surveyed"] is False
    graph,coords=graph_of(bp)
    zones=sorted(z["id"] for z in bp["zones"])
    centers={e["id"]:e["to"] for e in bp["entrances"]}
    paths=[]
    outage_matrix=[]
    pairs=[]
    for e in sorted(bp["entrances"],key=lambda x:x["id"]):
        start=e["to"]
        candidates=distinct_paths(graph,start,"hq")
        pair=two_independent_routes(candidates,coords)
        assert pair is not None, "SINGLE-CORRIDOR PROBLEM: "+e["id"]
        shortest=min(candidates,key=lambda r:(length(r,coords),tuple(r)))
        paths.append({
          "entry":e["id"],"start_sector":start,
          "shortest_route":shortest,"shortest_straight_segments_sum_m":round(length(shortest,coords),1),
          "independent_routes":[{"zones":p,"schematic_segment_sum_m":round(length(p,coords),1)} for p in pair],
          "all_simple_routes":len(candidates),
          "can_reach_hq_if_any_other_single_zone_closed":True
        })
        for removed in zones:
            if removed=="hq":continue
            if removed==start:
                status="ENTRY_SECTOR_CLOSED"
                reachable=False
            else:
                reachable=bool(distinct_paths(graph,start,"hq",{removed}))
                status="ALTERNATIVE_ROUTE_EXISTS" if reachable else "BLOCKED_BY_ONE_CLOSED_SECTOR"
                if not reachable:raise AssertionError(f"Single zone {removed} cuts {e['id']} to HQ")
            outage_matrix.append({"entry":e["id"],"closed_sector":removed,
                                  "reachable":reachable,"status":status})
        for a,b in itertools.combinations((z for z in zones if z!="hq" and z!=start),2):
            reachable=bool(distinct_paths(graph,start,"hq",{a,b}))
            pairs.append({"entry":e["id"],"closed_sectors":[a,b],"reachable":reachable})

    # Track whether a realistic two-sector lockdown can force entire entries
    # into a predictable choke. No claim these conceptual sectors can be
    # physically blocked or traveled in the proposed terrain.
    blocked_pairs=[x for x in pairs if not x["reachable"]]
    assert not blocked_pairs, f"DOUBLE-SECTOR CHOKEPOINT: {blocked_pairs}"
    all_props=json.loads(MICRO.read_text(encoding="utf-8"))["asset_placements"]
    role_counts={}
    for p in all_props:
        role_counts[p["zone"]]=role_counts.get(p["zone"],0)+1
    report={
      "stage":"4.7",
      "status":"CONCEPTUAL_ROUTE_GRAPH_AUDITED_NOT_IN_GAME_VALIDATED",
      "map":"Livonia",
      "terrain_surveyed":False,
      "real_world_pathfinding_available":False,
      "real_world_line_of_sight_checked":False,
      "real_world_terrain_height_checked":False,
      "physical_obstacles_checked":False,
      "ps4_ps5_performance_tested":False,
      "deployment_allowed":False,
      "coordinate_system":"SCHEMATIC_2D_LOCAL_METRES_NOT_TERRAIN_WALKING_DISTANCE",
      "sector_count":len(zones),
      "entrance_count":len(centers),
      "route_edges":len(bp["links"]),
      "pilot_symbols_in_all_sectors":len(all_props),
      "prop_budget":sum(z["object_budget"] for z in bp["zones"]),
      "zone_symbol_counts":role_counts,
      "entrance_paths":paths,
      "single_sector_lockout":outage_matrix,
      "two_sector_lockout_tested":len(pairs),
      "two_sector_lockout_failures":blocked_pairs,
      "balanced_geometrically_on_the_map":False,
      "world_geometry_not_verified":True,
      "design_alerts":[
        "The entry itself has a SINGLE designated connection; camping the immediate entry sector may block that entry.",
        "Graph paths are hypothetical links and may cross obstacles, water, grades or existing terrain assets.",
        "Even node-disjoint paper routes can share a narrow physical doorway or real-world chokepoint.",
        "HQ, ridge and loot sightlines are not raycast in DayZ; there is no factual PvP balance certification."
      ],
      "human_next_checks":[
        "Confirm actual approach roads and paths for all 3 entrances and 2+ HQ routes",
        "Confirm ridge does not dominate both HQ and checkpoint through real sightlines",
        "Survey building dimensions, tree/rock collisions and exact Y with DayZ terrain API",
        "Verify real first 5 props spawn on a privately approved console Nitrado test instance",
        "Retest graph assumptions with real measured in-game walk routes"
      ]
    }
    assert len(paths)==3 and len(outage_matrix)==3*7 and len(pairs)==3*15
    assert len(bp["links"])==16, "East-side bypass missing"
    assert all(p["can_reach_hq_if_any_other_single_zone_closed"] for p in paths)
    assert report["deployment_allowed"] is False
    return report

def build()->dict:
    bp=json.loads(BP.read_text(encoding="utf-8"))
    r=summarize(bp)
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"pvp_route_stress_report.json"
    path.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    matrix=OUT/"sector_lockout_matrix.csv"
    with matrix.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["entry","closed_sector","reachable","status"])
        writer.writeheader()
        writer.writerows(r["single_sector_lockout"])
    note=b"BEILEYS47 - ROUTE STRESS IS ONLY A CONCEPTUAL GRAPH. NO REAL TERRAIN PATHS. DO NOT UPLOAD TO NITRADO.\n"
    files={"DO_NOT_DEPLOY.txt":note,"pvp_route_stress_report.json":path.read_bytes(),
           "sector_lockout_matrix.csv":matrix.read_bytes()}
    digest={n:hashlib.sha256(v).hexdigest() for n,v in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(digest,indent=2)+"\n").encode()
    zip_path=OUT/"beileys47-route-stress-design-only.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):add_bytes(z,name,data)
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(files)
        for name,h in digest.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
    for route in r["entrance_paths"]:
        print(f"DESIGN {route['entry']}: shortest {route['shortest_straight_segments_sum_m']} m in schematic; >=2 distinct paper routes.")
    print(f"PASS: 21 single-sector and {len(r['two_sector_lockout_failures'])} failed / {r['two_sector_lockout_tested']} two-sector lockout tests.")
    print("NOT measured: walkable paths, exact Y, sightlines, collision or PlayStation FPS.")
    return r

if __name__=="__main__":build()
