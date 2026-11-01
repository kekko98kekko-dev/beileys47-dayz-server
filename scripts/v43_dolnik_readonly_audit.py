#!/usr/bin/env python3
"""Read-only exact facts needed for a single comprehensive Dolnik M3S loadout.

No raw player data, world storage, vehicle coordinates or persistent entity edits.
"""
import json,os,posixpath,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players

OUT=Path("deploy/v43/DOLNIK_FINAL_LOADOUT_PREFLIGHT.json")
CLASSNAMES=[
 "Truck_01_Covered","WoodenLog","WoodenPlank","MetalPlate","Barrel_Green","Barrel_Blue","Barrel_Red","WoodenCrate",
 "FlagKit","FlagPoleKit","TerritoryFlag","Rope","MetalWire","NailBox","Nail","Stone","LargeStone",
 "SledgeHammer","Shovel","Pickaxe","Hammer","Hatchet","Handsaw","Hacksaw","Pliers","Whetstone","EpoxyPutty","Blowtorch",
 "TireRepairKit","ElectricalRepairKit","DuctTape","SewingKit","LeatherSewingKit",
 "TruckBattery","CarBattery","MotorbikeBattery","SparkPlug","GlowPlug","HeadlightH7","CanisterGasoline",
 "GasMask","GasMask_Filter","NBCJacketGray","NBCPantsGray","NBCBootsGray","NBCGlovesGray","NBCHeadgearGray",
 "PlateCarrierVest","PlateCarrierPouches","PlateCarrierHolster","AliceBag_Green","AssaultBag_Green",
 "M4A1","Mag_STANAG_30Rnd","AmmoBox_556x45_20Rnd","AKM","Mag_AKM_30Rnd","Glock19","Mag_Glock_15Rnd",
 "BandageDressing","SalineBag","Morphine","Epinephrine","TetracyclineAntibiotics","VitaminBottle",
 "FoodCan_Unknown","BakedBeansCan","Canteen","WaterBottle","CombatKnife","Rangefinder","Battery9V",
 "Battery9V","PetrolLighter","Flashlight","UniversalLight","NVGoggles","NVGHeadstrap",
 "TentMedium","MediumTent","Tarp","CombinationLock4","CableReel","Generator","CarTent",
 "Flag_Chernarus","Flag_Pirates","Flag_Altis"
]
EVENTS=("VehicleBEILEYS47DolnikTest","VehicleBEILEYS47DolnikRescueV40","VehicleBEILEYS47DolnikUltimateV43")
def xml(token,mission,name):
 return ET.fromstring(download_one(token,posixpath.join(mission,name)))
def main():
 token=os.environ.get("NITRADO_API_TOKEN","").strip()
 if not token:raise NitradoError("Nitrado token missing")
 mission=resolve_mission(token)
 events=xml(token,mission,"db/events.xml")
 spawns=xml(token,mission,"cfgeventspawns.xml")
 types=xml(token,mission,"db/types.xml")
 cfg=xml(token,mission,"cfgspawnabletypes.xml")
 globals_=xml(token,mission,"db/globals.xml")
 t=cfg.find("type[@name='Truck_01_Covered']")
 if t is None:raise ValueError("Live M3S config unavailable")
 parts={}
 for group in t.findall("attachments"):
  for item in group.findall("item"):
   name=item.get("name")
   parts.setdefault(name,[]).append({"chance":item.get("chance"),
    "quantmin":item.get("quantmin"),"quantmax":item.get("quantmax"),
    "group_chance":group.get("chance")})
 cargo=[i.get("name") for g in t.findall("cargo") for i in g.findall("item")]
 evs={}
 for name in EVENTS:
  e=events.find(f"event[@name='{name}']")
  s=spawns.find(f"event[@name='{name}']")
  evs[name]={"has_event":e is not None,"has_spawn":s is not None,
   "nominal":e.findtext("nominal") if e is not None else None,
   "min":e.findtext("min") if e is not None else None,
   "max":e.findtext("max") if e is not None else None,
   "children":[x.get("type") for x in e.findall("./children/child")] if e is not None else [],
   "positions":[{k:pos.get(k) for k in ("x","z","a")} for pos in s.findall("pos")][:3] if s is not None else []}
 reg={e.get("name"):e.text for e in globals_.findall("var") if e.get("name") in
      ("CleanupLifetimeLimit","CleanupLifetimeDefault","CleanupAvoidance","CleanupLifetimeDeadPlayer",
       "RestartSpawn","FlagRefreshFrequency")}
 specials={}
 for name in ("WoodenCrate","Barrel_Green","Barrel_Blue","Barrel_Red","CarBattery","TruckBattery",
              "AliceBag_Green","GunCase_Black","GunCase_White"):
  v=types.find(f"type[@name='{name}']")
  specials[name]={k:v.findtext(k) for k in ("lifetime","nominal","min")} if v is not None else None
 report={
  "mode":"V43 READ ONLY","server_state":game_status(game_state(token)),
  "players":players(game_state(token)),"nitrado_changes":0,
  "cannot_see_persisted_truck_instances":True,
  "old_and_rescue_events":evs,
  "items_in_live_types_xml":{n:types.find(f"type[@name='{n}']") is not None for n in dict.fromkeys(CLASSNAMES)},
  "truck_attachment_groups":len(t.findall("attachments")),"truck_parts":parts,
  "current_truck_cargo_count":len(cargo),"current_truck_cargo_names":cargo[:100],
  "special_types":specials,"cleaning_globals":reg,
  "world_persistence_unchanged":True
 }
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
