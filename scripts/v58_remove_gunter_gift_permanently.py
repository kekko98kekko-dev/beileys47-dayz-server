#!/usr/bin/env python3
"""V58: remove ONE gift Gunter source and restore original black-Gunter profile.

The original class profile is recovered from a private V54 *pre-gift* backup,
not reconstructed by guesswork. Do not touch storage_1, other vehicles,
world persistence, vanilla Gunter event, or any unrelated world configuration.

An already spawned Gunter is persisted in DayZ world data; removing its CE
source does NOT guarantee physical removal. Owner may dispose of it in game.
"""
from __future__ import annotations
import copy,hashlib,json,os,posixpath,re,sys,time,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError,call_api
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v36_nitrado_backups_readonly import analyze
from v53_gunter_gift import EVENT,CAR,X,Z,YAW,FILES,patch as gift_builder,parse,data

ROOT=Path(__file__).resolve().parents[1]
OLD_ARCHIVE=ROOT/"deploy/v58/v54_original/PRIVATE_ORIGINAL_XML_BEFORE_GIFT.zip"
OUT=Path("deploy/v58/GUNTER_REMOVAL_RESULT.json")
ROLLBACK=Path("deploy/v58/PRIVATE_PRE_REMOVAL_BACKUP.zip")
EXPECT_RESTOCK="2147483647"
REPO_GIFT_EVENT="VehicleBEILEYS47GunterGiftV53"

def guard(ok,msg):
    if not ok: raise NitradoError(msg)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def report(**kwargs):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
       "release":"BEILEYS47 V58",
       "purpose":"Permanently remove one Gunter gift CE event and dedicated position",
       "reversed_gift_event":EVENT,"original_location":[X,Z],
       "black_gunter_original_profile_restored_from_private_pre_gift_archive":True,
       "vanilla_gunter_and_other_vehicle_events_untouched":True,
       "world_persistence_files_modified":False,"wipe_performed":False,
       "physical_persisted_car_deleted":False,
       "note":"Removing the vehicle's event will not necessarily remove the already persistent car",
       **kwargs
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V58 STATUS",kwargs.get("status","unknown"),flush=True)

def original_archive():
    guard(OLD_ARCHIVE.is_file(),
          "Private V54 original archive missing; no speculative car profile restoration")
    with zipfile.ZipFile(OLD_ARCHIVE) as z:
        guard(z.testzip() is None,"V54 original ZIP failed CRC check")
        archive={}
        for rel in FILES:
            k="dayzOffline.enoch/"+rel
            guard(k in z.namelist(),"Missing V54 original "+rel)
            blob=z.read(k)
            guard(len(blob)>1000,"Suspiciously short V54 original "+rel)
            archive[rel]=blob
        s=z.read("SHA256.txt").decode("ascii")
        for rel in FILES:
            guard(sha(archive[rel])+"  "+rel in s,
                  "V54 original ZIP SHA mismatch "+rel)
    guard(parse(archive[FILES[0]]).find(f"event[@name='{EVENT}']") is None,
          "The V54 backup itself contains the custom gift event")
    guard(parse(archive[FILES[1]]).find(f"event[@name='{EVENT}']") is None,
          "The V54 backup itself contains the gift spawn point")
    return archive

def remove_matching_block(blob,tag,event):
    name=EVENT.encode("ascii")
    pat=rb"<"+tag+rb"\s+name=[\"']"+name+rb"[\"'][^>]*>.*?</"+tag+rb">"
    matches=list(re.finditer(pat,blob,re.DOTALL))
    guard(len(matches)==1,"Expected exactly one user gift "+tag.decode()+" block")
    m=matches[0]
    return blob[:m.start()]+blob[m.end():],m.group()

def same_xml_meaning(a,b):
    def normalized(node):
        return (str(node.tag),tuple(sorted(node.attrib.items())),
                (node.text or "").strip(),tuple(normalized(c) for c in node))
    return normalized(a)==normalized(b)

