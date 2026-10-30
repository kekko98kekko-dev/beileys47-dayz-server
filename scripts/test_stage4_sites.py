#!/usr/bin/env python3
"""Regression checks on Stage 4 pre-screening. No real terrain or PS5 testing."""
from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path

from scan_stage4_sites import SOURCE_FILES, fetch_source, read_positions, dist_nearest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/stage4_site_screening"
REPORT=OUT/"site_screen_report.json"
ARCHIVE=OUT/"beileys47-zone47-site-screen-only.zip"

def test()->None:
    data=json.loads(REPORT.read_text(encoding="utf-8"))
    assert data["stage"]==4 and data["status"]=="PROVISIONAL_SITE_SCREENING_NOT_SITE_APPROVAL"
    assert data["ready_to_export_object_spawner"] is False
    assert data["ready_for_live_deployment"] is False
    assert len(data["regions"])==3 and data["recommended_first_survey_region"]=="central"
    rules=data["search_rules"]
    fresh=json.loads((ROOT/"config/stage1_rules.json").read_text(encoding="utf-8"))["fresh_spawn_groups"]
    roots={p:ET.fromstring(fetch_source(p,data["source_commit"],None)) for p in SOURCE_FILES}
    groups,military,spawns,events,_=read_positions(roots,fresh,rules["event_prefixes"])

    points=set()
    for region in data["regions"]:
        assert region["decision"]=="SURVEY_REQUIRED_NO_SITE_APPROVED"
        assert region["passes_static_filters"]>=rules["per_region_top_n"]
        assert len(region["top_candidates"])==rules["per_region_top_n"]
        bounds=next(w["bounds_xz"] for w in rules["windows"] if w["id"]==region["id"])
        for candidate in region["top_candidates"]:
            x,z=candidate["x"],candidate["z"]
            assert isinstance(x,int) and isinstance(z,int)
            assert bounds[0]<=x<=bounds[1] and bounds[2]<=z<=bounds[3]
            assert (x,z) not in points
            points.add((x,z))
            assert candidate["status"]=="CANDIDATE_COORDINATE_ONLY_REQUIRES_IN_GAME_SURVEY"
            assert candidate["height_y"] is None and candidate["slope_degrees"] is None
            assert candidate["road_access_verified"] is False
            assert candidate["object_spawner_approved"] is False
            assert candidate["vegetation_or_collision_checked"] is False
            assert dist_nearest(x,z,spawns)>=rules["minimum_nearest_fresh_spawn_metres"]
            assert dist_nearest(x,z,events)>=rules["minimum_nearest_active_event_position_metres"]
            assert dist_nearest(x,z,groups)>=rules["minimum_nearest_terrain_group_metres"]
            assert dist_nearest(x,z,military)<=rules["maximum_nearest_military_group_metres"]
            assert abs(candidate["nearest_selected_fresh_spawn_m"]-dist_nearest(x,z,spawns))<=1
            assert abs(candidate["nearest_included_event_point_m"]-dist_nearest(x,z,events))<=1
        choices=region["top_candidates"]
        for a in range(len(choices)):
            for b in range(a+1,len(choices)):
                assert math.hypot(choices[a]["x"]-choices[b]["x"],choices[a]["z"]-choices[b]["z"])>=rules["minimum_separation_between_selected_centers_metres"]
    assert len(points)==9
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"DO_NOT_DEPLOY.txt","site_screen_report.json","site_screen_scatter.svg","sha256.json"}
        assert b"Never upload" in z.read("DO_NOT_DEPLOY.txt")
        assert json.loads(z.read("site_screen_report.json"))==data
        svg=z.read("site_screen_scatter.svg")
        assert b"NO TOPOGRAPHY" in svg and b"DO NOT DEPLOY" in svg
        assert b"<svg" in svg
    print("PASS: all 9 provisional centers independently respect source-coordinate exclusion criteria.")
    print("NOT VERIFIED: actual terrain footprint, road access, elevation, performance or Nitrado permissions.")

if __name__=="__main__":test()
