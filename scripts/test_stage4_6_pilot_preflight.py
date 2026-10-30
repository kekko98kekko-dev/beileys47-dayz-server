#!/usr/bin/env python3
"""Regression tests for centered surveying and planned (NOT GAME) pilot."""
from __future__ import annotations

import copy
import json
import zipfile
import tempfile
from pathlib import Path

from build_stage4_6_pilot_preflight import run, OUT, ROOT
from export_zone47_spawner import export, STAGE3_GAMEPLAY
from prepare_zone47_survey import OUT as SURVEY, build as make_survey

def test()->None:
    p=run()
    assert p["status"]=="PILOT_PLANNING_ONLY_NOT_NITRADO_INSTALLABLE"
    assert (p["center_x"],p["center_z"],p["orientation_degrees"])==(9000,7800,120)
    assert p["coordinate_reference"]=="WORLD_CENTER_OF_BLUEPRINT"
    assert p["pilot_prop_count"]==len(p["pilot_props"])==5
    assert len({x["sector"] for x in p["pilot_props"]})==5
    for prop in p["pilot_props"]:
        assert 0<prop["candidate_world_x"]<12800
        assert 0<prop["candidate_world_z"]<12800
        assert prop["ground_y"] is None and prop["selected_model_classname"] is None
        assert prop["ready_to_install"] is False
        assert prop["console_asset_verified"] is False
    assert p["deployment_allowed"] is False
    assert p["real_height_measurements"]==0
    with zipfile.ZipFile(OUT/"beileys47-micro-pilot-plan-only.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"README_DO_NOT_DEPLOY.txt","zone47_micro_pilot_plan.json","sha256.json"}
        assert b"DO NOT DEPLOY" in z.read("README_DO_NOT_DEPLOY.txt")
        assert "zone47_objects.json" not in z.namelist()
        assert json.loads(z.read("zone47_micro_pilot_plan.json"))==p

    make_survey()
    empty=json.loads(SURVEY.read_text(encoding="utf-8"))
    assert empty["version"]=="2.0"
    assert empty["site"]["coordinate_reference"]=="WORLD_CENTER_OF_BLUEPRINT"
    assert empty["site"]["world_center_x"] is None
    assert empty["site"]["world_center_z"] is None
    assert "world_origin_x" not in empty["site"]
    with tempfile.TemporaryDirectory(prefix="beileys47-center-gate-") as td:
        tmp=Path(td)
        survey=tmp/"empty_survey_v2.json"
        survey.write_text(json.dumps(empty),encoding="utf-8")
        output=tmp/"output"
        try:
            export(survey,STAGE3_GAMEPLAY,output)
        except ValueError as exc:
            assert "EXPORT BLOCKED" in str(exc)
        else:
            raise AssertionError("Empty centered survey incorrectly exported")
        assert not output.exists(),"Exporter produced files without measurements"
    print("PASS: five-point pilot is planning-only; centered v2 survey cannot export without real checks.")

if __name__=="__main__":test()
