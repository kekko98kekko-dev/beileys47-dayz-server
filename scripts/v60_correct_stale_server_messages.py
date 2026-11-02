#!/usr/bin/env python3
"""V60: three truthful DayZ PvP/help notices after Zone47 experimental retirement.

ONLY db/messages.xml. The physical historical Radunin outpost at X7100/Z6965
still exists; no new 9000/7800 Zone47 fortress or custom accessible bunker is
claimed. Read original, backup ZIP+SHA, edit only the exact three <text> values,
verify all remaining message fields and bytes, owner-authorized one restart,
verify post-reboot. No CE loot, worlds, vehicles, player data or wipe touched.
"""
from __future__ import annotations
import datetime as dt,hashlib,json,os,posixpath,sys,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,call_api,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,request_api_post,upload_file,wait_status
from v36_nitrado_backups_readonly import analyze

FILE="db/messages.xml"
OUT=Path("deploy/v60/MESSAGES_CORRECTION_RESULT.json")
ZIP=Path("deploy/v60/PRIVATE_PRE_V60_MESSAGES.zip")
REPLACE={
 "BEILEYS47 | ZONA47 PvP near 7100/6965, fortified bunker near 9022/7458, Dolnik medical and military loot. Fight, loot and survive. Sunday community challenge: bring your squad!":
 "BEILEYS47 | Radunin PvP near X7100 Z6965; military patrol near X9022 Z7458; Dolnik medical supplies. Fight, loot and survive!",
 "BEILEYS47 | ZONA 47 PvP: explore the military outpost near X7100 Z6965. Approach carefully; cover matters.":
 "BEILEYS47 | Radunin PvP: explore the military outpost near X7100 Z6965. Approach carefully; watch for infected.",
 "BEILEYS47 | Bunker siege near X9022 Z7458; medical/military loot at Dolnik X11490 Z461. Watch for infected.":
 "BEILEYS47 | Military patrol near X9022 Z7458; medical supplies at Dolnik X11490 Z461. Watch for infected."
}
def guard(cond,msg):
    if not cond:raise NitradoError(msg)
