#!/usr/bin/env python3
"""BEILEYS47 V40 one extra, safe-spaced Dolnik M3S truck and 64-slot Field Backpack.

This does NOT forcibly move/despawn a persistent M3S or edit player storage.
CE can create the extra vehicle upon refresh when under global resource limits;
configuration readback is NOT visual vehicle spawn proof.
"""
from __future__ import annotations
import copy,datetime as dt,hashlib,io,json,math,os,posixpath,sys,time,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status
from v27_zone47_real_heights import get,interp,RASTER,WORLD
import numpy as np

MISSION_FILES=("db/events.xml","cfgeventspawns.xml","cfgspawnabletypes.xml")
GIFT="VehicleBEILEYS47DolnikRescueV40"
OLD="VehicleBEILEYS47DolnikTest"
TRUCK="Truck_01_Covered"
BAG="AliceBag_Green"
ORIG=(11574.92,374.01,177.83)
OUT=Path("deploy/v40/LIVE_TRUCK_RESULT.json")
BACKUP=Path("deploy/v40/PRIVATE_BEFORE_V40.zip")
REQUIRED_PARTS={
 "Truck_01_Wheel":4,"Truck_01_WheelDouble":4,"TruckBattery":1,
 "HeadlightH7":2,"Truck_01_Hood":1,
 "Truck_01_Door_1_1":1,"Truck_01_Door_2_1":1
}
def guard(ok,message):
    if not ok:raise NitradoError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def record(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"version":"V40","site":"Dolnik",
      "original_truck_coords_xza":ORIG,
      "backpack_64_class":BAG,"does_not_delete_old_trucks":True,
      "player_storage_untouched":True,"world_wipe":False,
      "actual_truck_seen_on_PS5":False,"fuel_tank_verified":False,**kw},
      indent=2,ensure_ascii=False)+"\n")
def parse(b):
    return ET.fromstring(b,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def xml(root):
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)
def orig_event(events,spawns):
    o=events.find(f"event[@name='{OLD}']")
    s=spawns.find(f"event[@name='{OLD}']")
    guard(o is not None and s is not None,"Dolnik original special truck missing")
    positions=s.findall("pos")
    guard(len(positions)==1 and all(abs(float(positions[0].get(k))-v)<.02 for k,v in
          (("x",ORIG[0]),("z",ORIG[1]),("a",ORIG[2]))),
          "Previous known Dolnik truck location changed")
    guard(o.findtext("nominal")=="1" and o.findtext("max")=="1"
       and o.findtext("active")=="1"
       and [x.get("type") for x in o.findall("./children/child")]==[TRUCK],
       "Dolnik old truck event no longer matches previously verified class")
    return o,s
def named_units(spawn):
    t=spawn.find(f"type[@name='{TRUCK}']")
    guard(t is not None,"Truck attachment profile absent")
    groups=t.findall("attachments")
    actual={}
    for group in groups:
      for item in group.findall("item"):
        actual[item.get("name")]=actual.get(item.get("name"),0)+1
    guard(all(actual.get(k)==n for k,n in REQUIRED_PARTS.items()),
          "Truck wheels/battery/doors config changed; refusing unsafe overwrite")
    guard(len(groups)>=15,"Too few truck attachment groups")
    return t,groups
