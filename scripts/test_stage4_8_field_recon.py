#!/usr/bin/env python3
"""Stage 4.8 waypoint-provenance and empty-Y field-guide regression."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile

from build_stage4_8_field_recon import ROOT,OUT,build,bearing,cardinal
from build_stage4_terrain_survey_grid import local_to_world

def test()->None:
    r=build()
    assert r["status"]=="FIELD_RECON_COORDINATES_READY_NOT_PLAYABLE_OR_VERIFIED"
    assert r["stage"]=="4.8" and r["deployment_allowed"] is False
    assert r["candidate_world_center"]==[9000,7800]
    assert r["candidate_yaw_degrees"]==120
    assert r["selected_location_not_approved"] is True
    assert r["real_terrain_y_samples"]==0
    assert r["console_gameplay_tests_completed"]==0
    assert r["all_waypoints_Y_null"] is True
    assert r["legacy_entrance_ids_not_true_compass_directions"] is True
    assert len(r["waypoints"])==11
    assert len(r["route_segments"])==16
    assert len(r["two_independent_routes_per_entrance_to_inspect"])==6
    assert {x["waypoint_id"] for x in r["waypoints"]}=={
        "north","west","east","checkpoint","woods","service",
        "barracks","logistics","hq","ridge","secret"
    }
    bp=json.loads((ROOT/"config/stage4_zone47_blueprint.json").read_text(encoding="utf-8"))
    nodes={x["id"]:x for x in bp["entrances"]+bp["zones"]}
    indexed={x["waypoint_id"]:x for x in r["waypoints"]}
    for key,p in indexed.items():
        src=nodes[key]
        x,z=local_to_world(src["x"],src["z"],9000,7800,240,220,120)
        assert abs(p["provisional_world_x"]-x)<0.001
        assert abs(p["provisional_world_z"]-z)<0.001
        assert p["terrain_y"] is None
        assert p["actual_pathfinding_verified"] is False
        assert p["actual_collisions_verified"] is False
        az=bearing(x,z,9000,7800)
        assert p["compass_direction_from_site_center"]==cardinal(az)

    actual_compass=r["actual_compass_for_entrances_from_provisional_coordinate_transform"]
    # Labels are legacy names, not real-world compass directions after yaw.
    assert actual_compass["north"]!="N"
    assert actual_compass["west"]!="W"
    assert actual_compass["east"]!="E"

    for item,(a,b) in zip(r["route_segments"],bp["links"]):
        assert item["start_waypoint"]==a and item["end_waypoint"]==b
        assert item["ground_walkable"] is None
        assert item["line_of_sight_verified"] is None
        assert item["real_ground_y_available"] is False
        assert item["schematic_straight_line_m"]>0
        d=math.dist((indexed[a]["provisional_world_x"],indexed[a]["provisional_world_z"]),
                    (indexed[b]["provisional_world_x"],indexed[b]["provisional_world_z"]))
        assert abs(d-item["schematic_straight_line_m"])<=0.006
    assert any(set((x["start_waypoint"],x["end_waypoint"]))=={"service","secret"} for x in r["route_segments"])
    assert {x["test_id"] for x in r["two_independent_routes_per_entrance_to_inspect"]}=={
        "NORTH-1","NORTH-2","WEST-1","WEST-2","EAST-1","EAST-2"
    }
    for route in r["two_independent_routes_per_entrance_to_inspect"]:
        assert len(route["waypoint_ids"])==len(route["provisional_world_xz"])
        assert all(y is None for y in [route["route_confirmation"]["actual_ground_walkable"],
                                      route["route_confirmation"]["current_game_build"]])
        assert route["route_confirmation"]["evaluation"]=="UNTESTED_NO_REAL_TERRAIN_EVIDENCE"
        assert route["route_confirmation"]["actual_ground_walk_attempted"] is False
    with (OUT/"central_waypoints.csv").open(encoding="utf-8",newline="") as inp:
        waypoints=list(csv.DictReader(inp))
    with (OUT/"central_route_links.csv").open(encoding="utf-8",newline="") as inp:
        links=list(csv.DictReader(inp))
    assert len(waypoints)==11 and all(p["terrain_y"]=="" for p in waypoints)
    assert len(links)==16 and all(p["ground_walkable"]=="" for p in links)

    with zipfile.ZipFile(OUT/"beileys47-world-xz-field-guide-only.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"DO_NOT_DEPLOY.txt","central_field_recon.json",
                                     "central_waypoints.csv","central_route_links.csv","SHA256.json"}
        manifest=json.loads(z.read("SHA256.json"))
        for name,checksum in manifest.items():
            assert hashlib.sha256(z.read(name)).hexdigest()==checksum
        assert b"DO NOT INSTALL" in z.read("DO_NOT_DEPLOY.txt")
        assert "zone47_objects.json" not in z.namelist()
        assert json.loads(z.read("central_field_recon.json"))==r
    print("PASS: Stage 4.8 location transform, true provisional compass bearings, zero Y and 16 segment field checklist.")

if __name__=="__main__":test()
