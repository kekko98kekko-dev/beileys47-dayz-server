#!/usr/bin/env python3
"""Offline no-Nitrado checks for V48 selective building placement preview."""
import copy
import json
from v48_build_anywhere_preview import apply_preview, BALANCED, EXTENDED

def fixture():
    return {
      "version":123,
      "GeneralData":{"disableBaseDamage":False},
      "PlayerData":{"StaminaData":{"sprintStaminaModifierErc":0},"spawnGearPresetFiles":["custom/kit.json"]},
      "WorldsData":{"objectSpawnersArr":["custom/beileys47_dolnik.json"]},
      "BaseBuildingData":{
        "HologramData":{
          "disableIsCollidingBBoxCheck":False,
          "disableIsBaseViableCheck":False,
          "disableIsCollidingAngleCheck":False,
          "disableHeightPlacementCheck":False,
          "disableIsClippingRoofCheck":False,
          "disableIsPlacementPermittedCheck":False,
          "disableIsUnderwaterCheck":False,
          "disallowedTypesInUnderground":["FenceKit","TerritoryFlagKit","WatchtowerKit"]
        },
        "ConstructionData":{"disableIsCollidingCheck":False,"disablePerformRoofCheck":False}
      },
      "MapData":{"displayPlayerPosition":True},
      "VehicleData":{"boatDecayMultiplier":1}
    }

def test(profile, keys):
    old = fixture()
    new_raw, changes = apply_preview(json.dumps(old).encode(), profile)
    updated = json.loads(new_raw)
    assert len(changes) == len(keys)
    for section,key in keys:
        assert updated["BaseBuildingData"][section][key] is True
    expected = copy.deepcopy(old)
    for section,key in keys:
        expected["BaseBuildingData"][section][key] = True
    assert expected == updated
    assert updated["BaseBuildingData"]["HologramData"]["disableIsUnderwaterCheck"] is False
    assert updated["BaseBuildingData"]["HologramData"]["disallowedTypesInUnderground"] == old["BaseBuildingData"]["HologramData"]["disallowedTypesInUnderground"]
    repeat, repeat_changes = apply_preview(new_raw,profile)
    assert json.loads(repeat) == expected and repeat_changes == []

def main():
    test("balanced",BALANCED)
    test("extended",EXTENDED)
    bad=fixture()
    del bad["BaseBuildingData"]["HologramData"]["disableHeightPlacementCheck"]
    try: apply_preview(json.dumps(bad).encode())
    except ValueError: pass
    else: raise AssertionError("Missing config check accepted")
    print("V48 offline checks: PASS (balanced, extended, no collateral changes, idempotence, invalid-field refusal)")

if __name__ == "__main__":main()
