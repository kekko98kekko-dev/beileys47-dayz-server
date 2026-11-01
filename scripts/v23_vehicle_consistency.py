#!/usr/bin/env python3
"""Minimal V23 CE sanity fix. Exactly one events.xml numeric field, NO world resets."""
from __future__ import annotations
import hashlib,json,os,posixpath,re,sys,time,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
BASE="818b338e178851e0b765698bd7248fec7047926f53daf095a8218f76cdb2650b"
REL="db/events.xml"
OUT=Path("deploy/v23/RESULT.json")
BACKUP=Path("deploy/v23/private_events_before_v23.zip")
def digest(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok:raise NitradoError(msg)
def record(**kwargs):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"version":"V23","file":REL,
      "ps5_tested":False,"world_storage_untouched":True,"no_wipe_requested":True,**kwargs},indent=2)+"\n")
def patch(old):
    root=ET.fromstring(old)
    require(root.tag=="events","Expected events root")
    all_events=root.findall("event")
    motorbikes=[x for x in all_events if x.get("name")=="VehicleMotorbike"]
    require(len(motorbikes)==1,"Motorbike event missing or duplicated")
    moto=motorbikes[0]
    require((moto.findtext("nominal"),moto.findtext("min"),moto.findtext("max"))==("12","5","11"),
           "Live motorcycle target differed; refuse to override")
    # One typed XML element only. Keep full rest of file intact byte-for-byte.
    expr=rb'(<event\s+name=["\x27]VehicleMotorbike["\x27][^>]*>)(.*?)(</event>)'
    matches=list(re.finditer(expr,old,re.DOTALL))
    require(len(matches)==1,"Motorcycle raw element not uniquely matchable")
    m=matches[0];section=m.group(2)
    edited,count=re.subn(rb'<nominal>\s*12\s*</nominal>',b'<nominal>11</nominal>',section,count=1)
    require(count==1,"Motorcycle nominal not exactly patchable")
    new=old[:m.start(2)]+edited+old[m.end(2):]
    checked=ET.fromstring(new)
    reloaded=checked.find("event[@name='VehicleMotorbike']")
    require((reloaded.findtext("nominal"),reloaded.findtext("max"))==("11","11"),
            "Motorbike event verification mismatch")
    require(len(new)==len(old),"Unexpected byte-length change")
    return new
def save_original(old):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/db/events.xml",old)
        z.writestr("SHA256.txt",digest(old)+"  events.xml\n")
    with zipfile.ZipFile(BACKUP) as z:
        require(z.testzip() is None and digest(z.read("dayzOffline.enoch/db/events.xml"))==digest(old),
                "Rollback backup corrupt")
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    require(bool(token) and os.environ.get("BEILEYS47_V23_APPROVED")=="yes",
            "Approval or Nitrado secret unavailable")
    mission=resolve_mission(token)
    remote=posixpath.join(mission,REL)
    old=download_one(token,remote)
    if digest(old)!=BASE:
        record(status="blocked_source_drift",observed_sha=digest(old))
        raise NitradoError("Events file changed since V22 audit. Do not overwrite.")
    proposed=patch(old)
    save_original(old)
    state=game_state(token)
    s=game_status(state)
    p=players(state)
    if s not in {"started","running","stopped"} or (s!="stopped" and p!=0):
        record(status="blocked_players_or_status",player_count=p)
        raise NitradoError("Do not stop game server while player count is nonzero/unknown")
    time.sleep(2)
    again=game_state(token)
    require(game_status(again)==s and (s=="stopped" or players(again)==0),
            "Second player/state check failed")
    stopped=False;uploaded=False
    try:
        if s!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
            stopped=True
        require(digest(download_one(token,remote))==BASE,
                "Source changed after stop; refuse overwrite")
        upload_file(token,remote,proposed)
        uploaded=True
        require(digest(download_one(token,remote))==digest(proposed),
                "Upload readback hash mismatch")
        record(status="uploaded_verified_pending_start",old_sha=BASE,new_sha=digest(proposed))
    except Exception:
        if uploaded:
            try:
                upload_file(token,remote,old)
                require(digest(download_one(token,remote))==BASE,"Rollback hash mismatch")
                record(status="rolled_back_verified",old_sha=BASE)
            except Exception:
                record(status="manual_recovery_needed",old_sha=BASE)
        raise
    finally:
        if stopped:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:print("WARNING: normal restart failed; inspect Nitrado",flush=True)
    if stopped:wait_status(token,{"started","running"},attempts=50)
    require(digest(download_one(token,remote))==digest(proposed),"Post-start readback mismatch")
    record(status="installed_and_readback_verified",old_sha=BASE,new_sha=digest(proposed),
           server_status=game_status(game_state(token)),
           event_name="VehicleMotorbike",original_nominal=12,new_nominal=11,max=11)
    print("V23 SUCCESS: motorcycle event nominal11/max11, no wipe, no player storage change")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V23 BLOCKED/ERROR:",type(e).__name__,str(e)[:170],file=sys.stderr)
        raise SystemExit(1)
