#!/usr/bin/env python3
"""V37: two moderate vanilla infected spawn zones at actual new ZONA47 Livonia.

No scripted roaming, player identification, CE loot, world wipes, modded AI,
or claim of console visual testing. Original XML is saved and restored on error.
"""
from __future__ import annotations
import hashlib,json,math,os,posixpath,sys,time,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v20_unlimited_sprint import setting_state

ROOT=Path(__file__).resolve().parents[1]
FILE="env/zombie_territories.xml"
EVENT="db/events.xml"
CFG="cfggameplay.json"
OUT=Path("deploy/v37/LIVE_RESULT.json")
BACKUP=Path("deploy/v37/private_zombie_territories_before_v37.zip")
ZONES=(
 ("InfectedArmy",8960.0,7810.0,5,9,55),
 ("InfectedArmy",9040.0,7730.0,5,9,55),
)
PREVIOUS=(
 ("InfectedArmy",7100.,6965.),
 ("InfectedArmy",9022.5,7457.9),
 ("InfectedMedic",11490.,461.)
)
def sha(b):return hashlib.sha256(b).hexdigest()
def require(condition,message):
    if not condition:raise NitradoError(message)
def write_report(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"version":"V37","platform":"DayZ PlayStation Livonia",
      "no_wipe":True,"ps4_ps5_tested":False,
      "roaming_scripted_hordes":False,"two_vanilla_infected_patches":True,
      "player_storage_untouched":True,**kw},indent=2)+"\n")
def patch(old,events_blob):
    root=ET.fromstring(old)
    require(root.tag=="territory-type","Zombie territory XML root unexpected")
    events=ET.fromstring(events_blob)
    require(events.tag=="events" and
        events.find("event[@name='InfectedArmy']") is not None,
        "Vanilla InfectedArmy CE event missing")
    all_zones=[z for t in root.findall("territory") for z in t.findall("zone")]
    for name,x,z in PREVIOUS:
        require(any(a.get("name")==name and abs(float(a.get("x","nan"))-x)<.05
                    and abs(float(a.get("z","nan"))-z)<.05 for a in all_zones),
                "Original V16 infected territory not present")
    for name,x,z,dmin,dmax,r in ZONES:
        require(0<dmin<=dmax<=10 and 40<=r<=70,
                "Infected zone would be overly dense")
        require(8850<=x<=9100 and 7680<=z<=7900,
                "Infected zone outside central ZONA47")
        require(all(math.hypot(float(a.get("x","nan"))-x,
                 float(a.get("z","nan"))-z)>75 for a in all_zones),
                "Existing infected territory within 75m of new zone")
    a,b=ZONES
    require(math.hypot(a[1]-b[1],a[2]-b[2])>=a[5]+b[5],
            "Vanilla infected zones overlap")
    require(old.count(b"</territory-type>")==1,"Missing exact XML root closing")
    additions=['  <territory color="4278255360">']
    for name,x,z,dmin,dmax,r in ZONES:
        additions.append(f'    <zone name="{name}" smin="0" smax="0" dmin="{dmin}" dmax="{dmax}" x="{x:.1f}" z="{z:.1f}" r="{r}"/>')
    additions.append("  </territory>")
    payload=("\n"+"\n".join(additions)+"\n").encode()
    new=old.replace(b"</territory-type>",payload+b"</territory-type>")
    parsed=ET.fromstring(new)
    actual=[z for t in parsed.findall("territory") for z in t.findall("zone")]
    require(len(actual)==len(all_zones)+2,"New XML zones did not parse exactly")
    require([(z.get("name"),z.get("dmin"),z.get("dmax")) for z in actual[-2:]]==
        [("InfectedArmy","5","9"),("InfectedArmy","5","9")],
        "New zones inconsistent")
    require(new.replace(payload,b"",1)==old,"Other territory XML bytes changed")
    return new,len(all_zones)
def backup(old):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/"+FILE,old)
        z.writestr("SHA256.txt",sha(old)+" "+FILE+"\n")
    with zipfile.ZipFile(BACKUP) as z:
        require(z.testzip() is None and
            sha(z.read("dayzOffline.enoch/"+FILE))==sha(old),
            "Original XML backup corrupt")
def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    require(token and os.getenv("BEILEYS47_V37_APPROVED")=="yes",
            "Missing Nitrado access or approved flag")
    mission=resolve_mission(token)
    path=posixpath.join(mission,FILE)
    original=download_one(token,path)
    events=download_one(token,posixpath.join(mission,EVENT))
    gp=json.loads(download_one(token,posixpath.join(mission,CFG)))
    require("custom/beileys47_v35_zone47_full_25.json"
      in gp["WorldsData"]["objectSpawnersArr"],"V35 full area not active")
    new,baseline_count=patch(original,events)
    backup(original)
    state=game_state(token)
    status=game_status(state)
    online=players(state)
    if status not in {"started","running","stopped"} or (status!="stopped" and online!=0):
        write_report(status="BLOCKED_CONNECTED_PLAYERS",reported_players=online)
        raise NitradoError("Player online/unknown: no changes")
    require(setting_state(state)=="enabled","cfgGameplay setting unknown")
    time.sleep(2)
    again=game_state(token)
    require(game_status(again)==status and
       (status=="stopped" or players(again)==0),
       "Second zero-player/status check failed")
    stopped=False;attempted=False;restarted=False;success=False
    try:
        if status!="stopped":
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=45)
            stopped=True
        require(sha(download_one(token,path))==sha(original),
                "Source changed while stopping")
        attempted=True
        upload_file(token,path,new)
        require(sha(download_one(token,path))==sha(new),
                "Infected zone upload hash mismatch")
        if stopped:
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            wait_status(token,{"started","running"},attempts=55)
            restarted=True
        require(sha(download_one(token,path))==sha(new),
                "Post-restart infected XML hash mismatch")
        require(game_status(game_state(token)) in {"started","running"} if stopped else True,
                "Server did not return to started")
        success=True
        write_report(status="INSTALLED_AND_READBACK_VERIFIED",
            old_sha=sha(original),new_sha=sha(new),
            original_zones=baseline_count,new_zones=2,
            additional_dynamic_max=18,zone_centers=[[v[1],v[2]] for v in ZONES],
            server_status=game_status(game_state(token)))
        print("V37 PASS: 2 real moderate vanilla infected zones added to ZONA47, no wipe")
    except Exception:
        if attempted and not success:
            try:
                live_state=game_state(token)
                if game_status(live_state) in {"started","running"}:
                    require(players(live_state)==0,
                            "New player joined; do not interrupt for rollback")
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                    wait_status(token,{"stopped"},attempts=45)
                    stopped=True
                upload_file(token,path,original)
                require(sha(download_one(token,path))==sha(original),"Rollback failed")
                write_report(status="ROLLED_BACK_OLD_XML")
                if stopped:
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                    wait_status(token,{"started","running"},attempts=55)
                    restarted=True
            except Exception:
                write_report(status="CRITICAL_MANUAL_RECOVERY_REQUIRED")
        raise
    finally:
        if stopped and not restarted:
            try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
            except Exception:print("CRITICAL unable to confirm restart",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V37 ERROR:",type(e).__name__,str(e)[:180],file=sys.stderr)
        raise SystemExit(1)
