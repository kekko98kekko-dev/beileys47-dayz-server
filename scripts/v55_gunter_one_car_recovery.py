#!/usr/bin/env python3
"""V55 recover the undelivered Gunter gift. No 110-second premature disable.

Important: This requests a CE instance; physical materialization can ONLY be
verified in-game. One event / one position / nominal=max=1. After the first
boot, stage a *365-day restock* for subsequent reboots (without a second restart).
A CE event is NOT an instant remote spawn command. Any future deactivation of
this event may remove already spawned vehicles; do not auto-disarm.
No deletion of persistence, player items, cars, or other spawn points.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, posixpath, sys, time, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,call_api,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v36_nitrado_backups_readonly import analyze
from v53_gunter_gift import EVENT, CAR, FILES, X, Z, YAW, patch,parse,data,patch_for_postread

OUT=Path("deploy/v55/GUNTER_DELIVERY_ATTEMPT.json")
BACKUP=Path("deploy/v55/PRIVATE_ORIGINAL_GUNTER_XML.zip")
LONG_RESTOCK=31536000

def must(condition,message):
    if not condition:raise NitradoError(message)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def write_status(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
       "release":"V55","purpose":"ONE CAR CE SPAWN REQUEST AFTER V54 PREMATURE DISARM",
       "x":X,"z":Z, "vehicle":CAR,
       "gameplay_car_physically_verified":False,
       "no_storage_wipe":True,"no_other_vehicle_source_changed":True,
       "no_player_storage_modified":True,
       "does_not_claim_filled_gas_tank_or_radiator":True,
       **kw
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V55:",kw.get("status"),flush=True)
def copy_backup(blobs):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        for p,b in blobs.items(): z.writestr("dayzOffline.enoch/"+p,b)
        z.writestr("SHA256.txt","".join(sha(v)+" "+k+"\n" for k,v in blobs.items()))
    with zipfile.ZipFile(BACKUP) as z:
        must(z.testzip() is None,"Backup ZIP failed CRC check")
        for p,b in blobs.items():
            must(sha(z.read("dayzOffline.enoch/"+p))==sha(b),"Backup content invalid "+p)

def build(blobs,types):
    events=parse(blobs[FILES[0]])
    positions=parse(blobs[FILES[1]])
    old=events.find(f"event[@name='{EVENT}']")
    point=positions.find(f"event[@name='{EVENT}']")
    must(old is not None and point is not None,
         "V54 inactive event/point missing; no blind deployment")
    must(all(old.findtext(tag)=="0" for tag in ("active","nominal","min","max")),
         "Prior gift event not fully disabled; refuse duplicate spawn")
    must(len(point.findall("pos"))==1,"Expected exactly one existing gift point")
    at=point.find("pos")
    must(all(abs(float(at.get(k))-v)<0.005 for k,v in
             (("x",X),("z",Z),("a",YAW))),
         "Gift point changed; refuse")
    must([i.get("type") for i in old.findall("./children/child")]==[CAR],
         "Unexpected Gunter child")
    must(old.findtext("position")=="fixed",
         "Unexpected event positioning")
    # Reuse the existing, independently safety-tested V53 builder on an isolated
    # in-memory copy with ONLY the previous inactive gift/point removed.
    ev_clean=parse(blobs[FILES[0]])
    pos_clean=parse(blobs[FILES[1]])
    ev_clean.remove(ev_clean.find(f"event[@name='{EVENT}']"))
    pos_clean.remove(pos_clean.find(f"event[@name='{EVENT}']"))
    shadow=dict(blobs)
    shadow[FILES[0]]=data(ev_clean)
    shadow[FILES[1]]=data(pos_clean)
    armed,details=patch(shadow,types)
    must(armed is not None,"CE builder did not create the single gift event")
    ev=parse(armed[FILES[0]])
    gift=ev.find(f"event[@name='{EVENT}']")
    gift.find("restock").text="0"  # first boot: no artificial year-long wait
    gift.find("saferadius").text="0"
    gift.find("distanceradius").text="0"
    gift.find("cleanupradius").text="100"
    first=dict(armed)
    first[FILES[0]]=data(ev)
    must(patch_for_postread(first)[0], "First boot gift + cargo validation failed")
    # after first boot, write this as file for *future restarts*, with no second
    # restart; keep active=1 so car isn't potentially removed on reboot.
    final_ev=parse(first[FILES[0]])
    gift=final_ev.find(f"event[@name='{EVENT}']")
    gift.find("restock").text=str(LONG_RESTOCK)
    longterm=dict(first)
    longterm[FILES[0]]=data(final_ev)
    must(patch_for_postread(longterm)[0],"Long restock gift event malformed")
    must(first[FILES[1]]==longterm[FILES[1]] and
         first[FILES[2]]==longterm[FILES[2]],
         "Unexpected modifications beyond restock duration")
    return first,longterm,details

def read(token,remote):
    return {p:download_one(token,remote[p]) for p in FILES}
def upload_and_check(token,remote,rel,blob):
    upload_file(token,remote[rel],blob)
    must(sha(download_one(token,remote[rel]))==sha(blob),
         "Post-upload checksum mismatch "+rel)
def state(token):
    s=game_state(token)
    return game_status(s),players(s)
def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=55)
def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=55)
def recover(token,remote,original,first,longterm):
    s,n=state(token)
    if s in ("started","running"):stop(token)
    else:must(s=="stopped","Cannot recover unknown game state")
    for p in reversed(FILES):
        live=download_one(token,remote[p])
        must(sha(live) in {sha(original[p]),sha(first[p]),sha(longterm[p])},
             "Concurrent user edit detected: manual recovery "+p)
        if sha(live)!=sha(original[p]): upload_and_check(token,remote,p,original[p])
    start(token)
    write_status(status="ROLLBACK_OF_PARTIAL_V55_CONFIRMED")
def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    must(token and os.getenv("BEILEYS47_V55_APPROVED")=="yes",
         "Missing V55 owner approval/Nitrado API token")
    root=resolve_mission(token)
    remote={p:posixpath.join(root,p) for p in FILES}
    original=read(token,remote)
    types=parse(download_one(token,posixpath.join(root,"db/types.xml")))
    first,longterm,details=build(original,types)
    copy_backup(original)
    provider=analyze(
      call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
      call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    must(provider["provider_backup_exists"] and provider["restore_possible"] is True,
         "Nitrado provider recovery metadata unavailable")
    s,n=state(token)
    must(s in ("running","started"),"Game is not started")
    must(os.getenv("BEILEYS47_V55_PLAYER_INTERRUPT_APPROVED")=="yes",
         "Owner has not allowed interruption of connected players")
    write_status(status="VERIFIED_BACKUP_READY_BEFORE_RESTART",
       active_players_before=n, provider_backup_count=provider["backup_count"],**details)
    touched=False
    stopped=False
    try:
        stop(token);stopped=True
        must(all(sha(download_one(token,remote[p]))==sha(original[p]) for p in FILES),
             "Configuration edited by another admin before upload")
        for p in FILES:
            touched=True
            upload_and_check(token,remote,p,first[p])
        start(token);stopped=False
        must(all(sha(download_one(token,remote[p]))==sha(first[p]) for p in FILES),
             "Initial live event not identical to verified first boot")
        must(patch_for_postread(read(token,remote))[0],
             "First boot event missing")
        write_status(status="ONE_VEHICLE_EVENT_ACTIVE_FIRST_BOOT",
            event_nominal=1,event_max=1,restock_seconds=0,
            note="Check actual Gunter on PS5; engine CE may still choose not to materialize.",
            **details)
        # Do not restart again: this was likely the reason the V54 gift was lost.
        # Restrict FUTURE re-spawns without disrupting the now-running CE attempt.
        upload_and_check(token,remote,FILES[0],longterm[FILES[0]])
        must(patch_for_postread(read(token,remote))[0],
             "Post-adjustment event missing")
        write_status(status="ONE_VEHICLE_EVENT_ACTIVE_WITH_365_DAY_RESTOCK_STAGED",
            event_nominal=1,event_max=1,
            configured_restocks_after_NEXT_restart_seconds=LONG_RESTOCK,
            initial_boot_restocks_seconds=0,
            no_second_restart=True,
            note="Physical spawn unknown; deactivating this CE event before user verifies could remove car.",
            **details)
        print("V55: ONE active CE car event; no second reboot. Future restock is 365 days. PS5 verification REQUIRED.",flush=True)
    except Exception:
        if touched:
            try:
                recover(token,remote,original,first,longterm)
                stopped=False
            except Exception as e:
                write_status(status="CRITICAL_MANUAL_ROLLBACK_NEEDED",
                             recovery_error_type=type(e).__name__)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:print("CRITICAL: unable to verify game restarted")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V55 ERROR:",type(exc).__name__,str(exc)[:175],file=sys.stderr)
        if not OUT.exists():write_status(status="FAILED_BEFORE_EDIT")
        raise SystemExit(1)
