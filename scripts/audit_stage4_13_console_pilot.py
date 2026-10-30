#!/usr/bin/env python3
"""Stage 4.13: fail-closed audit of USER-SUPPLIED console trial attestation.

This tool never authenticates field evidence, communicates with Nitrado,
creates an Object Spawner, or authorizes deployment. Output is COUNTS ONLY.
Real private attestations must be kept outside the public GitHub checkout.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

from build_stage4_13_console_pilot import ROOT,OUT,PROTOCOL,PILOT,blank_packet,validate_protocol

REPORT=OUT/"console_pilot_no_evidence_audit.json"
PHASES=("P1","P3","P5")
REQUIRED_TRUE=(
    "authorized_private_server_owner",
    "mission_confirmed_dayzOffline_enoch",
    "console_build_matches_source",
    "walked_real_site_and_approaches",
    "verified_object_classnames_in_test_environment",
    "offline_copies_of_modified_configs_saved",
    "provider_backup_actually_available",
    "Nitrado_restore_process_reviewed",
    "active_players_and_persistence_protected"
)
RPT_STATES={"NO_LOG_ACCESS","REVIEWED_NO_MARKER","FAILED_TO_SPAWN"}
DECISIONS={"APPROVED_FOR_NEXT_PHASE","STOP_AND_RESTORE"}

def nonempty(x:object,min_len:int=8)->bool:
    return type(x)==str and len(x.strip())>=min_len

def iso8601(x:object)->bool:
    if not nonempty(x,16):return False
    try:
        stamp=datetime.fromisoformat(x.replace("Z","+00:00"))
        return stamp.tzinfo is not None and stamp.utcoffset() is not None
    except (TypeError,ValueError,OverflowError):
        return False

def audit(packet:dict,protocol:dict,pilot:dict)->dict:
    validate_protocol(protocol,pilot)
    if packet.get("stage")!="4.13" or packet.get("schema_version")!="1.0":
        raise ValueError("Invalid Stage 4.13 evidence schema")
    if packet.get("source_site_center")!=[9000,7800] or packet.get("source_yaw_preliminary_degrees")!=120:
        raise ValueError("Wrong site/rotation in evidence packet")
    if packet.get("automatic_deployment_allowed") is not False or packet.get("this_packet_is_not_an_object_spawner") is not True:
        raise ValueError("Unsafe attestation: deployment fields changed")
    expected=blank_packet(protocol,pilot)
    phases=packet.get("phases")
    if type(phases)!=list or len(phases)!=3:
        raise ValueError("Three ordered pilot phases are required")
    for index,p in enumerate(phases):
        e=expected["phases"][index]
        if p.get("phase")!=e["phase"] or p.get("expected_cumulative_count")!=e["expected_cumulative_count"]:
            raise ValueError("Reordered/modified P1-P3-P5 pilot")
        objs=p.get("objects")
        if type(objs)!=list or len(objs)!=len(e["objects"]):
            raise ValueError("Wrong cumulative object count")
        for provided,desired in zip(objs,e["objects"]):
            if any(provided.get(key)!=desired[key] for key in
                   ("marker_id","zone","candidate_world_x","candidate_world_z")):
                raise ValueError("Changed marker or candidate X/Z")
            y=provided.get("measured_ground_or_floor_y")
            if y is not None and (type(y) not in (float,int) or not math.isfinite(y) or not -200<=y<=1500):
                raise ValueError("Invalid real ground/floor Y entry")
            cls=provided.get("console_classname")
            if cls is not None and (not nonempty(cls,5) or
                                     not cls.startswith("Land_") or "/" in cls or "\\" in cls):
                raise ValueError("Object classname must be a plausible class identifier, NOT a direct P3D path")
        if p.get("rpt_status") is not None and p["rpt_status"] not in RPT_STATES:
            raise ValueError("Invalid RPT state")
        if p.get("manual_review_decision") is not None and p["manual_review_decision"] not in DECISIONS:
            raise ValueError("Invalid manual review decision")
        count=p.get("server_restart_observations")
        if count is not None and (type(count)!=int or count<0 or count>50):
            raise ValueError("Invalid restart count")
    pre=packet.get("preflight")
    if type(pre)!=dict:raise ValueError("Missing preflight")
    for key in REQUIRED_TRUE:
        if pre.get(key) not in (None,True,False) or type(pre.get(key)) not in (bool,type(None)):
            raise ValueError("Nonboolean preflight control "+key)
    backup_date=pre.get("provider_backup_utc")
    if backup_date is not None and not iso8601(backup_date):
        raise ValueError("Backup timestamp must be ISO8601 with timezone, from an actual provider backup")
    conditions=[
        *[pre.get(k) is True for k in REQUIRED_TRUE],
        *[nonempty(pre.get(k)) for k in
          ("console_build_reference","provider_backup_evidence_reference","preflight_review_reference")],
        iso8601(backup_date),
    ]
    initial_ok=all(conditions)
    phase_results=[]
    earlier_passed=initial_ok
    for p in phases:
        valid_items=0
        for obj in p["objects"]:
            y=obj.get("measured_ground_or_floor_y")
            item_ok=(
                nonempty(obj.get("console_classname"),5) and y is not None
                and nonempty(obj.get("height_evidence_reference"))
                and obj.get("observed_spawn_on_PS5") is True
                and obj.get("walkable_collision_checked") is True
                and obj.get("doors_and_routes_not_blocked") is True
                and nonempty(obj.get("visual_evidence_reference"))
            )
            if item_ok:valid_items+=1
        rpt=p.get("rpt_status")
        reported_failure=rpt=="FAILED_TO_SPAWN"
        complete=(
            earlier_passed and
            valid_items==p["expected_cumulative_count"]
            and type(p.get("server_restart_observations")) is int
            and p["server_restart_observations"]>=protocol["acceptance"]["required_restart_observations_per_phase"]
            and nonempty(p.get("restart_evidence_reference"))
            and p.get("no_new_crashes") is True
            and p.get("no_unacceptable_stutter_or_rubberbanding") is True
            and p.get("PS5_walkthrough_completed") is True
            and rpt in ("NO_LOG_ACCESS","REVIEWED_NO_MARKER")
            and (rpt=="NO_LOG_ACCESS" or nonempty(p.get("rpt_private_triage_reference")))
            and p.get("manual_review_decision")=="APPROVED_FOR_NEXT_PHASE"
            and nonempty(p.get("manual_review_reference"))
        )
        phase_results.append({
            "phase":p["phase"],
            "expected_count":p["expected_cumulative_count"],
            "filled_object_evidence_count":valid_items,
            "rpt_documented_failure_present":reported_failure,
            "phase_evidence_satisfies_manual_review_fields":complete,
            "status":"REVIEW_PACKET_PRESENT_UNAUTHENTICATED" if complete
                     else "BLOCKED_MISSING_EVIDENCE_OR_PREVIOUS_PHASE"
        })
        earlier_passed=complete
    all_fields=initial_ok and all(p["phase_evidence_satisfies_manual_review_fields"] for p in phase_results)
    return {
        "stage":"4.13",
        "status":"REVIEW_PACKET_COMPLETE_BUT_UNAUTHENTICATED" if all_fields
                 else "BLOCKED_NO_VERIFIABLE_FULL_PILOT_EVIDENCE",
        "preflight_fields_complete":initial_ok,
        "phases":phase_results,
        "reported_PS4_test_status_only":packet.get("playstation_4_compatibility_confirmed"),
        "PS4_runtime_independently_verified":False,
        "PS5_runtime_independently_verified":False,
        "user_supplied_evidence_is_NOT_independently_authenticated":True,
        "success_is_NOT_automatically_certified_from_attestation":True,
        "Nitrado_backup_existence_NOT_verified_by_this_script":True,
        "rollback_can_NOT_be_guaranteed_by_this_script":True,
        "release_allowed":False,
        "object_spawner_generated":False,
        "automatic_deployment_allowed":False,
        "notes":[
            "Do not trust a self-completed or synthetic evidence packet as independent proof of a DayZ runtime test.",
            "Provider console full backups are automatic and must be actually available before modifications.",
            "No RPT access is an explicitly recorded limitation, not evidence of successful object spawning.",
            "Actual PS4 and PS5 compatibility needs separate observations on each platform.",
            "No server files, private player data, passwords, IP addresses, or video URLs are reproduced in this summary."
        ]
    }

def run(input_path:Path|None,output_path:Path)->dict:
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    source=(json.loads(input_path.read_text(encoding="utf-8")) if input_path else blank_packet(protocol,pilot))
    report=audit(source,protocol,pilot)
    if input_path is not None:
        try:output_path.resolve().relative_to(ROOT.resolve())
        except ValueError:pass
        else:raise ValueError("Private test results cannot be written inside public repository")
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Stage 4.13: {report['status']}. No real console tests performed by the tool.")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,help="private, user-supplied completed JSON; never commit it")
    parser.add_argument("--output",type=Path,help="private output dir if --input is used")
    args=parser.parse_args()
    if args.input and not args.output:parser.error("Private input needs --output outside the repository")
    run(args.input,args.output or REPORT)
