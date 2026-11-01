#!/usr/bin/env python3
"""V35 BEILEYS47: install 25 additional ZONA47 classes in the live PS server.

OWNER AUTHORIZED experimental installation including potential wipe (not used).
Zero players, verified live source invariants, zipped original config+old scenes,
single isolated new spawner JSON, hash/readback/restart, fail-closed and rollback.
Gameplay verification on a real PS5/PS4 is *not* claimed by remote configuration.
"""
from __future__ import annotations
import copy,hashlib,json,math,os,posixpath,sys,time,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,entries_at,entry_name,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,request_api_post,upload_file,wait_status
from v20_unlimited_sprint import setting_state

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"config/v33/BEILEYS47_ZONE47_25_NOT_LIVE.json"
GATES=ROOT/"config/v33/QUALITY_GATES_NOT_PS5_TESTED.json"
NEW="custom/beileys47_v35_zone47_full_25.json"
P1="custom/beileys47_v29_zone47_p1_guardbox.json"
V16="custom/beileys47_v16_three_hotspots.json"
DOLNIK="custom/beileys47_dolnik_military_base_v9.json"
CFG="cfggameplay.json"
OUT=Path("deploy/v35/LIVE_DEPLOY_RESULT.json")
ARCHIVE=Path("deploy/v35/private_live_before_v35.zip")
NEW_SHA_EXPECTED=None
def sha(blob):return hashlib.sha256(blob).hexdigest()
def demand(ok,reason):
    if not ok:raise NitradoError(reason)
def result(**data):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
       "release":"BEILEYS47 V35 ZONA47 full experimental installation",
       "game":"DayZ PlayStation Livonia",
       "owner_authorized":True,
       "no_wipe":True,"no_player_storage_access":True,
       "physical_PS5_PS4_collision_tests_completed":False,
       "full_world_backup_verified":False,
       **data},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def candidate():
    blob=SOURCE.read_bytes()
    js=json.loads(blob)
    gates=json.loads(GATES.read_text())
    objects=js.get("Objects")
    demand(isinstance(objects,list) and len(objects)==25,"Candidate must have 25 objects")
    demand(gates["p1_preserved"] is True and gates["visual_clearance_conflicts"]==0
           and gates["candidate_new_objects"]==25
           and gates["PS4_PS5_model_footprint_validated"] is False
           and gates["deployment_allowed"] is False,
           "Candidate provenance/geometric preflight failed")
    coords=set()
    for o in objects:
       demand(isinstance(o,dict) and isinstance(o.get("name"),str)
             and o["name"].startswith("Land_"),"Non-vanilla/unknown object class syntax")
       p=o.get("pos")
       demand(isinstance(p,list) and len(p)==3
              and all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) for v in p),
              "Invalid coordinates")
       x,y,z=map(float,p)
       demand(8800<x<9100 and 280<y<340 and 7650<z<7950,
              "One candidate outside surveyed central site")
       demand(o.get("ypr")==[120,0,0] and o.get("scale")==1
              and o.get("enableCEPersistency") is False,"Unexpected P3D placement data")
       key=(round(x,3),round(z,3))
       demand(key not in coords,"Duplicate terrain position")
       coords.add(key)
    return blob,objects