def sha(x):return hashlib.sha256(x).hexdigest()
def write_result(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
      "release":"V60","scope":"ONLY three obsolete server announcement text values",
      "no_wipe":True,"world_storage_modified":False,"player_data_modified":False,
      "ce_loot_vehicle_scene_changed":False,"older_announcements_corrected":3,
      **kw
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V60 STATUS",kw.get("status"),flush=True)
def fields(blob):
    d=ET.fromstring(blob)
    guard(d.tag=="messages","Unexpected DayZ messages.xml root")
    messages=d.findall("message")
    guard(len(messages)>=6,"Expected at least six existing announcements")
    for m in messages:
        guard(m.find("text") is not None,"Announcement missing <text>")
    return d,messages
def patch(blob):
    d,messages=fields(blob)
    texts=[m.findtext("text") for m in messages]
    expected=list(REPLACE)
    already=list(REPLACE.values())
    if all(x in texts for x in already) and not any(x in texts for x in expected):
        return blob,True
    guard(all(texts.count(x)==1 for x in expected),
          "Unexpected message texts: refuse blind overwrite")
    guard(not any(x in texts for x in already),
          "Partially applied message correction, refuse edit")
    data=blob
    for old,new in REPLACE.items():
        guard(len(new)<=160 and all(c not in new for c in "<>&"),
              "New announcement violates XML/length rules")
        o=old.encode("utf-8");n=new.encode("utf-8")
        guard(data.count(o)==1,"Byte-level exact message not unique")
        data=data.replace(o,n,1)
    nextdoc,nm=fields(data)
    guard(len(nm)==len(messages),"Some other announcement disappeared")
    for prev,cur in zip(messages,nm):
        for tag in ("delay","repeat","deadline","onconnect","shutdown"):
            guard(prev.findtext(tag)==cur.findtext(tag),
                  "Nontext announcement timing or shutdown flag changed")
        t=prev.findtext("text")
        guard(cur.findtext("text")==REPLACE.get(t,t),
              "Unexpected announcement text modified")
    guard(all(x not in [m.findtext("text") for m in nm] for x in expected),
          "Obsolete announcement remains after replacement")
    # Ensure no accidental editing outside the three exact replacements.
    rewind=data
    for old,new in REPLACE.items():
        guard(rewind.count(new.encode())==1,"Replacement not unique")
        rewind=rewind.replace(new.encode(),old.encode(),1)
    guard(rewind==blob,"Byte differences outside expected three texts")
    return data,False
def backup(original):
    ZIP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ZIP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/"+FILE,original)
        z.writestr("SHA256.txt",sha(original)+"  "+FILE+"\n")
    with zipfile.ZipFile(ZIP) as z:
        guard(z.testzip() is None and
          sha(z.read("dayzOffline.enoch/"+FILE))==sha(original),
          "Original announcement archive invalid")
def state(token):
    s=game_state(token)
    return game_status(s),players(s)
def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=55)
def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=55)
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(token and os.getenv("BEILEYS47_V60_CORRECT_MESSAGES_APPROVED")=="yes",
          "No owner approval or Nitrado API token")
    mission=resolve_mission(token)
    remote=posixpath.join(mission,FILE)
    old=download_one(token,remote)
    new,done=patch(old)
    if done:
        write_result(status="ALREADY_CORRECT_NO_RESTART")
        return
    provider=analyze(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    guard(provider["provider_backup_exists"] and provider["restore_possible"] is True,
          "Provider recovery point is not confirmed")
    initial,count=state(token)
    guard(initial in ("started","running"),"Game not initially running")
    backup(old)
    write_result(status="ORIGINAL_BACKUP_VERIFIED_PRE_EDIT",players_before=count,
                 provider_backup_records=provider["backup_count"])
    stopped=False
    touched=False
    try:
        stop(token);stopped=True
        guard(sha(download_one(token,remote))==sha(old),
              "Concurrent administrator change detected")
        touched=True
        upload_file(token,remote,new)
        guard(sha(download_one(token,remote))==sha(new),
              "Messages failed remote SHA verification")
        start(token);stopped=False
        guard(sha(download_one(token,remote))==sha(new),
              "Messages changed after restart")
        guard(patch(download_one(token,remote))[1] is True,
              "Obsolete announcements not corrected on live Nitrado")
        final,count=state(token)
        guard(final in ("started","running"),"Server not running after update")
        write_result(status="CORRECTED_AND_VERIFIED_POST_RESTART",
                     original_sha=sha(old),updated_sha=sha(new),
                     original_messages_count=len(fields(old)[1]),
                     new_messages_count=len(fields(new)[1]),
                     final_server_status=final,
                     player_count_after=count,
                     no_other_file_modified=True,
                     provider_backup_records=provider["backup_count"])
        print("V60 SUCCESS: 3 stale notices removed without changing CE/world/vehicles.",flush=True)
    except Exception:
        if touched:
            try:
                s,n=state(token)
                if s in ("started","running"):
                    stop(token);stopped=True
                else:guard(s=="stopped","Unknown state before rollback")
                now=download_one(token,remote)
                guard(sha(now) in (sha(old),sha(new)),
                      "Concurrent external edit detected, manual rollback only")
                if sha(now)==sha(new):
                    upload_file(token,remote,old)
                    guard(sha(download_one(token,remote))==sha(old),
                          "Rollback checksum mismatch")
                start(token);stopped=False
                write_result(status="ROLLED_BACK_AFTER_FAILURE")
            except Exception as exc:
                write_result(status="CRITICAL_MANUAL_RECOVERY_REQUIRED",
                             exception_type=type(exc).__name__)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:print("CRITICAL: server restart not confirmed",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as ex:
        print("V60 ERROR",type(ex).__name__,str(ex)[:170],file=sys.stderr)
        if not OUT.exists():write_result(status="FAILED_BEFORE_ANY_SERVER_EDIT")
        raise SystemExit(1)
