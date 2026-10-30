#!/usr/bin/env python3
"""Adversarial offline Central Economy source-integrity guards."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from build_mission import modify_spawns
from build_stage2 import update_type_values,update_vehicles

def reject(fn,expected:str)->None:
    try:fn()
    except (ValueError,AssertionError) as ex:
        assert expected in str(ex),(expected,str(ex))
    else:raise AssertionError("Malformed official data/config was not rejected: "+expected)

def test()->None:
    dup_groups=ET.fromstring("""<playerspawnpoints><fresh><generator_posbubbles>
      <group name="Brena"><pos x="1" z="2"/></group>
      <group name="Brena"><pos x="3" z="4"/></group>
      <group name="Sobotka"><pos x="5" z="6"/></group>
    </generator_posbubbles></fresh></playerspawnpoints>""")
    reject(lambda:modify_spawns(dup_groups,{"fresh_spawn_groups":["Brena","Sobotka"]}),"Duplicate")
    missing_name=ET.fromstring("""<playerspawnpoints><fresh><generator_posbubbles>
      <group><pos x="1" z="2"/></group>
      <group name="Sobotka"><pos x="5" z="6"/></group>
    </generator_posbubbles></fresh></playerspawnpoints>""")
    reject(lambda:modify_spawns(missing_name,{"fresh_spawn_groups":["Brena","Sobotka"]}),"unnamed")
    dup_types=ET.fromstring("""<types>
       <type name="SKS"/><type name="SKS"/>
    </types>""")
    reject(lambda:update_type_values(dup_types,{"required_item_types":["SKS"]}),"Duplicate")
    bad_vehicles=ET.fromstring("""<spawnabletypes>
       <type name="Hatchback_02"/><type name="Hatchback_02"/>
    </spawnabletypes>""")
    reject(lambda:update_vehicles(bad_vehicles,{"vehicle_attachment_rules":{}}),"Duplicate")
    def car(rawchance:str)->ET.Element:
        return ET.fromstring(f"""<spawnabletypes><type name="Hatchback_02">
         <attachments>
           <item name="WheelA" chance="{rawchance}"/><item name="WheelB" chance="0.7"/>
           <item name="WheelC" chance="0.7"/><item name="WheelD" chance="0.7"/>
           <item name="SparkPlug" chance="0.5"/>
         </attachments></type></spawnabletypes>""")
    rules={"vehicle_attachment_rules":{"Hatchback_02":{
        "wheel_chance_first_four":0.9,"repair_part_chance_floor":0.75}}}
    for invalid in ("NaN","Infinity","-0.1","1.1"):
        reject(lambda x=invalid:update_vehicles(car(x),rules),"invalid original wheel chance")
    for invalid in (float("nan"),float("inf"),-0.1,1.1,True):
        broken={"vehicle_attachment_rules":{"Hatchback_02":{
           "wheel_chance_first_four":invalid,"repair_part_chance_floor":0.75}}}
        reject(lambda b=broken:update_vehicles(car("0.5"),b),"invalid vehicle probability rule")
    result=update_vehicles(car("0.5"),rules)
    assert len(result)==1 and len(result[0]["parts"])==5
    print("PASS: malformed spawn groups, duplicate CE types and nonfinite vehicle probabilities fail closed.")
    print("Tests are purely synthetic; no game engine or Nitrado is available.")

if __name__=="__main__":test()
