#!/usr/bin/env python3
"""Synthetic-only tests for Stage 4.5 height ingestion; no real Y measurements."""
from __future__ import annotations

import copy
import json
import math
import tempfile
import zipfile
from pathlib import Path

from prepare_stage4_height_capture import ROOT, OUT, build
from audit_stage4_height_samples import analyze, run

def test()->None:
    build()
    reference=json.loads((ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json").read_text(encoding="utf-8"))
    assert len(reference["regions"])==3
    for region in reference["regions"]:
        p=OUT/f"{region['region']}_surfaceY_empty.json"
        data=json.loads(p.read_text(encoding="utf-8"))
        assert data["status"]=="UNMEASURED_CAPTURE_TEMPLATE"
        assert len(data["points"])==182
        assert len({(x["kind"],x["id"]) for x in data["points"]})==182
        assert all(p["ground_y"] is None for p in data["points"])
        incomplete=analyze(data,reference,region["region"])
        assert incomplete["status"]=="BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE"
        assert incomplete["provided_y_count"]==0
        assert incomplete["object_spawner_ready"] is False
        assert incomplete["max_local_grid_grade_degrees"] is None
        assert incomplete["deployment_allowed"] is False
    archive=OUT/"beileys47-zone47-height-capture-templates-only.zip"
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len([x for x in z.namelist() if x.endswith("_surfaceY_empty.json")])==3
        assert b"DO NOT DEPLOY" in z.read("NO_REAL_HEIGHTS_DO_NOT_DEPLOY.txt")
        assert all("zone47_objects.json" not in n for n in z.namelist())

    region="central"
    original=json.loads((OUT/"central_surfaceY_empty.json").read_text(encoding="utf-8"))
    # Data is deliberately SYNTHETIC and never saved as a map sample.
    flat=copy.deepcopy(original)
    flat["measurement"]={
       "method":"DayZ_CGame_SurfaceY","dayz_game_build":"SYNTHETIC_TEST_ONLY",
       "captured_utc":"2026-10-30T00:00:00Z",
       "evidence_reference":"SYNTHETIC_UNIT_TEST_DO_NOT_IMPORT",
       "remarks":"All values are fake and only test pipeline calculations"
    }
    for p in flat["points"]:
        p["ground_y"]=round(200+0.01*(p["x"]-9000)+0.01*(p["z"]-7800),6)
    good=analyze(flat,reference,region)
    assert good["status"]=="MEASUREMENTS_COMPLETE_REQUIRE_MANUAL_VERIFICATION"
    assert good["provenance_complete"] is True
    assert good["grade_sample_pairs"]==287
    assert good["max_local_grid_grade_degrees"]<2
    assert good["max_minus_min_ground_y_m"]<18
    assert good["terrain_approval"] is False
    assert good["object_spawner_ready"] is False
    assert good["source_not_independently_authenticated"] is True
    assert good["playstation_runtime_tested"] is False

    missing=copy.deepcopy(flat)
    missing["points"][0]["ground_y"]=None
    report=analyze(missing,reference,region)
    assert report["status"]=="BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE"
    no_provenance=copy.deepcopy(flat)
    no_provenance["measurement"]["evidence_reference"]=None
    assert analyze(no_provenance,reference,region)["provenance_complete"] is False
    for invalid_timestamp in ("2026-02-30T00:00:00Z", "not-a-valid-utc-time",
                              "2026-10-30T00:00:00+01:00", None):
        malformed=copy.deepcopy(flat)
        malformed["measurement"]["captured_utc"]=invalid_timestamp
        result=analyze(malformed,reference,region)
        assert result["provenance_complete"] is False
        assert result["status"]=="BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE"
    wrong_method=copy.deepcopy(flat)
    wrong_method["measurement"]["method"]=["DayZ_CGame_SurfaceY"]
    assert analyze(wrong_method,reference,region)["provenance_complete"] is False

    # A real measured-Y report must never appear in a public artifact
    # directory, even if the submitted input is incomplete or synthetic.
    with tempfile.TemporaryDirectory(prefix="beileys47-private-height-audit-") as dirname:
        private=Path(dirname)
        capture=private/"synthetic_only.json"
        capture.write_text(json.dumps(flat),encoding="utf-8")
        public=ROOT/"dist/stage4_height_capture/DO_NOT_PUBLISH_MEASURED_AUDIT.json"
        try: run(capture,public)
        except ValueError as e: assert "outside the public repository" in str(e)
        else: raise AssertionError("Measured elevation report leaked to public artifacts")
        assert not public.exists()
        private_result=private/"measured_report.json"
        secure=run(capture,private_result)
        assert secure["provided_y_count"]==182
        assert secure["deployment_allowed"] is False
        try: run(capture,private_result)
        except ValueError as e: assert "refuse overwrite" in str(e)
        else: raise AssertionError("Measured report overwrote existing evidence")

    bad=copy.deepcopy(flat)
    bad["points"][0]["x"]+=100
    try:analyze(bad,reference,region)
    except ValueError as e: assert "coordinate mismatch" in str(e)
    else:raise AssertionError("Swapped/stale coordinate accepted")

    bad=copy.deepcopy(flat)
    bad["points"][0]["ground_y"]=float("nan")
    try:analyze(bad,reference,region)
    except ValueError as e:assert "finite measured" in str(e)
    else:raise AssertionError("NaN ground elevation was accepted")

    bad=copy.deepcopy(flat)
    bad["points"][1]["id"]=bad["points"][0]["id"]
    try:analyze(bad,reference,region)
    except ValueError as e:assert "duplicate" in str(e)
    else:raise AssertionError("Duplicate point IDs accepted")

    steep=copy.deepcopy(flat)
    for p in steep["points"]:
        p["ground_y"]=100+0.3*(p["x"]-9000)
    report=analyze(steep,reference,region)
    assert report["status"]=="REVIEW_REQUIRED_STEEP_GRADE"
    assert report["max_local_grid_grade_degrees"]>10
    assert report["deployment_allowed"] is False

    existing=run(OUT/"central_surfaceY_empty.json")
    assert existing["provided_y_count"]==0
    saved=json.loads((OUT/"terrain_height_audit.json").read_text(encoding="utf-8"))
    assert saved["terrain_approval"] is False
    assert saved["deployment_allowed"] is False
    assert "SYNTHETIC_TEST_ONLY" not in json.dumps(saved)

    print("PASS: Stage 4.5 empty/complete/slope/nonfinite/coordinate/provenance safety tests.")
    print("NO real Livonia Y heights acquired; synthetic unit-test samples were not published.")

if __name__=="__main__":test()
