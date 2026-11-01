#!/usr/bin/env python3
"""BEILEYS47 V16, guarded PlayStation vanilla content upgrade.
Safe scope: three playable-interest zones, custom static props, CE loot tuning,
three moderate infected hotspot zones, rare-case drops, server notices.
Requires original V15 deployment present. NO wiping or storage access.
"""
import hashlib,json,os,sys,time,posixpath,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import (game_state,game_status,players,
                                  request_api_post,upload_file,wait_status)

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"deploy/v16/APPLY_RESULT.json"
CUSTOM_PATH="custom/beileys47_v16_three_hotspots.json"
SOURCE_FILES=[
  "cfggameplay.json","cfgweather.xml","mapgrouppos.xml","mapgroupproto.xml",
  "db/types.xml","db/events.xml","cfgspawnabletypes.xml",
  "env/zombie_territories.xml","db/messages.xml",
  "custom/beileys47_hotspot_zone47.json",
  "custom/beileys47_dolnik_military_base_v9.json"
]

def must(cond,msg):
    if not cond:raise NitradoError(msg)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def xm(blob):return ET.fromstring(blob,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
def outxml(root):return ET.tostring(root,encoding="utf-8",xml_declaration=True)
def byname(root,tag,name):
    val=root.find(f"{tag}[@name='{name}']")
    must(val is not None,"Missing "+tag+" "+name)
    return val
def audit(**fields):
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps({"service":SERVICE_ID,"version":"V16",
      "wipe":False,"ps5_tested":False,**fields},indent=2)+"\n")

def prop(name,x,y,z,yaw=0):
    return {"name":name,"pos":[round(x,5),round(y,5),round(z,5)],
            "ypr":[yaw,0,0],"scale":1,"enableCEPersistency":False}

def build_scenes():
    """Small-footprint world edits at already-grounded Livonia landmark elevations.
    New Y positions nearby are estimates: require PS5 inspection.
    """
    p=[]
    # ZONA 47 Radunin extension: the existing original 9 props remain.
    for x,z,a in [(7083,6953,0),(7123,6955,120),(7094,6992,240),(7125,6984,70)]:
        p.append(prop("Land_Mil_Fortified_Nest_Small",x,222.9,z,a))
    for x,z,a in [(7088,6982,0),(7120,6974,90),(7118,6945,170)]:
        p.append(prop("Land_Container_1Mo",x,222.9,z,a))
    for x,z,a in [(7084,6965,0),(7115,6963,0),(7103,6989,0),
                  (7108,6940,0),(7090,6942,0),(7122,6990,0)]:
        p.append(prop("Land_Roadblock_WoodenCrate",x,222.85,z,a))
    for x,z,a in [(7092,6970,0),(7113,6970,0),(7100,6982,0),
                  (7117,6945,0),(7088,6949,0)]:
        p.append(prop("Land_Roadblock_Table",x,222.85,z,a))
    p.extend([prop("Land_Wreck_sed01_aban1_police",7080,222.4,6985,75),
              prop("Land_wreck_truck01_aban2_green",7128,222.4,6946,140)])
    # The bunker is an EXISTING Bohemia Land_Bunker2_Double, at X9022.5 Z7457.9.
    # Fortify its surroundings WITHOUT duplicating / burying another bunker.
    for x,z,a in [(9005,7451,45),(9040,7455,180),(9030,7439,115)]:
        p.append(prop("Land_Mil_Fortified_Nest_Small",x,323.5,z,a))
    for x,z,a in [(9001,7438,90),(9039,7439,10)]:
        p.append(prop("Land_Container_1Mo",x,323.5,z,a))
    for x,z,a in [(8999,7465,0),(9036,7474,0),(9011,7438,0),(9043,7470,0)]:
        p.append(prop("Land_Roadblock_WoodenCrate",x,323.5,z,a))
    # Dolnik: only lightweight loot-proxy props OUTSIDE the two tents; no new tents.
    p.extend([prop("Land_Roadblock_Table",11500.0,212.7,448.5,40),
              prop("Land_Roadblock_Table",11468.0,214.7,466.0,120),
              prop("Land_Roadblock_WoodenCrate",11469.2,214.7,465.5,90)])
    assert len(p)==32
    return p

