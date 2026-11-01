#!/usr/bin/env python3
"""V21 truthful in-game discovery messages: single guarded DayZ console file change.

Never edits DayZ persistence, loot, objects, cars, settings, or storage.  No wipe.
Requires a previous real Nitrado SHA, zero connected players, rollback and readback.
"""
from __future__ import annotations
import hashlib,json,os,posixpath,sys,time,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import (
    game_state,game_status,players,upload_file,request_api_post,wait_status
)

FILE="db/messages.xml"
EXPECTED_SHA="3b3f45b6f33870382c43786cf59697e4bf91b3858d8e2ef4fa53277543cae3b1"
OUT=Path("deploy/v21/MESSAGES_RESULT.json")
BACKUP=Path("deploy/v21/private_messages_original.zip")
MESSAGES=(
    (90,"BEILEYS47 | ZONA 47 PvP: explore the military outpost near X7100 Z6965. Approach carefully; cover matters."),
    (115,"BEILEYS47 | Bunker siege near X9022 Z7458; medical/military loot at Dolnik X11490 Z461. Watch for infected."),
)
def digest(blob:bytes)->str:return hashlib.sha256(blob).hexdigest()
def guard(ok:bool,msg:str):
    if not ok:raise NitradoError(msg)
def record(**fields):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
        "v21":"discovery_messages","platform":"DayZ PlayStation","service_id":SERVICE_ID,
        "ps5_runtime_verified":False,"world_persistence_verified":False,"no_world_wipe_action":True,
        **fields
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def patch(original:bytes):
    guard(isinstance(original,bytes) and b"</messages>" in original,"Expected closing DayZ message tag")
    root=ET.fromstring(original)
    guard(root.tag=="messages","Wrong XML root")
    previous=root.findall("message")
    guard(len(previous)==4,"V20 message count differs; manual review required")
    guard(all(len((m.findtext("text") or ""))<=160 for m in previous),"Existing message too long")
    guard(not any(m.findtext("shutdown")=="1" for m in previous),
          "Existing automatic shutdown rule: manual review before changing messages")
    targets=[]
    for repeat,msg in MESSAGES:
        guard(len(msg)<=160 and repeat>=60 and all(c not in msg for c in "<>&"),
              "New message violates DayZ limits")
        guard(not any(msg==(m.findtext("text") or "") for m in previous),
              "Message already present; abort rather than duplicate")
        targets.append(
            f"  <message><delay>0</delay><repeat>{repeat}</repeat><deadline>0</deadline>"
            f"<onconnect>0</onconnect><shutdown>0</shutdown><text>{msg}</text></message>\n"
        )
    # Preserve original XML byte-for-byte; append only before its last closing root.
    head,closing=original.rsplit(b"</messages>",1)
    guard(not closing.strip(),"Unexpected trailing document content")
    updated=head+b"".join(v.encode("utf-8") for v in targets)+b"</messages>"+closing
    checked=ET.fromstring(updated).findall("message")
    guard(len(checked)==6,"Expected six game messages")
    # ElementTree serializes an element's trailing whitespace as .tail.
    # Appending a new node may add a harmless newline after the prior last node.
    # Preserve the original prefix bytes exactly, and compare the prior
    # four elements semantically without the incidental last-node .tail.
    def message_semantics(node):
        node_copy=ET.fromstring(ET.tostring(node,encoding="utf-8"))
        node_copy.tail=None
        return ET.tostring(node_copy,encoding="unicode")
    original_semantics=[message_semantics(x) for x in previous]
    guard([message_semantics(x) for x in checked[:4]]==original_semantics,
          "Existing notifications were altered")
    guard([(int(m.findtext("repeat","0")),m.findtext("text")) for m in checked[4:]]==list(MESSAGES),
          "New messages differ from target")
    return updated
def save_backup(blob):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/db/messages.xml",blob)
        z.writestr("SHA256.txt",digest(blob)+"  db/messages.xml\n")
    with zipfile.ZipFile(BACKUP) as z:
        guard(z.testzip() is None and digest(z.read("dayzOffline.enoch/db/messages.xml"))==digest(blob),
              "Backup unreadable")
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(token and os.environ.get("BEILEYS47_V21_APPROVED")=="yes",
          "Missing authorization or Nitrado secret")
    mission=resolve_mission(token)
    remote=posixpath.join(mission,FILE)
    old=download_one(token,remote)
    if digest(old)!=EXPECTED_SHA:
        record(status="blocked_unexpected_live_file",live_sha=digest(old))
        raise NitradoError("Live messages changed; no overwrite")
    updated=patch(old)
    save_backup(old)
    status=game_state(token)
    guard(game_status(status) in {"started","running","stopped"} and
          (game_status(status)=="stopped" or players(status)==0),
          "Players online or unverifiable")
    time.sleep(2)
    confirm=game_state(token)
    guard(game_status(confirm)==game_status(status) and
          (game_status(confirm)=="stopped" or players(confirm)==0),
          "Second player/status check failed")
    initially_running=game_status(status)!="stopped"
    stopped=False
    uploaded=False
    try:
        if initially_running:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
            stopped=True
        guard(digest(download_one(token,remote))==EXPECTED_SHA,"Concurrent mission modification detected")
        upload_file(token,remote,updated)
        uploaded=True
        guard(digest(download_one(token,remote))==digest(updated),"Uploaded file SHA mismatch")
        record(status="uploaded_readback_ok",old_sha=EXPECTED_SHA,new_sha=digest(updated),
               changed_file=FILE,original_messages_preserved=4,new_messages=2)
    except Exception:
        if uploaded:
            try:
                upload_file(token,remote,old)
                guard(digest(download_one(token,remote))==EXPECTED_SHA,"Rollback readback mismatch")
                record(status="rollback_success",old_sha=EXPECTED_SHA)
            except Exception as exc:
                record(status="manual_recovery_required",old_sha=EXPECTED_SHA)
                print("CRITICAL ROLLBACK ERROR",type(exc).__name__,flush=True)
        raise
    finally:
        if stopped:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:print("CRITICAL: restart request failed; check Nitrado",flush=True)
    if initially_running:wait_status(token,{"started","running"},attempts=50)
    guard(digest(download_one(token,remote))==digest(updated),"Post-restart messages changed")
    record(status="installed_and_nitrado_readback_verified",
           old_sha=EXPECTED_SHA,new_sha=digest(updated),changed_file=FILE,
           original_messages_preserved=4,new_messages=2,
           server_status=game_status(game_state(token)))
    print("V21 PASS: added 2 DayZ location messages; original 4 intact; no wipe; PS5 rendering untested")

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V21 ERROR:",type(exc).__name__,str(exc)[:160],file=sys.stderr)
        raise SystemExit(1)
