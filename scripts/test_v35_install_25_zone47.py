#!/usr/bin/env python3
"""V35 offline tests: real 25-object source, reversible single registry addition."""
import json,copy
from v35_install_25_zone47 import (
  candidate,patched_gameplay,separated,NEW,P1,V16,DOLNIK,NitradoError
)
def baseline():
 return {
 "GeneralData":{"disableBaseDamage":True,"extra":99},
 "PlayerData":{"StaminaData":{
   "sprintStaminaModifierErc":0,"sprintStaminaModifierCro":0,
   "staminaKgToStaminaPercentPenalty":0},
   "MovementData":{"timeToSprint":0.01,"timeToStrafeSprint":0.01},
   "other":"untouched"},
 "WorldsData":{"objectSpawnersArr":[V16,DOLNIK,P1],"other":"unchanged"},
 "BuildingData":{"enabled":True}
 }
def reject(state):
 try:patched_gameplay(json.dumps(state).encode())
 except (NitradoError,ValueError,TypeError,KeyError):return
 raise AssertionError("Unsafe gameplay baseline accepted")
def main():
 raw,objects=candidate()
 assert len(objects)==25 and all(o["enableCEPersistency"] is False for o in objects)
 assert all(o["name"].startswith("Land_") for o in objects)
 orig=baseline()
 amended,names=patched_gameplay(json.dumps(orig).encode())
 mod=json.loads(amended)
 assert mod["WorldsData"]["objectSpawnersArr"]==names+[NEW]
 assert mod["PlayerData"]==orig["PlayerData"]
 assert mod["BuildingData"]==orig["BuildingData"]
 assert mod["GeneralData"]==orig["GeneralData"]
 assert mod["WorldsData"]["other"]==orig["WorldsData"]["other"]
 assert len(set(tuple(o["pos"]) for o in objects))==25
 reject(mod)
 bad=copy.deepcopy(orig)
 bad["PlayerData"]["StaminaData"]["sprintStaminaModifierErc"]=1
 reject(bad)
 bad=copy.deepcopy(orig);bad["WorldsData"]["objectSpawnersArr"].remove(P1)
 reject(bad)
 bad=copy.deepcopy(orig);bad["WorldsData"]["objectSpawnersArr"].append(P1)
 reject(bad)
 # Simulate the existing guard box at its real V29 location.
 old={
 P1:json.dumps({"Objects":[{"name":"Land_Mil_GuardBox_Green",
      "pos":[9057.3275,302.7723,7822.7058]}]}).encode(),
 V16:json.dumps({"Objects":[{"name":"Land_Mil_Fortified_Nest_Small",
      "pos":[7100,300,6970]}]}).encode(),
 DOLNIK:json.dumps({"Objects":[{"name":"Land_Medical_Tent_Big",
      "pos":[11508,220,441]}]}).encode()
 }
 assert separated(objects,old)==3
 old[P1]=json.dumps({"Objects":[{"name":"Land_Mil_GuardBox_Green",
  "pos":objects[0]["pos"]}]}).encode()
 try:separated(objects,old)
 except NitradoError:pass
 else:raise AssertionError("Scene overlap accepted")
 print("PASS V35: 25 real candidate scene objects, previous spawners preserved, rollback-safe single edit, proximity fail closed")
if __name__=="__main__":main()
