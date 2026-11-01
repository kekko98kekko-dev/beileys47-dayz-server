#!/usr/bin/env python3
"""V44 BEILEYS47: ONE new CE M3S at original Dolnik site with full vanilla loadout.

Disable the two old Dolnik *events*; cannot delete their persisted instances
from opaque storage. Keep other vehicles, bases, crates, players intact.
No wipe. All actual names validated against live types.xml before any write.
"""
from __future__ import annotations
import copy,datetime as dt,hashlib,json,os,posixpath,sys,time,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players,upload_file,request_api_post,wait_status

OLD=("VehicleBEILEYS47DolnikTest","VehicleBEILEYS47DolnikRescueV40")
NEW="VehicleBEILEYS47DolnikUltimateV43"
TRUCK="Truck_01_Covered"
XYZ=("11574.92","374.01","177.83")
FILES=("db/events.xml","cfgeventspawns.xml","cfgspawnabletypes.xml")
OUT=Path("deploy/v44/DOLNIK_ULTIMATE_RESULT.json")
ARCH=Path("deploy/v44/PRIVATE_ORIGINAL_DOLNIK_XML.zip")
SUPPORT_CARGO={
    # Full pole kit, materials and flag. 32 stones are individual cargo items.
    "TerritoryFlagKit":1,"TerritoryFlag":1,"Rope":2,"MetalWire":2,
    "Stone":32,"NailBox":6,
    # Building/repair tools, locksmithing.
    "SledgeHammer":1,"Shovel":1,"Pickaxe":1,"Hammer":1,"Hatchet":1,
    "Hacksaw":1,"Pliers":1,"Whetstone":2,"Blowtorch":1,
    "EpoxyPutty":3,"TireRepairKit":2,"DuctTape":3,
    "SewingKit":1,"LeatherSewingKit":1,"CombinationLock4":2,
    # Fuel + batteries, and spark/glow plugs. No nonexistent scooter battery.
    "CanisterGasoline":2,"CarBattery":1,"TruckBattery":1,
    "SparkPlug":2,"GlowPlug":1,"HeadlightH7":2,"Battery9V":4,
    # Premium survival loadout; protection & important weapons.
    "AliceBag_Green":1,"PlateCarrierVest":1,"PlateCarrierPouches":1,
    "PlateCarrierHolster":1,"NVGoggles":1,"NVGHeadstrap":1,
    "GasMask":1,"GasMask_Filter":2,"M4A1":1,"AKM":1,
    "Mag_STANAG_30Rnd":2,"Mag_AKM_30Rnd":2,
    "AmmoBox_556x45_20Rnd":2,"Glock19":1,"Mag_Glock_15Rnd":2,
    "CombatKnife":1,"Rangefinder":1,
    "BandageDressing":3,"Morphine":1,"Epinephrine":1,
    "TetracyclineAntibiotics":1,"VitaminBottle":1,"SalineBag":1,
    "Canteen":1,"BakedBeansCan":2,
}
OPTIONAL={"TerritoryFlagKit":"Rope"}  # If no craftable kit CE type, provide ingredients.
BARRELS=("Barrel_Green","Barrel_Blue","Barrel_Red","Barrel_Green")
CRATES=("WoodenCrate",)*4
REQUIRED_FIXED={"Truck_01_Wheel":4,"Truck_01_WheelDouble":4,
  "TruckBattery":1,"HeadlightH7":2,"Truck_01_Hood":1,
  "Truck_01_Door_1_1":1,"Truck_01_Door_2_1":1,
  "WoodenLog":1,"WoodenPlank":1,"MetalPlate":1}
OMIT_NAME_FRAGMENTS=("guncase","briefcase","scientificbriefcase","smallprotectorcase",
                     "seachest","casekeys")
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
 if not ok:raise NitradoError(msg)
