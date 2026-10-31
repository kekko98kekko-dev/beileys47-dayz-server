#!/usr/bin/env python3
"""Fail-closed offline static audit. Never claims real Nitrado/PS5 verification."""
import hashlib, json, math
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
MISSION=ROOT/"mission"
KIT=MISSION/"franco_v8/beileys47_freshspawn_v8.json"
BASE=MISSION/"dolnik_replacement_v9/beileys47_dolnik_military_base_v9.json"
GROUPS=MISSION/"dolnik_replacement_v9/dolnik_mapgrouppos_additions_ONLY.xml"
SPAWN=MISSION/"stable_v10/cfgplayerspawnpoints.xml"
CFG=MISSION/"stable_v10/cfggameplay.json"
OFFICIAL_SHA="13a6b2e3cbeeb1eb23e09af81bc36ba4d53871b5"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def spawn_positions(xml):
    root=ET.fromstring(xml)
    assert root.tag=="playerspawnpoints"
    positions=[]
    for section in ("fresh","hop","travel"):
        branch=root.find(section)
        assert branch is not None, "Missing spawn section "+section
        gen=branch.find("generator_params")
        assert float(gen.findtext("grid_width") or 0)>0
        assert float(gen.findtext("grid_height") or 0)>0
        points=branch.findall("./generator_posbubbles//pos")
        assert points, "Empty spawn section "+section
        positions.extend((float(p.attrib["x"]),float(p.attrib["z"])) for p in points)
    return positions

def check_kit(kit):
    assert kit["spawnWeight"]>=1
    slot={s["slotName"]:s["discreteItemSets"] for s in kit["attachmentSlotItemSets"]}
    assert {"Body","Legs","Feet","Back"}<=set(slot)
    assert any(v["itemType"]=="TaloonBag_Blue" for v in slot["Back"])
    variants=kit["discreteUnsortedItemSets"]
    assert len(variants)==81
    for i,v in enumerate(variants):
        things=Counter(v["simpleChildrenTypes"])+Counter(q["itemType"] for q in v["complexChildrenTypes"])
        assert v["spawnWeight"]>=1
        assert sum(things[x] for x in ("Apple","Pear","Plum"))==2, i
        assert sum(things[x] for x in ("PeachesCan","SpaghettiCan","BakedBeansCan"))==2, i
        assert things["CombatKnife"]==1 and things["BandageDressing"]==2 and things["ChernarusMap"]==1, i

def check_cfg(cfg):
    assert cfg["PlayerData"]["spawnGearPresetFiles"]==["custom/beileys47_freshspawn_v8.json"]
    assert all(cfg["MapData"][k] is True for k in ("ignoreMapOwnership","ignoreNavItemsOwnership","displayPlayerPosition","displayNavInfo"))
    assert cfg["WorldsData"]["objectSpawnersArr"]==[
      "custom/beileys47_hotspot_zone47.json",
      "custom/beileys47_dolnik_military_base_v9.json"],"old broken scene or duplicate hotspots active"

def check_spawn_clear(points, objects, minimum=150):
    dist=min(math.hypot(x-o["pos"][0],z-o["pos"][2]) for x,z in points for o in objects)
    assert dist>minimum, "spawn collision risk: %.2fm"%dist
    return dist

def check_ce_groups(text, objects):
    groups=ET.fromstring("<map>"+text+"</map>").findall("group")
    assert len(groups)==len(objects)==29
    matched=set()
    for group in groups:
        xyz=[float(x) for x in group.attrib["pos"].split()]
        found=[i for i,o in enumerate(objects) if i not in matched
          and o["name"]==group.attrib["name"]
          and all(abs(a-b)<0.015 for a,b in zip(xyz,o["pos"]))]
        assert len(found)==1, "CE group without exact unique V9 object: "+group.attrib["name"]
        matched.add(found[0])

def main():
    raw=SPAWN.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
    assert blob==OFFICIAL_SHA, "not byte-identical to Bohemia DZ_130 Livonia spawn XML"
    points=spawn_positions(raw.decode("utf-8-sig"))
    assert len(points)==151
    objects=read_json(BASE)["Objects"]
    check_kit(read_json(KIT))
    check_cfg(read_json(CFG))
    check_ce_groups(GROUPS.read_text(encoding="utf-8-sig"),objects)
    dist=check_spawn_clear(points,objects)
    print("PASS static stable V10: 151 original Livonia positions; 81 kit variants; 29 CE groups; no V7 scene. Nearest spawner %.1fm."%dist)
    print("NOT VERIFIED on Nitrado/PS5; no deploy and no guarantee of unclipped scenery or working loot.")

if __name__=="__main__":
    main()
