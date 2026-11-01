#!/usr/bin/env python3
"""BEILEYS47 V29: one-object ZONA47 live field pilot, never a 26-object mass deploy.

Coordinates from a calibrated 2048x2048 Livonia terrain raster; ground Y is not a
verified model origin. Target is one small vanilla guardbox, not a guaranteed
playable building. Requires zero players, source SHA guard, config rollback.
Does not touch player storage, CE, persistence, old object files, or execute wipe.
"""
from __future__ import annotations
import copy,hashlib,json,math,os,posixpath,sys,time,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,entries_at,entry_name,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,request_api_post,upload_file,wait_status
from v20_unlimited_sprint import setting_state

ROOT=Path(__file__).resolve().parents[1]
SURVEY=ROOT/"config/stage4_14_public_terrain_survey.json"
ROLES=ROOT/"config/stage4_10_placement_roles.json"
REL="custom/beileys47_v29_zone47_p1_guardbox.json"
CFG="cfggameplay.json"
BASE_SHA="191721e42a8f5b4081736c6777e12f1afe7797af2d6b8c3bd8f9019f24e3f1d7"
V16="custom/beileys47_v16_three_hotspots.json"
DOLNIK="custom/beileys47_dolnik_military_base_v9.json"
OUT=Path("deploy/v29/RESULT.json")
BACKUP=Path("deploy/v29/private_original_cfggameplay.zip")
CLASS="Land_Mil_GuardBox_Green"
ID="checkpoint_03"
RADIUS=45.0

def need(ok,msg):
    if not ok:raise NitradoError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def result(**extra):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
     "stage":"V29 P1","target":"ONE vanilla candidate guardbox",
     "live_server_modified_if_installed":True,"all_26_built":False,
     "PS4_PS5_visual_certain":False,"collisions_tested":False,
     "object_origin_verified":False,"provider_world_backup_verified":False,
     "full_world_wipe_requested":False,"persistence_storage_unchanged":True,
     **extra},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def build_scene():
    source=json.loads(SURVEY.read_text(encoding="utf-8"))
    need(source["selected_site"]=="central" and source["deployment_allowed"] is False,
         "Calibrated ground survey unexpectedly marked deploy approved")
    site=[x for x in source["candidate_sites"] if x["region"]=="central"]
    need(len(site)==1 and site[0]["center_x"]==9000 and site[0]["center_z"]==7800,
         "Unexpected source site")
    p=[x for x in site[0]["placements"] if x["id"]==ID]
    need(len(p)==1 and p[0]["class_candidate_unverified"]==CLASS,
         "Guardbox class candidate differs from terrain survey")
    roles=json.loads(ROLES.read_text(encoding="utf-8"))["placement_options"]
    need(roles[ID]["proposed_visual_model_classname"]==CLASS,
         "Role to class mapping changed")
    values=[float(p[0][key]) for key in ("x","terrain_y","z")]
    need(all(math.isfinite(v) for v in values),"Nonfinite terrain")
    x,y,z=values
    need(9030<x<9090 and 290<y<315 and 7800<z<7860,"Unexpected site coordinates")
    need(float(p[0]["local_12m_ground_relief_m"])<2.0,
         "Terrain too uneven for single guardbox pilot")
    obj={"name":CLASS,"pos":[round(x,4),round(y,4),round(z,4)],
         "ypr":[120,0,0],"scale":1.0,"enableCEPersistency":False}
    return (json.dumps({"Objects":[obj]},indent=2)+"\n").encode(),obj

def patch_gameplay(blob:bytes):
    gp=json.loads(blob.decode("utf-8-sig"))
    need(isinstance(gp,dict) and isinstance(gp.get("WorldsData"),dict),
         "Missing valid gameplay")
    names=gp["WorldsData"].get("objectSpawnersArr")
    need(isinstance(names,list) and len(names)==len(set(names)) and
         all(isinstance(v,str) for v in names),"Spawner list invalid")
    need(V16 in names and DOLNIK in names,
         "Existing V16/Dolnik objects not registered")
    need(REL not in names, "Pilot file already active")
    need(len(names)<=20,"Unexpectedly many world spawners")
    modified=copy.deepcopy(gp)
    modified["WorldsData"]["objectSpawnersArr"].append(REL)
    restore=copy.deepcopy(modified)
    restore["WorldsData"]["objectSpawnersArr"]=names
    need(restore==gp,"Other gameplay fields altered")
    new=(json.dumps(modified,indent=2,ensure_ascii=False)+"\n").encode()
    need(json.loads(new)==modified,"Invalid JSON candidate")
    return new,names

