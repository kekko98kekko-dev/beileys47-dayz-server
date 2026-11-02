#!/usr/bin/env python3
"""V50 BEILEYS47 integrated GET-only release inventory.

Reports what DayZ PS4/PS5 Nitrado really has in its LIVE files.
Never modifies Nitrado, starts/stops it, reads world storage or player records.
Do not confuse configured scenes and actual PS5 physical gameplay verification.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import posixpath
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission, download_one, call_api, NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
from v20_unlimited_sprint import setting_state
from v44_single_original_dolnik_truck import installed as truck_installed
from v37_zone47_infected_patches import already_installed as two_infected_installed
from v45_safe_loot_ttl import patch as pending_ttl_patch
from v48_build_anywhere_preview import BALANCED
from v36_nitrado_backups_readonly import analyze

PATHS=(
    "cfggameplay.json",
    "custom/beileys47_v16_three_hotspots.json",
    "custom/beileys47_dolnik_military_base_v9.json",
    "custom/beileys47_v35_zone47_full_25.json",
    "env/zombie_territories.xml",
    "db/events.xml",
    "cfgeventspawns.xml",
    "cfgspawnabletypes.xml",
    "db/types.xml",
    "db/messages.xml",
    "cfgweather.xml",
    "mapgroupproto.xml",
    "cfgplayerspawnpoints.xml",
)
OUT=Path("deploy/v50/INDEPENDENT_LIVE_RELEASE_AUDIT.json")

def digest(blob):return hashlib.sha256(blob).hexdigest()
def safe_number(v):
    return type(v) in (int,float)
def review(blobs,server,provider=None):
    gp=json.loads(blobs["cfggameplay.json"])
    v16=json.loads(blobs["custom/beileys47_v16_three_hotspots.json"])
    dolnik=json.loads(blobs["custom/beileys47_dolnik_military_base_v9.json"])
    v35=json.loads(blobs["custom/beileys47_v35_zone47_full_25.json"])
    event=ET.fromstring(blobs["db/events.xml"])
    proto=ET.fromstring(blobs["mapgroupproto.xml"])
    weather=ET.fromstring(blobs["cfgweather.xml"])
    types=ET.fromstring(blobs["db/types.xml"])
    messages=ET.fromstring(blobs["db/messages.xml"])
    zones=ET.fromstring(blobs["env/zombie_territories.xml"])
    spawnpoints=ET.fromstring(blobs["cfgplayerspawnpoints.xml"])
    active=gp.get("WorldsData",{}).get("objectSpawnersArr",[])
    build=gp.get("BaseBuildingData",{})
    st=gp.get("PlayerData",{}).get("StaminaData",{})
    map_data=gp.get("MapData",{})
    zone_index={(z.get("name"),z.get("x"),z.get("z")) for z in zones.findall(".//zone")}
    def nominal(name):
        e=event.find(f"event[@name='{name}']")
        return int(e.findtext("nominal")) if e is not None and e.findtext("nominal","").isdigit() else None
    old_names=("VehicleBEILEYS47DolnikTest","VehicleBEILEYS47DolnikRescueV40")
    older_disabled=all((e:=event.find(f"event[@name='{n}']")) is not None and
                       e.findtext("active")=="0" and e.findtext("nominal")=="0"
                       for n in old_names)
    try:
        truck=truck_installed({p:blobs[p] for p in
            ("db/events.xml","cfgeventspawns.xml","cfgspawnabletypes.xml")})
    except Exception:truck=False
    try:
        infected=two_infected_installed(blobs["env/zombie_territories.xml"])
    except Exception:infected=False
    try:
        _,ttl_left=pending_ttl_patch(blobs["db/types.xml"])
        ttl_count=len(ttl_left)
    except Exception:ttl_count=None
    checks={
      "v16_three_hotspots_scene_registered":"custom/beileys47_v16_three_hotspots.json" in active,
      "v16_scene_32_props":len(v16.get("Objects",[]))==32,
      "dolnik_two_tents":sum("Tent" in o.get("name","") for o in dolnik.get("Objects",[]))==2,
      "dolnik_tent_lootmax_10_and_8":
          proto.find("group[@name='Land_Medical_Tent_Big']") is not None and
          proto.find("group[@name='Land_Medical_Tent_Big']").get("lootmax")=="10" and
          proto.find("group[@name='Land_Mil_Tent_Big2_4']") is not None and
          proto.find("group[@name='Land_Mil_Tent_Big2_4']").get("lootmax")=="8",
      "v57_bugged_zone47_26_props_disabled":
          "custom/beileys47_v35_zone47_full_25.json" not in active and
          "custom/beileys47_v29_zone47_p1_guardbox.json" not in active and
          len(v35.get("Objects",[]))==25,
      "v16_original_infected_territories":all(x in zone_index for x in (
          ("InfectedArmy","7100.0","6965.0"),
          ("InfectedArmy","9022.5","7457.9"),
          ("InfectedMedic","11490.0","461.0"))),
      "v57_zone47_infected_territories_retired":
          not infected and all(
              (name,f"{x:.1f}",f"{z:.1f}") not in zone_index
              for name,x,z,*rest in (
                  ("InfectedArmy",8960.0,7810.0),
                  ("InfectedArmy",9040.0,7730.0)
              )
          ),
      "v20_unlimited_sprint_configured":
          all(st.get(k)==0 for k in ("sprintStaminaModifierErc",
                                      "sprintStaminaModifierCro",
                                      "staminaKgToStaminaPercentPenalty")),
      "v48_build_anywhere_balanced_configured":
          all(build.get(s,{}).get(k) is True for s,k in BALANCED),
      "v44_new_dolnik_truck_event_registered":truck and older_disabled,
      "v45_loot_lifetime_4h_rules":ttl_count==0,
      "night_acceleration_8":str((server.get("settings") or {}).get("config",{})
                         .get("serverNightTimeAcceleration")) in ("8","8.0"),
      "fog_disabled":weather.find("fog/limits") is not None and
              weather.find("fog/limits").get("max")=="0.0",
      "helis_nominal_at_least_5":nominal("StaticHeliCrash") is not None and nominal("StaticHeliCrash")>=5,
      "convoys_nominal_at_least_5":nominal("StaticMilitaryConvoy") is not None and nominal("StaticMilitaryConvoy")>=5,
      "motorcycles_nominal_11":nominal("VehicleMotorbike")==11,
      "six_server_messages":len(messages.findall("message"))>=6,
    }
    special_keys=("GunCase_Black","GunCase_White","GunCase_Orange",
                  "GunCaseKeys_Red","GunCaseKeys_Blue","GunCaseKeys_Orange")
    key_available={key:(types.find(f"type[@name='{key}']") is not None)
                   for key in special_keys}
    expected=['pending_gameplay_check: physically find truck & inspect fuel and cargo',
      'pending_gameplay_check: physical stacking of crates/barrels/fences',
      'pending_gameplay_check: fresh spawn inventory / actual Dolnik positioning',
      'retired_zone47_bugged_26_props_and_two_infected_patches: new manual map design pending',
      'pending_gameplay_check: loot, key interactions, PS4/PS5 performance and persistence',
      'not_supported_vanilla_console: true scripted roaming hordes',
      'not_supported_vanilla_console: fridge cooling or winner-specific auto item payouts',
      'not_supported_vanilla_console: exact 2-restart loose-loot removal',
      'not_supported_vanilla_console: exactly timed persistent plank refills / instant truck replacement',
      'not_installed: custom underground bunker and functional lockable shipping containers']
    return {
        "mode":"GET_ONLY_NO_REMOTE_CHANGES",
        "server_status":game_status(server),"players_online":players(server),
        "gameplay_file_enabled":setting_state(server)=="enabled",
        "checks":checks,"critical_regressions":[k for k,v in checks.items() if not v],
        "map_position_display_configured":map_data.get("displayPlayerPosition") is True,
        "map_ownership_ignored":map_data.get("ignoreMapOwnership") is True,
        "starter_preset_paths":gp.get("PlayerData",{}).get("spawnGearPresetFiles",[]),
        "spawnpoint_xml_root":spawnpoints.tag,
        "configured_guncase_key_classes":key_available,
        "provider_backup_availability":provider,
        "loot_lifetime_classes_remaining_above_4h":ttl_count,
        "configured_object_spawners_count":len(active),
        "observed_v35_object_count":len(v35.get("Objects",[])),
        "world_persistence_save_verified":False,
        "ps5_ps4_runtime_tested":False,
        "exactly_one_physical_m3s_verified":False,
        "stored_old_trucks_deleted_verified":False,
        "full_original_scope_100_percent":False,
        "unverified_or_unavailable":expected,
        "file_checksums_sha256":{p:digest(blob) for p,blob in blobs.items()}
    }

def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Missing read-only Nitrado secret")
    mission=resolve_mission(token)
    blobs={path:download_one(token,posixpath.join(mission,path)) for path in PATHS}
    srv=game_state(token)
    provider=None
    try:
        provider=analyze(
            call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
            call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    except Exception:
        provider={"status":"not_confirmed_in_this_read"}
    result=review(blobs,srv,provider)
    result["recorded_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V50 GET-only audit; status:",result["server_status"],
          "checks:",len(result["checks"]),"passes:",sum(result["checks"].values()),
          "missing:",result["critical_regressions"],
          "ps5_verified:",False)
    if result["critical_regressions"]:
        raise NitradoError("Configuration regression(s) found; inspect V50 audit artifact")

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V50 ERROR",type(e).__name__,str(e)[:150],flush=True)
        raise SystemExit(1)