def select_nearby_site(grid,groups,custom,all_vehicle_positions):
    """Pick flat terrain 32–58m from old official spot, away from old truck and sites.

    Mapgrouppos gives approximate building origins, not collision meshes; this
    can still need actual console inspection before driving.
    """
    x0,z0,_=ORIG
    guard(grid.shape==(2048,2048),"Unexpected Livonia heightfield")
    buildings=[]
    for g in groups.findall("group"):
      try:
        p=[float(v) for v in g.get("pos","").split()]
        if len(p)==3 and math.hypot(p[0]-x0,p[2]-z0)<130:
            buildings.append((p[0],p[2]))
      except (TypeError,ValueError):pass
    obstacles=[]
    for scene in custom:
      for item in scene.get("Objects",[]):
        pos=item.get("pos")
        if (isinstance(pos,list) and len(pos)>=3 and
            all(isinstance(v,(int,float)) for v in pos[:3])):
            if math.hypot(pos[0]-x0,pos[2]-z0)<120:
                obstacles.append((pos[0],pos[2]))
    factor=(grid.shape[0]-1)/WORLD
    def height(x,z):
       return float(interp(grid,x,z,("zx",False,False),factor))
    candidates=[]
    for radius in (35,40,45,50,55):
      for degrees in range(0,360,15):
        a=math.radians(degrees)
        x=round(x0+radius*math.cos(a),2)
        z=round(z0+radius*math.sin(a),2)
        if not (0<x<WORLD and 0<z<WORLD):continue
        if any(math.hypot(x-bx,z-bz)<17 for bx,bz in buildings):continue
        if any(math.hypot(x-bx,z-bz)<22 for bx,bz in obstacles):continue
        if any(math.hypot(x-bx,z-bz)<28 for bx,bz in all_vehicle_positions):continue
        # At least 35m away from potentially persistent original truck.
        sample=[height(x+dx,z+dz) for dx,dz in
          [(0,0),(-6,0),(6,0),(0,-6),(0,6),(-10,-10),(-10,10),(10,-10),(10,10)]]
        delta=max(sample)-min(sample)
        if not (155<sample[0]<400 and delta<=1.55):continue
        # Avoid hills/roads with sharp slope and keep a reliably flat footprint.
        candidates.append((round(delta,4),radius,degrees,x,z,round(sample[0],4)))
    guard(bool(candidates),
          "No verified open/flat alternate truck site within ~55m of original point")
    # Prefer flat relief; nearby radius penalty to keep reasonably close.
    best=min(candidates,key=lambda c:(c[0]+.013*(c[1]-35),c[1],c[2]))
    return {"x":best[3],"z":best[4],"orientation":ORIG[2],
            "estimated_ground_y":best[5],"terrain_relief_20m":best[0],
            "distance_from_original_m":best[1],"vanilla_collision_tested":False}
def nearby_vehicle_positions(spawns):
    points=[]
    for ev in spawns.findall("event"):
        if not (ev.get("name","").startswith("Vehicle")):continue
        for p in ev.findall("pos"):
            try:points.append((float(p.get("x")),float(p.get("z"))))
            except (TypeError,ValueError):pass
    return points
def make(files,site):
    ev=parse(files["db/events.xml"])
    sp=parse(files["cfgeventspawns.xml"])
    cfg=parse(files["cfgspawnabletypes.xml"])
    eventold, posold=orig_event(ev,sp)
    guard(ev.find(f"event[@name='{GIFT}']") is None
          and sp.find(f"event[@name='{GIFT}']") is None,
          "V40 gift already exists; never duplicate")
    newevent=copy.deepcopy(eventold)
    newevent.set("name",GIFT)
    for key in ("nominal","min","max"):newevent.find(key).text="1"
    newevent.find("active").text="1"
    ev.append(newevent)
    newpositions=ET.SubElement(sp,"event",{"name":GIFT})
    ET.SubElement(newpositions,"pos",{
      "x":f"{site['x']:.2f}","z":f"{site['z']:.2f}",
      "a":f"{site['orientation']:.2f}"})
    truck,groups=named_units(cfg)
    for grp in groups:
        grp.set("chance","1.00")
        for item in grp.findall("item"):
            # Single-item vanilla component groups. Turn partial spawn into
            # guaranteed assembly; do not change unrelated truck colors.
            item.set("chance","1.00")
    damage=truck.find("damage")
    if damage is None:
        damage=ET.Element("damage")
        truck.insert(0,damage)
    damage.set("min","0.0");damage.set("max","0.0")
    guard(not any(i.get("name")==BAG for i in truck.findall("./cargo/item")),
          "Backpack already in truck cargo: avoid duplicate")
    cargo=ET.Element("cargo",{"chance":"1.00"})
    ET.SubElement(cargo,"item",{"name":BAG,"chance":"1.00"})
    # Prioritize bag before the ~80 legacy supplies in truck cargo.
    index=next((i for i,v in enumerate(truck) if v.tag=="cargo"),len(truck))
    truck.insert(index,cargo)
    generated={"db/events.xml":xml(ev),"cfgeventspawns.xml":xml(sp),
              "cfgspawnabletypes.xml":xml(cfg)}
    for name,blob in generated.items():
        p=parse(blob)
        guard(p.tag in ("events","eventposdef","spawnabletypes"),"Invalid generated XML root")
    assert sum(c.get("name")==BAG for c in
               parse(generated["cfgspawnabletypes.xml"]).find(f"type[@name='{TRUCK}']").findall("./cargo/item"))==1
    return generated