def patched_gameplay(original):
    gp=json.loads(original.decode("utf-8-sig"))
    demand(isinstance(gp,dict) and isinstance(gp.get("WorldsData"),dict)
           and isinstance(gp.get("PlayerData"),dict),
           "Not recognized DayZ gameplay JSON")
    items=gp["WorldsData"].get("objectSpawnersArr")
    demand(isinstance(items,list) and all(isinstance(x,str) for x in items)
           and len(items)==len(set(items)) and len(items)<=24,
           "Object spawner registration list invalid")
    demand(all(x in items for x in (P1,V16,DOLNIK)),
           "Existing known scenes missing; don't overwrite")
    demand(NEW not in items,"V35 scene already registered: no duplicate installation")
    stamina=gp["PlayerData"].get("StaminaData",{})
    movement=gp["PlayerData"].get("MovementData",{})
    demand(all(stamina.get(x)==0 for x in (
      "sprintStaminaModifierErc","sprintStaminaModifierCro",
      "staminaKgToStaminaPercentPenalty")),"V20 sprint baseline drifted")
    demand(movement.get("timeToSprint")==0.01 and movement.get("timeToStrafeSprint")==0.01,
           "V20 transition baseline drifted")
    edited=copy.deepcopy(gp)
    edited["WorldsData"]["objectSpawnersArr"].append(NEW)
    demand(len(edited["WorldsData"]["objectSpawnersArr"])==len(items)+1,
           "Unexpected registration diff")
    copyback=copy.deepcopy(edited)
    copyback["WorldsData"]["objectSpawnersArr"]=items
    demand(copyback==gp,"Non-target gameplay setting changed")
    return (json.dumps(edited,indent=2,ensure_ascii=False)+"\n").encode(),items
def separated(objects,oldscenes):
    # The 25 new objects must not interfere with previously registered assets.
    # P1 is already screened into V32, and 3 other live regions are geographically distinct.
    checked=0
    for rel,blob in oldscenes.items():
        scene=json.loads(blob)
        prev=scene.get("Objects")
        demand(isinstance(prev,list),"Existing scene malformed: "+rel)
        for one in prev:
            pos=one.get("pos")
            demand(isinstance(pos,list) and len(pos)==3,"Malformed prior scene")
            x,z=float(pos[0]),float(pos[2])
            for o in objects:
                sep=math.hypot(x-o["pos"][0],z-o["pos"][2])
                if rel==P1:
                    demand(sep>=7.0,"V35 prop too close to installed P1")
                else:
                    demand(sep>=30.0,"V35 prop too close to a previous world scene")
            checked+=1
    return checked
