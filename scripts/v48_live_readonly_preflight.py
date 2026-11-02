#!/usr/bin/env python3
"""V48 one-off GET-only preflight of LIVE DayZ building config (no edits)."""
from __future__ import annotations
import hashlib,json,os,posixpath,sys
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
from v20_unlimited_sprint import setting_state
from v48_build_anywhere_preview import apply_preview,BALANCED
OUT=Path("deploy/v48/LIVE_PREFLIGHT.json")
def save(**k):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"stage":"V48","mode":"GET_ONLY","any_remote_changes":False,**k},indent=2)+"\n",encoding="utf-8")
def h(b): return hashlib.sha256(b).hexdigest()
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token: raise NitradoError("Missing API secret")
    mission=resolve_mission(token)
    live=download_one(token,posixpath.join(mission,"cfggameplay.json"))
    candidate,changes=apply_preview(live,"balanced")
    gs=game_state(token)
    state=game_status(gs); count=players(gs); enabled=setting_state(gs)
    data=json.loads(live)
    old_sections={s:data.get(s) for s in ("GeneralData","PlayerData","WorldsData","UIData","MapData","VehicleData")}
    out=json.loads(candidate)
    if not all(out.get(s)==v for s,v in old_sections.items()):
        raise NitradoError("Unexpected edits outside BaseBuildingData")
    flagged={f"{s}.{k}":data["BaseBuildingData"][s][k] for s,k in sorted(BALANCED)}
    save(status="READY_FOR_CONTROLLED_INSTALL" if state in ("started","running") and count==0 and enabled=="enabled" else "NOT_READY",
         server_status=state,players_online=count,gameplay_setting=enabled,
         gameplay_sha256=h(live),candidate_sha256=h(candidate),original_bytes=len(live),
         selected_current_flags=flagged,keys_to_change=changes,
         guaranteed_non_target_sections_unchanged=True,
         v46_types_xml_touched=False,
         world_wipe=False,ps5_building_tested=False)
    print("V48 read-only preflight completed. status:",state,"players:",count,"gameplay:",enabled,
          "flags-to-change:",len(changes),"original sha:",h(live),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        save(status="ERROR_NO_CHANGES",exception=type(exc).__name__)
        print("V48 READONLY ERROR",type(exc).__name__,str(exc)[:120],file=sys.stderr)
        raise SystemExit(1)