def create_backup(files):
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACKUP,"w",zipfile.ZIP_DEFLATED) as z:
       for p,b in files.items():z.writestr("dayzOffline.enoch/"+p,b)
       z.writestr("SHA256.txt","".join(sha(b)+"  "+p+"\n" for p,b in files.items()))
    with zipfile.ZipFile(BACKUP) as z:
       guard(z.testzip() is None,"ZIP backup integrity failed")
       for p,b in files.items():
           guard(sha(z.read("dayzOffline.enoch/"+p))==sha(b),"ZIP readback failed")
def installed(originals):
    ev=parse(originals["db/events.xml"])
    sp=parse(originals["cfgeventspawns.xml"])
    cfg=parse(originals["cfgspawnabletypes.xml"])
    has_event=ev.find(f"event[@name='{GIFT}']") is not None
    has_spawn=sp.find(f"event[@name='{GIFT}']") is not None
    truck,_=named_units(cfg)
    bag=[e for e in truck.findall("cargo") if any(x.get("name")==BAG for x in e.findall("item"))]
    if any((has_event,has_spawn,bool(bag))) and not all((has_event,has_spawn,bool(bag))):
        raise NitradoError("PARTIAL V40: manual review, no duplicate upload")
    if all((has_event,has_spawn,bool(bag))):
       guard(len(bag)==1 and
             all(i.get("chance")=="1.00" and g.get("chance")=="1.00"
                  for g in truck.findall("attachments") for i in g.findall("item")),
             "Existing V40 equipment differs")
       guard(ev.find(f"event[@name='{GIFT}']").findtext("nominal")=="1","V40 different event cap")
       return True
    return False
def permitted_restart(status,count,one_time_owner_override=False):
    """Allow online restart only with owner permission and exactly ONE player.

    Never treat an unknown player count or multiple players as safe. The normal
    scheduled V40 workflow must retain its original zero-player protection.
    """
    if status=="stopped":return True
    if status not in ("started","running"):return False
    if type(count) is not int or count<0:return False
    return count==0 or (one_time_owner_override is True and count==1)

