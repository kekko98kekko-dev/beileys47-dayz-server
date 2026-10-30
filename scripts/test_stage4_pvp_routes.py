#!/usr/bin/env python3
"""Stage 4.7 graph tests: positive/negative, strategic fallback, ZIP integrity."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import zipfile

from stress_test_stage4_pvp_routes import ROOT,OUT,build,summarize,graph_of,distinct_paths,two_independent_routes,length

def test()->None:
    report=build()
    assert report["stage"]=="4.7"
    assert report["status"]=="CONCEPTUAL_ROUTE_GRAPH_AUDITED_NOT_IN_GAME_VALIDATED"
    assert report["terrain_surveyed"] is False
    assert report["deployment_allowed"] is False
    assert report["real_world_line_of_sight_checked"] is False
    assert report["real_world_pathfinding_available"] is False
    assert len(report["entrance_paths"])==3
    assert report["route_edges"]==15
    assert report["sector_count"]==8
    assert report["pilot_symbols_in_all_sectors"]==26
    assert len(report["single_sector_lockout"])==21
    assert report["two_sector_lockout_tested"]==45
    assert len(report["design_alerts"])>=3
    assert all(not r["reachable"] if r["status"]=="ENTRY_SECTOR_CLOSED" else r["reachable"]
               for r in report["single_sector_lockout"])
    for entry in report["entrance_paths"]:
        routes=entry["independent_routes"]
        assert len(routes)==2
        assert set(routes[0]["zones"][1:-1]).isdisjoint(routes[1]["zones"][1:-1])
        assert routes[0]["zones"][0]==routes[1]["zones"][0]==entry["start_sector"]
        assert routes[0]["zones"][-1]==routes[1]["zones"][-1]=="hq"
        assert entry["shortest_straight_segments_sum_m"]>0
    bp=json.loads((ROOT/"config/stage4_zone47_blueprint.json").read_text(encoding="utf-8"))
    graph,coords=graph_of(bp)
    assert bool(distinct_paths(graph,"service","hq",{"logistics"}))
    assert bool(distinct_paths(graph,"woods","hq",{"ridge"}))
    assert bool(distinct_paths(graph,"checkpoint","hq",{"barracks"}))
    assert not distinct_paths(graph,"checkpoint","hq",{"checkpoint"})
    # Mutated paper graph: remove northern sector's alternative access to
    # logistics (checkpoint -> service). That collapses independent routes.
    broken=copy.deepcopy(bp)
    broken["links"]=[pair for pair in broken["links"] if set(pair) not in ({"checkpoint","service"},{"checkpoint","woods"})]
    try:summarize(broken)
    except AssertionError as err:
        assert "SINGLE-CORRIDOR" in str(err) or "Single zone" in str(err)
    else:raise AssertionError("Broken paper route topology unexpectedly accepted")
    bad=copy.deepcopy(bp)
    bad["coordinate_system"]["terrain_surveyed"]=True
    try:summarize(bad)
    except AssertionError:pass
    else:raise AssertionError("Fake terrain survey claim accepted")
    assert len(report["two_sector_lockout_failures"])<=report["two_sector_lockout_tested"]
    with (OUT/"sector_lockout_matrix.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==21
    with zipfile.ZipFile(OUT/"beileys47-route-stress-design-only.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"DO_NOT_DEPLOY.txt","pvp_route_stress_report.json","sector_lockout_matrix.csv","SHA256.json"}
        digests=json.loads(z.read("SHA256.json"))
        for file,hashsum in digests.items():
            assert hashlib.sha256(z.read(file)).hexdigest()==hashsum
        assert "zone47_objects.json" not in z.namelist()
        assert json.loads(z.read("pvp_route_stress_report.json"))==report
    print("PASS: Stage 4.7 disjoint paper routes, lockout regression and design-only ZIP.")

if __name__=="__main__":test()
