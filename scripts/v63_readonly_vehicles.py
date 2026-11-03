#!/usr/bin/env python3
import os,posixpath,json,xml.etree.ElementTree as ET
from nitrado_snapshot import resolve_mission,download_one
from deploy_beileys47_v15 import game_state,game_status,players
from pathlib import Path

def main():
 token=os.environ["NITRADO_API_TOKEN"]
 mission=resolve_mission(token)
 def read(name):return download_one(token,posixpath.join(mission,name))
 events=ET.fromstring(read("db/events.xml"))
 positions=ET.fromstring(read("cfgeventspawns.xml"))
 spawns=ET.fromstring(read("cfgspawnabletypes.xml"))
 types=ET.fromstring(read("db/types.xml"))
 names={t.get("name") for t in types.findall("type")}
 list_events=[]
 for e in events.findall("event"):
  if e.get("name","").startswith("Vehicle"):
   name=e.get("name")
   pos=positions.find(f"event[@name='{name}']")
   list_events.append({"name":name,"active":e.findtext("active"),
     "nominal":e.findtext("nominal"),"min":e.findtext("min"),
     "max":e.findtext("max"),"restock":e.findtext("restock"),
     "children":[c.get("type") for c in e.findall("./children/child")],
     "positions":[dict(p.attrib) for p in pos.findall("pos")] if pos is not None else []})
 profiles={}
 for name in ("Truck_01_Covered","Offroad_02","Hatchback_02_Black"):
  p=spawns.find(f"type[@name='{name}']")
  profiles[name]={"exists":p is not None,
    "cargo":[i.get("name") for i in p.findall("./cargo/item")],
    "attachments":[i.get("name") for i in p.findall("./attachments/item")]} if p is not None else {"exists":False}
 check=["Offroad_02","PowerGenerator","Spotlight","GasCanister","GasCanisterLarge","StaticFlagPole","Flag_Bohemia","SparkPlug","TruckBattery","CarBattery","Battery9V","NVGoggles","CableReel","GasMask"]
 out={"vehicles":list_events,"profiles":profiles,"classes":{k:k in names for k in check},
    "state":game_status(game_state(token))}
 Path("deploy/v63").mkdir(parents=True,exist_ok=True)
 Path("deploy/v63/READONLY.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
 print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__":main()
