#!/usr/bin/env python3
"""V44: 2 old truck CE sources disabled, one new original-site maximal cargo."""
from pathlib import Path
import xml.etree.ElementTree as ET
from v44_single_original_dolnik_truck import (
  build,parse,installed,OLD,NEW,TRUCK,FILES,
  REQUIRED_FIXED,SUPPORT_CARGO,BARRELS,CRATES,XYZ,NitradoError
)
ROOT=Path(__file__).resolve().parents[1]
def fixture():
 ev=ET.Element("events")
 positions=ET.Element("eventposdef")
 for name,(x,z,a) in zip(OLD,[XYZ,("11605.23","356.51","177.83")]):
    t=ET.SubElement(ev,"event",{"name":name})
    for tag,value in (("nominal","1"),("min","1"),("max","1"),("active","1")):
        ET.SubElement(t,tag).text=value
    ET.SubElement(ET.SubElement(t,"children"),"child",{"type":TRUCK})
    l=ET.SubElement(positions,"event",{"name":name})
    ET.SubElement(l,"pos",{"x":x,"z":z,"a":a})
 stock=parse((ROOT/"mission/v11_gameplay/beileys47_vehicle_loadouts_v11.xml").read_bytes())
 # The source contains 17 original M3S groups; V40 added a 64-slot backpack,
 # but V43 replaces ALL old cargo so that is not needed in fixture.
 main=stock.find(f"type[@name='{TRUCK}']")
 assert main is not None
 # CE types inventory fixture is deliberately restricted to class candidates.
 types=ET.Element("types")
 allkeys={TRUCK,*SUPPORT_CARGO,*BARRELS,*CRATES,*REQUIRED_FIXED}
 for c in allkeys:
    if c=="TerritoryFlagKit":continue  # test optional fallback / craft materials
    ET.SubElement(types,"type",{"name":c})
 return ({
     "db/events.xml":ET.tostring(ev),
     "cfgeventspawns.xml":ET.tostring(positions),
     "cfgspawnabletypes.xml":ET.tostring(stock)
   },types)
def main():
    files,types=fixture()
    assert not installed(files)
    modified,report=build(files,types)
    assert set(modified)==set(FILES)
    assert report["old_ce_events_disabled"]==list(OLD)
    assert report["barrel_slots"]==4 and report["crate_slots"]==4
    assert "TerritoryFlagKit" in report["optional_missing"]
    assert report["cargo_entries"]==sum(SUPPORT_CARGO.values())-1
    assert installed(modified)
    ev=parse(modified["db/events.xml"])
    sp=parse(modified["cfgeventspawns.xml"])
    for old in OLD:
       e=ev.find(f"event[@name='{old}']")
       assert e.findtext("nominal")=="0" and e.findtext("active")=="0"
    assert ev.find(f"event[@name='{NEW}']").findtext("nominal")=="1"
    position=sp.find(f"event[@name='{NEW}']").find("pos")
    assert [position.get(k) for k in ("x","z","a")]==list(XYZ)
    truck=parse(modified["cfgspawnabletypes.xml"]).find(f"type[@name='{TRUCK}']")
    assert sum(i.get("name").startswith("Barrel_") for i in truck.findall("./attachments/item"))==4
    assert sum(i.get("name")=="WoodenCrate" for i in truck.findall("./attachments/item"))==4
    for kind in ("WoodenLog","WoodenPlank","MetalPlate"):
       stack=[i for i in truck.findall("./attachments/item") if i.get("name")==kind]
       assert len(stack)==1 and stack[0].get("quantmin")=="100"
    assert all(x.get("chance")=="1.00" for x in truck.findall("./cargo/item"))
    assert not any("case" in x.get("name","").lower() for x in truck.findall("./cargo/item"))
    assert sum(x.get("name")=="Stone" for x in truck.findall("./cargo/item"))==32
    assert len([x for x in truck.findall("./cargo/item") if x.get("name")=="NailBox"])==6
    assert truck.find("damage").get("min")=="0.0"
    try:build(modified,types)
    except NitradoError:pass
    else:raise AssertionError("Duplicate old+new events accepted")
    lost=ET.fromstring(ET.tostring(types))
    lost.remove(lost.find("type[@name='WoodenCrate']"))
    try:build(files,lost)
    except NitradoError:pass
    else:raise AssertionError("Missing mandatory class accepted")
    print("PASS V44: 1 original truck event, 2 old CE sources off, 4 barrels/4 crates, 32 flag stones, no cases, 100% rack quantities")
if __name__=="__main__":main()
