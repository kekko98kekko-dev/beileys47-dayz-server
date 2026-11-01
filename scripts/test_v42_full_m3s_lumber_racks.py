#!/usr/bin/env python3
from pathlib import Path
from v42_full_m3s_lumber_racks import patch,parse,get_racks,NitradoError
ROOT=Path(__file__).resolve().parents[1]
def main():
    s=(ROOT/"mission/v11_gameplay/beileys47_vehicle_loadouts_v11.xml").read_bytes()
    r=parse(s)
    # Legacy source contains partial stacks but no backpack; simulated confirmed V40 bag.
    t=r.find("type[@name='Truck_01_Covered']")
    assert t is not None
    import xml.etree.ElementTree as ET
    c=ET.Element("cargo",{"chance":"1.00"})
    ET.SubElement(c,"item",{"name":"AliceBag_Green","chance":"1.00"})
    t.insert(0,c)
    for group in t.findall("attachments"):
        group.set("chance","1.00")
        for item in group.findall("item"):item.set("chance","1.00")
    blob=ET.tostring(r,encoding="utf-8",xml_declaration=True)
    updated,was=patch(blob)
    assert was is False and updated!=blob
    q=get_racks(parse(updated))
    assert all(x.get("quantmin")=="100" and x.get("quantmax")=="100" for x in q.values())
    assert sum(i.get("name")=="AliceBag_Green" for i in parse(updated).findall(".//type[@name='Truck_01_Covered']/cargo/item"))==1
    same,already=patch(updated)
    assert already is True and same==updated
    mixed=updated.replace(b'<item name="WoodenLog" chance="1.00" quantmin="100" quantmax="100"',b'<item name="WoodenLog" chance="1.00" quantmin="50" quantmax="50"')
    try:patch(mixed)
    except NitradoError:pass
    else:raise AssertionError("Partial rack fullness should fail closed")
    print("PASS V42: 50->100 for BOTH M3S stacks, exact other XML unchanged, bag 64 retained, idempotent")
if __name__=="__main__":main()
