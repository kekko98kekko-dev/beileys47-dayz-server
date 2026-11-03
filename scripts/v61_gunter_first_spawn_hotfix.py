#!/usr/bin/env python3
"""V61 Gunter recovery: correct V59 initial 365-day restock to 0 and restart ONCE.

For BEILEYS47 DayZ PS5 Livonia. This is NOT an instant vehicle command;
the DayZ Central Economy may still defer or reject placement. No world wipe,
no persistent player/vehicle data modification, no deletion of other vehicles.
"""
from __future__ import annotations
import datetime as dt
import hashlib,json,os,posixpath,sys,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,call_api,NitradoError
from deploy_beileys47_v15 import upload_file,game_state,game_status,players,request_api_post,wait_status
from v36_nitrado_backups_readonly import analyze
from v53_gunter_gift import parse,data

EVENT="VehicleBEILEYS47GunterRescueV59"
CAR="Hatchback_02_Black"
X,Z=8933.20,7211.91
E="db/events.xml"
P="cfgeventspawns.xml"
S="cfgspawnabletypes.xml"
OUT=Path("deploy/v61/GUNTER_HOTFIX_RESULT.json")
BACK=Path("deploy/v61/PRIVATE_ORIGINAL_EVENTS_XML.zip")
def must(check,why):
    if not check:raise NitradoError(why)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def report(**info):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    obj=dict(release="V61_GUNTER_FIRST_BOOT_RESTOCK_FIX",event=EVENT,
             target_x=X,target_z=Z,world_wipe=False,
             player_persistence_modified=False,
             car_physically_verified=False,
             filled_tank_verified=False,filled_radiator_verified=False,**info)
    OUT.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V61 STATUS",info.get("status"),flush=True)
def backup(blob):
    BACK.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACK,"w",zipfile.ZIP_DEFLATED) as f:
        f.writestr("dayzOffline.enoch/"+E,blob)
        f.writestr("SHA256.txt",sha(blob)+"  "+E+"\n")
    with zipfile.ZipFile(BACK) as f:
        must(f.testzip() is None and sha(f.read("dayzOffline.enoch/"+E))==sha(blob),
             "Pre-edit backup failed integrity check")
def validate(event_blob,pos_blob,profile_blob):
    ev=parse(event_blob).find(f"event[@name='{EVENT}']")
    must(ev is not None,"V59 event not present; refuse to create duplicates")
    must(ev.findtext("active")=="1" and ev.findtext("position")=="fixed",
         "Unexpected V59 event status")
    must(all(ev.findtext(k)=="1" for k in ("nominal","min","max")),
         "Expected exactly one V59 event")
    must([x.get("type") for x in ev.findall("./children/child")]==[CAR],
         "Unexpected vehicle class")
    pe=parse(pos_blob).find(f"event[@name='{EVENT}']")
    must(pe is not None and len(pe.findall("pos"))==1,"Missing unique target location")
    pos=pe.find("pos")
    must(all(abs(float(pos.get(k))-v)<0.01 for k,v in (("x",X),("z",Z))),
         "Target location changed by administrator")
    sp=parse(profile_blob).find(f"type[@name='{CAR}']")
    must(sp is not None,"Gunter 2 classname profile absent")
    cargo=[x.get("name") for x in sp.findall("./cargo/item")]
    must("AKM" in cargo and cargo.count("Mag_AKM_Drum75Rnd")>=2,
         "V59 75-round loadout not present")
    return ev
def patch(event_blob,pos_blob,profile_blob):
    old=validate(event_blob,pos_blob,profile_blob)
    must(old.findtext("restock") in ("31536000","0"),"Unexpected restock config")
    if old.findtext("restock")=="0" and old.findtext("distanceradius")=="0":
        return event_blob,True
    root=parse(event_blob)
    ev=root.find(f"event[@name='{EVENT}']")
    ev.find("restock").text="0"
    ev.find("saferadius").text="0"
    ev.find("distanceradius").text="0"
    ev.find("cleanupradius").text="100"
    new=data(root)
    validate(new,pos_blob,profile_blob)
    must(parse(new).find(f"event[@name='{EVENT}']").findtext("restock")=="0",
         "Zero restock not applied")
    # Verify no unrelated CE event changes.
    a=parse(event_blob); b=parse(new)
    a.remove(a.find(f"event[@name='{EVENT}']"))
    b.remove(b.find(f"event[@name='{EVENT}']"))
    import xml.etree.ElementTree as ET
    must(ET.tostring(a)==ET.tostring(b),"Other CE event changed")
    return new,False