def snapshot(files):
    ARCHIVE.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ARCHIVE,"w",zipfile.ZIP_DEFLATED) as z:
        for rel,blob in files.items():
            z.writestr("dayzOffline.enoch/"+rel,blob)
        z.writestr("SHA256.txt","".join(
           sha(blob)+"  "+rel+"\n" for rel,blob in files.items()))
    with zipfile.ZipFile(ARCHIVE) as z:
        demand(z.testzip() is None,"Saved rollback archive integrity failed")
        for rel,blob in files.items():
            demand(sha(z.read("dayzOffline.enoch/"+rel))==sha(blob),
                   "Backup readback differs: "+rel)
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    demand(token and os.environ.get("BEILEYS47_V35_OWNER_APPROVED")=="yes",
           "Owner approval or Nitrado token unavailable")
    mission=resolve_mission(token)
    raw,objects=candidate()
    cfgpath=posixpath.join(mission,CFG)
    newpath=posixpath.join(mission,NEW)
    live=download_one(token,cfgpath)
    amended,registered=patched_gameplay(live)
    oldscenes={rel:download_one(token,posixpath.join(mission,rel)) for rel in registered}
    count=separated(objects,oldscenes)
    existing={entry_name(x) for x in entries_at(token,posixpath.join(mission,"custom"))}
    demand(posixpath.basename(NEW) not in existing,
           "Target file name already exists; refuse overwriting any scene")
    originals={CFG:live,**oldscenes}
    snapshot(originals)
    state=game_state(token)
    status=game_status(state)
    online=players(state)
    if status not in {"started","running","stopped"} or (status!="stopped" and online!=0):
        result(status="BLOCKED_PLAYERS_OR_SERVER_STATE",reported_players=online,
               registered_scene_count=len(registered),old_objects_checked=count)
        raise NitradoError("Player connected / missing player count; no server changes")
    demand(setting_state(state)=="enabled","cfgGameplay switch disabled or unknown")
    time.sleep(2)
    again=game_state(token)
    demand(game_status(again)==status and
       (status=="stopped" or players(again)==0) and setting_state(again)=="enabled",
       "Second player/status/cfgGameplay preflight failed")
    was_running=status!="stopped"
    stopped=False
    file_uploaded=False
    gameplay_attempted=False
    installed=False
    restarted=False
    try:
       if was_running:
           request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
           wait_status(token,{"stopped"},attempts=50)
           stopped=True
       demand(sha(download_one(token,cfgpath))==sha(live),
              "Live gameplay changed after stop; fail closed")
       for rel,blob in oldscenes.items():
           demand(sha(download_one(token,posixpath.join(mission,rel)))==sha(blob),
                  "An old scene changed; fail closed")
       upload_file(token,newpath,raw)
       file_uploaded=True
       demand(sha(download_one(token,newpath))==sha(raw),
              "New scene did not verify after upload")
       gameplay_attempted=True
       upload_file(token,cfgpath,amended)
       demand(sha(download_one(token,cfgpath))==sha(amended),
              "Updated gameplay did not verify")
       result(status="UPLOADED_BEFORE_RESTART",new_object_count=len(objects),
              previous_objects_audited=count,old_cfg_sha=sha(live),
              new_cfg_sha=sha(amended),new_scene_sha=sha(raw))
       if was_running:
           request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
           wait_status(token,{"started","running"},attempts=55)
           restarted=True
       demand(sha(download_one(token,cfgpath))==sha(amended),
              "Post-restart gameplay file changed")
       demand(sha(download_one(token,newpath))==sha(raw),
              "Post-restart scene file changed")
       reg=json.loads(download_one(token,cfgpath))["WorldsData"]["objectSpawnersArr"]
       demand(reg==registered+[NEW],"Incorrect spawner registry after restart")
       demand(game_status(game_state(token)) in {"started","running"} if was_running else True,
              "Server not running after install")
       installed=True
       result(status="INSTALLED_AND_NITRADO_READBACK_VERIFIED",
              old_cfg_sha=sha(live),new_cfg_sha=sha(amended),
              new_scene_sha=sha(raw),original_scene_count=len(registered),
              new_object_count=len(objects),total_zone47_plan_objects=26,
              prior_scene_objects_checked=count,
              server_state=game_status(game_state(token)),
              next="Required PS5/PS4 rendering, placement, interaction and FPS check")
       print("V35 INSTALL SUCCESS: 25 new ZONA47 objects registered, P1 retained, no wipe")
    except Exception:
       if gameplay_attempted and not installed:
           try:
               current=game_status(game_state(token))
               if current in {"started","running"}:
                   # Do not disrupt a player who might have joined since restart.
                   statusnow=game_state(token)
                   demand(players(statusnow)==0,
                          "New player joined: do not stop for automatic rollback")
                   request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                   wait_status(token,{"stopped"},attempts=45)
                   stopped=True
               upload_file(token,cfgpath,live)
               demand(sha(download_one(token,cfgpath))==sha(live),
                      "Original gameplay rollback mismatched")
               result(status="ROLLED_BACK_ORIGINAL_GAMEPLAY",
                      unreferenced_new_scene_may_remain=file_uploaded)
               if was_running:
                   request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                   wait_status(token,{"started","running"},attempts=55)
                   restarted=True
           except Exception as e:
               result(status="CRITICAL_MANUAL_RECOVERY_NEEDED",
                      unreferenced_new_scene_may_remain=file_uploaded)
               print("CRITICAL rollback failed:",type(e).__name__,flush=True)
       raise
    finally:
       if was_running and stopped and not restarted:
           try:
               request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
               wait_status(token,{"started","running"},attempts=55)
           except Exception:
               print("CRITICAL cannot confirm server running: check Nitrado",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V35 DEPLOY BLOCKED/ERROR:",type(e).__name__,str(e)[:190],file=sys.stderr)
        raise SystemExit(1)
