#!/usr/bin/env python3
"""V40 offline: exact Dolnik event and all truck parts + single 64-slot backpack."""
import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from v40_dolnik_truck_rescue import (make,parse,installed,select_nearby_site,
    TRUCK,BAG,GIFT,OLD,REQUIRED_PARTS,NitradoError,ORIG)
ROOT=Path(__file__).resolve().parents[1]
def fake_files():
    model=(ROOT/"mission/v11_gameplay/beileys47_vehicle_loadouts_v11.xml").read_bytes()
    cfg=parse(model)
    truck=cfg.find(f"type[@name='{TRUCK}']")
    assert truck is not None
    xml=ET.Element("spawnabletypes")
    xml.append(truck)
    events=b'''<events><event name="VehicleBEILEYS47DolnikTest">
    <nominal>1</nominal><min>1</min><max>1</max><lifetime>300</lifetime>
    <restock>0</restock><saferadius>150</saferadius>
    <distanceradius>100</distanceradius><cleanupradius>100</cleanupradius>
    <flags deletable="0" init_random="0" remove_damaged="1"/>
    <position>fixed</position><limit>mixed</limit><active>1</active>
    <children><child lootmax="0" lootmin="0" max="1" min="1" type="Truck_01_Covered"/></children>
    </event></events>'''
    positions=b'''<eventposdef>
    <event name="VehicleBEILEYS47DolnikTest">
      <pos x="11574.92" z="374.01" a="177.83"/>
    </event>
    <event name="VehicleTruck01"><pos x="11574.92" z="374.01" a="177.83"/></event>
    </eventposdef>'''
    return {"db/events.xml":events,"cfgeventspawns.xml":positions,
        "cfgspawnabletypes.xml":ET.tostring(xml)}
def main():
    files=fake_files()
    assert not installed(files)
    terrain=np.full((2048,2048),215.3,dtype=np.float32)
    groups=parse(b'<map>')
    site=select_nearby_site(terrain,groups,[],[(ORIG[0],ORIG[1])])
    assert 35<=site["distance_from_original_m"]<=55
    assert site["terrain_relief_20m"]==0
    generated=make(files,site)
    assert set(generated)==set(files)
    assert installed(generated)
    e=parse(generated["db/events.xml"])
    sp=parse(generated["cfgeventspawns.xml"])
    assert e.find(f"event[@name='{OLD}']").findtext("nominal")=="1"
    assert e.find(f"event[@name='{GIFT}']").findtext("nominal")=="1"
    assert len(e.findall(f"event[@name='{GIFT}']"))==1
    assert len(sp.find(f"event[@name='{GIFT}']").findall("pos"))==1
    tr=parse(generated["cfgspawnabletypes.xml"]).find(f"type[@name='{TRUCK}']")
    counts={}
    for g in tr.findall("attachments"):
       assert g.get("chance")=="1.00"
       for i in g.findall("item"):
         assert i.get("chance")=="1.00"
         counts[i.get("name")]=counts.get(i.get("name"),0)+1
    assert all(counts.get(k)==n for k,n in REQUIRED_PARTS.items())
    assert tr.find("damage").get("min")=="0.0"
    assert sum(i.get("name")==BAG for i in tr.findall(".//cargo/item"))==1
    assert tr.find("cargo/item").get("name")==BAG
    try:make(generated,site)
    except NitradoError:pass
    else:raise AssertionError("Double V40 event was accepted")
    try:select_nearby_site(terrain,groups,[],[(ORIG[0]+x,ORIG[1]+y)
                   for x in range(-100,101,10) for y in range(-100,101,10)])
    except NitradoError:pass
    else:raise AssertionError("Site search should block crowded land")
    print("PASS V40: alternate site avoids legacy position, 100% parts, pristine truck, one 64-slot Field Backpack, no duplicate")
if __name__=="__main__":main()
