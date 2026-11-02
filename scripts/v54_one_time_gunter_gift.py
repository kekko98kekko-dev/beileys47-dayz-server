#!/usr/bin/env python3
"""V54 single-use Gunter gift: arm CE once, restart, then DISARM on second restart.

No permanent vehicle-spawn event and no permanent global cargo changes.
Car should persist after CE event disabled IF vanilla CE materializes it;
actual in-game creation, radiator water and full petrol are NOT API-verifiable.
Fail closed with backup/rollback; no world wipe or persisted-data mutation.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import posixpath
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission, download_one, call_api, NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v36_nitrado_backups_readonly import analyze
from v53_gunter_gift import FILES,EVENT,CAR,CARGO,X,Z,patch,parse,data,patch_for_postread

OUT=Path("deploy/v54/ONE_TIME_GUNTER_RESULT.json")
BACKUP=Path("deploy/v54/PRIVATE_ORIGINAL_XML_BEFORE_GIFT.zip")
# A very long restock provides a further safeguard during the brief first arm.
RESTOCK_SECONDS=604800
# CE may need time after startup to materialize the fixed vehicle.
SETTLE_SECONDS=110

def require(ok,msg):
    if not ok:raise NitradoError(msg)

def sha(blob):return hashlib.sha256(blob).hexdigest()

def report(**data):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
        "version":"V54","kind":"ONE_TIME_VEHICLE_GIFT_NO_RECURRING_SPAWN",
        "vehicle":"Gunter 2 black","world_x":X,"world_z":Z,
        "gift_cargo":CARGO,
        "fuel_tank_full_confirmed":False,
        "coolant_filled_confirmed":False,
        "one_physical_vehicle_seen_PS5":False,
        "cargo_seen_PS5":False,"world_wipe":False,
        "player_storage_modified":False,"world_storage_modified":False,
        **data
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V54:",data.get("status"),flush=True)

def backup(original):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        for rel,b in original.items():z.writestr("dayzOffline.enoch/"+rel,b)
        z.writestr("SHA256.txt","".join(sha(b)+"  "+rel+"\n" for rel,b in original.items()))
    with zipfile.ZipFile(BACKUP) as z:
        require(z.testzip() is None,"Original XML rollback ZIP corrupt")
        for rel,b in original.items():
            require(sha(z.read("dayzOffline.enoch/"+rel))==sha(b),
                    "Backup checksum mismatch: "+rel)

def arm(original,live_types):
    edited,details=patch(original,live_types)
    require(edited is not None,"V53 already exists; refuse duplicate gift")
    root=parse(edited[FILES[0]])
    ev=root.find(f"event[@name='{EVENT}']")
    require(ev is not None,"Arm event missing")
    ev.find("restock").text=str(RESTOCK_SECONDS)
    ev.find("saferadius").text="0"
    edited[FILES[0]]=data(root)
    valid,check=patch_for_postread(edited)
    require(valid and check["cargo_counts"]==CARGO,
            "Armed event or cargo preset failed offline check")
    return edited,details

def disarm(armed,original):
    # Preserve event name and physical point as an *inactive* definition.
    # Do not touch another event or any persistence files.
    root=parse(armed[FILES[0]])
    ev=root.find(f"event[@name='{EVENT}']")
    require(ev is not None and ev.findtext("active")=="1",
            "Unrecognised live gift event")
    require(ev.findtext("restock")==str(RESTOCK_SECONDS),
            "Gift event was edited by another administrator")
    for key in ("nominal","min","max","active"):ev.find(key).text="0"
    new=dict(armed)
    new[FILES[0]]=data(root)
    new[FILES[2]]=original[FILES[2]] # Fully revert temporary global black-Gunter loadout.
    e=parse(new[FILES[0]]).find(f"event[@name='{EVENT}']")
    require(all(e.findtext(k)=="0" for k in ("nominal","min","max","active")),
            "Gift source not disabled")
    require(new[FILES[1]]==armed[FILES[1]],"Spawn positions changed during disarm")
    require(new[FILES[2]]==original[FILES[2]],"Original Gunter profile not restored")
    return new

def server(token):
    v=game_state(token)
    return game_status(v),players(v)

def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=55)

def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=55)

def restore_if_possible(token,remote,expected,original,modified,was_running):
    # Caller invokes this ONLY after an error. Refuse to overwrite concurrent edits.
    status,count=server(token)
    if status in ("started","running"):
        require(type(count) is int and count==0,
                "Players joined: automatic rollback not safe")
        stop(token)
    else:require(status=="stopped","Unknown server state, no rollback")
    for rel in reversed(FILES):
        remote_now=download_one(token,remote[rel])
        require(sha(remote_now) in ({sha(original[rel])}|{
            sha(v[rel]) for v in expected if v is not None}),
            "Concurrent edit in "+rel+"; refuse overwrite")
        if sha(remote_now)!=sha(original[rel]):
            upload_file(token,remote[rel],original[rel])
            require(sha(download_one(token,remote[rel]))==sha(original[rel]),
                    "Rollback hash mismatch "+rel)
    if was_running:start(token)

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    require(token and os.environ.get("BEILEYS47_V54_APPROVED")=="yes",
            "Missing authorised Nitrado token")
    mission=resolve_mission(token)
    remote={p:posixpath.join(mission,p) for p in FILES}
    original={p:download_one(token,remote[p]) for p in FILES}
    live_types=parse(download_one(token,posixpath.join(mission,"db/types.xml")))
    armed,details=arm(original,live_types)
    stopped={"attempted":False}
    # Backups must exist before editing any Nitrado file.
    backup(original)
    provider=analyze(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    require(provider["provider_backup_exists"] and provider["restore_possible"] is True,
            "Nitrado provider backups not confirmed")
    state,n=server(token)
    if state not in ("started","running") or type(n) is not int or n!=0:
        report(status="BLOCKED_NEEDS_EMPTY_RUNNING_SERVER_NO_CHANGES",
               server_status=state,players=n,**details)
        return
    time.sleep(2)
    state2,n2=server(token)
    require(state2==state and type(n2) is int and n2==0,
            "New players appeared; no changes")
    report(status="BACKUP_READY_PRE_ARM",
           provider_backup_records=provider["backup_count"],**details)
    last=[None]
    stopped_now=False
    did_restart=False
    phase="NOT_STARTED"
    try:
        stop(token)
        stopped_now=True
        phase="STOPPED_FOR_ARM"
        for rel in FILES:
            require(sha(download_one(token,remote[rel]))==sha(original[rel]),
                    "Concurrent edit before arm "+rel)
        for rel in FILES:
            stopped["attempted"]=True
            upload_file(token,remote[rel],armed[rel])
            require(sha(download_one(token,remote[rel]))==sha(armed[rel]),
                    "Arm readback failed "+rel)
        last.append(armed)
        phase="ARMED_CONFIG"
        start(token)
        stopped_now=False
        did_restart=True
        phase="ARMED_SERVER_RESTARTED"
        require(all(sha(download_one(token,remote[r]))==sha(armed[r]) for r in FILES),
                "Armed profile drift after restart")
        report(status="FIRST_BOOT_ARMED_ONE_TIME_GIFT",
               note="Not proof vehicle appeared; preparing automatic disarm",
               provider_backup_records=provider["backup_count"])
        # No blind long-lived CE vehicle event. Disarm in this same workflow.
        time.sleep(SETTLE_SECONDS)
        now,n=server(token)
        require(now in ("started","running"),"Server not running after gift boot")
        if type(n) is not int or n!=0:
            report(status="IMPORTANT_DISARM_BLOCKED_BY_CONNECTED_PLAYERS",
                   players=n,server_status=now,
                   restock_delay_seconds=RESTOCK_SECONDS,
                   note="Event still armed: must disarm at next empty-server window")
            return
        # Confirm no admin edited the XML during the settlement period.
        for rel in FILES:
            require(sha(download_one(token,remote[rel]))==sha(armed[rel]),
                    "Concurrent edit during gift spawn window: "+rel)
        disabled=disarm(armed,original)
        stop(token)
        stopped_now=True
        phase="STOPPED_FOR_DISARM"
        for rel in FILES:
            require(sha(download_one(token,remote[rel]))==sha(armed[rel]),
                    "Concurrent edit just before disarm "+rel)
        for rel in (FILES[0],FILES[2]):
            upload_file(token,remote[rel],disabled[rel])
            require(sha(download_one(token,remote[rel]))==sha(disabled[rel]),
                    "Disarm write/readback failed "+rel)
        last.append(disabled)
        phase="DISARM_CONFIG_WRITTEN"
        start(token)
        stopped_now=False
        phase="FULLY_DISARMED_RESTARTED"
        for rel in FILES:
            require(sha(download_one(token,remote[rel]))==sha(disabled[rel]),
                    "Final one-time gift state readback failed "+rel)
        ev=parse(download_one(token,remote[FILES[0]])).find(f"event[@name='{EVENT}']")
        require(ev is not None and all(ev.findtext(k)=="0" for k in
               ("nominal","min","max","active")),"Car gift event still active")
        report(status="ONE_TIME_EVENT_DISARMED_POST_RESTART_VERIFIED",
               active_gift_event=False,
               long_term_gunter_class_loadout_restored=True,
               one_time_ce_spawn_requested=True,
               physical_car_exists_unknown=True,
               final_server_status=server(token)[0],
               provider_backup_records=provider["backup_count"])
        print("V54 SUCCESS: one temporary CE spawn attempt made, then EVENT DISABLED, no recurring fixed vehicle source.",flush=True)
    except Exception as error:
        if stopped["attempted"] and phase not in ("FULLY_DISARMED_RESTARTED",):
            try:
                # Rollback only from known pre-run, armed, or disabled bytes.
                restore_if_possible(token,remote,last,original,
                                    stopped,was_running=True)
                stopped_now=False
                report(status="ROLLED_BACK_AFTER_FAILURE",
                       last_phase=phase,error_type=type(error).__name__)
            except Exception as rescue:
                report(status="CRITICAL_MANUAL_REVIEW_REQUIRED",
                       last_phase=phase,error_type=type(error).__name__,
                       restore_error=type(rescue).__name__)
        raise
    finally:
        if stopped_now:
            try:start(token)
            except Exception:print("CRITICAL: cannot verify server restart",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V54 ERROR",type(e).__name__,str(e)[:190],file=sys.stderr)
        if not OUT.exists():report(status="FAILED_PRE_EDIT")
        raise SystemExit(1)
