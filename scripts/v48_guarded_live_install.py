#!/usr/bin/env python3
"""BEILEYS47 V48: ONE guarded build placement config install on Nitrado.

No world/storage edits, no wipes, no scheduled retries. STOP if any players
are online, source SHA differs from independent live audit or gameplay disabled.
Backup the exact original cfggameplay.json before changing the file.
"""
from __future__ import annotations
import hashlib,json,os,posixpath,sys,time,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import (
    game_state,game_status,players,upload_file,request_api_post,wait_status
)
from v20_unlimited_sprint import setting_state
from v48_build_anywhere_preview import apply_preview,BALANCED
BASE_SHA="02d2a587131f002294b465b2ac4c775c301e12c1cfc566a4b4ac9f35c25d010c"
PROFILE="balanced"
REL="cfggameplay.json"
REPORT=Path("deploy/v48/CONTROLLED_INSTALL_STATUS.json")
BACKUP=Path("deploy/v48/PRIVATE_ORIGINAL_CF_GGAMEPLAY.zip")
def digest(b):return hashlib.sha256(b).hexdigest()
def need(ok,reason):
    if not ok:raise NitradoError(reason)
def report(**fields):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "version":"V48","scope":"BALANCED BUILDING ONLY",
        "target_file":REL,"world_wipe":False,"other_mission_files_touched":False,
        "storage_1_edited":False,"ps5_building_verified":False,**fields
    },indent=2)+"\n")
def parsed(b):
    v=json.loads(b)
    need(isinstance(v,dict),"Invalid gameplay JSON")
    return v
def exact_semantics(current,expected):
    return parsed(current)==parsed(expected)
def make_backup(original):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/cfggameplay.json",original)
        z.writestr("SHA256.txt",digest(original)+"  dayzOffline.enoch/cfggameplay.json\n")
    with zipfile.ZipFile(BACKUP) as z:
        need(z.testzip() is None and
             digest(z.read("dayzOffline.enoch/cfggameplay.json"))==digest(original),
             "Failed exact-source backup verification")
def health(token):
    gs=game_state(token)
    return game_status(gs),players(gs),setting_state(gs)
def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    need(token and os.getenv("BEILEYS47_V48_APPROVED")=="yes",
         "No API secret or explicit V48 approval")
    mission=resolve_mission(token)
    remote=posixpath.join(mission,REL)
    original=download_one(token,remote)
    observed=digest(original)
    need(observed==BASE_SHA,
         "Source differs from independently audited V48 SHA. Refuse to overwrite.")
    candidate,changed=apply_preview(original,PROFILE)
    need(len(changed)==len(BALANCED)==5,
         "Expected exactly five previously disabled build checks")
    before=parsed(original); after=parsed(candidate)
    for block in ("GeneralData","PlayerData","WorldsData","UIData","MapData","VehicleData"):
        need(before.get(block)==after.get(block),"Unexpected nonbuilding edit "+block)
    current_status,count,enabled=health(token)
    if enabled!="enabled":
        report(status="BLOCKED_GAMEPLAY_SETTING_NOT_CONFIRMED",settings=enabled)
        print("V48 NO ACTION: gameplay JSON is not confirmed enabled",flush=True)
        return
    if current_status not in ("started","running") or count!=0:
        report(status="WAITING_FOR_IDLE_NO_CHANGES",server_status=current_status,
               players_online=count,original_sha256=observed)
        print("V48 NO ACTION: server not running idle with known player count 0",
              "status:",current_status,"players:",count,flush=True)
        return
    time.sleep(2)
    status2,count2,enabled2=health(token)
    if status2!=current_status or count2!=0 or enabled2!="enabled":
        report(status="PLAYER_OR_GAMEPLAY_STATE_CHANGED_NO_ACTION")
        print("V48 NO ACTION: second idle preflight failed",flush=True)
        return
    make_backup(original)
    report(status="BACKUP_VERIFIED_PRE_STOP",original_sha256=observed,
           candidate_sha256=digest(candidate),changed_keys=changed)
    stopped=False; restarted=False; upload_attempted=False; installed=False
    try:
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
        stopped=True
        wait_status(token,{"stopped"},attempts=55)
        need(digest(download_one(token,remote))==observed,
             "Config edited by another administrator during stop")
        upload_attempted=True
        upload_file(token,remote,candidate)
        need(exact_semantics(download_one(token,remote),candidate),
             "Post-upload JSON not semantically equal to audited candidate")
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
        wait_status(token,{"started","running"},attempts=55)
        restarted=True
        # Short readback repeat to avoid making a judgement on a stale transient.
        remote_after=download_one(token,remote)
        if not exact_semantics(remote_after,candidate):
            time.sleep(2)
            remote_after=download_one(token,remote)
        need(exact_semantics(remote_after,candidate),
             "Post-restart gameplay settings semantic mismatch")
        installed=True
        report(status="INSTALLED_SEMANTICALLY_VERIFIED",original_sha256=observed,
               uploaded_sha256=digest(candidate),live_sha256=digest(remote_after),
               raw_hash_same_as_candidate=digest(remote_after)==digest(candidate),
               fields_changed=changed,server_status=health(token)[0],
               no_container_stacking_claim=True)
        print("V48 LIVE SUCCESS: 5 balanced building switches verified after restart, no wipe.",flush=True)
    except Exception as exc:
        if upload_attempted and not installed:
            try:
                gs=game_state(token)
                if game_status(gs) in ("started","running"):
                    need(players(gs)==0,"Player connected; defer rollback to manual maintenance")
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                    wait_status(token,{"stopped"},attempts=55)
                    stopped=True
                    restarted=False
                need(game_status(game_state(token))=="stopped",
                     "Server state unknown: refuse rollback")
                current=download_one(token,remote)
                # Never overwrite an administrator's unrelated edits.
                need(exact_semantics(current,candidate) or digest(current)==observed,
                     "Unexpected remote edits: manual recovery only")
                if digest(current)!=observed:
                    upload_file(token,remote,original)
                    need(digest(download_one(token,remote))==observed,
                         "Exact original gameplay rollback hash mismatch")
                report(status="ROLLED_BACK_AFTER_INSTALL_FAILURE",
                       original_sha256=observed,error_type=type(exc).__name__)
            except Exception as recovery:
                report(status="CRITICAL_MANUAL_RECOVERY_REQUIRED",
                       original_sha256=observed,error_type=type(exc).__name__,
                       recovery_error_type=type(recovery).__name__)
                print("CRITICAL V48: manual restore/inspection required.",flush=True)
        raise
    finally:
        if stopped and not restarted:
            try:
                request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                wait_status(token,{"started","running"},attempts=55)
                restarted=True
                print("V48 safety: server restarted after maintenance/abort",flush=True)
            except Exception:
                print("CRITICAL V48: server restart not confirmed; check Nitrado now.",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V48 DEPLOY ERROR:",type(exc).__name__,str(exc)[:180],file=sys.stderr)
        if not REPORT.exists():report(status="FAILED_BEFORE_SAFE_DEPLOYMENT")
        raise SystemExit(1)
