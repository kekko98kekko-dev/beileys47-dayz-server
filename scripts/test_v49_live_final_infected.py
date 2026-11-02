#!/usr/bin/env python3
"""V49 offline safety tests; no remote access and no player interruption."""
import hashlib
import json
import zipfile
from unittest.mock import patch
import v49_live_final_infected as v49
from v37_zone47_infected_patches import patch as make_zones,already_installed
def sample_gameplay():
    return json.dumps({
        "WorldsData":{"objectSpawnersArr":[v49.SPECIAL_SCENE]},
        "BaseBuildingData":{
           "HologramData":{
              "disableIsCollidingBBoxCheck":True,
              "disableIsBaseViableCheck":True,
              "disableIsCollidingAngleCheck":True,
              "disableHeightPlacementCheck":True},
           "ConstructionData":{"disableIsCollidingCheck":True}
        },
        "PlayerData":{"StaminaData":{
           "sprintStaminaModifierErc":0.0,
           "sprintStaminaModifierCro":0.0,
           "staminaKgToStaminaPercentPenalty":0.0}}
    }).encode()
def main():
    assert v49.world_feature_gate(sample_gameplay())
    for bad in (
        lambda g:g["WorldsData"]["objectSpawnersArr"].clear(),
        lambda g:g["BaseBuildingData"]["HologramData"].update({"disableHeightPlacementCheck":False}),
        lambda g:g["PlayerData"]["StaminaData"].update({"sprintStaminaModifierErc":1})
    ):
        src=json.loads(sample_gameplay());bad(src)
        try: v49.world_feature_gate(json.dumps(src).encode())
        except v49.NitradoError:pass
        else:raise AssertionError("Missing existing live feature accepted")
    assert v49.known_players(0) and v49.known_players(1) and v49.known_players(10)
    assert not v49.known_players(None) and not v49.known_players(True)
    assert not v49.known_players(11) and not v49.known_players(-1)
    old=b'''<?xml version="1.0"?><territory-type><territory color="4">
    <zone name="InfectedArmy" x="7100.0" z="6965.0" r="95" dmin="12" dmax="18"/>
    <zone name="InfectedArmy" x="9022.5" z="7457.9" r="85" dmin="10" dmax="14"/>
    <zone name="InfectedMedic" x="11490.0" z="461.0" r="75" dmin="6" dmax="10"/>
    </territory></territory-type>'''
    events=b'<events><event name="InfectedArmy"/><event name="InfectedMedic"/></events>'
    new,count=make_zones(old,events)
    assert count==3 and already_installed(new) and not already_installed(old)
    assert v49.meaning(new)==v49.meaning(new.replace(b'<territory-type>',b'<territory-type>\n'))
    assert v49.meaning(new)!=v49.meaning(old)
    v49.backup(old)
    with zipfile.ZipFile(v49.BACKUP) as z:
        assert z.testzip() is None
        assert z.read("dayzOffline.enoch/"+v49.FILE)==old
        assert hashlib.sha256(old).hexdigest() in z.read("SHA256.txt").decode()
    v49.BACKUP.unlink()
    print("PASS V49: existing features and game safety preserved, 2 zones validated, backup checksum and failed preflight tested")
if __name__=="__main__":main()
