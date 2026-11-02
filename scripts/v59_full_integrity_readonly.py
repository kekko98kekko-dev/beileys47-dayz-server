#!/usr/bin/env python3
"""V59 expanded BEILEYS47 Nitrado PlayStation/Livonia release integrity.

100% GET-only. Never download player persistence or read ADM player data.
Tests config syntax and relationships; CANNOT prove actual FPS, in-world car
counts, terrain/model Y alignment, loot already in container or true PS5 tests.
Do not treat passing static checks as '0 bugs'.
"""
from __future__ import annotations
import collections,datetime as dt,hashlib,json,math,os,posixpath,re,sys
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,call_api,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
from v20_unlimited_sprint import setting_state
from v50_full_live_audit import PATHS,review as baseline_review
from v36_nitrado_backups_readonly import analyze as backup_review
from v53_gunter_gift import EVENT as REMOVED_GUNTER, CAR as GUNTER_CLASS
from v44_single_original_dolnik_truck import NEW as DOLNIK_EVENT,OLD as OLD_DOLNIK_EVENTS,TRUCK

EXTRAS=(
    "db/globals.xml","db/economy.xml","cfgeconomycore.xml",
    "cfgrandompresets.xml","cfglimitsdefinition.xml",
)
OUT=Path("deploy/v59/EXPANDED_SERVER_AUDIT.json")
REMOVED_ZONES=(("InfectedArmy","8960.0","7810.0"),("InfectedArmy","9040.0","7730.0"))
REMOVED_SCENES=(
    "custom/beileys47_v35_zone47_full_25.json",
    "custom/beileys47_v29_zone47_p1_guardbox.json",
)
PRESERVE_SCENES=(
    "custom/beileys47_v16_three_hotspots.json",
    "custom/beileys47_dolnik_military_base_v9.json",
)
ROOT_TAGS={
    "db/types.xml":"types","db/events.xml":"events",
    "cfgeventspawns.xml":"eventposdef","cfgspawnabletypes.xml":"spawnabletypes",
    "db/messages.xml":"messages","cfgweather.xml":"weather",
    "env/zombie_territories.xml":"territory-type",
    "cfgplayerspawnpoints.xml":"playerspawnpoints",
    "db/globals.xml":"variables","db/economy.xml":"economy",
}

def sh(b):return hashlib.sha256(b).hexdigest()
def parse(blob):return ET.fromstring(blob)
def unique(seq):
    counts=collections.Counter(seq)
    return [k for k,n in counts.items() if n>1]
def numeric(v):
    try:return math.isfinite(float(v))
    except (ValueError,TypeError):return False
def getint(e,field):
    try:return int(e.findtext(field))
    except (ValueError,TypeError,AttributeError):return None
def output(result):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V59 AUDIT status:",result.get("server",{}).get("status"),
          "checks",len(result["checks"]),"pass",sum(result["checks"].values()),
          "critical",len(result["critical_findings"]),
          "warnings",len(result["warnings"]),
          "optional_read_errors",len(result.get("optional_read_errors",{})),
          flush=True)
    for finding in (result["critical_findings"]+result["warnings"])[:25]:
        print("V59 FINDING:",finding["severity"],finding["code"],
              finding.get("count",""),flush=True)