def parse(data):
 return ET.fromstring(data,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def tobytes(root):
 return ET.tostring(root,encoding="utf-8",xml_declaration=True)
def report(**kw):
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({"stage":"V44","mode":"ONE ORIGINAL DOLNIK M3S CE EVENT",
   "original_xza":[float(x) for x in XYZ],
   "world_wipe":False,"player_storage_edited":False,
   "existing_persisted_trucks_removed":False,
   "world_has_exactly_one_truck_verified":False,
   "actual_vehicle_fuel_tank_filled":False,
   "actual_console_cargo_arrangement_tested":False,
   **kw},indent=2,ensure_ascii=False)+"\n")
def check_source(events,spawns):
 original=[]
 for name in OLD:
  e=events.find(f"event[@name='{name}']")
  p=spawns.find(f"event[@name='{name}']")
  require(e is not None and p is not None,"Missing old Dolnik event/spawn "+name)
  require(e.findtext("nominal")=="1" and e.findtext("max")=="1"
          and e.findtext("active")=="1","Old event drift "+name)
  require([c.get("type") for c in e.findall("./children/child")]==[TRUCK],
          "Old event no longer unique M3S "+name)
  require(len(p.findall("pos"))==1,"Old position count changed "+name)
  original.append((e,p))
 first=original[0][1].find("pos")
 require(all(abs(float(first.get(k))-float(v))<.01 for k,v in zip(("x","z","a"),XYZ)),
         "Original Dolnik point unexpectedly changed")
 require(events.find(f"event[@name='{NEW}']") is None and
         spawns.find(f"event[@name='{NEW}']") is None,
         "Ultimate event already exists or partly created")
 return original
