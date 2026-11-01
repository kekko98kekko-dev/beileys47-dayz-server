#!/usr/bin/env python3
"""Read-only verify actual old Dolnik special truck event, parts and 64-slot backpack."""
from __future__ import annotations
import json,os,posixpath,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
OUT=Path("deploy/v39/TRUCK_LIVE_PREFLIGHT.json")
EVENT="VehicleBEILEYS47DolnikTest"
S=(11574.92,374.01,177.83)
def xml(token,mission,f):return ET.fromstring(download_one(token,posixpath.join(mission,f)))
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Nitrado token unavailable")
    mission=resolve_mission(token)
    events=xml(token,mission,"db/events.xml")
    positions=xml(token,mission,"cfgeventspawns.xml")
    spawn=xml(token,mission,"cfgspawnabletypes.xml")
    types=xml(token,mission,"db/types.xml")
    gamestate=game_state(token)
    target=events.find(f"event[@name='{EVENT}']")
    spawnloc=positions.find(f"event[@name='{EVENT}']")
    trucks={}
    for name in ("Truck_01_Covered","Truck_01_Covered_Blue","Truck_01_Covered_Orange"):
        el=spawn.find(f"type[@name='{name}']")
        if el is None:
            trucks[name]={"exists":False}
            continue
        groups=el.findall("attachments")
        truckitems={}
        for e in groups:
            for item in e.findall("item"):
                key=item.get("name")
                truckitems.setdefault(key,[]).append({
                  "item_chance":item.get("chance"),
                  "group_chance":e.get("chance")})
        cargo=[i.get("name") for i in el.findall("./cargo/item")]
        trucks[name]={"exists":True,"attachment_groups":len(groups),
                      "parts":truckitems,"cargo":cargo}
    spot=[]
    if spawnloc is not None:
        spot=[{"x":x.get("x"),"z":x.get("z"),"orientation":x.get("a")} for x in spawnloc.findall("pos")][:6]
    report={"mode":"READ_ONLY","nitrado_write_actions":0,
       "status":game_status(gamestate),"players":players(gamestate),
       "old_truck_event_exists":target is not None,
       "old_truck_nominal":target.findtext("nominal") if target is not None else None,
       "old_truck_min":target.findtext("min") if target is not None else None,
       "old_truck_max":target.findtext("max") if target is not None else None,
       "old_event_children":[v.get("type") for v in target.findall("./children/child")] if target is not None else [],
       "old_dolnik_spots":spot,
       "original_site_xza":list(S),
       "field_backpack_64_AliceBag_Green_defined":types.find("type[@name='AliceBag_Green']") is not None,
       "truck_variants":trucks,
       "does_not_observe_actual_vehicle_positions":True,
       "cannot_guarantee_force_respawn_from_event_nominal_alone":True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
