#!/usr/bin/env python3
"""Import a PC DayZ SurfaceY diagnostic log into Stage 4.5 capture JSON.

Logs are USER-SUPPLIED and cannot authenticate source. Reject duplicates,
missing points, shifted positions or malformed heights. No deployment.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from audit_stage4_height_samples import ROOT, analyze

OUT=ROOT/"dist/stage4_height_capture"
LOG_LINE=re.compile(
    r"Z47_ALT\|(GRID|PROP)\|([A-Za-z0-9_-]+)\|([0-9.]+)\|([0-9.]+)\|([-+]?[0-9]+(?:\.[0-9]+)?)"
)

def convert(log:Path,template:Path,output:Path,game_build:str,utc:str,evidence:str)->dict:
    data=json.loads(template.read_text(encoding="utf-8"))
    ref=json.loads((ROOT/"dist/stage4_terrain_survey/terrain_survey_grid.json").read_text(encoding="utf-8"))
    expect={(p["kind"],p["id"]):p for p in data["points"]}
    seen={}
    for line in log.read_text(encoding="utf-8",errors="replace").splitlines():
        matches=list(LOG_LINE.finditer(line))
        if len(matches)>1:raise ValueError("Invalid log line: multiple sample records")
        if not matches:continue
        match=matches[0]
        kind,sid,x,z,y=match.groups()
        key=(kind,sid)
        if key not in expect:raise ValueError("Unknown logged point "+str(key))
        if key in seen:raise ValueError("Duplicate logged point "+str(key))
        px,pz=expect[key]["x"],expect[key]["z"]
        if abs(float(x)-px)>=0.01 or abs(float(z)-pz)>=0.01:
            raise ValueError("Coordinate mismatch "+str(key))
        seen[key]=float(y)
    if len(seen)!=len(expect):
        raise ValueError(f"Incomplete capture: {len(seen)} of {len(expect)} terrain points")
    data["status"]="USER_SUPPLIED_SURFACEY_LOG_UNVERIFIED"
    data["measurement"].update({
        "method":"DayZ_CGame_SurfaceY",
        "dayz_game_build":game_build,
        "captured_utc":utc,
        "evidence_reference":evidence
    })
    for p in data["points"]:
        p["ground_y"]=seen[(p["kind"],p["id"])]
    report=analyze(data,ref,data["region"])
    if report["provided_y_count"]!=182 or not report["provenance_complete"]:
        raise ValueError("Measurement report lacks values or provenance")
    if report["status"]=="BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE":
        raise ValueError("Height audit remains blocked")
    if output.resolve()==template.resolve():
        raise ValueError("Never overwrite original blank template")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Parsed {len(seen)} user-supplied SurfaceY measurements into {output}")
    print("WARNING: not independently authenticated; run height audit; never deploy this file.")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--template",type=Path,default=OUT/"central_surfaceY_empty.json")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--game-build",required=True)
    p.add_argument("--captured-utc",required=True)
    p.add_argument("--evidence",required=True)
    v=p.parse_args()
    convert(v.log,v.template,v.output,v.game_build,v.captured_utc,v.evidence)