def build(files,live_types):
  src={p:parse(files[p]) for p in FILES}
  events,spawns,cfg=(src[p] for p in FILES)
  require(events.tag=="events" and spawns.tag=="eventposdef" and cfg.tag=="spawnabletypes",
          "Unexpected live XML root")
  original=check_source(events,spawns)
  valid={t.get("name") for t in live_types.findall("type") if t.get("name")}
  for classname in (TRUCK,*BARRELS,*CRATES,*REQUIRED_FIXED):
     require(classname in valid,"Required vanilla classname absent "+classname)
  truck=cfg.find(f"type[@name='{TRUCK}']")
  require(truck is not None,"M3S equipment profile missing")
  actual={}
  for group in truck.findall("attachments"):
      for item in group.findall("item"):
          actual[item.get("name")]=actual.get(item.get("name"),0)+1
  require(all(actual.get(k)==v for k,v in REQUIRED_FIXED.items()),
          "Truck mechanical/rack configuration changed unexpectedly")
  # Add 4 barrel and 4 crate dedicated attachment groups. These are real M3S slots.
  for classname in (*BARRELS,*CRATES):
      grp=ET.SubElement(truck,"attachments",{"chance":"1.00"})
      ET.SubElement(grp,"item",{"name":classname,"chance":"1.00"})
  for g in truck.findall("attachments"):
      g.set("chance","1.00")
      for item in g.findall("item"):
          item.set("chance","1.00")
          if item.get("name") in ("WoodenLog","WoodenPlank","MetalPlate"):
              item.set("quantmin","100");item.set("quantmax","100")
  damage=truck.find("damage")
  if damage is None:damage=ET.SubElement(truck,"damage")
  damage.set("min","0.0");damage.set("max","0.0")
  # Remove ALL inherited cargo, including weapon cases and fancy briefcases.
  for node in list(truck):
      if node.tag=="cargo":truck.remove(node)
  accepted={}
  skipped={}
  for classname,n in SUPPORT_CARGO.items():
      if classname not in valid:
          if classname in OPTIONAL:
              skipped[classname]="crafting required: kit not CE-spawnable"
              continue
          require(False,"Requested important cargo class absent: "+classname)
      accepted[classname]=n
  for classname,n in accepted.items():
      require(all(q not in classname.casefold() for q in OMIT_NAME_FRAGMENTS),
              "Forbidden case cargo included "+classname)
      for _ in range(n):
          g=ET.SubElement(truck,"cargo",{"chance":"1.00"})
          ET.SubElement(g,"item",{"name":classname,"chance":"1.00"})
  # Disable old *event sources* without modifying actual persistent old trucks.
  for e,_ in original:
      for tag in ("nominal","min","max","active"):
          q=e.find(tag)
          require(q is not None,"Old event missing required setting "+tag)
          q.text="0"
  # Reuse vanilla event shape, with one original fixed spawn point.
  successor=copy.deepcopy(original[0][0])
  successor.set("name",NEW)
  for tag in ("nominal","min","max","active"):
      successor.find(tag).text="1"
  events.append(successor)
  pos=ET.SubElement(spawns,"event",{"name":NEW})
  ET.SubElement(pos,"pos",{"x":XYZ[0],"z":XYZ[1],"a":XYZ[2]})
  new={name:tobytes(src[name]) for name in FILES}
  # Strong XML-level invariants / no disappearing non-target events
  ve=parse(new["db/events.xml"]);vs=parse(new["cfgeventspawns.xml"])
  for name in OLD:
      o=ve.find(f"event[@name='{name}']")
      require(o.findtext("nominal")=="0" and o.findtext("active")=="0",
              "Old event not disabled "+name)
      require(vs.find(f"event[@name='{name}']") is not None,
              "Old spawn position unexpectedly removed")
  require(ve.find(f"event[@name='{NEW}']").findtext("nominal")=="1",
          "Ultimate event missing")
  require(len(vs.find(f"event[@name='{NEW}']").findall("pos"))==1,
          "Ultimate positions duplicate")
  tc=parse(new["cfgspawnabletypes.xml"]).find(f"type[@name='{TRUCK}']")
  total_cargo=sum(len(x.findall("item")) for x in tc.findall("cargo"))
  require(total_cargo==sum(accepted.values()),"Cargo count inaccurate")
  require(not any(any(v in x.get("name","").casefold() for v in OMIT_NAME_FRAGMENTS)
          for x in tc.findall("./cargo/item")),"Forbidden cargo survived")
  for name,amount in {("Barrel_Green"):2,("Barrel_Blue"):1,("Barrel_Red"):1,
                      ("WoodenCrate"):4}.items():
      require(sum(x.get("name")==name for x in tc.findall("./attachments/item"))==amount,
              "Truck container slot missing "+name)
  return new,{"cargo_entries":total_cargo,"cargo_classnames":accepted,
              "optional_missing":skipped,"barrel_slots":4,"crate_slots":4,
              "new_event":NEW,"old_ce_events_disabled":list(OLD),
              "truck_variant":TRUCK}
def backup(files):
 ARCH.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(ARCH,"w",zipfile.ZIP_DEFLATED) as z:
  for name,blob in files.items():
      z.writestr("dayzOffline.enoch/"+name,blob)
  z.writestr("SHA256.txt","".join(sha(b)+" "+p+"\n" for p,b in files.items()))
 with zipfile.ZipFile(ARCH) as z:
  require(z.testzip() is None,"Original XML ZIP corrupt")
  for p,b in files.items():
      require(sha(z.read("dayzOffline.enoch/"+p))==sha(b),"Backup mismatch "+p)
def installed(files):
  ev=parse(files["db/events.xml"])
  pos=parse(files["cfgeventspawns.xml"])
  cfg=parse(files["cfgspawnabletypes.xml"])
  e=ev.find(f"event[@name='{NEW}']")
  p=pos.find(f"event[@name='{NEW}']")
  if (e is None and p is None):return False
  require(e is not None and p is not None,"Partially installed new truck event")
  require(all(ev.find(f"event[@name='{k}']").findtext("active")=="0" for k in OLD),
          "Old event unexpectedly active")
  require(e.findtext("nominal")=="1" and len(p.findall("pos"))==1,
          "New event differs")
  loc=p.find("pos")
  require(all(abs(float(loc.get(k))-float(v))<.01 for k,v in zip(("x","z","a"),XYZ)),
          "New site differs")
  truck=cfg.find(f"type[@name='{TRUCK}']")
  require(truck is not None and
       sum(x.get("name")=="WoodenCrate" for x in truck.findall("./attachments/item"))==4,
       "Ultimate full truck loadout differs")
  return True
