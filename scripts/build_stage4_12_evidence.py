#!/usr/bin/env python3
"""Stage 4.12: class-evidence ledger and publicly shareable ZERO-LOG audit.

The official Livonia map-group list gives identifier provenance only. P3D
visual models alone do not provide a legal console Object Spawner class.
Nothing is approved for live deployment.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from triage_stage4_12_rpt import ROOT,OUTPUT,PROVENANCE,known_candidates,run
from audit_stage4_10_all_placements import ROOT as ROOT_410

DIR=ROOT/"dist/stage4_12_rpt_diagnostics"

def build()->dict:
    assert ROOT==ROOT_410
    candidates=json.loads((ROOT/"config/stage4_asset_candidates.json").read_text(encoding="utf-8"))
    layout=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text(encoding="utf-8"))
    roles=json.loads((ROOT/"config/stage4_10_placement_roles.json").read_text(encoding="utf-8"))
    new=json.loads((ROOT/"config/stage4_11_p3d_role_candidates.json").read_text(encoding="utf-8"))
    names=known_candidates()
    assert set(names)=={m["name"] for m in candidates["models"]}
    assert len(layout["asset_placements"])==len(roles["placement_options"])==26
    assert len(new["suggestions"])==17
    assert new["approval"]["deployment_allowed"] is False

    classes=[]
    for name in names:
        classes.append({
            "source_class_candidate":name,
            "source_layer":"OFFICIAL_PINNED_LIVONIA_MAP_GROUP_IDENTIFIER",
            "central_economy_commit":candidates["pinned_commit"],
            "provenance":"BohemiaInteractive/DayZ-Central-Economy/dayzOffline.enoch/mapgrouppos.xml",
            "has_official_mapgroup_identifier_evidence":True,
            "validated_object_spawner_name":False,
            "validated_on_playstation":False,
            "current_RPT_failure_evidence":None,
            "status":"SOURCE_PRESENT_RUNTIME_UNTESTED"
        })
    placements=[]
    for p in layout["asset_placements"]:
        label=p["id"]
        ref=roles["placement_options"][label]["proposed_visual_model_classname"]
        if ref:
            assert ref in names
            source="SOURCE_PINNED_MAPGROUP_NAME_BUT_RUNTIME_UNTESTED"
        else:
            assert label in new["suggestions"]
            assert new["suggestions"][label]["verified_console_object_classname"] is None
            source="P3D_VISUAL_REFERENCE_ONLY_NO_CONSOLE_CLASS_NAME"
        placements.append({
            "marker_id":label,
            "visual_role":p["visual_role"],
            "proposed_source_classname_from_stage4_10":ref,
            "class_source_evidence":source,
            "verified_dayz_console_object_spawner_classname":None,
            "p3d_model_path_is_NOT_validated_spawner_class":True,
            "actual_RPT_file_evidence":None,
            "physical_collision_verified":False,
            "ground_or_floor_Y_verified":False,
            "test_result":"NOT_TESTED_NO_SERVER_LOG",
            "deployment_allowed":False
        })
    assert len([p for p in placements if p["proposed_source_classname_from_stage4_10"]])==9
    report={
        "stage":"4.12",
        "status":"READ_ONLY_SOURCE_EVIDENCE_LEDGER_WITH_ZERO_SERVER_LOGS",
        "official_object_spawner_documentation":PROVENANCE,
        "bohemia_official_logged_failure_marker":"Object spawner failed to spawn",
        "pinned_CE_mapgroup_identifiers":len(classes),
        "world_object_classnames_runtime_confirmed":0,
        "previously_suggested_model_source_names":9,
        "new_P3D_reference_placements_without_console_classnames":17,
        "symbolic_placements_total":26,
        "PS4_PS5_spawn_tests_completed":0,
        "actual_RPT_files_analyzed_in_public_pipeline":0,
        "terrain_y_measured":False,
        "class_candidates":classes,
        "symbolic_placements":placements,
        "official_example":"Land_Wall_Gate_FenR is shown in Bohemia docs but is NOT a verified candidate for our project.",
        "next_private_action":"When a private Nitrado RPT becomes available, analyze it locally using triage_stage4_12_rpt.py --log and --output outside the public repository. Never upload logs.",
        "cannot_infer_success_from_no_failure_marker":True,
        "any_deployment_allowed":False
    }
    DIR.mkdir(parents=True,exist_ok=True)
    ledger=DIR/"class_evidence_no_runtime.json"
    ledger.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    blank=run(None,OUTPUT)
    assert blank["status"]=="NO_REAL_LOG_AVAILABLE" and blank["actual_successfully_spawned_objects_count"] is None
    note=(
        "STAGE 4.12: source evidence is NOT console spawn verification.\n"
        "No actual logs provided. No Nitrado writes. This is not a game upload package.\n"
        "NEVER commit private RPT, ADM, player data, personal names or raw diagnostics.\n"
    ).encode("utf-8")
    files={
        "NO_SERVER_TEST_AND_DO_NOT_DEPLOY.txt":note,
        "class_evidence_no_runtime.json":ledger.read_bytes(),
        "rpt_triage_no_logs.json":OUTPUT.read_bytes()
    }
    digest={k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(digest,indent=2)+"\n").encode()
    path=DIR/"beileys47-spawner-log-preflight-only.zip"
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as zipf:
        for k,v in sorted(files.items()):zipf.writestr(k,v)
    with zipfile.ZipFile(path) as zipf:
        assert zipf.testzip() is None and set(zipf.namelist())==set(files)
        for k,hashval in digest.items():assert hashlib.sha256(zipf.read(k)).hexdigest()==hashval
        assert not any("zone47_objects" in name or "cfggameplay" in name for name in zipf.namelist())
    print("PASS: 13 official Livonia identifier candidates and 26 markers tracked with ZERO console verification.")
    print("PASS: privacy-safe EMPTY RPT audit and non-installable SHA-256 recovery archive.")
    return report

if __name__=="__main__":build()
