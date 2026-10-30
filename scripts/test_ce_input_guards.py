#!/usr/bin/env python3
"""Adversarial offline Central Economy source-integrity guards."""
from __future__ import annotations

import copy
import xml.etree.ElementTree as ET

from build_mission import modify_spawns,modify_types
from build_stage2 import update_type_values,update_vehicles,update_gameplay
from build_stage3 import modify_events

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
    reject(lambda:update_vehicles(bad_vehicles,{"vehicle_attachment_rules":{"Hatchback_02":{"wheel_chance_first_four":0.9,"repair_part_chance_floor":0.75}}}),"Duplicate target")
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

    stage1_loot=ET.fromstring('<types><type name="BandageDressing"><nominal>5</nominal><min>2</min></type></types>')
    for invalid in (True, "1.4", float("nan"), float("inf")):
        stage1_rules={"required_items":["BandageDressing"],"loot_multipliers":{"BandageDressing":invalid}}
        reject(lambda b=stage1_rules:modify_types(copy.deepcopy(stage1_loot),b),"Invalid multiplier")

    # Python True == 1: semantic fields must reject JSON boolean values,
    # not accidentally write them into DayZ XML/JSON numeric parameters.
    loot=ET.fromstring('<types><type name="SKS"><nominal>5</nominal><min>2</min></type></types>')
    for invalid in (True, "1.4", float("nan"), float("inf")):
        bad={"required_item_types":["SKS"],"type_multipliers":{"SKS":invalid}}
        reject(lambda b=bad:update_type_values(copy.deepcopy(loot),b),"invalid item multiplier")

    gameplay={"GeneralData":{"disableBaseDamage":False,"disableContainerDamage":False},
              "PlayerData":{"StaminaData":{"staminaMax":100,
                                           "staminaKgToStaminaPercentPenalty":1.75}}}
    good={"gameplay":{"staminaMax":105,"staminaKgToStaminaPercentPenalty":1.65,
                      "disableBaseDamage":False,"disableContainerDamage":False}}
    assert len(update_gameplay(copy.deepcopy(gameplay),good))==2
    for invalid in (True, "105", float("nan"), float("inf")):
        broken=copy.deepcopy(good)
        broken["gameplay"]["staminaMax"]=invalid
        reject(lambda b=broken:update_gameplay(copy.deepcopy(gameplay),b),"Invalid gameplay setting")
    boolean_old=copy.deepcopy(gameplay)
    boolean_old["PlayerData"]["StaminaData"]["staminaMax"]=True
    reject(lambda:update_gameplay(boolean_old,good),"Invalid gameplay setting")

    events_xml='''<events>
      <event name="StaticHeliCrash"><active>1</active><position>fixed</position>
        <nominal>1</nominal><children><child type="WreckA" max="1"/></children></event>
      <event name="StaticMilitaryConvoy"><active>1</active><position>fixed</position>
        <nominal>1</nominal></event>
    </events>'''
    approved={"events":{
        "StaticHeliCrash":{"vanilla_nominal":1,"target_nominal":2,
                           "child_type":"WreckA","vanilla_child_max":1,"target_child_max":2},
        "StaticMilitaryConvoy":{"vanilla_nominal":1,"target_nominal":2}}}
    assert len(modify_events(ET.fromstring(events_xml),approved))==2
    for name,key in (("StaticHeliCrash","target_nominal"),
                     ("StaticHeliCrash","vanilla_child_max"),
                     ("StaticHeliCrash","target_child_max"),
                     ("StaticMilitaryConvoy","vanilla_nominal")):
        altered=copy.deepcopy(approved)
        altered["events"][name][key]=True
        reject(lambda b=altered:modify_events(ET.fromstring(events_xml),b),
               "Invalid event integer rule")
    print("PASS: malformed CE input, boolean-as-integer event and gameplay guards fail closed.")
    print("Tests are purely synthetic; no game engine or Nitrado is available.")

if __name__=="__main__":test()
