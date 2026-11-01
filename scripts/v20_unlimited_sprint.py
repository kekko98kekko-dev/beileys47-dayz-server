#!/usr/bin/env python3
"""BEILEYS47 V20: guarded DayZ PS5 unlimited sprint, quicker sprint transition.

Only cfggameplay.json; preserves ALL existing WorldData/spawners, player kit, settings.
No world/storage/persistence access. Refuses drift from last V18/V19 live baseline.
Does not attempt to alter maximum movement speed (not an exposed gameplay setting).
"""
from __future__ import annotations
import copy,hashlib,json,os,posixpath,sys,time,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import (
    game_state,game_status,players,upload_file,request_api_post,wait_status,
)

REL="cfggameplay.json"
# Confirmed from live Nitrado V18 remote snapshot; V19 made no gameplay file edits.
BASE_SHA="c10b1a0d42f3ab2c057bb6fe87ceeaaf1c0cfb4d0e37adbaa03eb94dc4b42950"
OUT=Path("deploy/v20/RESULT.json")
BACKUP=Path("deploy/v20/private_cfggameplay_before_v20.zip")
STAMINA_TARGET={
    "sprintStaminaModifierErc":0.0,       # upright sprint consumes no stamina
    "sprintStaminaModifierCro":0.0,       # crouched sprint consumes no stamina
    "staminaKgToStaminaPercentPenalty":0.0, # backpack/weight does not shrink bar
}
MOVEMENT_TARGET={
    "timeToSprint":0.01,                 # fastest documented transition, NOT faster max speed
    "timeToStrafeSprint":0.01,
}

def need(condition:bool,message:str):
    if not condition:raise NitradoError(message)

