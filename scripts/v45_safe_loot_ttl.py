#!/usr/bin/env python3
"""V45: bounded, reversible 4-hour CE cleanup for ordinary loose map loot.

No two-restart counter in DayZ PS XML. 4h is wall-clock, not exactly two
restarts. Preserves all containers, bases, vehicle/batteries, building materials,
flags, kits, special keys, unique quest items and player inventories.
"""
from __future__ import annotations
import datetime as dt,hashlib,json,os,posixpath,sys,time,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
PATH="db/types.xml"
LIFETIME=14400
ALLOWED={"food","tools","weapons","clothes","medical","ammunition","drinks"}
PROTECTED=("barrel","crate","chest","case","container","tent","shelter","flag",
 "vehicle","motorbike","truck","carbattery","battery","wheel","tire",
 "fence","watchtower","plank","woodenlog","log","stone","nail","metalplate",
 "wire","rope","kit","key","stash","generator","cablereel","locker",
 "turret","fuel","canister","gasoline","woodpile","pileofwood",
 "building","territory","handmade","storage","ammo_box","seachest","gunrack")
OUT=Path("deploy/v45/ORDINARY_LOOT_CLEANUP_STATUS.json")
BACKUP=Path("deploy/v45/PRIVATE_TYPES_BEFORE_TTL.zip")
def guard(ok,msg):
 if not ok:raise NitradoError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def report(**k):
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({
    "version":"V45","mode":"wallclock ground-loot cleanup",
    "ttl_seconds":LIFETIME,"exact_two_restart_counter":False,
    "container_contents_untouched":True,"player_inventory_untouched":True,
    "vehicle_and_base_lifetimes_preserved":True,"wipe_performed":False,**k},
    indent=2)+"\n",encoding="utf-8")
def parse(raw):
 return ET.fromstring(raw,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def patch(old):
 root=parse(old)
 guard(root.tag=="types","Unexpected types.xml root")
 changed=[];ignored=0
 for t in root.findall("type"):
    name=t.get("name","")
    if not name or any(word in name.lower() for word in PROTECTED):
       ignored+=1;continue
    categories={c.get("name","").lower() for c in t.findall("category")}
    if not (categories&ALLOWED):continue
    life=t.find("lifetime");nominal=t.find("nominal")
    if life is None or nominal is None:continue
    try:l=int(life.text);n=int(nominal.text)
    except (TypeError,ValueError):continue
    if n<=0 or l<=LIFETIME:continue
    # Do not truncate very long-lifetime unusual loot entries: protecting
    # already persistent objects is more important than aggressive cleanup.
    if l>=604800:continue
    changed.append({"name":name,"previous_seconds":l,"new_seconds":LIFETIME})
    life.text=str(LIFETIME)
 guard(len(changed)<=900,"Too many CE entries selected; refuse broad economy damage")
 if not changed:return old,[]
 updated=ET.tostring(root,encoding="utf-8",xml_declaration=True)
 check=parse(updated)
 mapping={t.get("name"):t.findtext("lifetime") for t in check.findall("type")}
 guard(all(mapping[c["name"]]==str(LIFETIME) for c in changed),
       "Cleanup writeback missed an item")
 original=parse(old)
 for t in original.findall("type"):
     name=t.get("name")
     if any(x["name"]==name for x in changed):
         t.find("lifetime").text=str(LIFETIME)
 guard(ET.tostring(original)==ET.tostring(check),
       "Other types.xml attributes edited")
 return updated,changed
def backup(original):
 BACKUP.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
     z.writestr("dayzOffline.enoch/"+PATH,original)
     z.writestr("SHA256.txt",sha(original)+" "+PATH+"\n")
 with zipfile.ZipFile(BACKUP) as z:
     guard(z.testzip() is None and
       sha(z.read("dayzOffline.enoch/"+PATH))==sha(original),
       "Original types.xml rollback corrupt")
def main():
 token=os.getenv("NITRADO_API_TOKEN","").strip()
 guard(token and os.getenv("BEILEYS47_V45_APPROVED")=="yes",
       "No permission/secret")
 if (os.getenv("GITHUB_EVENT_NAME")=="schedule" and
         dt.datetime.now(dt.timezone.utc).date()>dt.date(2026,11,30)):
     report(status="RENTAL_EXPIRED_NO_ACTION");return
 mission=resolve_mission(token);remote=posixpath.join(mission,PATH)
 old=download_one(token,remote)
 changed,items=patch(old)
 if not items:
     report(status="ALREADY_CAPPED_OR_NO_QUALIFYING_LOOT",modified_types=0,
            no_restart=True)
     print("V45: Ordinary loot lifetimes already <=4h or no qualifying entries")
     return
 backup(old)
 state=game_state(token);status=game_status(state);online=players(state)
 if status not in ("started","running","stopped") or (status!="stopped" and online!=0):
     report(status="WAITING_FOR_IDLE",online_players=online,
            qualifying_types=len(items),no_restart=True)
     print("V45 WAIT: server occupied, no edits")
     return
 time.sleep(2)
 again=game_state(token)
 guard(game_status(again)==status and (status=="stopped" or players(again)==0),
       "Second zero-player check failed")
 stopped=False;restarted=False;attempted=False;success=False
 try:
     if status!="stopped":
         request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
         wait_status(token,{"stopped"},attempts=55)
         stopped=True
     guard(sha(download_one(token,remote))==sha(old),
           "Live CE source changed while stopping")
     attempted=True
     upload_file(token,remote,changed)
     guard(sha(download_one(token,remote))==sha(changed),
           "Live types.xml upload readback failed")
     if stopped:
         request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
         wait_status(token,{"started","running"},attempts=55)
         restarted=True
     guard(sha(download_one(token,remote))==sha(changed),
           "Post-restart CE types hash differs")
     success=True
     report(status="INSTALLED_AND_READBACK_VERIFIED",
            modified_type_count=len(items),
            modified_classnames=[x["name"] for x in items][:120],
            original_sha=sha(old),new_sha=sha(changed),
            server_status=game_status(game_state(token)))
     print("V45 LIVE SUCCESS: only ordinary loot TTL capped at 4h, containers/bases/vehicles untouched")
 except Exception:
     if attempted and not success:
         try:
             current=game_state(token)
             if game_status(current) in ("started","running"):
                 guard(players(current)==0,"Player joined; don't interrupt for rollback")
                 request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                 wait_status(token,{"stopped"},attempts=55)
                 stopped=True
             upload_file(token,remote,old)
             guard(sha(download_one(token,remote))==sha(old),
                   "Original CE rollback mismatch")
             report(status="ROLLED_BACK_ORIGINAL_TYPES")
             if stopped:
                 request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                 wait_status(token,{"started","running"},attempts=55)
                 restarted=True
         except Exception:
             report(status="CRITICAL_MANUAL_RESTORE")
     raise
 finally:
     if stopped and not restarted:
         try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
         except Exception:print("CRITICAL: server restart status unknown")
if __name__=="__main__":
 try:main()
 except Exception as e:
   print("V45 ERROR",type(e).__name__,str(e)[:200],file=sys.stderr)
   raise SystemExit(1)