def build(original):
    gp=json.loads(original["cfggameplay.json"])
    scene=json.loads(original["custom/beileys47_dolnik_military_base_v9.json"])
    must(len(scene.get("Objects",[]))==18 and
         sum("Tent" in x.get("name","") for x in scene["Objects"])==2,
         "V15 Dolnik 2-tent base missing: refuse")
    weather=xm(original["cfgweather.xml"])
    fog=weather.find("fog")
    must(fog is not None and fog.find("limits").get("max")=="0.0",
         "V15 no-fog weather missing: refuse")
    events=xm(original["db/events.xml"])
    byname(events,"event","VehicleBEILEYS47DolnikTest")
    arr=gp.get("WorldsData",{}).get("objectSpawnersArr")
    must(isinstance(arr,list) and "custom/beileys47_dolnik_military_base_v9.json" in arr,
         "Live object spawner list inconsistent")
    must(CUSTOM_PATH not in arr, "V16 spawner already active; avoid duplication")
    scene_v16=build_scenes()
    arr.append(CUSTOM_PATH)
    changes={"cfggameplay.json":(json.dumps(gp,indent=2,ensure_ascii=False)+"\n").encode(),
             CUSTOM_PATH:(json.dumps({"Objects":scene_v16},indent=2,ensure_ascii=False)+"\n").encode()}

    map_proto=xm(original["mapgroupproto.xml"])
    # Both remaining tents already have valid medical/military CE point layouts.
    # Increase their max loot slots; respects existing categories and point positions.
    med=byname(map_proto,"group","Land_Medical_Tent_Big")
    mil=byname(map_proto,"group","Land_Mil_Tent_Big2_4")
    must(med.get("lootmax")=="8" and mil.get("lootmax")=="5",
         "Unexpected source loot prototypes: refuse")
    med.set("lootmax","10")
    mil.set("lootmax","8")
    changes["mapgroupproto.xml"]=outxml(map_proto)

    map_pos=xm(original["mapgrouppos.xml"])
    original_count=len(map_pos.findall("group"))
    valid_group_classes={x.get("name") for x in map_proto.findall("group")}
    # Register CE loot only at new boxes/containers that the real map prototype supports.
    loot_groups=[p for p in scene_v16 if p["name"] in
                 {"Land_Container_1Mo","Land_Roadblock_WoodenCrate"}]
    must(len(loot_groups)==16, "Unexpected V16 world loot locations")
    original_coords=set((g.get("name"),g.get("pos")) for g in map_pos.findall("group"))
    for ob in loot_groups:
        must(ob["name"] in valid_group_classes,"Unknown CE prototype: "+ob["name"])
        x,y,z=ob["pos"]
        pos=f"{x:.6f} {y:.6f} {z:.6f}"
        must((ob["name"],pos) not in original_coords,"Duplicate V16 mapgroup")
        ET.SubElement(map_pos,"group",{"name":ob["name"],"pos":pos,
                      "rpy":f"0 0 {-ob['ypr'][0]:.6f}",
                      "a":f"{90-ob['ypr'][0]:.6f}"})
    must(len(map_pos.findall("group"))==original_count+16,
         "Map group count not increased by 15")
    changes["mapgrouppos.xml"]=outxml(map_pos)

    db=xm(original["db/types.xml"])
    # Keep rare cases rare and leave original survival economy broadly intact.
    rare={"GunCase_Black":(4,2),"GunCase_White":(4,2),
          "GunCase_Orange":(2,1),"ScientificBriefcase":(1,0),
          "ScientificBriefcaseKeys":(2,1),
          "ShippingContainerKeys_Blue":(2,1),
          "ShippingContainerKeys_Red":(2,1)}
    for name,(nominal,minv) in rare.items():
        e=byname(db,"type",name)
        e.find("nominal").text=str(nominal)
        e.find("min").text=str(minv)
        # All added types need loot categories and usage to work with CE groups.
        if name in {"GunCase_Orange","ScientificBriefcase","ScientificBriefcaseKeys",
                    "ShippingContainerKeys_Blue","ShippingContainerKeys_Red"}:
            if e.find("category") is None:
                ET.SubElement(e,"category",name="containers" if "Case" in name or "Briefcase" in name else "tools")
            if e.find("usage") is None:
                ET.SubElement(e,"usage",name="Military")
    for name,newnom in {"BandageDressing":18,"Morphine":16,
                        "AmmoBox_556x45_20Rnd":15}.items():
        e=byname(db,"type",name)
        n=e.find("nominal")
        if int(n.text)<newnom:n.text=str(newnom)
    changes["db/types.xml"]=outxml(db)

    types={x.get("name") for x in db.findall("type")}
    spawn=xm(original["cfgspawnabletypes.xml"])
    # Special cases can carry a chance-based REWARD; not a custom lock plugin.
    for cname,loot in (("GunCase_Black","AmmoBox_556x45_20Rnd"),
                       ("GunCase_White","FirstAidKit"),
                       ("GunCase_Orange","NailBox")):
        must(loot in types,"Unknown reward class: "+loot)
        case=spawn.find(f"type[@name='{cname}']")
        if case is None:case=ET.SubElement(spawn,"type",name=cname)
        # One non-guaranteed reward for newly generated cases.
        cargo=ET.SubElement(case,"cargo",chance="0.75")
        ET.SubElement(cargo,"item",name=loot,chance="1.0")
    changes["cfgspawnabletypes.xml"]=outxml(spawn)

    infected=xm(original["env/zombie_territories.xml"])
    must(infected.tag=="territory-type","Unknown infected territory format")
    existing={(z.get("name"),z.get("x"),z.get("z"))
              for t in infected.findall("territory") for z in t.findall("zone")}
    squads=[("InfectedArmy",7100.0,6965.0,12,18,95),
            ("InfectedArmy",9022.5,7457.9,10,14,85),
            ("InfectedMedic",11490.0,461.0,6,10,75)]
    terr=ET.SubElement(infected,"territory",color="4278255360")
    for name,x,z,dmin,dmax,rad in squads:
        must(name in {event.get("name") for event in events.findall("event")},
             "Missing infected event: "+name)
        key=(name,str(x),str(z))
        must(key not in existing,"Duplicate infected zone")
        ET.SubElement(terr,"zone",{"name":name,"smin":"0","smax":"0",
                      "dmin":str(dmin),"dmax":str(dmax),
                      "x":str(x),"z":str(z),"r":str(rad)})
    changes["env/zombie_territories.xml"]=outxml(infected)

    messages=xm(original["db/messages.xml"])
    ET.SubElement(messages,"message")
    msg=messages[-1]
    for key,value in {"delay":"0","repeat":"100","deadline":"0","onconnect":"0",
                      "shutdown":"0","text":"BEILEYS47 | ZONA47 PvP near 7100/6965, fortified bunker near 9022/7458, Dolnik medical and military loot. Fight, loot and survive. Sunday community challenge: bring your squad!"}.items():
        ET.SubElement(msg,key).text=value
    changes["db/messages.xml"]=outxml(messages)

    for name,content in changes.items():
        if name.endswith(".json"):json.loads(content)
        else:xm(content)
        must(len(content)>60,"Unexpected tiny generated file")
    assert len(changes)==8
    return changes,{"props":len(scene_v16),"new_ce_loot_positions":len(loot_groups),
                     "horde_zones":len(squads),"new_files":[CUSTOM_PATH],
                     "modified_files":len(changes)-1}

