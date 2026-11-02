#!/usr/bin/env python3
"""V53: one fixed-event Gunter 2 at player-supplied Livonia X/Z with supplies.

This creates a CE VEHICLE SPAWN CONFIGURATION, not a live spawned instance.
The standard cfgspawnabletypes profile is per classname, not per event:
future black Gunter 2 vehicles will share the new parts and cargo preset.
Vanilla console XML cannot guarantee a prefilled fuel tank / wet radiator.
No db/types.xml, storage_1, player data, world wipe or unrelated events changed.
"""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, math, os, posixpath
import sys, time, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission, download_one, NitradoError
from deploy_beileys47_v15 import (
    game_state, game_status, players, upload_file,
    request_api_post, wait_status
)
from v36_nitrado_backups_readonly import analyze
from nitrado_snapshot import call_api

EVENT = "VehicleBEILEYS47GunterGiftV53"
BASE_EVENT = "VehicleHatchback02"
CAR = "Hatchback_02_Black"
X, Z = 9416.80, 3489.65
# "a" is vehicle yaw; user supplied no orientation. Set a deterministic candidate.
YAW = 0.0
FILES = ("db/events.xml", "cfgeventspawns.xml", "cfgspawnabletypes.xml")
REQ_PARTS = {
    "Hatchback_02_Wheel": 4, "CarRadiator": 1,
    "CarBattery": 1, "SparkPlug": 1,
}
CARGO = {
    "CanisterGasoline": 1, "TireRepairKit": 1, "CarRadiator": 1,
    "WaterBottle": 2, "AliceBag_Green": 1,
    "BakedBeansCan": 2, "TacticalBaconCan": 2
}
OUT = Path("deploy/v53/GUNTER_GIFT_LIVE_RESULT.json")
ARCH = Path("deploy/v53/PRIVATE_ORIGINAL_3XML.zip")

def guard(test, message):
    if not test: raise NitradoError(message)

def sha(b): return hashlib.sha256(b).hexdigest()

def parse(b):
    return ET.fromstring(b, parser=ET.XMLParser(
        target=ET.TreeBuilder(insert_comments=True)))

def data(root): return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def emit(**kwargs):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "release": "V53_GUNTER_GIFT",
        "vehicle": "Gunter 2 (black)",
        "event": EVENT, "x": X, "z": Z, "yaw_candidate": YAW,
        "storage_1_modified": False, "world_wipe": False,
        "existing_vehicles_removed": False,
        "gas_tank_full_verified": False, "radiator_water_full_verified": False,
        "physical_vehicle_spawn_verified": False,
        "cargo_contents_physically_verified": False,
        "class_profile_side_effect": "All future Hatchback_02_Black CE spawns share this loadout",
        **kwargs
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("V53:", kwargs.get("status", "UNKNOWN"), flush=True)

def event_template(events):
    base=events.find(f"event[@name='{BASE_EVENT}']")
    guard(base is not None, "Vanilla Gunter event not found in live XML")
    guard(base.findtext("position") == "fixed", "Unexpected vanilla car event position")
    guard(any(c.get("type")==CAR for c in base.findall("./children/child")),
          "Black Gunter not configured in vanilla event")
    return base

def validate_location(spawns):
    guard(0 < X < 12800 and 0 < Z < 12800, "Location outside Livonia")
    # CE potential collision with pre-existing fixed *vehicle spawn points*.
    closest=[]
    for ev in spawns.findall("event"):
        name=ev.get("name","")
        if not name.startswith("Vehicle"): continue
        for pt in ev.findall("pos"):
            try:
                x,z=float(pt.get("x")),float(pt.get("z"))
                d=math.hypot(x-X,z-Z)
                closest.append((round(d,2),name))
            except (TypeError,ValueError): continue
    if closest:
        nearest=min(closest)
        guard(nearest[0] >= 12, "Vehicle spawn point too close ("+
              str(nearest)+"); manual map inspection needed")
        return {"nearest_existing_vehicle_spawn_m": nearest[0],
                "nearest_existing_vehicle_spawn_event": nearest[1]}
    return {"nearest_existing_vehicle_spawn_m": None}