def analyze(blobs,provider,server,optional_errors):
    checks={}
    critical=[]
    warnings=[]
    observations={}
    def chk(name,test,message=None):
        checks[name]=bool(test)
        if not test:
            critical.append({"severity":"critical","code":name,"detail":message or "Check failed"})
    def warn(code,detail,count=None):
        x={"severity":"warning","code":code,"detail":detail}
        if count is not None:x["count"]=count
        warnings.append(x)
    baseline=baseline_review({p:blobs[p] for p in PATHS},server,provider)
    for k,v in baseline["checks"].items(): chk("base_"+k,v)
    chk("server_running",baseline["server_status"] in ("started","running"))
    chk("gameplay_overrides_enabled",baseline["gameplay_file_enabled"])
    chk("map_player_position_available",baseline["map_position_display_configured"])
    chk("map_ownership_ignored",baseline["map_ownership_ignored"])
    chk("nitrado_backup_available",
        provider.get("provider_backup_exists") is True and provider.get("restore_possible") is True)
    chk("configuration_files_all_parse",
        all(p in blobs for p in PATHS))
    for p,tag in ROOT_TAGS.items():
        if p in blobs:
            actual=parse(blobs[p]).tag
            # XML spec differences: record mismatch as warning for less rigid optional files.
            if p in ("db/globals.xml","db/economy.xml","cfgplayerspawnpoints.xml"):
                if actual != tag:warn("unexpected_xml_root_"+p,
                                    "Review root tag, no auto write; found "+actual)
            else:chk("xml_root_"+p,actual==tag,"unexpected XML root")
    gp=json.loads(blobs["cfggameplay.json"])
    refs=gp.get("WorldsData",{}).get("objectSpawnersArr",[])
    chk("spawner_registry_is_unique",isinstance(refs,list) and not unique(refs))
    chk("zone47_retired_and_not_referenced",
        all(p not in refs for p in REMOVED_SCENES))
    chk("dolnik_and_three_hotspots_registered",
        all(p in refs for p in PRESERVE_SCENES))
    extra_scenes=[p for p in refs if p not in PRESERVE_SCENES]
    observations["active_world_scenes"]=list(refs)
    if extra_scenes:warn("additional_registered_scenes",
       "Unrelated scene registrations require runtime altitude/interaction checks",
       len(extra_scenes))
    for p in refs:
        chk("active_scene_file_exists_"+p,p in blobs,
            "Registered Object Spawner JSON missing from current mission: "+p)
        if p not in blobs:continue
        try:objects=json.loads(blobs[p]).get("Objects")
        except (ValueError,AttributeError):objects=None
        chk("active_scene_json_valid_"+p,isinstance(objects,list))
        if not isinstance(objects,list):continue
        chk("active_scene_nonempty_"+p,len(objects)>0)
        coords=[]
        bad=[]
        for idx,o in enumerate(objects):
            v=o.get("pos") if isinstance(o,dict) else None
            valid=(isinstance(o,dict) and isinstance(o.get("name"),str) and
               isinstance(v,list) and len(v)==3 and all(numeric(q) for q in v) and
               0<=float(v[0])<=12800 and 0<=float(v[2])<=12800 and
               -20<=float(v[1])<=1200 and
               isinstance(o.get("ypr"),list) and len(o["ypr"])==3)
            if valid:coords.append((round(float(v[0]),3),round(float(v[2]),3)))
            else:bad.append(idx)
        chk("active_scene_positions_valid_"+p,len(bad)==0,
            "Invalid scene coordinates/model orientation on indices: "+str(bad[:8]))
        repeated=unique(coords)
        if repeated:warn("duplicate_scene_xz_"+p,
                         "Identical horizontal positions in active scene",
                         len(repeated))
        observations.setdefault("active_scene_object_counts",{})[p]=len(objects)
    events=parse(blobs["db/events.xml"])
    points=parse(blobs["cfgeventspawns.xml"])
    spawnprofiles=parse(blobs["cfgspawnabletypes.xml"])
    items=parse(blobs["db/types.xml"])
    names=[q.get("name") for q in items.findall("type")]
    evs=events.findall("event")
    evnames=[e.get("name") for e in evs]
    posnames=[e.get("name") for e in points.findall("event")]
    profiles=[e.get("name") for e in spawnprofiles.findall("type")]
    chk("unique_ce_item_names",not unique(names))
    chk("unique_ce_event_names",not unique(evnames))
    chk("unique_event_position_groups",not unique(posnames))
    chk("unique_spawnable_profile_names",not unique(profiles))
    itemset=set(names)
    eventset=set(evnames)
    poss=set(posnames)
    chk("gift_gunter_event_removed",REMOVED_GUNTER not in eventset)
    chk("gift_gunter_fixed_point_removed",REMOVED_GUNTER not in poss)
    chk("vanilla_gunter_event_preserved","VehicleHatchback02" in eventset)
    chk("vanilla_black_gunter_profile_preserved",GUNTER_CLASS in profiles)
    chk("dolnik_new_m3s_event_present",DOLNIK_EVENT in eventset and DOLNIK_EVENT in poss)
    chk("dolnik_old_sources_inactive",all(
        (e:=events.find("event[@name='"+name+"']")) is not None and
        getint(e,"nominal")==0 and e.findtext("active")=="0"
        for name in OLD_DOLNIK_EVENTS))
    chk("dolnik_ultimate_spawns_truck",
        any(c.get("type")==TRUCK for c in
            events.find("event[@name='"+DOLNIK_EVENT+"']").findall("./children/child"))
        if DOLNIK_EVENT in eventset else False)
    chk("dolnik_original_position_unique",
        len(points.find("event[@name='"+DOLNIK_EVENT+"']").findall("pos"))==1
        if DOLNIK_EVENT in poss else False)
    invalid_counts=[]
    for e in evs:
        a=getint(e,"nominal");mi=getint(e,"min");ma=getint(e,"max")
        if any(x is None or x<0 for x in (a,mi,ma)):
            invalid_counts.append(e.get("name"))
    chk("ce_event_counts_parse_nonnegative",not invalid_counts,
        "Invalid CE event counts: "+str(invalid_counts[:8]))
    odd_count=[e.get("name") for e in evs
               if None not in (getint(e,"nominal"),getint(e,"max"))
               and getint(e,"nominal")>getint(e,"max")]
    if odd_count:warn("events_nominal_above_max",
                     "Event target above max; engine may cap it",len(odd_count))
    invalid_type=[]
    odd_type=[]
    for e in items.findall("type"):
        a=getint(e,"nominal");mi=getint(e,"min");life=getint(e,"lifetime")
        if a is None or mi is None or life is None or min(a,mi,life)<0:
            invalid_type.append(e.get("name"))
        elif mi>a and a>0:odd_type.append(e.get("name"))
    chk("ce_type_core_counts_and_lifetime_nonnegative",not invalid_type,
        "CE types with invalid fields: "+str(invalid_type[:8]))
    if odd_type:warn("loot_min_above_nominal",
                     "Loot threshold above target, inspect balance",len(odd_type))
    custom_bad=[]
    for e in evs:
        if not (e.get("name") or "").startswith("VehicleBEILEYS47"):continue
        if e.findtext("active")!="1":continue
        group=points.find("event[@name='"+e.get("name")+"']")
        if group is None or not group.findall("pos"):custom_bad.append(e.get("name"))
        for child in e.findall("./children/child"):
            if child.get("type") not in itemset:custom_bad.append(e.get("name"))
    chk("active_custom_vehicle_events_have_point_and_types",not custom_bad,
        "Active BEILEYS47 vehicle event lost point or classname: "+str(custom_bad))
    unknown_spawns=[n for n in posnames if n not in eventset]
    if unknown_spawns:warn("positions_without_corresponding_event",
        "Unused event position names; may be legitimate legacy definitions",len(unknown_spawns))
    observations["ce_counts"]={
        "item_types":len(names),"events":len(evs),
        "spawn_position_event_groups":len(posnames),"spawnable_profiles":len(profiles),
        "event_nominal_gt_max":len(odd_count),"loot_min_gt_nominal":len(odd_type),
        "unknown_event_position_groups":len(unknown_spawns)
    }
    zone_doc=parse(blobs["env/zombie_territories.xml"])
    zone_nodes=zone_doc.findall(".//zone")
    tuples={(z.get("name"),z.get("x"),z.get("z")) for z in zone_nodes}
    chk("zone47_2_custom_infected_spawns_removed",
        all(z not in tuples for z in REMOVED_ZONES))
    invalid_zones=[]
    for idx,z in enumerate(zone_nodes):
        # original vanilla territories may omit some fields; check required geometry.
        if not all(numeric(z.get(k)) for k in ("x","z","r")): invalid_zones.append(idx)
        else:
            if float(z.get("r"))<0 or float(z.get("r"))>2000:invalid_zones.append(idx)
    chk("infected_geometries_valid",not invalid_zones,
        "Invalid infected zone coordinates/radius "+str(invalid_zones[:8]))
    observations["infected_territory_zones_count"]=len(zone_nodes)
    for p in ("cfgeconomycore.xml","db/economy.xml","db/globals.xml",
              "cfgrandompresets.xml","cfglimitsdefinition.xml"):
        if p not in blobs:warn("not_readable_"+p,
            "Optional economy file unavailable, complete economy cross-check unresolved")
    if "db/globals.xml" in blobs:
        root=parse(blobs["db/globals.xml"])
        variables=[e.get("name") for e in root.findall(".//var")]
        chk("globals_unique_variables",not unique(variables))
        observations["globals_variables"]=len(variables)
    w=parse(blobs["cfgweather.xml"])
    for tag in ("fog","rain","overcast"):
        e=w.find(tag+"/limits")
        if e is not None:
            mi,ma=e.get("min"),e.get("max")
            chk("weather_"+tag+"_bounds",numeric(mi) and numeric(ma)
                and float(mi)<=float(ma))
    message_doc=parse(blobs["db/messages.xml"])
    contents="\n".join((a.text or "") for m in message_doc.findall("message")
                       for a in m.iter())
    if re.search(r"\bzona[\s_-]*47\b|gunter\s*gift",contents,re.I):
        warn("outdated_in_game_messages",
             "Server message may mention removed Zone47 or personal Gunter gift")
    observations["messages_count"]=len(message_doc.findall("message"))
    preset_paths=gp.get("PlayerData",{}).get("spawnGearPresetFiles",[])
    observations["starter_kit_refs"]=preset_paths
    if isinstance(preset_paths,list):
        for p in preset_paths:
            if not isinstance(p,str) or p.startswith("/") or ".." in p:
                chk("starter_kit_path_safe",False,"Unexpected gear path")
                continue
            chk("starter_kit_exists_"+p,p in blobs,
                "Referenced spawnGearPresetFiles path not downloadable: "+p)
    else:chk("starter_kit_paths_list",False)
    observations["backup_count"]=provider.get("backup_count")
    observations["provider_restore_possible"]=provider.get("restore_possible")
    observations["physical_vehicle_instances_examined"]=False
    observations["physical_spawns_and_model_y_tested"]=False
    observations["ps5_ps4_fps_latency_measured"]=False
    observations["persistence_restore_drill_executed"]=False
    observations["RPT_logs_part_of_this_check"]=False
    observations["world_storage_read"]=False
    observations["remaining_limitations"]=[
      "In-game verification is required for object geometry, collision and real loot contents",
      "A running server cannot guarantee zero lag, no crashes or no bugs on PS4/PS5",
      "Persistent cars, tents and bases are not enumerated through the configuration API",
      "Bunker, special functional locks, script-driven hordes and fridge cooling are not implemented",
      "A provider backup record does not certify a successful restoration",
    ]
    return checks,critical,warnings,observations,baseline

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Missing read-only Nitrado token")
    mission=resolve_mission(token)
    blobs={}
    optional={}
    for p in dict.fromkeys((*PATHS,*EXTRAS)):
        try:blobs[p]=download_one(token,posixpath.join(mission,p))
        except Exception as ex:
            if p in PATHS:raise
            optional[p]=type(ex).__name__
    gp=json.loads(blobs["cfggameplay.json"])
    refs=gp.get("WorldsData",{}).get("objectSpawnersArr",[])
    kit=gp.get("PlayerData",{}).get("spawnGearPresetFiles",[])
    if not isinstance(refs,list):raise NitradoError("Invalid objectSpawner refs")
    for p in (*refs,*(kit if isinstance(kit,list) else [])):
        if p in blobs:continue
        if not isinstance(p,str) or not p or ".." in p or p.startswith("/") or "\\" in p:
            optional[str(p)[:50]]="unsafe path"
            continue
        try:blobs[p]=download_one(token,posixpath.join(mission,p))
        except Exception as e:optional[p]=type(e).__name__
    s0=game_state(token)
    try:provider=backup_review(
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
        call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    except Exception as e:
        provider={"provider_backup_exists":False,"restore_possible":None,
                  "provider_error_type":type(e).__name__}
    checks,critical,warnings,obs,baseline=analyze(blobs,provider,s0,optional)
    s1=game_state(token)
    checks["server_still_running_after_readonly_audit"]=(game_status(s1) in
        ("started","running"))
    if not checks["server_still_running_after_readonly_audit"]:
        critical.append({"severity":"critical","code":"server_still_running_after_readonly_audit"})
    report={
      "version":"V59","mode":"GET_ONLY_NO_RESTART_NO_WIPE","platform":"DayZ PlayStation Livonia",
      "utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "server":{"status":game_status(s1),"players_online":players(s1),
                "gameplay_override":setting_state(s1)},
      "config_only_proof":True,
      "checks":checks,"critical_findings":critical,"warnings":warnings,
      "optional_read_errors":optional,"observations":obs,
      "provider_backup":provider,"file_count_read":len(blobs),
      "file_sha256":{p:sh(v) for p,v in blobs.items()},
      "world_mutations":0,"physical_PS5_test":False,
      "never_claim_perfect_runtime":True
    }
    output(report)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V59 ERROR",type(e).__name__,str(e)[:170],file=sys.stderr)
        raise SystemExit(1)
