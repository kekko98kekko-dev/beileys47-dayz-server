#!/usr/bin/env python3
"""Stage 4.13 adversarial and synthetic-only console pilot tests.

No sample in this script is actual Nitrado / DayZ performance evidence.
All filled test records exist only in a temporary directory, NEVER release.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from build_stage4_13_console_pilot import ROOT,OUT,PROTOCOL,PILOT,build,blank_packet
from audit_stage4_13_console_pilot import REPORT,audit,run

def expect_reject(fn,fragment:str):
    try:fn()
    except ValueError as e:assert fragment in str(e),(fragment,str(e))
    else:raise AssertionError("Unsafe evidence accepted: "+fragment)

def test()->None:
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    template=build()
    assert template["stage"]=="4.13"
    assert template["status"]=="BLANK_CONSOLE_TRIAL_EVIDENCE_NOT_GAME_DATA"
    assert [x["phase"] for x in template["phases"]]==["P1","P3","P5"]
    assert [len(x["objects"]) for x in template["phases"]]==[1,3,5]
    assert all(x["console_classname"] is None and x["measured_ground_or_floor_y"] is None
               for p in template["phases"] for x in p["objects"])
    assert all(p["server_restart_observations"] is None for p in template["phases"])
    assert template["automatic_deployment_allowed"] is False
    report=run(None,REPORT)
    assert report["status"]=="BLOCKED_NO_VERIFIABLE_FULL_PILOT_EVIDENCE"
    assert report["preflight_fields_complete"] is False
    assert all(not p["phase_evidence_satisfies_manual_review_fields"] for p in report["phases"])
    assert report["automatic_deployment_allowed"] is False
    assert report["release_allowed"] is False
    assert report["object_spawner_generated"] is False
    assert json.loads(REPORT.read_text(encoding="utf-8"))==report

    # TEST DATA ONLY: invent an entirely synthetic user assertion packet to
    # test logic, then remove it. Never publish these as DayZ measurements.
    fake=copy.deepcopy(template)
    pre=fake["preflight"]
    for key in (
        "authorized_private_server_owner","mission_confirmed_dayzOffline_enoch",
        "console_build_matches_source","walked_real_site_and_approaches",
        "verified_object_classnames_in_test_environment","offline_copies_of_modified_configs_saved",
        "provider_backup_actually_available","Nitrado_restore_process_reviewed",
        "active_players_and_persistence_protected"
    ):pre[key]=True
    pre["console_build_reference"]="SYNTHETIC_BUILD_NOT_REAL"
    pre["provider_backup_evidence_reference"]="SYNTHETIC_BACKUP_NOT_REAL"
    pre["provider_backup_utc"]="2026-10-30T10:00:00+01:00"
    pre["preflight_review_reference"]="SYNTHETIC_ONLY_NO_REAL_PERSON"
    for phase in fake["phases"]:
        phase["server_restart_observations"]=2
        phase["restart_evidence_reference"]="FAKE_RESTART_UNIT_TEST"
        phase["no_new_crashes"]=True
        phase["no_unacceptable_stutter_or_rubberbanding"]=True
        phase["PS5_walkthrough_completed"]=True
        phase["rpt_status"]="NO_LOG_ACCESS"
        phase["manual_review_decision"]="APPROVED_FOR_NEXT_PHASE"
        phase["manual_review_reference"]="FAKE_MANUAL_APPROVAL_UNIT_TEST"
        for item in phase["objects"]:
            item.update({
                "console_classname":"Land_SyntheticClass_NotVerified",
                "measured_ground_or_floor_y":200.25,
                "height_evidence_reference":"SYNTHETIC_HEIGHT_NOT_MAP",
                "observed_spawn_on_PS5":True,
                "walkable_collision_checked":True,
                "doors_and_routes_not_blocked":True,
                "visual_evidence_reference":"FAKE_VISUAL_UNIT_TEST"
            })
    positive=audit(fake,protocol,pilot)
    assert positive["status"]=="REVIEW_PACKET_COMPLETE_BUT_UNAUTHENTICATED"
    assert all(x["phase_evidence_satisfies_manual_review_fields"] for x in positive["phases"])
    assert positive["PS5_runtime_independently_verified"] is False
    assert positive["release_allowed"] is False
    assert positive["automatic_deployment_allowed"] is False
    assert positive["user_supplied_evidence_is_NOT_independently_authenticated"] is True

    damaged=copy.deepcopy(fake)
    damaged["preflight"]["provider_backup_actually_available"]=False
    result=audit(damaged,protocol,pilot)
    assert result["status"]=="BLOCKED_NO_VERIFIABLE_FULL_PILOT_EVIDENCE"
    assert all(x["status"].startswith("BLOCKED_") for x in result["phases"])

    damaged=copy.deepcopy(fake)
    damaged["phases"][0]["objects"][0]["measured_ground_or_floor_y"]=None
    result=audit(damaged,protocol,pilot)
    assert not any(x["phase_evidence_satisfies_manual_review_fields"] for x in result["phases"])

    damaged=copy.deepcopy(fake)
    damaged["phases"][1]["rpt_status"]="FAILED_TO_SPAWN"
    result=audit(damaged,protocol,pilot)
    assert result["phases"][0]["phase_evidence_satisfies_manual_review_fields"] is True
    assert result["phases"][1]["phase_evidence_satisfies_manual_review_fields"] is False
    assert result["phases"][2]["phase_evidence_satisfies_manual_review_fields"] is False

    damaged=copy.deepcopy(fake)
    damaged["phases"][0]["server_restart_observations"]=1
    result=audit(damaged,protocol,pilot)
    assert all(not x["phase_evidence_satisfies_manual_review_fields"] for x in result["phases"])

    damaged=copy.deepcopy(fake)
    damaged["phases"][0]["objects"][0]["doors_and_routes_not_blocked"]=False
    assert all(not x["phase_evidence_satisfies_manual_review_fields"]
               for x in audit(damaged,protocol,pilot)["phases"])

    damaged=copy.deepcopy(fake)
    damaged["phases"][2]["objects"][0]["console_classname"]="structures/industrial/fake.p3d"
    expect_reject(lambda:audit(damaged,protocol,pilot),"NOT a direct P3D path")

    damaged=copy.deepcopy(fake)
    damaged["phases"][1]["objects"][1]["candidate_world_x"]+=20
    expect_reject(lambda:audit(damaged,protocol,pilot),"Changed marker or candidate X/Z")

    damaged=copy.deepcopy(fake)
    damaged["phases"][0]["objects"][0]["measured_ground_or_floor_y"]=float("nan")
    expect_reject(lambda:audit(damaged,protocol,pilot),"Invalid real ground/floor Y")

    damaged=copy.deepcopy(fake)
    damaged["preflight"]["provider_backup_utc"]="some date"
    expect_reject(lambda:audit(damaged,protocol,pilot),"Backup timestamp")

    damaged=copy.deepcopy(fake)
    damaged["automatic_deployment_allowed"]=True
    expect_reject(lambda:audit(damaged,protocol,pilot),"Unsafe attestation")

    with tempfile.TemporaryDirectory(prefix="beileys47-synthetic-pilot-") as td:
        folder=Path(td)
        src=folder/"FAKE_NOT_DAYZ.json";dest=folder/"PRIVATE_SUMMARY.json"
        src.write_text(json.dumps(fake),encoding="utf-8")
        local=run(src,dest)
        assert local["status"]=="REVIEW_PACKET_COMPLETE_BUT_UNAUTHENTICATED"
        assert json.loads(dest.read_text(encoding="utf-8"))==local
        assert "FAKE_MANUAL_APPROVAL_UNIT_TEST" not in dest.read_text(encoding="utf-8")
        expect_reject(lambda:run(src,ROOT/"dist/test_stage4_13_private_never.json"),
                      "Private test results cannot be written")

    with zipfile.ZipFile(OUT/"beileys47-console-pilot-templates-only.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist())=={"DO_NOT_DEPLOY.txt","blank_1_3_5_console_trial.json","SHA256.json"}
        h=json.loads(z.read("SHA256.json"))
        for name,digest in h.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
        assert json.loads(z.read("blank_1_3_5_console_trial.json"))==template
        assert b"DO NOT UPLOAD" in z.read("DO_NOT_DEPLOY.txt")
        assert "zone47_objects.json" not in z.namelist()
    assert all("SYNTHETIC" not in p.read_text(encoding="utf-8")
               for p in (REPORT,OUT/"blank_1_3_5_console_trial.json"))
    print("PASS Stage 4.13: staged 1/3/5 safety, insufficient evidence, simulated failures, private outputs.")
    print("NOT done: real Nitrado backup/restoration, real PS5/P4, Y or DayZ object spawn testing.")

if __name__=="__main__":test()