def check_scene_separation(token,mission,files,obj):
    checked=0
    for rel in files:
        need(".." not in rel and rel.endswith(".json"),"Unsafe existing spawner path")
        content=json.loads(download_one(token,posixpath.join(mission,rel)))
        existing=content.get("Objects")
        need(isinstance(existing,list),"Existing spawner schema not supported")
        for item in existing:
            pos=item.get("pos")
            need(isinstance(pos,list) and len(pos)==3,"Existing object location unknown")
            x,z=float(pos[0]),float(pos[2])
            need(math.isfinite(x) and math.isfinite(z),"Existing object position invalid")
            distance=math.hypot(x-obj["pos"][0],z-obj["pos"][2])
            need(distance>=RADIUS,
                 "Pilot is within 45 metres of configured existing Object Spawner object")
            checked+=1
    return checked

def backup(old):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/cfggameplay.json",old)
        z.writestr("SHA256.txt",sha(old)+"  cfggameplay.json\n")
    with zipfile.ZipFile(BACKUP) as z:
        need(z.testzip() is None and
             sha(z.read("dayzOffline.enoch/cfggameplay.json"))==sha(old),
             "Rollback copy integrity failed")

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    need(token and os.environ.get("BEILEYS47_V29_PILOT_APPROVED")=="yes",
         "Nitrado secret or owner pilot approval missing")
    mission=resolve_mission(token)
    cfg_path=posixpath.join(mission,CFG)
    p1_path=posixpath.join(mission,REL)
    old=download_one(token,cfg_path)
    if sha(old)!=BASE_SHA:
        result(status="blocked_source_drift",observed_sha=sha(old))
        raise NitradoError("Current gameplay differs from verified V21 baseline; no overwrite")
    new,existing_spawners=patch_gameplay(old)
    raw_p1,obj=build_scene()
    known=check_scene_separation(token,mission,existing_spawners,obj)
    names={entry_name(x) for x in entries_at(token,posixpath.join(mission,"custom"))}
    need(posixpath.basename(REL) not in names,
         "Pilot scene filename already exists; do not overwrite another file")
    backup(old)
    gs=game_state(token)
    st=game_status(gs)
    count=players(gs)
    if st not in {"started","running","stopped"} or (st!="stopped" and count!=0):
        result(status="blocked_players_or_status",player_count=count)
        raise NitradoError("Cannot interrupt game with players connected or unknown count")
    need(setting_state(gs)=="enabled","cfgGameplay switch is not confirmed enabled")
    time.sleep(2)
    again=game_state(token)
    need(game_status(again)==st and (st=="stopped" or players(again)==0),
         "Second player/state check failed")
    need(setting_state(again)=="enabled","cfgGameplay became unavailable")
    stopped=False
    new_scene_uploaded=False
    gameplay_attempted=False
    try:
        if st!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=45)
            stopped=True
        need(sha(download_one(token,cfg_path))==BASE_SHA,
             "Gameplay changed while server stopping")
        upload_file(token,p1_path,raw_p1)
        new_scene_uploaded=True
        need(sha(download_one(token,p1_path))==sha(raw_p1),
             "Pilot JSON readback hash mismatch")
        gameplay_attempted=True
        upload_file(token,cfg_path,new)
        need(sha(download_one(token,cfg_path))==sha(new),
             "Reference gameplay upload did not verify")
        result(status="uploaded_verified_restart_pending",
               original_gameplay_sha=BASE_SHA,
               new_gameplay_sha=sha(new),pilot_scene_sha=sha(raw_p1),
               old_scenes_checked=len(existing_spawners),
               old_objects_checked=known,object=obj,
               no_CE_or_world_persistence_changes=True)
    except Exception:
        if gameplay_attempted:
            try:
                upload_file(token,cfg_path,old)
                need(sha(download_one(token,cfg_path))==BASE_SHA,
                     "Rollback gameplay hash mismatch")
                result(status="rolled_back_gameplay_reference",
                       orphan_nonreferenced_pilot_may_remain=new_scene_uploaded)
            except Exception:
                result(status="manual_recovery_required",
                       orphan_nonreferenced_pilot_may_remain=new_scene_uploaded)
        else:
            result(status="not_referenced",orphan_nonreferenced_pilot_may_remain=new_scene_uploaded)
        raise
    finally:
        if stopped:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:
                print("CRITICAL: restart request failed, check Nitrado",flush=True)
    if stopped:wait_status(token,{"started","running"},attempts=55)
    need(sha(download_one(token,cfg_path))==sha(new),
         "Post-restart gameplay mismatch")
    need(sha(download_one(token,p1_path))==sha(raw_p1),
         "Post-restart scene mismatch")
    result(status="installed_and_readback_verified",
           original_gameplay_sha=BASE_SHA,new_gameplay_sha=sha(new),
           scene_sha=sha(raw_p1),object=obj,
           old_scenes_checked=len(existing_spawners),old_objects_checked=known,
           server_status=game_status(game_state(token)),
           next_step="PS5 position/ground contact/door collision and PS4 performance test")
    print("PASS V29 P1: 1 pilot guardbox, two remote files verified, no wipe")

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V29 GUARDED:",type(e).__name__,str(e)[:200],file=sys.stderr)
        raise SystemExit(1)
