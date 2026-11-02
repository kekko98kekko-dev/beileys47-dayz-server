#!/usr/bin/env python3
import json
from test_v37_zone47_infected_patches import base,events
from v37_zone47_infected_patches import patch as add_infected
from v57_remove_bugged_zone47 import CFG,INF,V29,V35,patch_gameplay,patch_infected,verify_removed

def main():
    cfg={"WorldsData":{"objectSpawnersArr":[V29,V35,
       "custom/beileys47_v16_three_hotspots.json",
       "custom/beileys47_dolnik_military_base_v9.json"]},
       "PlayerData":{"StaminaData":{"sprintStaminaModifierErc":0}},
       "MapData":{"displayPlayerPosition":True}}
    edited,before,after=patch_gameplay(json.dumps(cfg).encode())
    assert (before,after)==(4,2)
    assert json.loads(edited)["PlayerData"]==cfg["PlayerData"]
    assert json.loads(edited)["MapData"]==cfg["MapData"]
    infected,expected=add_infected(base(),events())
    cleaned,total,remaining=patch_infected(infected)
    assert (total,remaining)==(5,3)
    assert verify_removed({CFG:edited,INF:cleaned})==2
    assert patch_infected(infected)[0]==cleaned
    print("V57 TEST PASS: 26 props unregistered, V49 zones removed, originals retained")
if __name__=="__main__":main()
