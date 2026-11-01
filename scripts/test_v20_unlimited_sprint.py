#!/usr/bin/env python3
"""Offline V20 gameplay field-scope/security tests. Zero Nitrado access."""
import copy,json
from v20_unlimited_sprint import patch,setting_state,NitradoError,STAMINA_TARGET,MOVEMENT_TARGET

def sample():
    return {"version":123,
      "GeneralData":{"disableBaseDamage":False,"disableContainerDamage":False},
      "PlayerData":{
        "spawnGearPresetFiles":["custom/beileys47-kit.json"],
        "StaminaData":{"sprintStaminaModifierErc":0.9,"sprintStaminaModifierCro":0.7,
           "staminaWeightLimitThreshold":6000.0,"staminaMax":105,
           "staminaKgToStaminaPercentPenalty":1.65,"staminaMinCap":5.0,
           "sprintSwimmingStaminaModifier":1.0,"sprintLadderStaminaModifier":1.0,
           "obstacleTraversalStaminaModifier":1.0},
        "MovementData":{"timeToSprint":0.45,"timeToStrafeSprint":0.3,
            "timeToStrafeJog":0.1,"allowStaminaAffectInertia":True},
        "ShockHandlingData":{"shockRefillSpeedConscious":5.0}
      },
      "WorldsData":{"objectSpawnersArr":["custom/beileys47_v16_three_hotspots.json",
                         "custom/beileys47_dolnik_military_base_v9.json"],
        "environmentMinTemps":[1,2,3]},
      "MapData":{"ignoreMapOwnership":True}}
def reject(blob):
    try:patch(blob)
    except (NitradoError,ValueError,KeyError,TypeError):return
    raise AssertionError("Unsafe candidate accepted")

def main():
    original=sample()
    data=json.dumps(original,separators=(",",":")).encode()
    result,changes=patch(data)
    new=json.loads(result)
    assert len(changes)==5 and new["PlayerData"]["StaminaData"]["staminaMax"]==105
    for k,v in STAMINA_TARGET.items():
        assert new["PlayerData"]["StaminaData"][k]==v
    for k,v in MOVEMENT_TARGET.items():
        assert new["PlayerData"]["MovementData"][k]==v
    assert new["PlayerData"]["StaminaData"]["obstacleTraversalStaminaModifier"]==1.0
    assert new["PlayerData"]["StaminaData"]["sprintSwimmingStaminaModifier"]==1.0
    assert new["PlayerData"]["MovementData"]["allowStaminaAffectInertia"] is True
    assert new["WorldsData"]==original["WorldsData"]
    assert new["GeneralData"]==original["GeneralData"]
    assert new["MapData"]==original["MapData"]
    assert new["PlayerData"]["spawnGearPresetFiles"]==original["PlayerData"]["spawnGearPresetFiles"]
    again,changes2=patch(result)
    assert json.loads(again)==new
    assert all(c["before"]==c["after"] for c in changes2.values())
    cases=[]
    n=copy.deepcopy(original);del n["WorldsData"]["objectSpawnersArr"][0];cases.append(n)
    n=copy.deepcopy(original);n["PlayerData"]["StaminaData"]["staminaMax"]=0;cases.append(n)
    n=copy.deepcopy(original);n["PlayerData"]["StaminaData"]["sprintStaminaModifierErc"]=True;cases.append(n)
    n=copy.deepcopy(original);del n["PlayerData"]["MovementData"]["timeToSprint"];cases.append(n)
    n=copy.deepcopy(original);n["PlayerData"]["StaminaData"]["staminaKgToStaminaPercentPenalty"]="zero";cases.append(n)
    n=copy.deepcopy(original);n["PlayerData"]["MovementData"]["timeToStrafeSprint"]=-0.5;cases.append(n)
    for invalid in cases:reject(json.dumps(invalid).encode())
    assert setting_state({"settings":{"config":{"enableCfgGameplayFile":1}}})=="enabled"
    assert setting_state({"settings":{"config":{"enableCfgGameplayFile":0}}})=="disabled"
    assert setting_state({"settings":{}})=="unknown"
    print("PASS V20: zero sprint drain, no load penalty, faster sprint transition, unchanged gameplay/world and fail-closed guards")

if __name__=="__main__":main()
