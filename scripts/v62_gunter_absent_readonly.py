#!/usr/bin/env python3
"""Read-only diagnosis of missing V59 Gunter at Livonia X8933.20 Z7211.91.
No Nitrado writes, no restarts, no reading world persistence/players/ADM logs.
Output only structural config and aggregate engine RPT evidence.
"""
from __future__ import annotations
import collections,datetime,json,math,os,posixpath,re,sys
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission,download_one,call_api,entries_at,is_dir,entry_name,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players

X,Z=8933.20,7211.91
EVENT="VehicleBEILEYS47GunterRescueV59"
CAR="Hatchback_02_Black"
OUT=Path("deploy/v62/GUNTER_DIAGNOSTIC_GET_ONLY.json")
def fetch(token,mission,path):
    return download_one(token,posixpath.join(mission,path))
def xml(token,mission,path):
    return ET.fromstring(fetch(token,mission,path))
def nearest(points,n=12):
    return sorted(points,key=lambda v:v["distance_m"])[:n]
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise RuntimeError("Nitrado token missing")
    mission=resolve_mission(token)
    events=xml(token,mission,"db/events.xml")
    pos=xml(token,mission,"cfgeventspawns.xml")
    spawn=xml(token,mission,"cfgspawnabletypes.xml")
    types=xml(token,mission,"db/types.xml")
    cfgeconomy=xml(token,mission,"cfgeconomycore.xml")
    globalsdoc=xml(token,mission,"db/globals.xml")
    es=events.findall(f"event[@name='{EVENT}']")
    ps=pos.findall(f"event[@name='{EVENT}']")
    carprofiles=spawn.findall(f"type[@name='{CAR}']")
    targettypes=types.findall(f"type[@name='{CAR}']")
    matches=[]
    for group in pos.findall("event"):
        eventname=group.get("name","")
        if not eventname.startswith("Vehicle"):continue
        for p in group.findall("pos"):
            try:
                x=float(p.get("x"));z=float(p.get("z"))
                d=math.hypot(x-X,z-Z)
                if d<1500:
                    matches.append({"event":eventname,"distance_m":round(d,1),
                                    "x":round(x,1),"z":round(z,1)})
            except (TypeError,ValueError):continue
    event=es[0] if len(es)==1 else None
    point=ps[0].find("pos") if len(ps)==1 and len(ps[0].findall("pos"))==1 else None
    cargo=collections.Counter(i.get("name") for pr in carprofiles for i in pr.findall("./cargo/item"))
    part=collections.Counter(i.get("name") for pr in carprofiles for i in pr.findall("./attachments/item"))
    base=events.find("event[@name='VehicleHatchback02']")
    out={
       "mode":"READ_ONLY","server_files_changed":False,"restart_performed":False,
       "persistence_read":False,"player_logs_read":False,
       "event_definitions_count":len(es),"matching_position_event_count":len(ps),
       "matching_car_profile_count":len(carprofiles),"matching_car_type_count":len(targettypes),
       "event_values":({t.tag:(t.text.strip() if t.text else None)
                        for t in event if t.tag not in ("children","flags")}
                       if event is not None else {}),
       "event_flags":(dict(event.find("flags").attrib) if event is not None and event.find("flags") is not None else None),
       "event_children":([dict(i.attrib) for i in event.findall("./children/child")] if event is not None else []),
       "position":({k:point.get(k) for k in ("x","z","a")} if point is not None else None),
       "base_event_values":({t.tag:(t.text.strip() if t.text else None)
                        for t in base if t.tag not in ("children","flags")} if base is not None else {}),
       "base_event_flags":(dict(base.find("flags").attrib) if base is not None and base.find("flags") is not None else None),
       "nearby_vehicle_spawn_positions":nearest([v for v in matches if v["event"]!=EVENT]),
       "nearest_vehicle_spawn_m":(min([v["distance_m"] for v in matches if v["event"]!=EVENT],default=None)),
       "car_cargo_entry_count":sum(cargo.values()),
       "car_attachment_entry_count":sum(part.values()),
       "selected_cargo_counts":{k:cargo[k] for k in ("AKM","Mag_AKM_Drum75Rnd","CanisterGasoline","CarRadiator","PlateCarrierVest_Black","NVGoggles")},
       "car_types_xml":([dict(t.attrib,**{c.tag:(c.text or "").strip() for c in t if c.tag not in ("flags","category","usage","value")}) for t in targettypes][:2]),
       "globals_relevant":{v.get("name"):v.get("value") for v in globalsdoc.findall("var") if any(
                    q in (v.get("name") or "").lower() for q in ("vehicle","restart","clean","initial"))},
       "ce_economy_files":[dict(x.attrib) for x in cfgeconomy.findall(".//file") if "event" in (x.get("type","").lower())][:15],
       "rpt_files_checked":0,"rpt_search_status":"NOT_FOUND",
       "rpt_target_event_mentions":0,"rpt_gunter_class_mentions":0,
       "rpt_vehicle_spawn_failure_lines":0,
       "rpt_ce_event_error_lines":0,
    }
    # Optional read-only inspect of registered world object spawners near site.
    try:
        config=json.loads(fetch(token,mission,"cfggameplay.json"))
        refs=config.get("WorldsData",{}).get("objectSpawnersArr",[])
        sc=[]
        for p in refs[:20]:
            if not isinstance(p,str) or not p.startswith("custom/") or ".." in p:continue
            try:
                raw=json.loads(fetch(token,mission,p))
                objs=raw.get("Objects",[])
                for o in objs:
                    xyz=o.get("pos") if isinstance(o,dict) else None
                    if isinstance(xyz,list) and len(xyz)==3:
                        d=math.hypot(float(xyz[0])-X,float(xyz[2])-Z)
                        if d<250:sc.append({"scene":p,"distance_m":round(d,1),
                                             "class":str(o.get("name",""))[:96]})
            except (ValueError,NitradoError,TypeError,KeyError):continue
        out["nearby_custom_objects"]=nearest(sc)
    except Exception as e:out["custom_object_scan"]="unavailable_"+type(e).__name__
    # Nitrado PS logs paths, limited files and line counts; no raw player information.
    try:
        meta=call_api(token,f"/services/{SERVICE_ID}/gameservers").get("gameserver",{})
        user=meta.get("username","")
        if re.fullmatch(r"[A-Za-z0-9_-]{1,64}",str(user)):
            base="/games/"+user
            candidates=[
                base+"/ftproot/dayzps/logs",base+"/noftp/logs",
                base+"/ftproot/dayzps/config",base+"/ftproot/logs",
                base+"/ftproot/dayzstandalone/logs",base+"/ftproot/dayzps/profiles",
            ]
            for directory in candidates:
                try:
                    entries=entries_at(token,directory)
                except NitradoError:continue
                names=[entry_name(e) for e in entries if not is_dir(e)
                       and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}\\.(?:RPT|rpt)",entry_name(e))]
                for name in sorted(set(names),reverse=True)[:2]:
                    try:
                        blob=download_one(token,posixpath.join(directory,name))
                    except NitradoError:continue
                    out["rpt_files_checked"]+=1
                    out["rpt_search_status"]="SCANNED"
                    for line in blob.decode("utf-8","replace").splitlines():
                        lo=line.lower()
                        if EVENT.lower() in lo:out["rpt_target_event_mentions"]+=1
                        if CAR.lower() in lo:out["rpt_gunter_class_mentions"]+=1
                        if "vehicle" in lo and any(k in lo for k in ("spawn fail","can't spawn","cannot spawn","failed to spawn","spawn error")):
                            out["rpt_vehicle_spawn_failure_lines"]+=1
                        if ("central economy" in lo or "ce " in lo or "event" in lo) and any(
                            k in lo for k in ("invalid","failed","error","unknown")):
                            out["rpt_ce_event_error_lines"]+=1
                if out["rpt_files_checked"]:break
    except Exception as e:out["rpt_search_status"]="NOT_AVAILABLE_"+type(e).__name__
    try:
        st=game_state(token)
        out["server_status"]=game_status(st)
        out["online_players_count"]=players(st)
    except Exception as e:out["server_status"]="UNKNOWN_"+type(e).__name__
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