def prune_config(live,original,types):
    guard(all(p in live and p in original for p in FILES),"Missing one of three original files")
    # Rebuild expected V55 black profile from the actual pre-V54 state;
    # this must match the current *entire* target profile exactly.
    expected,_=gift_builder(original,types)
    guard(expected is not None,"Failed to reproduce one original gift config")
    old_profile=parse(original[FILES[2]]).find(f"type[@name='{CAR}']")
    expected_profile=parse(expected[FILES[2]]).find(f"type[@name='{CAR}']")
    live_tree=parse(live[FILES[2]])
    live_profile=live_tree.find(f"type[@name='{CAR}']")
    guard(old_profile is not None and expected_profile is not None and live_profile is not None,
          "Black Gunter profile missing")
    guard(ET.tostring(live_profile)==ET.tostring(expected_profile),
          "A different admin has edited black Gunter after V55: do not override")
    original_tree=parse(original[FILES[2]])
    cmp_live=copy.deepcopy(live_tree)
    cmp_orig=copy.deepcopy(original_tree)
    cmp_live.remove(cmp_live.find(f"type[@name='{CAR}']"))
    cmp_orig.remove(cmp_orig.find(f"type[@name='{CAR}']"))
    # Other profiles may have been edited after V54 (that is fine); preserve them.
    before_tags=[(k.get("name"),ET.tostring(k)) for k in live_tree.findall("type")]
    i=list(live_tree).index(live_profile)
    live_tree.remove(live_profile)
    live_tree.insert(i,copy.deepcopy(old_profile))
    new_profile_file=data(live_tree)
    guard(ET.tostring(parse(new_profile_file).find(f"type[@name='{CAR}']"))==
          ET.tostring(old_profile),"Pre-gift black Gunter was not restored")
    profiles_new=parse(new_profile_file)
    others_new=[(k.get("name"),ET.tostring(k)) for k in profiles_new.findall("type")
                if k.get("name")!=CAR]
    others_before=[p for p in before_tags if p[0]!=CAR]
    guard(others_before==others_new,
          "Restoration would change a different vehicle or item")
    ev_tree=parse(live[FILES[0]])
    po_tree=parse(live[FILES[1]])
    ev=ev_tree.find(f"event[@name='{EVENT}']")
    point=po_tree.find(f"event[@name='{EVENT}']")
    guard(ev is not None and point is not None,
          "A gift source/point is already missing; avoid partial destruction")
    guard(ev.findtext("restock")==EXPECT_RESTOCK and
          ev.findtext("active")=="1" and
          all(ev.findtext(k)=="1" for k in ("nominal","min","max")) and
          ev.findtext("position")=="fixed" and
          [a.get("type") for a in ev.findall("./children/child")]==[CAR],
          "Gift event does not match V56 baseline; refuse to remove unknown event")
    pts=point.findall("pos")
    guard(len(pts)==1,"Expected exactly one gift location")
    pos=pts[0]
    guard(all(abs(float(pos.get(k))-v)<.005
              for k,v in (("x",X),("z",Z),("a",YAW))),
          "Gift event coords differ; refuse")
    rem_ev,_=remove_matching_block(live[FILES[0]],b"event",EVENT)
    rem_po,_=remove_matching_block(live[FILES[1]],b"event",EVENT)
    parsed_ev=parse(rem_ev)
    parsed_pos=parse(rem_po)
    guard(parsed_ev.find(f"event[@name='{EVENT}']") is None and
          parsed_pos.find(f"event[@name='{EVENT}']") is None,
          "Gift source remains after removal")
    ev_copy=copy.deepcopy(ev_tree);ev_copy.remove(ev_copy.find(f"event[@name='{EVENT}']"))
    po_copy=copy.deepcopy(po_tree);po_copy.remove(po_copy.find(f"event[@name='{EVENT}']"))
    guard(same_xml_meaning(ev_copy,parsed_ev),
          "Another CE event altered during target removal")
    guard(same_xml_meaning(po_copy,parsed_pos),
          "Another fixed CE spawn point altered during target removal")
    new={FILES[0]:rem_ev,FILES[1]:rem_po,FILES[2]:new_profile_file}
    guard(len(new)==3 and set(new)==set(FILES),"Unexpected write set")
    verify_removed(new,original)
    return new

def verify_removed(blobs,original):
    guard(parse(blobs[FILES[0]]).find(f"event[@name='{EVENT}']") is None,
          "Gift CE event still present")
    guard(parse(blobs[FILES[1]]).find(f"event[@name='{EVENT}']") is None,
          "Gift CE spawn point still present")
    current_profile=parse(blobs[FILES[2]]).find(f"type[@name='{CAR}']")
    original_profile=parse(original[FILES[2]]).find(f"type[@name='{CAR}']")
    guard(current_profile is not None and original_profile is not None and
          ET.tostring(current_profile)==ET.tostring(original_profile),
          "Original black Gunter profile not restored")
    for rel in (FILES[0],FILES[1]):
        root=parse(blobs[rel])
        guard(root.tag==("events" if rel==FILES[0] else "eventposdef"),
              "Unparseable CE configuration")

