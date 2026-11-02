#!/usr/bin/env python3
"""Offline regression: V53 must add only one event/point and one car profile."""
from __future__ import annotations
import xml.etree.ElementTree as ET
from v53_gunter_gift import (
    CAR, EVENT, CARGO, FILES, patch, patch_for_postread, parse, data, X, Z
)

def sample():
    events=ET.fromstring("""<events><event name="VehicleHatchback02">
    <nominal>8</nominal><min>5</min><max>10</max><lifetime>300</lifetime>
    <restock>0</restock><saferadius>500</saferadius>
    <distanceradius>500</distanceradius><cleanupradius>200</cleanupradius>
    <flags deletable="0" init_random="0" remove_damaged="1"/>
    <position>fixed</position><limit>mixed</limit><active>1</active>
    <children><child lootmax="0" lootmin="0" max="5" min="3"
      type="Hatchback_02_Black"/></children></event>
    <event name="VehicleOther"><nominal>3</nominal></event></events>""")
    pos=ET.fromstring("""<eventposdef>
      <event name="VehicleHatchback02"><pos x="120" z="150" a="0"/></event>
    </eventposdef>""")
    sp=ET.Element("spawnabletypes")
    t=ET.SubElement(sp,"type",{"name":CAR})
    parts=(["Hatchback_02_Wheel"]*5+
        ["CarRadiator","CarBattery","SparkPlug"]+
        ["HeadlightH7"]*2+
        ["Hatchback_02_Door_1_1","Hatchback_02_Door_1_2",
         "Hatchback_02_Door_2_1","Hatchback_02_Door_2_2",
         "Hatchback_02_Hood","Hatchback_02_Trunk"])
    for n in parts:
        g=ET.SubElement(t,"attachments",{"chance":"1.00"})
        ET.SubElement(g,"item",{"name":n,"chance":"0.60"})
    ET.SubElement(sp,"type",{"name":"Truck_01_Covered"})
    types=ET.Element("types")
    for n in {CAR,*parts,*CARGO}:
        ET.SubElement(types,"type",{"name":n})
    return dict(zip(FILES,map(data,(events,pos,sp)))),types

def main():
    before,types=sample()
    edited,detail=patch(before,types)
    assert edited is not None and detail["configured_cargo_entries"]==10
    ok,stats=patch_for_postread(edited)
    assert ok and stats["cargo_counts"]==CARGO
    assert int(parse(edited[FILES[0]]).find(f"event[@name='{EVENT}']").findtext("max"))==1
    p=parse(edited[FILES[1]]).find(f"event[@name='{EVENT}']/pos")
    assert float(p.get("x"))==X and float(p.get("z"))==Z
    assert (patch(edited,types))[0] is None
    tampered=dict(before)
    tampered[FILES[1]]=tampered[FILES[1]].replace(
        b'x="120"',b'x="9416.70"').replace(b'z="150"',b'z="3489.65"')
    try:
        patch(tampered,types)
        raise AssertionError("Nearest vehicle collision guard failed")
    except Exception as ex:
        assert "too close" in str(ex)
    bad=dict(before)
    bad[FILES[2]]=bad[FILES[2]].replace(
        b'<type name="Truck_01_Covered" />',
        b'<type name="Truck_01_Covered"><cargo /></type>')
    mod,_=patch(bad,types)
    assert mod is not None
    print("V53 PASS: structure/cargo/position, 100% attachment preset, collision guard, no other class mutation")
    print("V53 CAUTION: fuel tank/coolant and true vehicle appearance require PS5 test")

if __name__=="__main__": main()
