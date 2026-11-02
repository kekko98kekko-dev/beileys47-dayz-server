#!/usr/bin/env python3
"""V57: retire physically broken Zone 47 (26 object-spawner objects + 2 infected patches).

Remove only V29 P1 and V35 25-prop scene references from cfggameplay.json.
Remove only the V49/V37 custom two-zone territory group from zombie_territories.xml.
Keep original JSON scenes on disk (inactive) for future manual-map reconstruction.
No wipe, no changes to CE vehicles, Gunter gift, loot, or world persistence.
One owner-approved restart; verify actual remote files after startup; rollback on failure.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import posixpath
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission, download_one, call_api, NitradoError
from deploy_beileys47_v15 import game_state, game_status, players, request_api_post, upload_file, wait_status
from v36_nitrado_backups_readonly import analyze
from v37_zone47_infected_patches import ZONES,PREVIOUS

CFG="cfggameplay.json"
INF="env/zombie_territories.xml"
V29="custom/beileys47_v29_zone47_p1_guardbox.json"
V35="custom/beileys47_v35_zone47_full_25.json"
PRESERVE={"custom/beileys47_v16_three_hotspots.json","custom/beileys47_dolnik_military_base_v9.json"}
OUT=Path("deploy/v57/ZONE47_REMOVAL_LIVE_RESULT.json")
BACKUP=Path("deploy/v57/PRIVATE_ORIGINAL_ZONE47_CONFIG.zip")

def guard(ok,msg):
    if not ok:raise NitradoError(msg)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def emit(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({
        "release":"BEILEYS47 V57",
        "scope":"Remove 26 malformed Zone47 world props and two related infected patches",
        "retired_spawner_paths":[V29,V35],
        "source_scene_jsons_deleted":False,
        "game_persistence_wipe":False,
        "game_vehicle_events_changed":False,
        "gunter_2_event_changed":False,
        "player_storage_modified":False,
        "provider_backup_is_not_tested_restore":True,
        "ps5_visual_confirmation_pending":True,
        **kw},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V57 STATUS",kw.get("status"),flush=True)

def load(blob):
    js=json.loads(blob.decode("utf-8-sig"))
    guard(isinstance(js,dict),"Unexpected cfggameplay root")
    ws=js.get("WorldsData")
    guard(isinstance(ws,dict),"WorldsData missing")
    refs=ws.get("objectSpawnersArr")
    guard(isinstance(refs,list) and all(isinstance(x,str) for x in refs)
          and len(set(refs))==len(refs),"Invalid or duplicate object-spawner registry")
    return js,refs

def patch_gameplay(blob):
    gp,refs=load(blob)
    guard(V29 in refs and V35 in refs,
          "V29 or V35 not registered, refuse unexpected region state")
    guard(PRESERVE.issubset(set(refs)),
          "Dolnik/V16 no longer registered, refuse to edit unknown state")
    output=copy.deepcopy(gp)
    newrefs=[x for x in refs if x not in (V29,V35)]
    guard(len(refs)-len(newrefs)==2 and len(set(newrefs))==len(newrefs),
          "Expected exactly two separate scene refs")
    output["WorldsData"]["objectSpawnersArr"]=newrefs
    check=copy.deepcopy(output)
    check["WorldsData"]["objectSpawnersArr"]=refs
    guard(check==gp,"Any setting outside exact spawner list changed")
    new=(json.dumps(output,indent=2,ensure_ascii=False)+"\n").encode()
    guard(load(new)[1]==newrefs,"Final gameplay references mismatch")
    return new,len(refs),len(newrefs)

def zone_tuple(z):
    return (z.get("name"),z.get("x"),z.get("z"),
            z.get("dmin"),z.get("dmax"),z.get("r"),
            z.get("smin"),z.get("smax"))

def patch_infected(blob):
    root=ET.fromstring(blob)
    guard(root.tag=="territory-type","Unexpected infected territory root")
    original=[z for t in root.findall("territory") for z in t.findall("zone")]
    wanted={(n,f"{x:.1f}",f"{z:.1f}",str(dmin),str(dmax),str(r),"0","0")
            for n,x,z,dmin,dmax,r in ZONES}
    guard(len(wanted)==2,"V49 target set changed")
    matches=[z for z in original if zone_tuple(z) in wanted]
    guard(len(matches)==2 and {zone_tuple(z) for z in matches}==wanted,
          "Expected exactly two V49 infected zones at the same positions")
    # Require both zones to live in one V49-only territory group.
    owner_groups=[g for g in root.findall("territory")
                  if any(z in matches for z in g.findall("zone"))]
    guard(len(owner_groups)==1 and len(owner_groups[0].findall("zone"))==2,
          "Custom infected patches not in isolated removable group")
    keeper=owner_groups[0]
    guard(keeper.get("color")=="4278255360",
          "Custom V49 territory group differs from deployment")
    seen=0
    target_span=None
    for m in re.finditer(rb"<territory(?=[\s>])[^>]*>.*?</territory>",blob,re.DOTALL):
        try:g=ET.fromstring(m.group())
        except ET.ParseError:continue
        members=[zone_tuple(z) for z in g.findall("zone")]
        if set(members)==wanted and len(members)==2:
            seen+=1
            target_span=m.span()
    guard(seen==1 and target_span is not None,
          "Cannot isolate exact V49-only territory block in live bytes")
    start,end=target_span
    new=blob[:start]+blob[end:]
    parsed=ET.fromstring(new)
    remaining=[z for g in parsed.findall("territory") for z in g.findall("zone")]
    guard(len(original)-len(remaining)==2,
          "Incorrect infected zone deletion count")
    guard([zone_tuple(z) for z in remaining]==
          [zone_tuple(z) for z in original if z not in matches],
          "Non-47 territory group was modified")
    for name,x,z in PREVIOUS:
        guard(any(a.get("name")==name
                  and abs(float(a.get("x"))-x)<.05
                  and abs(float(a.get("z"))-z)<.05 for a in remaining),
              "Existing original infected territory lost")
    return new,len(original),len(remaining)

def verify_scene(token,root):
    positions=[]
    for p,expected in ((V29,1),(V35,25)):
        scene=json.loads(download_one(token,posixpath.join(root,p)))
        objs=scene.get("Objects")
        guard(isinstance(objs,list) and len(objs)==expected,
              "Scene size mismatch "+p)
        for o in objs:
            pos=o.get("pos")
            guard(len(pos)==3 and 8700<float(pos[0])<9200
                  and 7600<float(pos[2])<8000,
                  "Scene object outside bounded Zone 47, refuse broad removal")
            positions.append((float(pos[0]),float(pos[2])))
    guard(len(positions)==26,"Unexpected zone object count")
    return positions

def snapshot(before):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
        for path,blob in before.items():
            z.writestr("dayzOffline.enoch/"+path,blob)
            z.writestr("SHA256_"+path.replace("/","_")+".txt",sha(blob)+"\n")
    with zipfile.ZipFile(BACKUP) as z:
        guard(z.testzip() is None,"Private ZIP integrity check failed")
        for path,blob in before.items():
            guard(sha(z.read("dayzOffline.enoch/"+path))==sha(blob),
                  "Private rollback content mismatch "+path)

def server(token):
    d=game_state(token)
    return game_status(d),players(d)

def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=60)

def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=60)

def verify_removed(blobs):
    _,active=load(blobs[CFG])
    guard(V29 not in active and V35 not in active,
          "One or more removed spawners still registered")
    guard(PRESERVE.issubset(active),"A preserved spawner is no longer active")
    root=ET.fromstring(blobs[INF])
    zones=[z for g in root.findall("territory") for z in g.findall("zone")]
    for name,x,z,*_ in ZONES:
        guard(not any(a.get("name")==name
               and a.get("x")==f"{x:.1f}" and a.get("z")==f"{z:.1f}"
               for a in zones),"Bugged-zone infected source remains")
    return len(active)

def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    guard(token and os.getenv("BEILEYS47_V57_REMOVE_ZONE47_APPROVED")=="yes",
          "Missing user authorization or API credential")
    root=resolve_mission(token)
    paths=(CFG,INF)
    remotes={p:posixpath.join(root,p) for p in paths}
    old={p:download_one(token,remotes[p]) for p in paths}
    positions=verify_scene(token,root)
    new_cfg,old_refs,new_refs=patch_gameplay(old[CFG])
    new_inf,old_zones,new_zones=patch_infected(old[INF])
    edited={CFG:new_cfg,INF:new_inf}
    active=verify_removed(edited)
    guard(active==new_refs,"Inactive scene check invalid")
    current_status,current_players=server(token)
    guard(current_status in ("started","running"),
          "Server currently not started; no maintenance")
    guard(os.getenv("BEILEYS47_V57_ALLOW_PLAYER_DISCONNECT")=="yes",
          "Must explicitly approve one maintenance restart")
    provider=analyze(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    guard(provider["provider_backup_exists"] and provider["restore_possible"] is True,
          "No provider restore point; abort changes")
    snapshot(old)
    emit(status="BACKUPS_READY_PRE_RESTART", old_spawner_refs=old_refs,
         new_spawner_refs=new_refs,zone47_props_retired=len(positions),
         old_zombie_zones=old_zones,new_zombie_zones=new_zones,
         provider_backup_count=provider["backup_count"],
         players_before_stop=current_players)
    stopped=False
    touched=False
    rebooted=False
    try:
        stop(token);stopped=True
        for p in paths:
            guard(sha(download_one(token,remotes[p]))==sha(old[p]),
                  "Other admin edited "+p+" during stop")
        for p in paths:
            touched=True
            upload_file(token,remotes[p],edited[p])
            guard(sha(download_one(token,remotes[p]))==sha(edited[p]),
                  "Unable to verify uploaded "+p)
        verify_removed({p:download_one(token,remotes[p]) for p in paths})
        start(token);stopped=False;rebooted=True
        after={p:download_one(token,remotes[p]) for p in paths}
        verify_removed(after)
        guard(all(sha(after[p])==sha(edited[p]) for p in paths),
              "Post-restart file checksum drift")
        game_status_now,number=server(token)
        guard(game_status_now in ("started","running"),
              "Server did not return to running state")
        emit(status="REMOVED_AND_VERIFIED_AFTER_RESTART",
             inactive_object_files_preserved=True,post_restart_hashes_verified=True,
             zone47_props_retired=len(positions),
             original_spawner_refs=old_refs,remaining_spawner_refs=new_refs,
             zone47_infected_zones_removed=2,
             original_infected_zones=old_zones,
             remaining_infected_zones=new_zones,
             original_other_settings_preserved=True,
             final_status=game_status_now,reported_online_players=number,
             player_disconnect_permitted=True,
             provider_backup_count=provider["backup_count"])
        print("V57 SUCCESS: 26 Zone47 objects and two V49 infected zones deactivated; restarted; no wipe.",flush=True)
    except Exception:
        if touched:
            try:
                state,_=server(token)
                if state in ("started","running"):
                    stop(token);stopped=True
                else:guard(state=="stopped","Unknown server state before rollback")
                for p in paths:
                    live=download_one(token,remotes[p])
                    guard(sha(live) in {sha(old[p]),sha(edited[p])},
                          "Concurrent modification of "+p+"; manual recovery required")
                    if sha(live)!=sha(old[p]):
                        upload_file(token,remotes[p],old[p])
                        guard(sha(download_one(token,remotes[p]))==sha(old[p]),
                              "Rollback readback failed "+p)
                start(token);stopped=False
                emit(status="ROLLBACK_CONFIRMED_AFTER_FAILURE")
            except Exception as recover:
                emit(status="CRITICAL_MANUAL_RESTORE_NEEDED",
                     recovery_error_type=type(recover).__name__)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:print("V57 CRITICAL: game not verified running after failure",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("V57 ERROR",type(exc).__name__,str(exc)[:195],file=sys.stderr)
        if not OUT.exists():emit(status="FAILED_NO_LIVE_CHANGE")
        raise SystemExit(1)
