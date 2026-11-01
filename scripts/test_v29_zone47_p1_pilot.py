#!/usr/bin/env python3
"""Offline-only, exact scope and fail-closed assertions for V29 P1."""
import json,copy
from v29_zone47_p1_pilot import (
    build_scene,patch_gameplay,CLASS,REL,V16,DOLNIK,NitradoError,RADIUS
)

def orig():
    return {
      "version":123,"GeneralData":{"disableBaseDamage":True},
      "WorldsData":{"objectSpawnersArr":[
          "custom/beileys47_hotspot_zone47.json",DOLNIK,V16],
          "lightingConfig":0},
      "PlayerData":{"StaminaData":{"sprintStaminaModifierErc":0,
           "sprintStaminaModifierCro":0,"staminaKgToStaminaPercentPenalty":0},
           "MovementData":{"timeToSprint":.01,"timeToStrafeSprint":.01}},
      "MapData":{"ignoreMapOwnership":True}
    }
def reject(payload):
    try:patch_gameplay(json.dumps(payload).encode())
    except (NitradoError,ValueError,KeyError,TypeError):return
    raise AssertionError("Bad gameplay should fail closed")
def main():
    scene,ob=build_scene()
    doc=json.loads(scene)
    assert len(doc["Objects"])==1
    assert ob==doc["Objects"][0] and ob["name"]==CLASS
    assert 9030<ob["pos"][0]<9090 and 7800<ob["pos"][2]<7860
    assert 290<ob["pos"][1]<315
    assert ob["enableCEPersistency"] is False
    assert ob["scale"]==1.0 and ob["ypr"]==[120,0,0]
    original=orig()
    new,old_list=patch_gameplay(json.dumps(original).encode())
    target=json.loads(new)
    assert len(target["WorldsData"]["objectSpawnersArr"])==4
    assert target["WorldsData"]["objectSpawnersArr"][-1]==REL
    assert target["WorldsData"]["objectSpawnersArr"][:-1]==old_list
    assert target["GeneralData"]==original["GeneralData"]
    assert target["PlayerData"]==original["PlayerData"]
    assert target["MapData"]==original["MapData"]
    assert target["WorldsData"]["lightingConfig"]==original["WorldsData"]["lightingConfig"]
    reject(target)
    bad=copy.deepcopy(original);bad["WorldsData"]["objectSpawnersArr"].remove(V16);reject(bad)
    bad=copy.deepcopy(original);bad["WorldsData"]["objectSpawnersArr"].remove(DOLNIK);reject(bad)
    bad=copy.deepcopy(original);bad["WorldsData"]["objectSpawnersArr"].append(V16);reject(bad)
    bad=copy.deepcopy(original);bad["WorldsData"]["objectSpawnersArr"]=None;reject(bad)
    print("PASS V29 P1: 1 real ground-Y guardbox, no lost existing scenes, no non-target edits, fail closed")

if __name__=="__main__":main()
