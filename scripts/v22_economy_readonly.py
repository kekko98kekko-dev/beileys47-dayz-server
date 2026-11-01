#!/usr/bin/env python3
"""V22 conservative read-only examination of live DayZ console economy/vehicle/spawn settings."""
from __future__ import annotations
import hashlib,json,os,posixpath,re,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
FILES=("db/types.xml","db/events.xml","cfgspawnabletypes.xml",
       "cfgeventspawns.xml","cfgplayerspawnpoints.xml","cfggameplay.json","db/messages.xml")
ITEMS=("BandageDressing","Morphine","TetracyclineAntibiotics","CharcoalTablets",
       "WaterBottle","SodaCan_Cola","HuntingKnife","NailBox","WoodenPlank",
       "AmmoBox_556x45_20Rnd","AmmoBox_762x39_20Rnd","Battery9V",
       "CarBattery","TruckBattery","SparkPlug","GlowPlug","CarRadiator",
       "TireRepairKit","EpoxyPutty","ElectronicRepairKit","DuctTape",
       "GunCase_Black","GunCase_White","GunCase_Orange",
       "GunCaseKeys_Red","GunCaseKeys_Blue","GunCaseKeys_Orange",
       "ScientificBriefcase","ScientificBriefcaseKeys",
       "ShippingContainerKeys_Blue","ShippingContainerKeys_Orange")
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Missing secret")
    mission=resolve_mission(token)
    raw={p:download_one(token,posixpath.join(mission,p)) for p in FILES}
    types=ET.fromstring(raw["db/types.xml"])
    ev=ET.fromstring(raw["db/events.xml"])
    spawn=ET.fromstring(raw["cfgspawnabletypes.xml"])
    points=ET.fromstring(raw["cfgplayerspawnpoints.xml"])
    gp=json.loads(raw["cfggameplay.json"])
    server=game_state(token)
    names={node.get("name"):node for node in types.findall("type")}
    report={"mode":"READ_ONLY","server_status":game_status(server),"players_connected":players(server),
        "source_hashes":{p:hashlib.sha256(b).hexdigest() for p,b in raw.items()},
        "loot_classes":{},"vehicle_events":[],"player_spawn_root":points.tag,
        "player_spawn_entries":len(list(points.iter())),"gameplay_world_spawners":
             gp.get("WorldsData",{}).get("objectSpawnersArr"),
        "messages_total":len(ET.fromstring(raw["db/messages.xml"]).findall("message")),
        "password_value_excluded":True,
        "ps5_tested":False,"persistence_backup_verified":False}
    for cls in ITEMS:
        n=names.get(cls)
        if n is None:
            report["loot_classes"][cls]={"registered":False}
            continue
        item={"registered":True,"nominal":n.findtext("nominal"),
              "min":n.findtext("min"),"lifetime":n.findtext("lifetime"),
              "restock":n.findtext("restock"),"quantmin":n.findtext("quantmin"),
              "quantmax":n.findtext("quantmax"),
              "usage":[x.get("name") for x in n.findall("usage")],
              "category":[x.get("name") for x in n.findall("category")]}
        st=spawn.find("type[@name='"+cls+"']")
        item["spawnable_present"]=st is not None
        if st is not None:item["cargo_names"]=[x.get("name") for x in st.findall(".//cargo/item")][:15]
        report["loot_classes"][cls]=item
    for e in ev.findall("event"):
        n=e.get("name","")
        if re.search(r"(Vehicle|HeliCrash|MilitaryConvoy|Boat)",n,re.I):
            report["vehicle_events"].append({ "name":n,"nominal":e.findtext("nominal"),
                "min":e.findtext("min"),"max":e.findtext("max"),
                "lifetime":e.findtext("lifetime"),"restock":e.findtext("restock")})
    settings=server.get("settings",{}) if isinstance(server.get("settings"),dict) else {}
    public={}
    for bucket,keys in settings.items():
        if isinstance(keys,dict):
            for k,v in keys.items():
                if re.fullmatch(r"(?i)(hostname|serverName|serverDescription|description|serverNightTimeAcceleration|disable3rdPerson|persistance|persistence)",str(k)):
                    public[str(k)]=v if isinstance(v,(int,float,bool)) else str(v)[:180]
    report["non_secret_public_settings"]=public
    out=Path("deploy/v22/LIVE_ECONOMY_READONLY.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