def patch(before, live_types):
    roots={p:parse(before[p]) for p in FILES}
    events,positions,spawns=[roots[p] for p in FILES]
    guard([r.tag for r in (events,positions,spawns)] ==
          ["events","eventposdef","spawnabletypes"], "Unexpected XML roots")
    available={e.get("name") for e in live_types.findall("type")}
    guard(all(n in available for n in [CAR, *REQ_PARTS, *CARGO]),
          "Unknown classname(s) in live db/types.xml: "+
          ",".join(sorted(set([CAR,*REQ_PARTS,*CARGO])-available)))
    evt=events.find(f"event[@name='{EVENT}']")
    pos=positions.find(f"event[@name='{EVENT}']")
    if evt is not None or pos is not None:
        guard(evt is not None and pos is not None,
              "Partially existing V53 event; no overwrite")
        guard(evt.findtext("nominal")=="1" and evt.findtext("active")=="1"
              and [c.get("type") for c in evt.findall("./children/child")]==[CAR]
              and len(pos.findall("pos"))==1,
              "Existing V53 event differs; do not replace")
        p=pos.find("pos")
        guard(all(abs(float(p.get(k))-v)<0.005 for k,v in
                  (("x",X),("z",Z),("a",YAW))),
              "Existing event at different location")
        ok, _=patch_for_postread(before)
        guard(ok, "Existing V53 event present but Gunter cargo is incomplete; refuse false success")
        return None, {"status":"ALREADY_CONFIGURED_NO_EDIT"}
    site=validate_location(positions)
    vanilla=event_template(events)
    new=copy.deepcopy(vanilla)
    new.set("name", EVENT)
    for key, val in (
        ("nominal","1"), ("min","1"), ("max","1"), ("active","1"),
        ("saferadius","15"), ("distanceradius","15"), ("cleanupradius","30")):
        tag=new.find(key)
        guard(tag is not None, "Missing CE field "+key)
        tag.text=val
    children=new.find("children")
    guard(children is not None, "Vanilla children missing")
    children.clear()
    ET.SubElement(children,"child", {
        "lootmax":"0","lootmin":"0","max":"1","min":"1","type":CAR
    })
    events.append(new)
    e=ET.SubElement(positions,"event",{"name":EVENT})
    ET.SubElement(e,"pos", {"x":f"{X:.2f}", "z":f"{Z:.2f}",
                           "a":f"{YAW:.2f}"})
    profile=spawns.find(f"type[@name='{CAR}']")
    guard(profile is not None, "Black Gunter spawnable type is missing")
    found={}
    for g in profile.findall("attachments"):
        for i in g.findall("item"):
            name=i.get("name")
            found[name]=found.get(name,0)+1
    guard(all(found.get(name,0)>=n for name,n in REQ_PARTS.items()),
          "Gunter vehicle parts incomplete in original profile")
    # There must not be an existing special Gunter cargo preset to destroy.
    guard(len(profile.findall("cargo"))==0,
          "Existing Gunter cargo customization found; preserve it; manual review")
    groups=profile.findall("attachments")
    guard(12 <= len(groups) <= 24,
          "Unexpected vehicle attachment layout; manual review")
    for g in groups:
        guard(len(g.findall("item"))==1,
              "Ambiguous attachment alternatives: refuse broad chance adjustment")
        g.set("chance","1.00")
        for i in g.findall("item"): i.set("chance","1.00")
    dmg=profile.find("damage")
    if dmg is None:
        dmg=ET.Element("damage")
        profile.insert(0,dmg)
    dmg.set("min","0.0")
    dmg.set("max","0.0")
    for classname,count in CARGO.items():
        for _ in range(count):
            g=ET.SubElement(profile,"cargo",{"chance":"1.00"})
            attrs={"name":classname,"chance":"1.00"}
            if classname in ("CanisterGasoline","WaterBottle"):
                attrs.update({"quantmin":"100","quantmax":"100"})
            ET.SubElement(g,"item", attrs)
    changed={p:data(roots[p]) for p in FILES}
    # Other event profiles, event spawn positions and vehicle types untouched
    old_event=parse(before[FILES[0]])
    new_event=parse(changed[FILES[0]])
    new_event.remove(new_event.find(f"event[@name='{EVENT}']"))
    guard(ET.tostring(new_event)==ET.tostring(old_event),
          "Existing CE events changed unexpectedly")
    old_pos=parse(before[FILES[1]])
    new_pos=parse(changed[FILES[1]])
    new_pos.remove(new_pos.find(f"event[@name='{EVENT}']"))
    guard(ET.tostring(new_pos)==ET.tostring(old_pos),
          "Existing CE event positions changed unexpectedly")
    old_types=parse(before[FILES[2]])
    new_types=parse(changed[FILES[2]])
    old_profile=old_types.find(f"type[@name='{CAR}']")
    new_profile=new_types.find(f"type[@name='{CAR}']")
    guard(old_profile is not None and new_profile is not None,
          "Missing Gunter profile")
    old_types.remove(old_profile)
    new_types.remove(new_profile)
    guard(ET.tostring(old_types)==ET.tostring(new_types),
          "Another spawnable profile changed unexpectedly")
    return changed, {**site,
         "configured_cargo_entries":sum(CARGO.values()),
         "configured_cargo":CARGO,
         "black_gunter_profile_modified_globally":True}

def make_backup(before):
    ARCH.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ARCH,"w",zipfile.ZIP_DEFLATED) as out:
        for path,blob in before.items():
            out.writestr("dayzOffline.enoch/"+path,blob)
        out.writestr("SHA256.txt",
                     "".join(sha(b)+"  "+p+"\n" for p,b in before.items()))
    with zipfile.ZipFile(ARCH) as z:
        guard(z.testzip() is None,"Corrupt V53 backup")
        for p,b in before.items():
            guard(sha(z.read("dayzOffline.enoch/"+p))==sha(b),
                  "Backup mismatch: "+p)

