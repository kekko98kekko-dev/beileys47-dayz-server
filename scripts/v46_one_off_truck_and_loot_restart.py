#!/usr/bin/env python3
"""BEILEYS47 V46: one owner-authorized restart for V44 M3S + V45 cleanup.

Uses reviewed validated patch functions and only mission configuration files.
One player may be disconnected by owner consent in THIS ONE-TIME push job.
The hourly V44/V45 retries still refuse to interrupt connected players.
"""
from __future__ import annotations
import hashlib,json,os,posixpath,sys,time,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v44_single_original_dolnik_truck import (
    FILES as TRUCK_FILES,build as truck_build,installed as truck_installed,parse as xmlparse)
from v45_safe_loot_ttl import patch as cleanup_patch
FILES=(*TRUCK_FILES,"db/types.xml")
OUT=Path("deploy/v46/ONE_RESTART_FINAL_RESULT.json")
BACKUP=Path("deploy/v46/PRIVATE_ALL_ORIGINAL_XML.zip")
def require(ok,msg):
 if not ok:raise NitradoError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def save_report(**data):
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({"version":"V46","one_time_owner_approval":True,
    "ground_loot_counter_based_on_restarts":False,"global_world_wipe":False,
    "player_storage_touched":False,
    "two_old_persistent_vehicle_instances_deletion_verified":False,
    "real_console_truck_fuel_and_inventory_verified":False,**data},indent=2)+"\n")
def can_restart(status,old_count,new_count):
 if status=="stopped":return True
 if status not in ("started","running"):return False
 return (type(old_count) is int and type(new_count) is int and
         0<=new_count<=old_count<=1)
def backup(files):
 BACKUP.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
    for path,blob in files.items():z.writestr("dayzOffline.enoch/"+path,blob)
    z.writestr("SHA256.txt","".join(sha(v)+" "+k+"\n" for k,v in files.items()))
 with zipfile.ZipFile(BACKUP) as z:
    require(z.testzip() is None,"Cannot trust original XML backup")
    for path,blob in files.items():
        require(sha(z.read("dayzOffline.enoch/"+path))==sha(blob),
                "Original backup hash mismatch "+path)
def main():
 token=os.environ.get("NITRADO_API_TOKEN","").strip()
 require(token and os.environ.get("BEILEYS47_V46_ONE_OFF")=="yes" and
     os.environ.get("GITHUB_EVENT_NAME")=="push",
     "This is owner-approved ONE-TIME push-only maintenance, not recurring")
 mission=resolve_mission(token)
 remote={p:posixpath.join(mission,p) for p in FILES}
 original={p:download_one(token,remote[p]) for p in FILES}
 modified={};truck_details=None
 if not truck_installed(original):
    patch,truck_details=truck_build(
       {p:original[p] for p in TRUCK_FILES},xmlparse(original["db/types.xml"]))
    modified.update(patch)
 ttl_mod,items=cleanup_patch(original["db/types.xml"])
 if items:modified["db/types.xml"]=ttl_mod
 if not modified:
    save_report(status="BOTH_ALREADY_CONFIGURED_NO_RESTART",
      ordinary_loot_types_changed=0,no_new_truck_event=False,
      no_restart=True)
    print("V46 ALREADY READY, no restart")
    return
 backup(original)
 now=game_state(token);status=game_status(now);players_before=players(now)
 if not can_restart(status,players_before,players_before):
    save_report(status="BLOCKED_MULTIPLE_OR_UNKNOWN_PLAYERS",
      players=players_before,config_backup_created=True)
    print("V46 SAFE BLOCK: cannot disconnect more than 1 player")
    return
 time.sleep(2)
 nextstate=game_state(token)
 require(game_status(nextstate)==status and
         can_restart(status,players_before,players(nextstate)),
         "Player count grew or server status changed; don't disconnect")
 report_before={"previously_online":players_before,
    "files_to_write":list(modified),
    "ordinary_loot_types_changed":len(items),
    "new_truck_event_to_install":truck_details is not None,
    "truck_loadout_summary":truck_details}
 stopped=False;restarted=False;attempted=[];success=False
 try:
    if status!="stopped":
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
        wait_status(token,{"stopped"},attempts=55);stopped=True
    for p in FILES:
        require(sha(download_one(token,remote[p]))==sha(original[p]),
                "Mission changed during stop "+p)
    for p in modified:
        attempted.append(p)
        upload_file(token,remote[p],modified[p])
        require(sha(download_one(token,remote[p]))==sha(modified[p]),
                "Upload readback mismatch "+p)
    if status!="stopped":
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
        wait_status(token,{"started","running"},attempts=60);restarted=True
    for p in modified:
        require(sha(download_one(token,remote[p]))==sha(modified[p]),
                "Post-restart hash mismatch "+p)
    require(truck_installed({p:download_one(token,remote[p]) for p in TRUCK_FILES}),
            "New unique Dolnik spawn event missing")
    require(not cleanup_patch(download_one(token,remote["db/types.xml"]))[1],
            "New ground-loot lifetime settings not stable")
    success=True
    save_report(status="BOTH_CONFIGS_INSTALLED_NITRADO_VERIFIED",
        server_status=game_status(game_state(token)),
        old_dolnik_ce_events_disabled=True,new_dolnik_ce_event_at_original_site=True,
        **report_before)
    print("V46 LIVE SUCCESS: one Dolnik premium M3S CE + safe ordinary loot TTL after single restart; no world wipe.")
 except Exception:
    if attempted and not success:
       try:
          state=game_state(token)
          if game_status(state) in ("started","running"):
             require(players(state)==0,"New online player; no disruptive rollback")
             request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
             wait_status(token,{"stopped"},attempts=55);stopped=True
          for p in reversed(attempted):
             upload_file(token,remote[p],original[p])
             require(sha(download_one(token,remote[p]))==sha(original[p]),
                     "Original mission restoration failed "+p)
          save_report(status="ROLLED_BACK_CONFIGS",**report_before)
          if stopped:
             request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
             wait_status(token,{"started","running"},attempts=55)
             restarted=True
       except Exception:
          save_report(status="CRITICAL_MANUAL_RESTORE_REQUIRED",**report_before)
    raise
 finally:
    if stopped and not restarted:
       try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
       except Exception:print("CRITICAL: cannot confirm Nitrado restart")
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("V46 ERROR",type(e).__name__,str(e)[:220],file=sys.stderr)
  raise SystemExit(1)
