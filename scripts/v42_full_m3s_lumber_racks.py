#!/usr/bin/env python3
"""V42: complete M3S lumber racks on future spawns; no persisted vehicle mutation.

Upgrade exactly WoodenLog and WoodenPlank attachment quantity 50% -> 100%
under Truck_01_Covered. Preserve metal, vehicle parts, AliceBag and all other
spawnable types. Nitrado readback, original byte ZIP, rollback if safe, no wipe.
"""
from __future__ import annotations
import datetime as dt,hashlib,json,os,posixpath,sys,time,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status

REL="cfgspawnabletypes.xml"
OUT=Path("deploy/v42/LIVE_LUMBER_RACKS.json")
BACKUP=Path("deploy/v42/PRIVATE_BEFORE_LUMBER_RACKS.zip")
ITEMS=("WoodenLog","WoodenPlank")
def guard(ok,msg):
    if not ok:raise NitradoError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def result(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"version":"V42","target":"Truck_01_Covered",
      "lumber_rack_quantity_percent":{"WoodenLog":100,"WoodenPlank":100},
      "max_rack_capacity_per_new_M3S":{"WoodenLog":50,"WoodenPlank":100},
      "existing_persistent_truck_modified":False,"not_proof_of_current_vehicle_cargo":True,
      "no_world_wipe":True,"no_other_vehicle_types_changed":True,
      **kw},indent=2)+"\n",encoding="utf-8")
def parse(raw):
    return ET.fromstring(raw,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def get_racks(root):
    truck=root.find("type[@name='Truck_01_Covered']")
    guard(truck is not None,"M3S spawnable type missing")
    guard(any(i.get("name")=="AliceBag_Green" for i in truck.findall("./cargo/item")),
          "Previously installed Field Backpack 64 is missing; refuse overwrite")
    racks={}
    for item in ITEMS:
        found=[(g,i) for g in truck.findall("attachments") for i in g.findall("item")
               if i.get("name")==item]
        guard(len(found)==1,"Expected exactly one "+item+" rack")
        group,it=found[0]
        guard(group.get("chance")=="1.00" and it.get("chance")=="1.00",
              item+" attachment isn't guaranteed")
        racks[item]=it
    return racks
def patch(blob):
    root=parse(blob)
    guard(root.tag=="spawnabletypes","Unexpected XML root")
    racks=get_racks(root)
    qty={(i.get("quantmin"),i.get("quantmax")) for i in racks.values()}
    if qty=={("100","100")}:
        return blob,True
    guard(qty=={("50","50")},
          "Found partial or unexpected M3S lumber quantities; refuse changes")
    for it in racks.values():
        it.set("quantmin","100");it.set("quantmax","100")
    updated=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    verify=parse(updated)
    new_racks=get_racks(verify)
    guard(all((i.get("quantmin"),i.get("quantmax"))==("100","100") for i in new_racks.values()),
          "M3S lumber racks were not changed to full")
    # Revert edited quantity in memory and assert entire XML tree is otherwise identical.
    for it in new_racks.values():
        it.set("quantmin","50");it.set("quantmax","50")
    guard(ET.tostring(verify)==ET.tostring(parse(blob)),
          "Changes outside the two lumber quantity attributes detected")
    return updated,False
def backup(blob):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/"+REL,blob)
        z.writestr("SHA256.txt",sha(blob)+"  "+REL+"\n")
    with zipfile.ZipFile(BACKUP) as z:
        guard(z.testzip() is None and
              sha(z.read("dayzOffline.enoch/"+REL))==sha(blob),
              "V42 original backup corrupted")
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(token and os.environ.get("BEILEYS47_V42_APPROVED")=="yes",
          "Missing Nitrado token or owner's prior material request authorization")
    if (os.environ.get("GITHUB_EVENT_NAME")=="schedule" and
        dt.datetime.now(dt.timezone.utc).date()>dt.date(2026,11,30)):
        result(status="RENTAL_EXPIRED_NO_ACTION");return
    mission=resolve_mission(token);path=posixpath.join(mission,REL)
    original=download_one(token,path)
    new,already=patch(original)
    if already:
        result(status="ALREADY_FULL_NO_ACTION",remote_sha=sha(original),no_restart=True)
        print("PASS V42: both M3S material racks already full, no restart")
        return
    backup(original)
    state=game_state(token)
    status=game_status(state)
    online=players(state)
    if status not in ("started","running","stopped") or (status!="stopped" and online!=0):
        result(status="WAITING_FOR_IDLE",reported_players=online,no_restart=True)
        print("V42 WAIT: player online/unknown, no changes")
        return
    time.sleep(2)
    again=game_state(token)
    guard(game_status(again)==status and
          (status=="stopped" or players(again)==0),
          "Zero-player recheck failed")
    stopped=False;restarted=False;attempted=False;success=False
    try:
        if status!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=55)
            stopped=True
        guard(sha(download_one(token,path))==sha(original),
              "Current cfgspawnabletypes changed during stop")
        attempted=True
        upload_file(token,path,new)
        guard(sha(download_one(token,path))==sha(new),"Post-upload SHA mismatch")
        if stopped:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            wait_status(token,{"started","running"},attempts=55)
            restarted=True
        guard(sha(download_one(token,path))==sha(new),
              "Post-restart SHA mismatch")
        success=True
        result(status="INSTALLED_AND_VERIFIED",
               original_sha=sha(original),installed_sha=sha(new),
               server_status=game_status(game_state(token)),
               next="Player should check existing truck racks; previously spawned trucks are not retroactively refilled")
        print("V42 INSTALL SUCCESS: M3S WoodenLog+WoodenPlank attachment quantities 100%, zaino 64 preserved, no wipe")
    except Exception:
        if attempted and not success:
            try:
                now=game_state(token)
                if game_status(now) in ("started","running"):
                    guard(players(now)==0,"Player joined; avoid disruptive rollback")
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                    wait_status(token,{"stopped"},attempts=50)
                    stopped=True
                upload_file(token,path,original)
                guard(sha(download_one(token,path))==sha(original),
                      "Original XML restoration SHA mismatch")
                result(status="ROLLED_BACK_ORIGINAL_XML")
                if stopped:
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                    wait_status(token,{"started","running"},attempts=55)
                    restarted=True
            except Exception:
                result(status="MANUAL_RECOVERY_REQUIRED")
        raise
    finally:
        if stopped and not restarted:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:print("CRITICAL restart confirmation unavailable",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as ex:
        print("V42 ERROR",type(ex).__name__,str(ex)[:190],file=sys.stderr)
        raise SystemExit(1)