def safe_backup(blobs):
    ROLLBACK.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ROLLBACK,"w",zipfile.ZIP_DEFLATED) as z:
        for rel,blob in blobs.items():
            z.writestr("dayzOffline.enoch/"+rel,blob)
        z.writestr("SHA256.txt","".join(sha(v)+"  "+k+"\n" for k,v in blobs.items()))
    with zipfile.ZipFile(ROLLBACK) as z:
        guard(z.testzip() is None,"Pre-removal ZIP is corrupt")
        for rel,blob in blobs.items():
            guard(sha(z.read("dayzOffline.enoch/"+rel))==sha(blob),
                  "Pre-removal ZIP hash mismatch "+rel)
def state(token):
    s=game_state(token)
    return game_status(s),players(s)
def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=60)
def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=60)

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(token and os.getenv("BEILEYS47_V58_REMOVE_GUNTER_APPROVED")=="yes",
          "Missing Nitrado API token or user deletion approval")
    original=original_archive()
    mission=resolve_mission(token)
    remote={p:posixpath.join(mission,p) for p in FILES}
    live={p:download_one(token,remote[p]) for p in FILES}
    live_types=parse(download_one(token,posixpath.join(mission,"db/types.xml")))
    edited=prune_config(live,original,live_types)
    safe_backup(live)
    provider=analyze(
      call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
      call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    guard(provider["provider_backup_exists"] and provider["restore_possible"] is True,
          "Nitrado backup verification failed")
    server_status,connected=state(token)
    guard(server_status in ("running","started"),
          "Live server not started; no modification")
    report(status="BACKUP_READY_BEFORE_RESTART",players_before=connected,
           provider_backup_count=provider["backup_count"])
    stopped=False;touched=False
    try:
        stop(token);stopped=True
        for rel in FILES:
            guard(sha(download_one(token,remote[rel]))==sha(live[rel]),
                  "Concurrent change of "+rel+" detected before upload")
        for rel in FILES:
            touched=True
            upload_file(token,remote[rel],edited[rel])
            guard(sha(download_one(token,remote[rel]))==sha(edited[rel]),
                  "Post-upload checksum mismatch: "+rel)
        verify_removed({p:download_one(token,remote[p]) for p in FILES},original)
        start(token);stopped=False
        after={p:download_one(token,remote[p]) for p in FILES}
        guard(all(sha(after[p])==sha(edited[p]) for p in FILES),
              "Post-restart remote hash changed")
        verify_removed(after,original)
        status,count=state(token)
        guard(status in ("started","running"),"Server not running after removal")
        report(status="GIFT_GUNTER_EVENT_POINT_PROFILE_REMOVED_VERIFIED",
              server_status=status,players_after=count,
              removed_dedicated_gunter_spawn=True,
              restored_original_black_car_profile=True,
              post_restart_file_checksums_verified=True,
              original_backups_validated=True,
              provider_backup_count=provider["backup_count"])
        print("V58 SUCCESS: dedicated gift Gunter event and position deleted; pre-gift black Gunter class restored; no wipe.",flush=True)
    except Exception:
        if touched:
            try:
                status,count=state(token)
                if status in ("running","started"):
                    stop(token);stopped=True
                else:guard(status=="stopped","Unknown status before rollback")
                for rel in FILES:
                    current=download_one(token,remote[rel])
                    guard(sha(current) in {sha(live[rel]),sha(edited[rel])},
                          "External concurrent modification, cannot safely roll back "+rel)
                    if sha(current)!=sha(live[rel]):
                        upload_file(token,remote[rel],live[rel])
                        guard(sha(download_one(token,remote[rel]))==sha(live[rel]),
                              "Rollback verification failed "+rel)
                start(token);stopped=False
                report(status="ROLLED_BACK_ON_ERROR")
            except Exception as recover:
                report(status="CRITICAL_MANUAL_RECOVERY_REQUIRED",
                       recovery_error_type=type(recover).__name__)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:print("V58 CRITICAL: server running not verified",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V58 ERROR",type(exc).__name__,str(exc)[:190],file=sys.stderr)
        if not OUT.exists():report(status="FAILED_BEFORE_MODIFICATION")
        raise SystemExit(1)
