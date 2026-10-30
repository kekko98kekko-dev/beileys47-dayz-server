#!/usr/bin/env python3
"""Stage 4.13: create a blank, non-installable PS4/PS5 pilot evidence packet.

Exactly 1 -> 3 -> 5 symbolic ZONA47 markers. Never create a mission file or
claim a server-ready world position, class name, or usable terrain Y.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from zip_deterministic import add_bytes

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"config/stage4_13_pilot_protocol.json"
PILOT=ROOT/"dist/stage4_6_preflight/zone47_micro_pilot_plan.json"
OUT=ROOT/"dist/stage4_13_console_pilot"

def validate_protocol(protocol:dict,pilot:dict)->None:
    assert protocol["stage"]=="4.13" and protocol["version"]=="1.0"
    assert protocol["status"]=="CONSOLE_PILOT_PROTOCOL_ONLY_NO_RUNTIME_TRIAL"
    assert protocol["safety"]["automatic_deployment_allowed"] is False
    assert protocol["safety"]["no_live_Nitrado_connection"] is True
    assert protocol["site"]["terrain_not_yet_verified"] is True
    assert protocol["site"]["map"]=="Livonia" and protocol["site"]["mission"]=="dayzOffline.enoch"
    assert pilot["status"]=="PILOT_PLANNING_ONLY_NOT_NITRADO_INSTALLABLE"
    assert pilot["deployment_allowed"] is False and pilot["real_height_measurements"]==0
    assert (pilot["center_x"],pilot["center_z"],pilot["orientation_degrees"])==(9000,7800,120)
    phases=protocol["rollout"]
    assert [(p["phase"],p["object_count"]) for p in phases]==[("P1",1),("P3",3),("P5",5)]
    ids=[p["placement_id"] for p in pilot["pilot_props"]]
    assert len(ids)==len(set(ids))==5
    assert [x["marker_ids"] for x in phases]==[ids[:1],ids[:3],ids]
    assert all(p["ground_y"] is None and p["selected_model_classname"] is None for p in pilot["pilot_props"])
    assert protocol["acceptance"]["required_restart_observations_per_phase"]==2
    assert protocol["provider_backup_limits"]["provider_states_manual_console_FTP_backups_not_supported"] is True

def blank_packet(protocol:dict,pilot:dict)->dict:
    validate_protocol(protocol,pilot)
    marker_map={p["placement_id"]:p for p in pilot["pilot_props"]}
    phases=[]
    for stage in protocol["rollout"]:
        objects=[]
        for marker_id in stage["marker_ids"]:
            original=marker_map[marker_id]
            objects.append({
                "marker_id":marker_id,
                "zone":original["sector"],
                "candidate_world_x":original["candidate_world_x"],
                "candidate_world_z":original["candidate_world_z"],
                "console_classname":None,
                "measured_ground_or_floor_y":None,
                "height_evidence_reference":None,
                "observed_spawn_on_PS5":None,
                "walkable_collision_checked":None,
                "doors_and_routes_not_blocked":None,
                "visual_evidence_reference":None
            })
        phases.append({
            "phase":stage["phase"],
            "expected_cumulative_count":stage["object_count"],
            "objects":objects,
            "server_restart_observations":None,
            "restart_evidence_reference":None,
            "no_new_crashes":None,
            "no_unacceptable_stutter_or_rubberbanding":None,
            "PS5_walkthrough_completed":None,
            "rpt_status":None,  # NO_LOG_ACCESS, REVIEWED_NO_MARKER, FAILED_TO_SPAWN
            "rpt_private_triage_reference":None,
            "manual_review_decision":None, # APPROVED_FOR_NEXT_PHASE or STOP_AND_RESTORE
            "manual_review_reference":None,
            "notes":None
        })
    return {
        "stage":"4.13",
        "schema_version":"1.0",
        "status":"BLANK_CONSOLE_TRIAL_EVIDENCE_NOT_GAME_DATA",
        "source_site_center":[9000,7800],
        "source_yaw_preliminary_degrees":120,
        "source_reference_stage":"4.6",
        "preflight":{
            "authorized_private_server_owner":None,
            "mission_confirmed_dayzOffline_enoch":None,
            "console_build_matches_source":None,
            "console_build_reference":None,
            "walked_real_site_and_approaches":None,
            "verified_object_classnames_in_test_environment":None,
            "offline_copies_of_modified_configs_saved":None,
            "provider_backup_actually_available":None,
            "provider_backup_utc":None,
            "provider_backup_evidence_reference":None,
            "Nitrado_restore_process_reviewed":None,
            "active_players_and_persistence_protected":None,
            "preflight_review_reference":None
        },
        "phases":phases,
        "playstation_4_compatibility_confirmed":None,
        "playstation_4_evidence_reference":None,
        "runtime_evidence_independently_authenticated":False,
        "no_actual_gameplay_test_has_been_performed_by_this_pipeline":True,
        "this_packet_is_not_an_object_spawner":True,
        "automatic_deployment_allowed":False,
        "warning":"BLANK TEMPLATE. No observed spawn, class, terrain Y, backup availability, PS5 performance or collision has been verified."
    }

def build()->dict:
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    result=blank_packet(protocol,pilot)
    OUT.mkdir(parents=True,exist_ok=True)
    packet=OUT/"blank_1_3_5_console_trial.json"
    packet.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    readme=(
        "BEILEYS47 STAGE 4.13 - EMPTY CONSOLE FIELD TRIAL RECORD ONLY.\n"
        "DO NOT UPLOAD TO NITRADO. All observations are blank. No runtime tests, no actual backup check.\n"
        "Nitrado documents scheduled daily backups and no manual console FTP full backup.\n"
        "Private server/player details and RPT logs must never be committed to GitHub.\n"
    ).encode("utf-8")
    files={"DO_NOT_DEPLOY.txt":readme,"blank_1_3_5_console_trial.json":packet.read_bytes()}
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}
    files["SHA256.json"]=(json.dumps(hashes,indent=2)+"\n").encode()
    archive=OUT/"beileys47-console-pilot-templates-only.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for name,content in sorted(files.items()):add_bytes(z,name,content)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist())==set(files)
        for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
        assert all("zone47_objects.json" not in x and "cfggameplay.json" not in x for x in z.namelist())
    print("PASS: Stage 4.13 1 -> 3 -> 5 BLANK console trial packet and SHA-256 archive.")
    print("NO REAL Nitrado backup, console tests, elevation Y or validated spawner classes.")
    return result

if __name__=="__main__":build()
