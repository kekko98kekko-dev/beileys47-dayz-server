#!/usr/bin/env python3
"""BEILEYS47 V16 live readback audit; NO writes to Nitrado."""
import os,json,hashlib,posixpath,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,SERVICE_ID,NitradoError
from deploy_beileys47_v15 import game_state,game_status
token=os.environ.get("NITRADO_API_TOKEN","").strip()
if not token:raise NitradoError("Nitrado secret unavailable")
mission=resolve_mission(token)
def get(name):return download_one(token,posixpath.join(mission,name))
def xml(name):return ET.fromstring(get(name))
gp=json.loads(get("cfggameplay.json"))
scene=json.loads(get("custom/beileys47_v16_three_hotspots.json"))
dolnik=json.loads(get("custom/beileys47_dolnik_military_base_v9.json"))
zombie=xml("env/zombie_territories.xml")
proto=xml("mapgroupproto.xml")
db=xml("db/types.xml")
weather=xml("cfgweather.xml")
events=xml("db/events.xml")
gs=game_state(token)
settings=gs.get("settings") or {}
night=settings.get("config",{}).get("serverNightTimeAcceleration") if isinstance(settings,dict) else None
horde={(z.get("name"),z.get("x"),z.get("z")) for t in zombie.findall("territory") for z in t.findall("zone")}
verify={
 "nitrado_state":game_status(gs),
 "v16_registered":"custom/beileys47_v16_three_hotspots.json" in gp["WorldsData"]["objectSpawnersArr"],
 "zone_scene_props":len(scene.get("Objects",[])),
 "dolnik_tents":sum("Tent" in obj["name"] for obj in dolnik.get("Objects",[])),
 "medical_tent_lootmax":proto.find("group[@name='Land_Medical_Tent_Big']").get("lootmax"),
 "military_tent_lootmax":proto.find("group[@name='Land_Mil_Tent_Big2_4']").get("lootmax"),
 "hordes_confirmed":all(x in horde for x in [
    ("InfectedArmy","7100.0","6965.0"),
    ("InfectedArmy","9022.5","7457.9"),
    ("InfectedMedic","11490.0","461.0")]),
 "no_fog":weather.find("fog/limits").get("max")=="0.0",
 "v15_truck_event_intact":events.find("event[@name='VehicleBEILEYS47DolnikTest']") is not None,
 "night_acceleration":night,
 "gun_case_orange_nominal":db.find("type[@name='GunCase_Orange']/nominal").text,
 "no_wipe":True,
 "gameplay_ps5_verified":False
}
verify["remote_settings_and_files_verified"]=(verify["nitrado_state"] in {"started","running"}
    and verify["v16_registered"] and verify["zone_scene_props"]==32
    and verify["dolnik_tents"]==2 and verify["medical_tent_lootmax"]=="10"
    and verify["military_tent_lootmax"]=="8" and verify["hordes_confirmed"]
    and verify["no_fog"] and verify["v15_truck_event_intact"]
    and str(night) in {"8","8.0"})
path=Path("deploy/v16/LIVE_AUDIT.json")
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(verify,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(verify,indent=2))
if not verify["remote_settings_and_files_verified"]:raise NitradoError("V16 live audit had a mismatch")
