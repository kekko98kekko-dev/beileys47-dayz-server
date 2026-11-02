#!/usr/bin/env python3
"""V56: only change live gift Gunter CE event restock to safe int32 maximum.

Only mission/db/events.xml; preserve exact bytes everywhere else. No restart,
no world wipe and no mutation of persisted existing vehicle. Next restart may
read new value. A restock value is NOT a guarantee of never respawning.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import upload_file,game_state,game_status,players
from v53_gunter_gift import EVENT,CAR,X,Z
from v36_nitrado_backups_readonly import analyze
from nitrado_snapshot import call_api

REL="db/events.xml"
POS="cfgeventspawns.xml"
OLD=31536000
NEW=2147483647  # 68.05 years; 100y exceeds signed int32 upper bound
OUT=Path("deploy/v56/GUNTER_RESTOCK_68Y_RESULT.json")
BACKUP=Path("deploy/v56/PRIVATE_ORIGINAL_EVENTS_XML.zip")

def ensure(cond,message):
    if not cond: raise NitradoError(message)

def digest(b):return hashlib.sha256(b).hexdigest()

def readxml(blob):
    return ET.fromstring(blob,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))

def write_report(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    result={
        "version":"V56","scope":"Gunter 2 one-gift restock only",
        "event":EVENT,"x":X,"z":Z,
        "old_restock_seconds":OLD,"new_restock_seconds":NEW,
        "new_restock_years_approx":round(NEW/31557600,4),
        "100_years_seconds":3153600000,
        "100_years_rejected_as_outside_signed_int32":True,
        "no_server_stop_or_restart":True,"world_wipe":False,
        "existing_persisted_gunter_edited":False,
        "physical_spawn_or_absolute_no_respawn_guarantee":False,
        "effective_in_server_runtime_after_next_normal_restart":"expected",
        **kw
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V56 STATUS",kw.get("status","UNKNOWN"),flush=True)

def verify_world_point(blobs):
    root=readxml(blobs)
    point=root.find(f"event[@name='{EVENT}']")
    ensure(point is not None,"Gift vehicle point disappeared")
    pts=point.findall("pos")
    ensure(len(pts)==1,"Gift vehicle spawn count is not one")
    p=pts[0]
    ensure(abs(float(p.get("x"))-X)<0.005 and abs(float(p.get("z"))-Z)<0.005,
           "Vehicle location drifted")

def inspected_event(blob):
    doc=readxml(blob)
    matching=doc.findall(f"event[@name='{EVENT}']")
    ensure(len(matching)==1,"Exactly one Gunter gift event required")
    ev=matching[0]
    ensure(ev.findtext("active")=="1", "Gunter gift event not active")
    ensure(all(ev.findtext(k)=="1" for k in ("nominal","min","max")),
           "One-car nominal/min/max guard mismatch")
    ensure([item.get("type") for item in ev.findall("./children/child")]==[CAR],
           "Gunter gift class changed")
    ensure(ev.findtext("position")=="fixed","Gift fixed spawn guard mismatch")
    return ev

def patch(blob,position_blob):
    verify_world_point(position_blob)
    current=inspected_event(blob)
    current_restock=current.findtext("restock")
    if current_restock==str(NEW):
        return blob,True
    ensure(current_restock==str(OLD),
           "Live restock is not V55 expected value; refuse to overwrite")
    pattern=rb'<event\s+name="VehicleBEILEYS47GunterGiftV53">.*?</event>'
    matches=list(re.finditer(pattern,blob,flags=re.DOTALL))
    ensure(len(matches)==1,"Expected single byte-identical V55 event block")
    start,end=matches[0].span()
    block=blob[start:end]
    o=b"<restock>"+str(OLD).encode()+b"</restock>"
    n=b"<restock>"+str(NEW).encode()+b"</restock>"
    ensure(block.count(o)==1,"Cannot isolate one exact restock tag")
    updated=blob[:start]+block.replace(o,n,1)+blob[end:]
    verify=inspected_event(updated)
    ensure(verify.findtext("restock")==str(NEW),
           "Maximum safe restock validation failed")
    ensure(updated.replace(n,o,1)==blob,
           "Unexpected byte changes outside target event restock")
    return updated,False

def make_backup(blob):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/"+REL,blob)
        z.writestr("SHA256.txt",digest(blob)+"  "+REL+"\n")
    with zipfile.ZipFile(BACKUP) as z:
        ensure(z.testzip() is None and
               digest(z.read("dayzOffline.enoch/"+REL))==digest(blob),
               "Private original XML zip corrupted")

def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    ensure(bool(token) and os.getenv("BEILEYS47_V56_APPROVED")=="yes",
           "Missing Nitrado token or owner V56 approval")
    mission=resolve_mission(token)
    events_remote=posixpath.join(mission,REL)
    pos_remote=posixpath.join(mission,POS)
    before=download_one(token,events_remote)
    positions=download_one(token,pos_remote)
    changed,already=patch(before,positions)
    if already:
        write_report(status="ALREADY_MAX_SAFE_RESTOCK_NO_ACTION")
        return
    make_backup(before)
    # Provider backup is required; changing live config without restarting.
    info=analyze(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    ensure(info["provider_backup_exists"] and info["restore_possible"] is True,
           "Nitrado backup verification failed; refuse update")
    state=game_state(token)
    status=game_status(state)
    ensure(status in ("started","running"),
           "Game is not running: refuse surprise startup")
    nplayers=players(state)
    # New file is only staged for next planned restart; don't interrupt players.
    ensure(digest(download_one(token,events_remote))==digest(before),
           "Another admin edited XML concurrently")
    write_report(status="PRIVATE_BACKUP_VERIFIED_PRE_UPLOAD",
                 players_online=nplayers,server_status=status,
                 provider_backup_count=info["backup_count"])
    touched=False
    try:
        touched=True
        upload_file(token,events_remote,changed)
        ensure(digest(download_one(token,events_remote))==digest(changed),
               "Nitrado uploaded XML bytes did not match")
        reloaded=download_one(token,events_remote)
        final,already=patch(reloaded,positions)
        ensure(already,"Updated max safe restock not present on server")
        ensure(game_status(game_state(token)) in ("started","running"),
               "Server unexpected state after no-restart file upload")
        write_report(status="STAGED_68Y_MAX_SAFE_RESTOCK_NO_RESTART",
                     xml_readback_verified=True,
                     only_changed_file=REL,
                     player_disconnect=False,
                     players_prior=nplayers,
                     provider_backup_count=info["backup_count"])
        print("V56 SUCCESS: Gunter restock=2147483647 staged, no stop/restart, existing car untouched.",flush=True)
    except Exception:
        if touched:
            try:
                now=download_one(token,events_remote)
                ensure(digest(now) in {digest(changed),digest(before)},
                       "Concurrent modification; manual review instead of rollback")
                if digest(now)==digest(changed):
                    upload_file(token,events_remote,before)
                    ensure(digest(download_one(token,events_remote))==digest(before),
                           "Rollback failed to restore original events.xml")
                write_report(status="ROLLED_BACK_AFTER_UPLOAD_FAILURE")
            except Exception as rescue:
                write_report(status="CRITICAL_MANUAL_REVIEW_REQUIRED",
                             rescue_error_type=type(rescue).__name__)
        raise

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V56 ERROR",type(exc).__name__,str(exc)[:190],file=sys.stderr)
        if not OUT.exists():write_report(status="FAILED_BEFORE_SERVER_UPLOAD")
        raise SystemExit(1)