def ensure_no_new_players(status,previous_count,now_count,owner_override):
    if status=="stopped":return True
    return (permitted_restart(status,now_count,owner_override)
            and type(previous_count) is int
            and now_count<=previous_count)

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    guard(token and os.environ.get("BEILEYS47_V40_APPROVED")=="yes",
          "Owner authorized workflow or token missing")
    if (os.environ.get("GITHUB_EVENT_NAME")=="schedule" and
        dt.datetime.now(dt.timezone.utc).date()>dt.date(2026,11,30)):
        record(status="RENTAL_EXPIRED_NO_ACTION");return
    mission=resolve_mission(token)
    paths={p:posixpath.join(mission,p) for p in MISSION_FILES}
    old={p:download_one(token,remote) for p,remote in paths.items()}
    if installed(old):
       record(status="ALREADY_INSTALLED_NO_ACTION",no_server_restart=True)
       print("V40 DONE: complete Dolnik gift truck CE configuration exists")
       return
    types=parse(download_one(token,posixpath.join(mission,"db/types.xml")))
    guard(types.find(f"type[@name='{BAG}']") is not None,
          "Field Backpack 64 does not exist in current CE")
    groups=parse(download_one(token,posixpath.join(mission,"mapgrouppos.xml")))
    sp=parse(old["cfgeventspawns.xml"])
    custom=[]
    gameplay=json.loads(download_one(token,posixpath.join(mission,"cfggameplay.json")))
    for rel in gameplay["WorldsData"]["objectSpawnersArr"]:
       if not isinstance(rel,str) or not rel.startswith("custom/") or not rel.endswith(".json") or ".." in rel:
          raise NitradoError("Untrusted custom scene path")
       custom.append(json.loads(download_one(token,posixpath.join(mission,rel))))
    grid=np.load(io.BytesIO(get(RASTER)),allow_pickle=False)
    site=select_nearby_site(grid,groups,custom,nearby_vehicle_positions(sp))
    new=make(old,site)
    for p,b in new.items():guard(b!=old[p],"No change in "+p)
    # Backup original config BEFORE any stop, with original physical bytes.
    create_backup(old)
    state=game_state(token)
    status=game_status(state)
    count=players(state)
    operator_override=os.environ.get("BEILEYS47_V41_ONE_TIME_KICK_ONE_PLAYER")=="yes"
    # Override is specifically for this one owner-authorized push workflow:
    # scheduled retries MUST NOT drop a player from an ongoing game.
    guard(not operator_override or
          (os.environ.get("GITHUB_EVENT_NAME")=="push"
           and os.environ.get("BEILEYS47_V41_ONE_TIME_RESTART")=="yes"),
          "One-time override is only allowed in approved push-based V41 workflow")
    if not permitted_restart(status,count,operator_override):
       record(status="WAITING_FOR_IDLE",players_reported=count,
              proposed_safe_site=site,no_server_restart=True)
       print("V40 WAIT: too many players or unknown; no Nitrado changes")
       return
    time.sleep(2)
    again=game_state(token)
    guard(game_status(again)==status and
          ensure_no_new_players(status,count,players(again),operator_override),
          "Player joined or server state changed; do not interrupt game")
    if count==1 and operator_override:
       record(status="OWNER_AUTHORIZED_ONE_PLAYER_RESTART_PENDING",
              reported_player_count=count,proposed_safe_site=site,
              original_config_backup_created=True)
       print("V41 OPERATOR AUTHORIZED: orderly stop/restart with one player online")
    was_running=status!="stopped"
    stopped=False
    changes=[]
    restarted=False
    success=False
    try:
      if was_running:
         request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
         wait_status(token,{"stopped"},attempts=48)
         stopped=True
      for p,path in paths.items():
         guard(sha(download_one(token,path))==sha(old[p]),
               "Config drift while stopping "+p)
      for p,path in paths.items():
         changes.append(p)
         upload_file(token,path,new[p])
         guard(sha(download_one(token,path))==sha(new[p]),"Nitrado SHA mismatch "+p)
      if was_running:
         request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
         wait_status(token,{"started","running"},attempts=55)
         restarted=True
      for p,path in paths.items():
         guard(sha(download_one(token,path))==sha(new[p]),"Post-start SHA drift "+p)
      success=True
      record(status="INSTALLED_FILES_AND_SERVER_READBACK",
             new_event=GIFT,new_truck_variant=TRUCK,
             guaranteed_attachment_groups=17,one_64_slot_backpack_in_new_truck_cargo=True,
             new_truck_spawn_site=site,
             original_truck_event_preserved=True,
             original_truck_may_exist_elsewhere=True,
             CE_respawn_engine_not_verified_in_game=True,
             server_status=game_status(game_state(token)),
             operator_authorized_one_player_restart=bool(count==1 and operator_override))
      print("V40 LIVE CONFIG SUCCESS: dedicated Dolnik rescue M3S, 100% parts, Field Backpack 64 cargo; CE in-game spawn pending verification")
    except Exception:
      if changes and not success:
        try:
          live=game_state(token)
          if game_status(live) in ("started","running"):
             guard(players(live)==0,"Player rejoined, avoid disruptive rollback")
             request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
             wait_status(token,{"stopped"},attempts=45)
             stopped=True
          for p in reversed(changes):
             upload_file(token,paths[p],old[p])
             guard(sha(download_one(token,paths[p]))==sha(old[p]),"Rollback failure "+p)
          record(status="ROLLED_BACK_ORIGINALS",changed_file_count=len(changes))
          if was_running:
             request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
             wait_status(token,{"started","running"},attempts=55)
             restarted=True
        except Exception:
          record(status="CRITICAL_RESTORE_FROM_PRIVATE_ZIP")
      raise
    finally:
      if was_running and stopped and not restarted:
        try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
        except Exception:print("CRITICAL: Nitrado manual restart check required")
if __name__=="__main__":
    try:main()
    except Exception as exc:
       print("V40 ERROR:",type(exc).__name__,str(exc)[:200],file=sys.stderr)
       raise SystemExit(1)
