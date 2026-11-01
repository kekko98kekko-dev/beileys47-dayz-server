#!/usr/bin/env python3
"""V18: minimal, one-time gun case key economy fix, rollback protected, NO wipe."""
from __future__ import annotations
import hashlib,io,json,os,posixpath,re,sys,time,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,download_one,resolve_mission,NitradoError
from deploy_beileys47_v15 import (game_state,game_status,players,upload_file,
                                  request_api_post,wait_status)
FILE="db/types.xml"
ORIGINAL_SHA="de902e1aaac151ec16f2496ab1eb19780ef5459bccafaafc2bc1c141c9b4da2b"
OUT=Path("deploy/v18/ORANGE_KEY_RESULT.json")
BACKUP=Path("deploy/v18/private_predeploy_types_backup.zip")
def sha(b):return hashlib.sha256(b).hexdigest()
def need(c,msg):
    if not c:raise NitradoError(msg)
def write(**data):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"service":SERVICE_ID,"version":"V18-orange-case",
      "gameplay_tested":False,"persistence_wipe_requested":False,**data},indent=2)+"\n")
def patch(data):
    root=ET.fromstring(data)
    found={}
    for name in ("GunCase_Orange","GunCaseKeys_Orange","GunCase_Black",
                 "GunCaseKeys_Blue","GunCase_White","GunCaseKeys_Red"):
        entries=root.findall("type[@name='"+name+"']")
        need(len(entries)==1,"Expected one unique type: "+name)
        found[name]=entries[0]
    for name in ("GunCase_Orange","GunCase_Black","GunCase_White"):
        need(int(found[name].findtext("nominal"))>=2,"Unexpected case economy: "+name)
    for name in ("GunCaseKeys_Blue","GunCaseKeys_Red"):
        need(int(found[name].findtext("nominal"))>=1,"Existing blue/red key must stay available")
    target=found["GunCaseKeys_Orange"]
    nominal=target.findtext("nominal")
    minimum=target.findtext("min")
    if (nominal,minimum)==("2","1"):return data,False
    need((nominal,minimum)==("0","0"),"Unexpected orange keys; manual review needed")
    need(any(c.get("name")=="Military" for c in target.findall("usage")),
         "Orange keys have no eligible military spawn usage")
    expression=rb'(<type\s+name=["\x27]GunCaseKeys_Orange["\x27][^>]*>)(.*?)(</type>)'
    matches=list(re.finditer(expression,data,re.DOTALL))
    need(len(matches)==1,"Cannot safely isolate orange key type XML")
    m=matches[0]
    inner=m.group(2)
    updated,n=re.subn(rb"<nominal>\s*0\s*</nominal>",b"<nominal>2</nominal>",inner,count=1)
    need(n==1,"Orange nominal is not uniquely patchable")
    updated,n=re.subn(rb"<min>\s*0\s*</min>",b"<min>1</min>",updated,count=1)
    need(n==1,"Orange minimum is not uniquely patchable")
    new=data[:m.start(2)]+updated+data[m.end(2):]
    check=ET.fromstring(new)
    newcase=check.find("type[@name='GunCaseKeys_Orange']")
    need(newcase.findtext("nominal")=="2" and newcase.findtext("min")=="1",
         "Orange patch failed semantic validation")
    return new,True
def save_backup(raw):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/db/types.xml",raw)
        z.writestr("SHA256.txt",sha(raw)+"  db/types.xml\n")
    with zipfile.ZipFile(BACKUP) as z:
        need(z.testzip() is None,"Pre-deploy backup corrupted")
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    need(bool(token),"Missing Nitrado secret")
    need(os.environ.get("BEILEYS47_V18_ORANGE_APPROVED")=="yes",
         "This deployment was not explicitly authorized")
    mission=resolve_mission(token)
    full=posixpath.join(mission,FILE)
    old=download_one(token,full)
    if sha(old)!=ORIGINAL_SHA:
        print("Unexpected live types file SHA; refusing V18 overwrite",flush=True)
        write(status="blocked_checksum_mismatch",observed_sha=sha(old))
        raise NitradoError("Base file changed after V18 read-only audit")
    candidate,changed=patch(old)
    if not changed:
        write(status="already_configured",original_sha=sha(old))
        return
    save_backup(old)
    expected=sha(candidate)
    print("Verified targeted two-field XML patch; backup exists; no persistence files accessed.",flush=True)
    # Re-check players twice. An unknown count is a HARD stop.
    first=game_state(token)
    need(game_status(first) in {"started","running","stopped"},"Unexpected Nitrado state")
    need(game_status(first)=="stopped" or players(first)==0,"Players online/unknown")
    time.sleep(2)
    second=game_state(token)
    started=game_status(second)!="stopped"
    need(game_status(second) in {"started","running","stopped"},"Server state changed")
    need(not started or players(second)==0,"Players online/unknown on second check")
    uploaded=False
    stopped=False
    try:
        if started:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
            stopped=True
        # Ensure no drift while stopping.
        latest=download_one(token,full)
        need(sha(latest)==ORIGINAL_SHA,"Live file changed during stop")
        upload_file(token,full,candidate)
        uploaded=True
        need(sha(download_one(token,full))==expected,"New file readback checksum mismatch")
        write(status="uploaded_verified_pending_start",old_sha=sha(old),
              new_sha=expected,files_modified=[FILE])
    except Exception:
        if uploaded:
            try:
                upload_file(token,full,old)
                need(sha(download_one(token,full))==sha(old),"Rollback SHA mismatch")
                write(status="rolled_back_after_upload_error",old_sha=sha(old))
            except Exception as rollback_exc:
                write(status="rollback_failed_manual_recovery_required",old_sha=sha(old))
                print("ROLLBACK ERROR",type(rollback_exc).__name__,flush=True)
        raise
    finally:
        if started and stopped:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:print("WARNING: server restart API failed; inspect Nitrado",flush=True)
    if started:
        wait_status(token,{"started","running"},attempts=50)
    live=download_one(token,full)
    need(sha(live)==expected,"Post-restart type file readback mismatch")
    write(status="installed_and_nitrado_state_verified",old_sha=sha(old),
          new_sha=expected,files_modified=[FILE],server_running=started,
          gameplay_tested=False)
    print("V18 ORANGE KEY SUCCESS; PS5 case opening untested; no wipe requested",flush=True)
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("V18 SAFE DEPLOY ERROR",type(exc).__name__,str(exc)[:180],file=sys.stderr)
        raise SystemExit(1)
