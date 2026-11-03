#!/usr/bin/env python3
"""V64: authorized DayZ PS5/Livonia fleet CE reset, recurring Dolnik M3S,
one M1025 boss gift, and an Object Spawner lighting/flag area.

IMPORTANT: Changing Central Economy sources does not delete persisted cars.
No world/persistence delete is performed. The user can inspect actual spawns on PS5.
"""
from __future__ import annotations
import copy,hashlib,json,math,os,posixpath,sys,zipfile,time,random
from pathlib import Path
import xml.etree.ElementTree as ET
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,call_api,NitradoError
from deploy_beileys47_v15 import upload_file,game_state,game_status,players,request_api_post,wait_status
from v36_nitrado_backups_readonly import analyze

E="db/events.xml"; P="cfgeventspawns.xml"; S="cfgspawnabletypes.xml"
G="cfggameplay.json"; TYPES="db/types.xml"; MAP="mapgrouppos.xml"
SCENE="custom/beileys47_v64_boss_power_camp.json"
FILES=(E,P,S,G,SCENE)
TRUCK_EVT="VehicleBEILEYS47DolnikUltimateV43"
MIL_EVT="VehicleBEILEYS47BossM1025V64"
MIL="Offroad_02"; M3S="Truck_01_Covered"
MIL_X,MIL_Z=11573.63,387.30
CAMP_X,CAMP_Z=11559.57,379.49
OUT=Path("deploy/v64/DEPLOY_RESULT.json")
BACK=Path("deploy/v64/PRIVATE_ORIGINAL_CONFIG.zip")
def must(ok,msg):
    if not ok:raise NitradoError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def xml(b):return ET.fromstring(b,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def serialize(root):return ET.tostring(root,encoding="utf-8",xml_declaration=True)
def report(**kw):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    d=dict(version="V64",mode="ONE_M3S_RESTOCK_4H_AND_ONE_BOSS_M1025",
       requested_military_location=[MIL_X,MIL_Z],requested_power_camp=[CAMP_X,CAMP_Z],
       old_persistent_vehicles_deleted=False,
       player_data_deleted=False,base_data_deleted=False,
       world_wipe_performed=False,
       physical_vehicle_seen_PS5=False,
       actual_four_hour_unconditional_truck_regeneration=False,
       power_lights_wired_and_activated=False,
       **kw)
    OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    print("V64 STATUS",kw.get("status","?"),flush=True)
def choose(valid,*choices):
    return next((v for v in choices if v in valid),None)
def cargo_add(t,name,count=1):
    for _ in range(count):
        group=ET.SubElement(t,"cargo",{"chance":"1.00"})
        attrs={"name":name,"chance":"1.00"}
        if name in ("CanisterGasoline","Canteen","Battery9V","LargeGasCanister","Mag_AKM_Drum75Rnd"):
            attrs.update({"quantmin":"100","quantmax":"100"})
        ET.SubElement(group,"item",attrs)
def high_end(valid):
    alternatives={
        "vest":("PlateCarrierVest_Black","PlateCarrierVest_Green","PlateCarrierVest"),
        "helmet":("Mich2001Helmet","GorkaHelmet_Black","CombatHelmet_Black"),
        "jacket":("GorkaEJacket_Black","GorkaEJacket_Summer","BDUJacket"),
        "pants":("GorkaPants_Black","GorkaPants_Summer","BDUPants"),
        "boots":("MilitaryBoots_Black","CombatBoots_Black"),
        "gloves":("TacticalGloves_Black","TacticalGloves_Green"),
        "bag":("AliceBag_Black","AliceBag_Green"),
        "mask":("BalaclavaMask_Black","SkiMask_Black"),
        "nv":("NVGoggles",),
        "nvhead":("NVGHeadstrap",),
        "battery":("Battery9V",),
        "pouches":("PlateCarrierPouches",),
        "holster":("PlateCarrierHolster",),
        "weapon":("AKM",),
        "drum":("Mag_AKM_Drum75Rnd",),
        "optic":("PSO1Optic","KobraOptic"),
        "suppressor":("AK_Suppressor",),
        "medical":("BandageDressing",),
        "food":("TacticalBaconCan",),
        "gas_cylinder":("LargeGasCanister","MediumGasCanister","SmallGasCanister"),
        "gas_jerry":("CanisterGasoline",),
        "spark_for_generator":("SparkPlug",),
        "battery_light":("Battery9V",)
    }
    selected={}
    for key,options in alternatives.items():
        val=choose(valid,*options)
        must(val is not None,"Required boss item not in actual Livonia types.xml: "+key)
        selected[key]=val
    return selected
def terrain_height(map_blob,x,z):
    world=xml(map_blob);nearest=[]
    for g in world.findall("group"):
        pos=g.get("pos","").split()
        if len(pos)!=3:continue
        try:
            a,y,b=map(float,pos);d=math.hypot(x-a,z-b)
            if d<=200:nearest.append((d,y))
        except ValueError:continue
    nearest.sort()
    must(nearest and nearest[0][0] <= 75,
         "No reliable terrain height evidence within 75m; no approximate placement")
    near=[y for d,y in nearest if d<=min(50,max(12,nearest[0][0]+12))]
    must(len(near)>=1 and max(near)-min(near)<=16,
         "Nearby building reference heights disagree; stop instead of placing floating objects")
    # These are building ORIGIN heights, not exact terrain samples; actual PS5 check mandatory.
    return float(nearest[0][1]),round(nearest[0][0],2),len(near)
def scene_bytes(y,flag):
    def obj(name,x,z,dy=0.0,extras=None):
        it={"name":name,"pos":[round(x,2),round(y+dy,3),round(z,2)],
            "ypr":[0.0,0.0,0.0],"scale":1.0}
        if extras:it.update(extras)
        return it
    # Positions intentionally separate and near enough for manually wiring three lights.
    objs=[
        obj("PowerGenerator",CAMP_X,CAMP_Z),
        obj("Spotlight",CAMP_X+2.0,CAMP_Z),
        obj("Spotlight",CAMP_X,CAMP_Z+2.5),
        obj("Spotlight",CAMP_X-2.0,CAMP_Z),
        obj("StaticFlagPole",CAMP_X+4.5,CAMP_Z+4.0,extras={"customString":flag}),
        obj("CombinationLock4",CAMP_X+3.0,CAMP_Z+1.0),
        obj("CombinationLock4",CAMP_X+3.8,CAMP_Z+1.0)
    ]
    return (json.dumps({"Objects":objs},ensure_ascii=False,indent=2)+"\n").encode()
def build(orig,types,map_blob):
    roots={k:xml(orig[k]) for k in (E,P,S)}
    ev,positions,spawn=roots[E],roots[P],roots[S]
    must((ev.tag,positions.tag,spawn.tag)==("events","eventposdef","spawnabletypes"),
         "Unexpected DayZ CE roots")
    valid={t.get("name") for t in types.findall("type")}
    must(all(x in valid for x in (M3S,MIL,"PowerGenerator","Spotlight","CombinationLock4","Flag_Bohemia")),
         "One important DayZ vanilla classname absent from live types.xml")
    existing=ev.find(f"event[@name='{MIL_EVT}']")
    must(existing is None and positions.find(f"event[@name='{MIL_EVT}']") is None,
         "V64 military gift already defined; no duplicate retries")
    base=ev.find("event[@name='VehicleOffroad02']")
    truck=ev.find(f"event[@name='{TRUCK_EVT}']")
    point=positions.find(f"event[@name='{TRUCK_EVT}']")
    must(base is not None and truck is not None and point is not None,
         "Missing vanilla Offroad or unique Dolnik truck event")
    must(truck.findtext("active")=="1" and
         len(point.findall("pos"))==1 and
         [a.get("type") for a in truck.findall("./children/child")]==[M3S],
         "Expected single active Dolnik M3S event was changed")
    vehicle_events=[e for e in ev.findall("event") if e.get("name","").startswith("Vehicle")]
    must(len(vehicle_events)>=10,"Too few live vehicle events; check mission")
    before_names={e.get("name") for e in vehicle_events}
    offroad=copy.deepcopy(base)
    offroad.set("name",MIL_EVT)
    for k,v in [("active","1"),("nominal","1"),("min","1"),
                ("max","1"),("restock","0"),("saferadius","0"),
                ("distanceradius","0"),("cleanupradius","100")]:
        must(offroad.find(k) is not None,"Missing CE field "+k)
        offroad.find(k).text=v
    offroad.find("children").clear()
    ET.SubElement(offroad.find("children"),"child",{
        "lootmax":"0","lootmin":"0","max":"1","min":"1","type":MIL})
    # Disable all old boat/car/bike/truck CE sources INCLUDING the old Gunter event.
    for e in vehicle_events:
        name=e.get("name")
        if name==TRUCK_EVT:continue
        for k in ("active","nominal","min","max"):
            if e.find(k) is None:continue
            e.find(k).text="0"
    for k,v in [("active","1"),("nominal","1"),("min","1"),
                ("max","1"),("restock","14400")]:
        truck.find(k).text=v
    ev.append(offroad)
    p=ET.SubElement(positions,"event",{"name":MIL_EVT})
    ET.SubElement(p,"pos",{"x":f"{MIL_X:.2f}","z":f"{MIL_Z:.2f}","a":"178.00"})
    truck_p=spawn.find(f"type[@name='{M3S}']")
    mil_p=spawn.find(f"type[@name='{MIL}']")
    must(truck_p is not None and mil_p is not None,"Missing M3S/M1025 cargo preset")
    def truck_remove(n):
        return (n in {"HeadlightH7","Stone","SparkPlug","GlowPlug",
                      "CarBattery","TruckBattery","Battery9V"}
                or "kit" in n.casefold())
    removed=[]
    for group in list(truck_p):
        if group.tag!="cargo":continue
        items=group.findall("item")
        if any(truck_remove(i.get("name","")) for i in items):
            removed.extend(i.get("name") for i in items)
            truck_p.remove(group)
    # Battery9V intentionally only one in M3S cargo. Keep the installed TruckBattery
    # under attachments or the truck cannot function.
    cargo_add(truck_p,"Battery9V")
    # Material for owner to deploy generator/lights if static object spawner cannot create
    # usable connected items; truck is the large fallback store.
    for n,c in [("PowerGenerator",1),("Spotlight",3),("CableReel",1),
                ("Flag_Bohemia",1),("CombinationLock4",2),("CanisterGasoline",1)]:
        must(n in valid,"Missing camp backup item "+n)
        cargo_add(truck_p,n,c)
    for group in truck_p.findall("attachments"):
        group.set("chance","1.00")
        for item in group.findall("item"):item.set("chance","1.00")
    # M1025 military class guaranteed complete on next spawn.
    for group in mil_p.findall("attachments"):
        group.set("chance","1.00")
        for item in group.findall("item"):item.set("chance","1.00")
    dmg=mil_p.find("damage")
    if dmg is None:dmg=ET.Element("damage");mil_p.insert(0,dmg)
    dmg.set("min","0.0");dmg.set("max","0.0")
    # Keep vanilla canteen/fuel/tyre kit in the military vehicle.
    existing_cargo={i.get("name") for i in mil_p.findall("./cargo/item")}
    boss=high_end(valid)
    for k,n in boss.items():
        if n in existing_cargo and k in ("gas_jerry",):continue
        cargo_add(mil_p,n,2 if k in ("drum","medical") else 1)
    # Make sure the original truck installed parts are not removed with spare cargo.
    att={i.get("name") for i in truck_p.findall("./attachments/item")}
    must("TruckBattery" in att and "HeadlightH7" in att,
         "Mechanical M3S battery/headlights must remain installed")
    remaining=[i.get("name") for i in truck_p.findall("./cargo/item")]
    must(remaining.count("Battery9V")==1,"Exactly one 9V battery requested")
    must(all(not truck_remove(n) or n=="Battery9V" for n in remaining),
         "Unwanted truck cargo survived")
    y,d,n=terrain_height(map_blob,CAMP_X,CAMP_Z)
    flag="Flag_Bohemia"
    new={k:serialize(roots[k]) for k in (E,P,S)}
    gameplay=json.loads(orig[G].decode("utf-8"))
    world=gameplay.get("WorldsData",{})
    old_scenes=world.get("objectSpawnersArr",[])
    must(isinstance(old_scenes,list) and SCENE not in old_scenes,
         "Invalid gameplay scenes or old V64 scene already referenced")
    world["objectSpawnersArr"]=[*old_scenes,SCENE]
    gameplay["WorldsData"]=world
    new[G]=(json.dumps(gameplay,indent=2,ensure_ascii=False)+"\n").encode()
    new[SCENE]=scene_bytes(y,flag)
    # semantic proof all non-vehicle events untouched
    before_events=xml(orig[E]);after_events=xml(new[E])
    for e in before_events.findall("event"):
        name=e.get("name","")
        if name.startswith("Vehicle"):continue
        other=after_events.find(f"event[@name='{name}']")
        must(other is not None and ET.tostring(other)==ET.tostring(e),
             "Unrelated CE event altered: "+name)
    must(sum(e.findtext("active")=="1" for e in after_events.findall("event")
             if e.get("name","").startswith("Vehicle"))==2,
         "Exactly two active vehicle events required (one temporary military gift)")
    detail={"disabled_previous_vehicle_event_count":len(vehicle_events)-1,
        "only_recurring_vehicle_event":TRUCK_EVT,
        "truck_restock_seconds":14400,
        "military_once_event":MIL_EVT,
        "camp_static_scene":SCENE,
        "camp_y_estimate":round(y,3),
        "nearest_height_reference_distance_m":d,
        "height_reference_samples":n,
        "truck_removed_cargo_entries":removed,
        "military_kit":boss,
        "truck_fallback_generator_lights_flag_locks":True}
    return new,detail
def backup(original):
    BACK.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(BACK,"w",zipfile.ZIP_DEFLATED) as z:
        for k,b in original.items():z.writestr("dayzOffline.enoch/"+k,b)
        z.writestr("SHA256.txt","".join(sha(b)+"  "+k+"\n" for k,b in original.items()))
    with zipfile.ZipFile(BACK) as z:
        must(z.testzip() is None,"Original XML/JSON backup corrupted")
        must(all(sha(z.read("dayzOffline.enoch/"+k))==sha(b) for k,b in original.items()),
             "Original backup SHA mismatch")
def state(token):
    g=game_state(token);return game_status(g),players(g)
def stop(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
    wait_status(token,{"stopped"},attempts=65)
def start(token):
    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
    wait_status(token,{"started","running"},attempts=65)
def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    must(token and os.getenv("BEILEYS47_V64_APPROVED")=="yes","Missing Nitrado token or explicit owner approval")
    mission=resolve_mission(token)
    remote={k:posixpath.join(mission,k) for k in FILES}
    original={k:download_one(token,remote[k]) for k in (E,P,S,G)}
    try:
        old_scene=download_one(token,remote[SCENE])
        must(False,"V64 scene already exists; refuse overwrite")
    except NitradoError as e:
        must("already exists" not in str(e).lower(),"V64 scene exists")
    types=xml(download_one(token,posixpath.join(mission,TYPES)))
    height=download_one(token,posixpath.join(mission,MAP))
    new,detail=build(original,types,height)
    backup(original)
    prov=analyze(call_api(token,f"/services/{SERVICE_ID}/gameservers/backups"),
                 call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible"))
    must(prov["provider_backup_exists"] and prov["restore_possible"] is True,
         "Nitrado full backup unavailable; abort")
    old_state,online=state(token)
    must(old_state in ("started","running") and type(online) is int and online<=1,
         "Unexpected server status or >1 player; abort instead of interrupting others")
    report(status="BACKUP_READY_FOR_V64",players_before=online,
           provider_backup_count=prov["backup_count"],**detail)
    stopped=False;changed=[];started=False
    try:
        stop(token);stopped=True
        must(all(sha(download_one(token,remote[k]))==sha(original[k]) for k in original),
             "Concurrent admin modification; no writes")
        for k in FILES:
            changed.append(k)
            upload_file(token,remote[k],new[k])
            must(sha(download_one(token,remote[k]))==sha(new[k]),
                 "Nitrado uploaded different content: "+k)
        start(token);stopped=False;started=True
        must(all(sha(download_one(token,remote[k]))==sha(new[k]) for k in FILES),
             "Post-restart config readback mismatch")
        now,online2=state(token)
        must(now in ("started","running"),"Server not running after V64")
        # Like successful V55 method: one first boot with restock 0,
        # then restrict only future M1025 spawns WITHOUT another restart.
        after=xml(new[E]);gift=after.find(f"event[@name='{MIL_EVT}']")
        must(gift is not None and gift.findtext("restock")=="0","Missing first spawn M1025")
        gift.find("restock").text="31536000"
        staged=serialize(after)
        must(sha(download_one(token,remote[E]))==sha(new[E]),
             "Concurrent admin modification before staging one-off cooldown")
        upload_file(token,remote[E],staged)
        must(sha(download_one(token,remote[E]))==sha(staged),
             "Military long cooldown staging failed")
        report(status="CONFIG_INSTALLED_RESTART_VERIFIED_4H_M3S_AND_ONE_OFF_M1025",
               players_before=online,players_after=online2,
               provider_backup_count=prov["backup_count"],
               first_boot_military_restock_seconds=0,
               subsequent_restart_military_restock_seconds=31536000,
               ready_for_visual_PS5_testing=True,**detail)
        print("V64 SUCCESS: XML/JSON installed + restart verified; physical vehicle and powered camp need PS5 test",flush=True)
    except Exception:
        if changed and not started:
            # Restore only known files if no concurrent changes.
            try:
                current,_=state(token)
                if current in ("started","running"):stop(token);stopped=True
                else:must(current=="stopped","Unknown server state during rollback")
                for k in reversed(changed):
                    if k not in original:continue
                    live=download_one(token,remote[k])
                    must(sha(live) in (sha(new[k]),sha(original[k])),
                         "Concurrent change; manual recovery needed: "+k)
                    if sha(live)!=sha(original[k]):
                        upload_file(token,remote[k],original[k])
                report(status="V64_ROLLED_BACK_AFTER_ERROR",**detail)
            except Exception as ex:
                report(status="MANUAL_RECOVERY_NEEDED",recovery_error_type=type(ex).__name__,**detail)
        raise
    finally:
        if stopped:
            try:start(token)
            except Exception:print("CRITICAL V64: server start unconfirmed",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V64 ERROR",type(e).__name__,str(e)[:210],file=sys.stderr)
        if not OUT.exists():report(status="FAILED_BEFORE_WRITES")
        raise SystemExit(1)
