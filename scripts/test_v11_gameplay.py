#!/usr/bin/env python3
"""V11 static regression: no Nitrado or PS5 runtime claims."""
import json, math
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]/"mission"/"v11_gameplay"
def read(name): return (ROOT/name).read_text(encoding="utf-8-sig")
def wrap(name): return ET.fromstring("<root>"+read(name)+"</root>")

def main():
    weather=ET.fromstring(read("cfgweather_SUNNY_V11.xml"))
    assert weather.tag=="weather" and weather.get("reset")=="1" and weather.get("enable")=="1"
    for tag in ("fog","rain","snowfall"):
        sec=weather.find(tag)
        assert sec is not None, tag
        assert float(sec.find("current").get("actual"))==0,tag
        bounds=sec.find("limits")
        assert float(bounds.get("min"))==float(bounds.get("max"))==0,tag
        changes=sec.find("changelimits")
        assert float(changes.get("min"))==float(changes.get("max"))==0,tag
    over=weather.find("overcast")
    assert float(over.find("limits").get("max"))<=0.12
    assert float(weather.find("storm").get("density"))==0

    vehicles=ET.fromstring(read("beileys47_vehicle_loadouts_v11.xml"))
    assert vehicles.tag=="spawnabletypes"
    byname={e.get("name"):e for e in vehicles.findall("type")}
    assert len(byname)==17 and len(vehicles.findall("type"))==17
    for cls,e in byname.items():
        cargo=[k for c in e.findall("cargo") if c.get("chance")=="1.00" for k in c.findall("item")]
        assert {k.get("name") for k in cargo}>={"Canteen","CanisterGasoline","TireRepairKit"},cls
        for n in ("Canteen","CanisterGasoline","TireRepairKit"):
            matching=[k for k in cargo if k.get("name")==n]
            assert len(matching)==1 and matching[0].get("chance")=="1.00",cls
        for n in ("Canteen","CanisterGasoline"):
            item=next(k for k in cargo if k.get("name")==n)
            assert item.get("quantmin")==item.get("quantmax")=="100"
        if cls.startswith("Truck_01_Covered"):
            attachments=[k for a in e.findall("attachments") for k in a.findall("item")]
            for n in ("WoodenLog","WoodenPlank","MetalPlate"):
                matching=[x for x in attachments if x.get("name")==n]
                assert len(matching)==1 and matching[0].get("quantmin")==matching[0].get("quantmax")=="50"
    reg=ET.fromstring(read("cfgeconomycore_V11_REFERENCE_DO_NOT_OVERWRITE.xml"))
    assert len(reg.findall(".//file[@name='beileys47_vehicle_loadouts_v11.xml']"))==1

    evt=wrap("db_event_VehicleTruck01_FRAGMENT.xml").find("event")
    assert evt.get("name")=="VehicleTruck01"
    assert [evt.findtext(k) for k in ("nominal","min","max","position","active")]==["10","10","12","fixed","1"]
    assert evt.findtext("restock")=="0"
    pts=wrap("cfgeventspawns_truck12_FRAGMENT.xml").find("event")
    assert pts.get("name")=="VehicleTruck01"
    ps=[(float(p.get("x")),float(p.get("z"))) for p in pts.findall("pos")]
    assert len(ps)==12 and len(set(ps))==12
    assert min(math.hypot(x[0]-y[0],x[1]-y[1]) for i,x in enumerate(ps) for y in ps[i+1:])>2000
    assert min(math.hypot(x-11510,z-460) for x,z in ps)>800

    pile=wrap("db_types_PileOfWoodenPlanks_FRAGMENT.xml").find("type")
    assert pile.get("name")=="PileOfWoodenPlanks"
    assert pile.findtext("quantmin")==pile.findtext("quantmax")=="100"
    assert pile.findtext("lifetime")=="28800" # No false 15-day reset

    trial=json.loads(read("beileys47_test_items_v11.json"))
    objects=trial["Objects"]
    assert len(objects)==57
    assert len({x["name"] for x in objects})==57
    assert all(len(x["pos"])==3 and x["enableCEPersistency"] is False for x in objects)
    print("PASS: weather fog/rain/snow=0, 17 vehicle loadouts, M3S 50% material stacks, 12 truck spawns, pile full on spawn, 57 categorized trial items")
    print("STATIC ONLY. NO live deployment, vehicle persistence, 15-day refill or PS5 geometry proof.")

if __name__=="__main__":
    main()
