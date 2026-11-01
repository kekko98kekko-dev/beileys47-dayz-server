#!/usr/bin/env python3
"""BEILEYS47 nighttime setting inspector and strictly guarded updater.
Supports only a uniquely identified numeric serverNightTimeAcceleration setting.
No other game-setting updates and no wipe.
"""
import json,os,sys,time
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,request_api_post,wait_status
OUT=Path("deploy/v16/NIGHT_RESULT.json")
def save(**kwargs):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"service":SERVICE_ID,"feature":"night_only",
      "ps5_tested":False,"wipe":False,**kwargs},indent=2)+"\n")
def fail(x):
    raise NitradoError(x)
def run():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:fail("Missing Nitrado secret")
    gs=game_state(token)
    settings=gs.get("settings")
    if not isinstance(settings,dict):
        save(status="not_supported",reason="Nitrado has no structured settings in this API response")
        print("No structured settings; no changes.")
        return
    allowed={"servernighttimeacceleration","nighttimeacceleration",
             "server_night_time_acceleration"}
    hits=[]
    for category,items in settings.items():
        if not isinstance(items,dict):continue
        for key,value in items.items():
            if str(key).lower().replace(" ","") in allowed:
                hits.append((category,key,value))
    safe_keys=[f"{cat}.{key}" for cat,key,_ in hits]
    print("Night setting keys discovered:",safe_keys,flush=True)
    if len(hits)!=1:
        save(status="not_supported",reason="Could not resolve unique night multiplier",
             matches=safe_keys)
        return
    cat,key,val=hits[0]
    try:
        actual=float(val)
    except (TypeError,ValueError):
        save(status="not_supported",reason="Night setting value is not numerical",matches=safe_keys)
        return
    if not (0.1<=actual<=64):
        save(status="not_supported",reason="Night multiplier out of documented bounds",matches=safe_keys)
        return
    save(status="inspected",setting=f"{cat}.{key}",previous=actual,target=8)
    if actual==8:
        save(status="already_configured",setting=f"{cat}.{key}",previous=actual,target=8)
        return
    state=game_status(gs)
    count=players(gs)
    if state not in {"started","running","stopped"} or (state!="stopped" and count!=0):
        save(status="skipped",reason="players online, unknown player count or unexpected server state",
             setting=f"{cat}.{key}")
        return
    stopped=state=="stopped"
    try:
        if not stopped:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/settings",
                         {"category":cat,"key":key,"value":"8"})
        verify=game_state(token).get("settings",{}).get(cat,{}).get(key)
        if str(verify).strip() not in {"8","8.0"}:
            fail("Nitrado setting readback mismatch")
        save(status="verified",setting=f"{cat}.{key}",previous=actual,target=8)
    except Exception:
        save(status="update_failed",setting=f"{cat}.{key}",previous=actual,target=8)
        raise
    finally:
        try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
        except Exception: print("WARNING: Start request failed; check Nitrado.",flush=True)
    print("Night time multiplier updated to 8; restart requested.",flush=True)
if __name__=="__main__":
    try:run()
    except Exception as e:
        print("NIGHT ERROR:",str(e)[:200],file=sys.stderr)
        sys.exit(1)