def status(token):
    a=game_state(token)
    return game_status(a),players(a)
def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=55)
def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=55)
def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    must(token and os.getenv("BEILEYS47_V61_RESCUE_APPROVED")=="yes",
         "Nitrado token or owner restart approval missing")
    mission=resolve_mission(token)
    paths={p:posixpath.join(mission,p) for p in (E,P,S)}
    originals={p:download_one(token,paths[p]) for p in paths}
    new,already=patch(originals[E],originals[P],originals[S])
    # If already patched on disk still restart once (unless the runtime state is unknown).
    backup(originals[E])
    provider=analyze(call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
                     call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    must(provider["provider_backup_exists"] and provider["restore_possible"] is True,
         "Verified Nitrado backup prerequisite missing")
    st,online=status(token)
    must(st in ("started","running"),"Server not running, stop rather than change it")
    report(status="READY_BACKUP_CONFIRMED",players_before_restart=online,
           provider_backup_count=provider["backup_count"],already_zero_restock=already)
    stopped=False
    touched=False
    try:
        stop(token); stopped=True
        must(all(sha(download_one(token,paths[p]))==sha(originals[p]) for p in paths),
             "Unexpected concurrent admin changes before upload")
        if not already:
            touched=True
            upload_file(token,paths[E],new)
            must(sha(download_one(token,paths[E]))==sha(new),"Upload hash mismatch")
        must(sha(download_one(token,paths[P]))==sha(originals[P]) and
             sha(download_one(token,paths[S]))==sha(originals[S]),
             "Unexpected location or inventory file mutation")
        validate(download_one(token,paths[E]),originals[P],originals[S])
        start(token);stopped=False
        must(sha(download_one(token,paths[E]))==sha(new),
             "Events.xml changed after reboot")
        st2,online2=status(token)
        must(st2 in ("started","running"),"Server not running after restart")
        report(status="RESTART_COMPLETE_ZERO_RESTOCK_ACTIVE",
               players_before_restart=online,players_after_restart=online2,
               provider_backup_count=provider["backup_count"],
               configured_one_vehicle=True,restock_seconds=0,
               exact_position_verified_in_xml=True,loadout_verified_in_xml=True,
               requires_PS5_physical_check=True,
               note="DayZ CE may still refuse materialization (terrain, persisted event state or nearby players); do not report physical presence without PS5 proof.")
        print("V61 RESTART COMPLETE. ONE CE EVENT ACTIVE. IN-GAME CAR NOT VERIFIED.",flush=True)
    except Exception:
        if touched:
            try:
                current,_=status(token)
                if current in ("started","running"):
                    stop(token);stopped=True
                else:must(current=="stopped","Rollback unsafe unknown server status")
                now=download_one(token,paths[E])
                must(sha(now) in (sha(new),sha(originals[E])),
                     "Concurrent admin change; do not overwrite unknown edits")
                if sha(now)!=sha(originals[E]):
                    upload_file(token,paths[E],originals[E])
                    must(sha(download_one(token,paths[E]))==sha(originals[E]),
                         "Rollback mismatch")
                report(status="ROLLED_BACK_ON_ERROR")
            except Exception as e:
                report(status="MANUAL_REPAIR_REQUIRED",
                       error_type=type(e).__name__)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:
                print("CRITICAL: Could not verify server resumed",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as ex:
        print("V61 ERROR",type(ex).__name__,str(ex)[:210],file=sys.stderr)
        if not OUT.exists():report(status="FAILED_BEFORE_CHANGES")
        raise SystemExit(1)
