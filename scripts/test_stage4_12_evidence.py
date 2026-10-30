#!/usr/bin/env python3
"""Stage 4.12 ledger + archive regressions: all zero-live claims."""
from __future__ import annotations

import hashlib
import json
import zipfile

from build_stage4_12_evidence import ROOT,DIR,OUTPUT,build
from test_stage4_12_rpt import test as test_rpt

def test()->None:
    test_rpt()  # synthetic-only; private log fixture is temporary
    report=build()
    assert report["stage"]=="4.12"
    assert report["status"]=="READ_ONLY_SOURCE_EVIDENCE_LEDGER_WITH_ZERO_SERVER_LOGS"
    assert report["pinned_CE_mapgroup_identifiers"]==len(report["class_candidates"])==13
    assert report["previously_suggested_model_source_names"]==9
    assert report["new_P3D_reference_placements_without_console_classnames"]==17
    assert report["symbolic_placements_total"]==len(report["symbolic_placements"])==26
    assert report["PS4_PS5_spawn_tests_completed"]==0
    assert report["actual_RPT_files_analyzed_in_public_pipeline"]==0
    assert report["any_deployment_allowed"] is False
    assert report["cannot_infer_success_from_no_failure_marker"] is True
    assert all(not m["validated_object_spawner_name"] and not m["validated_on_playstation"]
               and m["current_RPT_failure_evidence"] is None for m in report["class_candidates"])
    assert all(p["verified_dayz_console_object_spawner_classname"] is None
               and p["actual_RPT_file_evidence"] is None
               and p["ground_or_floor_Y_verified"] is False
               and p["test_result"]=="NOT_TESTED_NO_SERVER_LOG"
               and p["deployment_allowed"] is False
               for p in report["symbolic_placements"])
    assert len({p["marker_id"] for p in report["symbolic_placements"]})==26
    assert "Land_Wall_Gate_FenR" not in {m["source_class_candidate"] for m in report["class_candidates"]}
    blank=json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert blank["inspected_line_count"]==0 and blank["evidence_kind"]=="NO_LOG_PROVIDED"
    assert blank["actual_successfully_spawned_objects_count"] is None
    with zipfile.ZipFile(DIR/"beileys47-spawner-log-preflight-only.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist())=={
            "NO_SERVER_TEST_AND_DO_NOT_DEPLOY.txt","class_evidence_no_runtime.json",
            "rpt_triage_no_logs.json","SHA256.json"
        }
        hashes=json.loads(z.read("SHA256.json"))
        for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
        assert json.loads(z.read("class_evidence_no_runtime.json"))==report
        assert b"NEVER commit private RPT" in z.read("NO_SERVER_TEST_AND_DO_NOT_DEPLOY.txt")
    print("PASS: Stage 4.12 verified empty-log source ledger, no privacy leaks or deployable outputs.")

if __name__=="__main__":test()