def provider_backup_gate(token):
    result=analyze(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    guard(result["provider_backup_exists"] and result["restore_possible"] is True,
          "Provider restore metadata not confirmed")
    return result["backup_count"]

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(bool(token) and os.environ.get("BEILEYS47_V53_APPROVED")=="yes",
          "Missing owner approval / Nitrado token")
    mission=resolve_mission(token)
    remote={p:posixpath.join(mission,p) for p in FILES}
    before={p:download_one(token,remote[p]) for p in FILES}
    types=parse(download_one(token,posixpath.join(mission,"db/types.xml")))
    new,details=patch(before,types)
    if new is None:
        emit(**details,no_restart=True)
        return
    make_backup(before)
    backups=provider_backup_gate(token)
    state=game_state(token)
    status,count=game_status(state),players(state)
    if status not in ("started","running","stopped") or (
            status!="stopped" and (type(count) is not int or count!=0)):
        emit(status="WAITING_FOR_EMPTY_SERVER",players_online=count,
             provider_backup_records=backups,**details)
        return
    time.sleep(2)
    again=game_state(token)
    guard(game_status(again)==status and
          (status=="stopped" or players(again)==0),
          "Player or server-state drift, no change")
    emit(status="BACKUP_VERIFIED_BEFORE_SERVER_STOP",
         provider_backup_records=backups,**details)
    stopped=False
    restarted=False
    touched=[]
    applied=False
    try:
        if status!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=55)
            stopped=True
        for p in FILES:
            guard(sha(download_one(token,remote[p]))==sha(before[p]),
                  "Concurrent XML change during stop: "+p)
        for p in FILES:
            touched.append(p)
            upload_file(token,remote[p],new[p])
            guard(sha(download_one(token,remote[p]))==sha(new[p]),
                  "Post-upload bytes differ: "+p)
        if status!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            wait_status(token,{"started","running"},attempts=55)
            restarted=True
        for p in FILES:
            guard(sha(download_one(token,remote[p]))==sha(new[p]),
                  "Post-restart bytes differ: "+p)
        check,meta=patch_for_postread(
            {p:download_one(token,remote[p]) for p in FILES})
        guard(check,"V53 event or cargo absent after restart")
        applied=True
        emit(status="INSTALLED_CE_CONFIG_AND_POST_RESTART_VERIFIED",
             provider_backup_records=backups,
             server_status=game_status(game_state(token)),
             **details)
    except Exception as ex:
        if touched and not applied:
            try:
                now=game_state(token)
                if game_status(now) in ("started","running"):
                    guard(players(now)==0,"Players joined; manual rollback required")
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                    wait_status(token,{"stopped"},attempts=55)
                    stopped=True
                for p in reversed(touched):
                    current=download_one(token,remote[p])
                    guard(sha(current) in (sha(new[p]),sha(before[p])),
                          "Concurrent administrator edits: refuse rollback")
                    if sha(current)!=sha(before[p]):
                        upload_file(token,remote[p],before[p])
                        guard(sha(download_one(token,remote[p]))==sha(before[p]),
                              "Rollback verification failed: "+p)
                emit(status="ROLLED_BACK_AFTER_ERROR",error_type=type(ex).__name__)
            except Exception as recovery:
                emit(status="CRITICAL_MANUAL_RECOVERY_NEEDED",
                     error_type=type(ex).__name__,
                     recovery_type=type(recovery).__name__)
            raise
        raise
    finally:
        if stopped and not restarted:
            try:
                request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                wait_status(token,{"started","running"},attempts=55)
                print("V53 safety restart completed",flush=True)
            except Exception:
                print("CRITICAL: server restart unconfirmed",flush=True)

def patch_for_postread(blobs):
    ev,po,sp=(parse(blobs[p]) for p in FILES)
    e=ev.find(f"event[@name='{EVENT}']")
    p=po.find(f"event[@name='{EVENT}']")
    t=sp.find(f"type[@name='{CAR}']")
    if e is None or p is None or t is None:return False,{}
    cargo={}
    for item in t.findall("./cargo/item"):
        n=item.get("name")
        cargo[n]=cargo.get(n,0)+1
    good=(e.findtext("nominal")=="1" and e.findtext("active")=="1"
          and len(p.findall("pos"))==1
          and abs(float(p.find("pos").get("x"))-X)<0.005
          and abs(float(p.find("pos").get("z"))-Z)<0.005
          and all(cargo.get(k)==n for k,n in CARGO.items()))
    return good,{"cargo_counts":cargo}

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V53 ERROR",type(e).__name__,str(e)[:190],file=sys.stderr)
        if not OUT.exists():emit(status="FAILED_BEFORE_ANY_SERVER_EDIT")
        raise SystemExit(1)