def main():
 token=os.getenv("NITRADO_API_TOKEN","").strip()
 require(token and os.getenv("BEILEYS47_V44_APPROVED")=="yes","Missing token/approval")
 if (os.getenv("GITHUB_EVENT_NAME")=="schedule"
         and dt.datetime.now(dt.timezone.utc).date()>dt.date(2026,11,30)):
      report(status="RENTAL_FINISHED_NO_ACTION");return
 mission=resolve_mission(token)
 remote={p:posixpath.join(mission,p) for p in FILES}
 files={p:download_one(token,remote[p]) for p in FILES}
 if installed(files):
      report(status="ALREADY_INSTALLED_NO_ACTION",no_restart=True)
      print("V44 PASS: single new Dolnik CE event configured; no change")
      return
 live_types=parse(download_one(token,posixpath.join(mission,"db/types.xml")))
 changed,details=build(files,live_types)
 backup(files)
 state=game_state(token);status=game_status(state);count=players(state)
 if status not in ("started","running","stopped") or (status!="stopped" and count!=0):
      report(status="WAITING_FOR_IDLE",players=count,
             original_xml_backup_created=True,**details)
      print("V44 WAIT: no player interruption, 3-file backup prepared")
      return
 time.sleep(2)
 again=game_state(token)
 require(game_status(again)==status and (status=="stopped" or players(again)==0),
         "Second player check failed")
 stopped=False;restarted=False;attempted=[];success=False
 try:
    if status!="stopped":
       request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
       wait_status(token,{"stopped"},attempts=55)
       stopped=True
    for p in FILES:
       require(sha(download_one(token,remote[p]))==sha(files[p]),
          "Remote XML changed while stopping "+p)
    for p in FILES:
       attempted.append(p)
       upload_file(token,remote[p],changed[p])
       require(sha(download_one(token,remote[p]))==sha(changed[p]),
               "Post-upload hash mismatch "+p)
    if stopped:
       request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
       wait_status(token,{"started","running"},attempts=55)
       restarted=True
    for p in FILES:
       require(sha(download_one(token,remote[p]))==sha(changed[p]),
               "Post-restart hash mismatch "+p)
    require(installed({p:download_one(token,remote[p]) for p in FILES}),
        "New single event not active after restart")
    success=True
    report(status="INSTALLED_NITRADO_CONFIG_VERIFIED",**details,
       live_state=game_status(game_state(token)),
       no_world_instance_deletion_attempted=True,
       ready_for_actual_console_spawn_test=True)
    print("V44 SUCCESS: previous 2 Dolnik CE events disabled, one max-supplies M3S event at original coordinates. Persisted vehicle removal NOT possible via XML.")
 except Exception:
    if attempted and not success:
      try:
        now=game_state(token)
        if game_status(now) in ("started","running"):
           require(players(now)==0,"Player rejoined; cannot interrupt for rollback")
           request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
           wait_status(token,{"stopped"},attempts=55)
           stopped=True
        for p in reversed(attempted):
           upload_file(token,remote[p],files[p])
           require(sha(download_one(token,remote[p]))==sha(files[p]),
                   "Original rollback hash mismatch "+p)
        report(status="ROLLED_BACK_BEFORE_WORLD_WIPE",**details)
        if stopped:
           request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
           wait_status(token,{"started","running"},attempts=55)
           restarted=True
      except Exception:
        report(status="CRITICAL_MANUAL_RECOVERY_REQUIRED",**details)
    raise
 finally:
    if stopped and not restarted:
       try:request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
       except Exception:print("CRITICAL: restart unconfirmed")
if __name__=="__main__":
 try:main()
 except Exception as ex:
   print("V44 ERROR:",type(ex).__name__,str(ex)[:200],file=sys.stderr)
   raise SystemExit(1)
