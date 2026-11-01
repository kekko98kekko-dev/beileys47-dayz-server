#!/usr/bin/env python3
"""V18 read-only live Nitrado inventory; no writes, restarts, wipes."""
from __future__ import annotations
import hashlib,json,os,posixpath,sys,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError,SERVICE_ID
from deploy_beileys47_v15 import game_state,game_status,players
from v20_unlimited_sprint import setting_state
from v21_safe_discovery_messages import MESSAGES as V21_NOTICES

REQUIRED=(
"cfggameplay.json","custom/beileys47_v16_three_hotspots.json",
"custom/beileys47_dolnik_military_base_v9.json",
"custom/beileys47_v29_zone47_p1_guardbox.json",
"custom/beileys47_v35_zone47_full_25.json","db/types.xml",
"cfgspawnabletypes.xml","db/events.xml","cfgweather.xml",
"mapgrouppos.xml","mapgroupproto.xml","db/messages.xml",
"env/zombie_territories.xml","cfgeventspawns.xml",
)
CASES=("GunCase_Black","GunCase_White","GunCase_Orange",
"GunCaseKeys_Blue","GunCaseKeys_Red","GunCaseKeys_Orange",
"ScientificBriefcase","ScientificBriefcaseKeys",
"ShippingContainerKeys_Blue","ShippingContainerKeys_Orange")
def evaluate(gs,raw):
    gp=json.loads(raw["cfggameplay.json"])
    scene=json.loads(raw["custom/beileys47_v16_three_hotspots.json"])
    dolnik=json.loads(raw["custom/beileys47_dolnik_military_base_v9.json"])
    p1=json.loads(raw["custom/beileys47_v29_zone47_p1_guardbox.json"])
    v35=json.loads(raw["custom/beileys47_v35_zone47_full_25.json"])
    versioned_v35=json.loads(Path("config/v33/BEILEYS47_ZONE47_25_NOT_LIVE.json").read_text(encoding="utf-8"))
    types=ET.fromstring(raw["db/types.xml"])
    spawn=ET.fromstring(raw["cfgspawnabletypes.xml"])
    events=ET.fromstring(raw["db/events.xml"])
    proto=ET.fromstring(raw["mapgroupproto.xml"])
    terr=ET.fromstring(raw["env/zombie_territories.xml"])
    messages=ET.fromstring(raw["db/messages.xml"])
    weather=ET.fromstring(raw["cfgweather.xml"])
    defined={e.get("name"):e for e in types.findall("type")}
    special={}
    for k in CASES:
        t=defined.get(k)
        if t is None:
            special[k]={"exists":False}
            continue
        car=spawn.find("type[@name='"+k+"']")
        special[k]={"exists":True,"nominal":int(t.findtext("nominal","0")),
           "minimum":int(t.findtext("min","0")),
           "categories":[v.get("name") for v in t.findall("category")],
           "usage":[v.get("name") for v in t.findall("usage")],
           "cargo_items":[v.get("name") for v in car.findall(".//cargo/item")] if car is not None else []}
    settings=gs.get("settings") if isinstance(gs.get("settings"),dict) else {}
    passwords=[str(v) for entries in settings.values() if isinstance(entries,dict)
               for key,v in entries.items() if str(key).lower() in {"password","serverpassword","password_server"}]
    hints=None if not passwords else all(v.strip()=="" for v in passwords)
    return {"service_id":SERVICE_ID,"mode":"read_only","status":game_status(gs),
      "players_count":players(gs),
      "files":{k:{"sha256":hashlib.sha256(v).hexdigest(),"bytes":len(v)} for k,v in raw.items()},
      "v16_registered":"custom/beileys47_v16_three_hotspots.json" in gp["WorldsData"]["objectSpawnersArr"],
      "v16_scene_props":len(scene.get("Objects",[])),
      "v29_p1_registered":"custom/beileys47_v29_zone47_p1_guardbox.json" in gp["WorldsData"]["objectSpawnersArr"],
      "v29_p1_scene_count":len(p1.get("Objects",[])),
      "v35_registered":"custom/beileys47_v35_zone47_full_25.json" in gp["WorldsData"]["objectSpawnersArr"],
      "v35_scene_count":len(v35.get("Objects",[])),
      "v35_exactly_matches_versioned_25":v35==versioned_v35,
      "v35_total_zone47_scene_objects":len(v35.get("Objects",[]))+len(p1.get("Objects",[])),

      "v29_p1_exact_guardbox":any(
        o.get("name")=="Land_Mil_GuardBox_Green"
        and len(o.get("pos",[]))==3
        and abs(o["pos"][0]-9057.3275)<0.001
        and abs(o["pos"][1]-302.7723)<0.001
        and abs(o["pos"][2]-7822.7058)<0.001
        for o in p1.get("Objects",[])
      ),
      "dolnik_tents":sum("Tent" in x.get("name","") for x in dolnik.get("Objects",[])),
      "rare_objects":special,
      "group_positions":len(ET.fromstring(raw["mapgrouppos.xml"]).findall("group")),
      "med_tent_lootmax":proto.find("group[@name='Land_Medical_Tent_Big']").get("lootmax"),
      "mil_tent_lootmax":proto.find("group[@name='Land_Mil_Tent_Big2_4']").get("lootmax"),
      "infected_zones":[dict(name=z.get("name"),x=z.get("x"),z=z.get("z"),dmin=z.get("dmin"),dmax=z.get("dmax"))
           for t in terr.findall("territory") for z in t.findall("zone")
           if (z.get("x"),z.get("z")) in {("7100.0","6965.0"),("9022.5","7457.9"),("11490.0","461.0")}],
      "heli_nominal":events.find("event[@name='StaticHeliCrash']/nominal").text,
      "convoy_nominal":events.find("event[@name='StaticMilitaryConvoy']/nominal").text,
      "weather_fog_max":weather.find("fog/limits").get("max"),
      "messages_count":len(messages.findall("message")),
      "v21_messages_exactly_present":all(sum(m.findtext("text")==text and int(m.findtext("repeat","0"))==repeat for m in messages.findall("message"))==1 for repeat,text in V21_NOTICES),
      "night_multiplier":settings.get("config",{}).get("serverNightTimeAcceleration"),
      "v20_sprint_settings":{k:gp["PlayerData"]["StaminaData"].get(k) for k in
        ("sprintStaminaModifierErc","sprintStaminaModifierCro","staminaKgToStaminaPercentPenalty")},
      "v20_movement_settings":{k:gp["PlayerData"]["MovementData"].get(k) for k in
        ("timeToSprint","timeToStrafeSprint")},
      "gameplay_json_switch":setting_state(gs),
      "password_appears_blank":hints,"public_join_confirmed_by_console":False,
      "ps5_placement_verified":False,"player_persistence_verified":False}
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Missing secret")
    mission=resolve_mission(token)
    raw={}
    for rel in REQUIRED:
        raw[rel]=download_one(token,posixpath.join(mission,rel))
        print("READ ONLY",rel,len(raw[rel]),flush=True)
    report=evaluate(game_state(token),raw)
    path=Path("deploy/v18/LIVE_PREFLIGHT.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if not report["v16_registered"] or report["v16_scene_props"]!=32:
        raise NitradoError("V16 reference mismatch; no dependent deployments permitted")
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("V18 READONLY ERROR:",type(exc).__name__,str(exc)[:150],file=sys.stderr)
        raise SystemExit(1)