def digest(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def report(**fields):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
        "service_id":SERVICE_ID,"version":"V20",
        "features":"no sprint stamina drain + faster sprint transition",
        "maximum_speed_multiplier_changed":False,
        "ps5_runtime_tested":False,
        "no_persistence_files_modified":True,
        "wipe":False,**fields
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def patch(old:bytes):
    """Return candidate and exact dictionary of modified gameplay paths.
    Reject any missing, nonnumeric or unexpected structure rather than silently editing.
    """
    parsed=json.loads(old.decode("utf-8-sig"))
    need(isinstance(parsed,dict),"Malformed gameplay root")
    worlds=parsed.get("WorldsData")
    need(isinstance(worlds,dict) and isinstance(worlds.get("objectSpawnersArr"),list),
         "Missing original V16 world spawners")
    need("custom/beileys47_v16_three_hotspots.json" in worlds["objectSpawnersArr"],
         "V16 static world spawner not registered")
    need("custom/beileys47_dolnik_military_base_v9.json" in worlds["objectSpawnersArr"],
         "Dolnik scene not registered; do not rewrite")
    pd=parsed.get("PlayerData")
    need(isinstance(pd,dict),"PlayerData missing")
    stamina=pd.get("StaminaData")
    movement=pd.get("MovementData")
    need(isinstance(stamina,dict) and isinstance(movement,dict),
         "StaminaData/MovementData absent")
    need(isinstance(stamina.get("staminaMax"),(int,float)) and
         type(stamina["staminaMax"]) is not bool and
         5<=stamina["staminaMax"]<=1000,"Stamina max invalid: do not reset")
    need(isinstance(stamina.get("staminaMinCap"),(int,float)) and
         type(stamina["staminaMinCap"]) is not bool and stamina["staminaMinCap"]>0,
         "Stamina minimum invalid")
    modified=copy.deepcopy(parsed)
    changes={}
    for group,targets in (("StaminaData",STAMINA_TARGET),("MovementData",MOVEMENT_TARGET)):
        for k,value in targets.items():
            v=modified["PlayerData"][group].get(k)
            need(type(v) in (float,int) and 0<=v<=100000,
                 "Missing or invalid existing gameplay number: "+group+"."+k)
            changes["PlayerData."+group+"."+k]={"before":v,"after":value}
            modified["PlayerData"][group][k]=value
    # Exact semantic diff: restore only intended keys; everything else identical.
    pristine=copy.deepcopy(modified)
    for group,targets in (("StaminaData",STAMINA_TARGET),("MovementData",MOVEMENT_TARGET)):
        for k in targets:
            pristine["PlayerData"][group][k]=parsed["PlayerData"][group][k]
    need(pristine==parsed,"Unexpected non-target gameplay change")
    encoded=(json.dumps(modified,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
    need(json.loads(encoded)==modified,"Candidate JSON invalid")
    return encoded,changes

def setting_state(gs:dict):
    settings=gs.get("settings")
    if not isinstance(settings,dict):return "unknown"
    hits=[]
    for category,items in settings.items():
        if isinstance(items,dict):
            for key,val in items.items():
                if "".join(c for c in str(key).lower() if c.isalnum())=="enablecfggameplayfile":
                    hits.append(val)
    if len(hits)!=1:return "unknown"
    val=hits[0]
    if val is True or val==1 or str(val).strip().lower() in {"1","true","yes"}:return "enabled"
    if val is False or val==0 or str(val).strip().lower() in {"0","false","no"}:return "disabled"
    return "unknown"

def make_backup(blob:bytes):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/cfggameplay.json",blob)
        z.writestr("SHA256.txt",digest(blob)+"  cfggameplay.json\n")
    with zipfile.ZipFile(BACKUP) as z:
        need(z.testzip() is None,"Backup ZIP failed checksum")
        need(digest(z.read("dayzOffline.enoch/cfggameplay.json"))==digest(blob),
             "Backup does not match original")
    print("Exact original gameplay backup created",flush=True)

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    need(bool(token),"Missing Nitrado access secret")
    need(os.environ.get("BEILEYS47_V20_APPROVED")=="yes","V20 not approved")
    mission=resolve_mission(token)
    remote=posixpath.join(mission,REL)
    original=download_one(token,remote)
    if digest(original)!=BASE_SHA:
        report(status="blocked_baseline_drift",observed_sha=digest(original))
        raise NitradoError("Gameplay source SHA differs from last verified V18/V19 live baseline")
    new,changes=patch(original)
    make_backup(original)
    first=game_state(token)
    status=game_status(first)
    count=players(first)
    need(status in {"started","running","stopped"} and (status=="stopped" or count==0),
         "Online/unknown players or server status")
    feature=setting_state(first)
    # Do not silently deploy an ignored config file.
    if feature=="disabled":
        report(status="blocked_enableCfgGameplayFile_disabled",setting_state=feature)
        raise NitradoError("Gameplay JSON not enabled by Nitrado; manual setting review required")
    if feature=="unknown":
        print("WARNING: Nitrado API does not expose enableCfgGameplayFile; gameplay effect needs PS5 verification",flush=True)
    time.sleep(2)
    second=game_state(token)
    status2=game_status(second)
    need(status2 in {"started","running","stopped"} and
         (status2=="stopped" or players(second)==0),
         "Second player/status preflight failed")
    need(status2==status,"Server changed status during preflight")
    need(setting_state(second)!="disabled","Gameplay JSON disabled")
    running_before=status2!="stopped"
    stopped_by_us=False
    uploaded=False
    try:
        if running_before:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
            stopped_by_us=True
        # Fail closed if a concurrent administrator edited this file.
        need(digest(download_one(token,remote))==BASE_SHA,"Gameplay drift during stop")
        upload_file(token,remote,new)
        uploaded=True
        need(digest(download_one(token,remote))==digest(new),"Upload readback mismatch")
        report(status="uploaded_verified_pending_restart",before_sha=digest(original),
               after_sha=digest(new),changed_values=changes,setting_state=feature)
    except Exception:
        if uploaded:
            try:
                upload_file(token,remote,original)
                need(digest(download_one(token,remote))==BASE_SHA,
                     "Rollback upload readback mismatch")
                report(status="rolled_back_after_error",before_sha=BASE_SHA)
            except Exception as rollback_error:
                report(status="manual_recovery_required",before_sha=BASE_SHA)
                print("CRITICAL: rollback failed",type(rollback_error).__name__,flush=True)
        raise
    finally:
        if stopped_by_us:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:
                print("CRITICAL: restart failed, check Nitrado status",flush=True)
    if running_before:
        wait_status(token,{"started","running"},attempts=50)
    need(digest(download_one(token,remote))==digest(new),
         "Post-start gameplay readback mismatch")
    report(status="installed_readback_verified",before_sha=BASE_SHA,
           after_sha=digest(new),changed_values=changes,
           server_status=game_status(game_state(token)),
           setting_state=feature)
    print("V20 SUCCESS: sprint drain 0, no load penalty, instant sprint transition; max speed vanilla",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V20 ERROR:",type(e).__name__,str(e)[:190],file=sys.stderr)
        raise SystemExit(1)