def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    must(bool(token),"Missing Nitrado secret")
    mode=os.environ.get("BEILEYS47_V16_MODE","preflight")
    must(mode in {"preflight","deploy"},"Invalid deploy mode")
    mission=resolve_mission(token)
    files={}
    for name in SOURCE_FILES:
        files[name]=download_one(token,posixpath.join(mission,name))
        print("READ",name,flush=True)
    changes,details=build(files)
    print("V16 STATIC VALIDATION PASSED:",details,flush=True)
    if mode=="preflight":
        audit(state="validated_not_live",sha256={n:sha(b) for n,b in changes.items()},details=details)
        print("DRY RUN ONLY. NO FILE UPLOAD.",flush=True)
        return
    # User authorized installation, but never interrupt an active multiplayer session.
    current=game_state(token)
    status=game_status(current)
    count=players(current)
    must(status in {"started","running","stopped"},"Server status unsafe: "+status)
    must(status=="stopped" or count==0,
         "Players online or count unknown: do not stop or change server.")
    remote_saved={}
    applied=[]
    stopped_before=status=="stopped"
    try:
        if not stopped_before:
            print("0 connected, sending Nitrado normal stop.",flush=True)
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token,{"stopped"},attempts=40)
        print("Server confirmed stopped. Uploading V16.",flush=True)
        for name,blob in changes.items():
            full=posixpath.join(mission,name)
            # Existing data already downloaded; new JSON has no previous version.
            old=files.get(name)
            remote_saved[name]=old
            upload_file(token,full,blob)
            applied.append(name)
            actual=download_one(token,full)
            must(sha(actual)==sha(blob),"Uploaded file checksum mismatch: "+name)
            print("VERIFIED",name,flush=True)
        audit(state="files_uploaded_verified",uploaded=applied,details=details,
              running_verified=False)
    except Exception as e:
        print("Upload failed. Attempting rollback for modified existing files.",flush=True)
        for name in reversed(applied):
            old=remote_saved.get(name)
            if old is not None:
                try:upload_file(token,posixpath.join(mission,name),old)
                except Exception:print("WARNING: rollback failed for",name,flush=True)
        audit(state="failed_partial_or_rolled_back",uploaded=applied,error=type(e).__name__)
        raise
    finally:
        # Never strand a server stopped due to this workflow. A successful
        # deployment always requests server start; a failed deploy also tries.
        if not stopped_before or applied:
            try:
                request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                print("Restart requested.",flush=True)
            except Exception:
                print("WARNING: Nitrado restart request failed.",flush=True)
    # Verify Nitrado service, never conflate server running with in-game content.
    for _ in range(30):
        time.sleep(6)
        if game_status(game_state(token)) in {"started","running"}:
            audit(state="nitrado_started",uploaded=applied,details=details,
                  running_verified=True,ps5_tested=False)
            print("NITRADO STARTED; gameplay PS5 still untested.",flush=True)
            return
    raise NitradoError("Uploads verified but Nitrado running state not confirmed")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("V16 ERROR:",str(e)[:240],file=sys.stderr)
        sys.exit(1)
