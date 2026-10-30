#!/usr/bin/env python3
"""Stage 4.12: offline RPT Object Spawner diagnostic triage, privacy first.

Bohemia documents RPT phrase "Object spawner failed to spawn" when a
specified class/P3D does not exist. Parsing CAN detect errors but absence of
errors is NEVER proof that an object spawned or works on PS4/PS5.

No live Nitrado connection, no upload, no log contents in the public report.
CLI only accepts a PRIVATE local RPT path. CI publishes an EMPTY report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/stage4_asset_candidates.json"
OUTPUT=ROOT/"dist/stage4_12_rpt_diagnostics/rpt_triage_no_logs.json"
MAX_BYTES=25_000_000
MAX_LINES=200_000
OFFICIAL_ERROR=re.compile(r"object\s+spawner\s+failed\s+to\s+spawn",re.I)
# These are heuristic warnings, NOT exact messages documented by Bohemia.
HINTS={
    "OBJECT_SPAWNER_REFERENCE":re.compile(r"objectSpawnersArr",re.I),
    "CFG_GAMEPLAY_REFERENCE":re.compile(r"cfgGameplay(?:\.json|File)?",re.I),
    "MISSING_FILE_HINT":re.compile(r"(?:no such file|file not found|cannot open|can't open)",re.I),
}
PROVENANCE="https://community.bistudio.com/wiki/DayZ:Object_Spawner"

def known_candidates()->list[str]:
    data=json.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["status"]=="CANDIDATE_CLASS_NAMES_ONLY_NOT_RUNTIME_VERIFIED"
    assert data["pinned_commit"]=="f220b2918b1d79a5055b1ee9be70c0ec1516e876"
    names=sorted(m["name"] for m in data["models"])
    assert len(names)==13 and len(set(names))==13
    assert all(re.fullmatch(r"Land_[A-Za-z0-9_]{3,100}",name) for name in names)
    assert all(m["object_spawner_confirmed"] is False and m["ps4_ps5_runtime_confirmed"] is False for m in data["models"])
    return names

def analyze_lines(lines:list[str],names:list[str],evidence_kind:str)->dict:
    """Only aggregate counts, source-known IDs, diagnostic codes and line numbers.

    DO NOT copy log text; it may contain player IDs, IPs, coordinates and chat.
    """
    if evidence_kind not in ("NO_LOG_PROVIDED","USER_SUPPLIED_PRIVATE_RPT"):
        raise ValueError("invalid evidence kind")
    if evidence_kind=="NO_LOG_PROVIDED" and lines:
        raise ValueError("Unprovided log cannot contain events")
    if len(lines)>MAX_LINES:
        raise ValueError("RPT too large: cap line count")
    matchers={name:re.compile(r"(?<![A-Za-z0-9_])"+re.escape(name)+r"(?![A-Za-z0-9_])",re.I)
              for name in names}
    official_count=0
    fail_unknown=0
    matches=Counter()
    # no raw user data; sanitizing by exclusion instead of redacting possible PII
    examples=[]
    hints=Counter()
    for number,line in enumerate(lines,1):
        if len(line)>200_000:raise ValueError("RPT line exceeds sanity cap")
        if OFFICIAL_ERROR.search(line):
            official_count+=1
            found=[name for name,rx in matchers.items() if rx.search(line)]
            for name in found:matches[name]+=1
            if not found:fail_unknown+=1
            if len(examples)<60:
                examples.append({
                    "line_number":number,
                    "diagnostic_code":"OBJECT_SPAWNER_FAILED_TO_SPAWN",
                    "source_known_candidate_mentions":found,
                    "class_on_line_not_unambiguously_extracted":len(found)!=1
                })
        # Hints cannot establish success, failure, or that a config loaded.
        for kind,rx in HINTS.items():
            if rx.search(line):hints[kind]+=1
    return {
       "stage":"4.12",
       "status":("NO_REAL_LOG_AVAILABLE" if evidence_kind=="NO_LOG_PROVIDED"
                 else "PRIVATE_RPT_TEXT_ANALYZED_OFFLINE_NOT_RUNTIME_VERIFIED"),
       "evidence_kind":evidence_kind,
       "official_failure_phrase": "Object spawner failed to spawn",
       "official_documentation":PROVENANCE,
       "inspected_line_count":len(lines),
       "official_object_spawner_failure_lines":official_count,
       "official_failure_lines_with_no_recognized_candidate":fail_unknown,
       "source_known_candidate_mentions_on_failure_lines":dict(sorted(matches.items())),
       "diagnostic_examples_NO_RAW_TEXT":examples,
       "heuristic_keyword_line_counts_NOT_ERRORS":dict(sorted(hints.items())),
       "known_name_count_from_pinned_CE_mapgrouppos":len(names),
       "known_names_are_NOT_certified_to_spawn":True,
       "missing_error_is_NOT_proof_of_success":True,
       "evidence_does_NOT_prove_PSN_gameplay_or_collision":True,
       "actual_successfully_spawned_objects_count":None,
       "candidate_console_spawnability_confirmed_count":0,
       "site_terrain_Y_verified":False,
       "PS4_PS5_runtime_approved":False,
       "deployment_allowed":False,
       "raw_log_contents_in_report":False,
       "limitations":[
           "Bohemia documents a precise RPT failure marker when an Object Spawner class or model path does not exist.",
           "Class names are recognized ONLY if printed on the same RPT line and belong to the 13 pinned Livonia map-group candidates.",
           "Zero failure lines can mean an empty/disabled spawner, incomplete log, wrong startup, or missing log coverage.",
           "Log output cannot verify physical object positions, collisions, model compatibility on a specific console or DayZ FPS.",
           "Keyword counts for cfgGameplay/objectSpawnersArr are context hints, not proof of any successful configuration.",
           "Store actual server logs privately; player names, IDs, IPs, and world locations must never be committed to GitHub."
       ]
    }

def analyze_file(path:Path,names:list[str])->dict:
    if not path.is_file() or path.stat().st_size>MAX_BYTES:
        raise ValueError("Missing or overlimit private RPT file")
    raw=path.read_bytes()
    if b"\x00" in raw:raise ValueError("Unsupported binary or UTF-16 RPT file")
    txt=raw.decode("utf-8",errors="replace")
    lines=txt.splitlines()
    return analyze_lines(lines,names,"USER_SUPPLIED_PRIVATE_RPT")

def run(input_path:Path|None,output_path:Path)->dict:
    names=known_candidates()
    report=(analyze_file(input_path,names) if input_path is not None
            else analyze_lines([],names,"NO_LOG_PROVIDED"))
    if input_path is not None:
        # Do not permit accidental upload of a real report under dist/ in a
        # public source tree. The user must use a private output directory.
        try:
            output_path.resolve().relative_to(ROOT.resolve())
        except ValueError:
            pass
        else:
            raise ValueError("Private log reports cannot be written into public repository tree")
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("STAGE 4.12: "+report["status"])
    print(f"Official spawner failure-marker lines: {report['official_object_spawner_failure_lines']}")
    print("No verified PS5 spawnability or Nitrado access. Raw lines never written.")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Offline privacy-safe DayZ Object Spawner RPT error triage")
    parser.add_argument("--log",type=Path,help="PRIVATE local RPT from user's DayZ server; never in Git")
    parser.add_argument("--output",type=Path,help="Output summary JSON OUTSIDE repository if --log is specified")
    args=parser.parse_args()
    if args.log is not None and args.output is None:
        parser.error("Real log requires explicit --output OUTSIDE repository")
    run(args.log,args.output if args.output is not None else OUTPUT)
