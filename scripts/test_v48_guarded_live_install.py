#!/usr/bin/env python3
"""V48 protected installer OFFLINE regression checks; never calls Nitrado."""
import hashlib,json,os,zipfile
from unittest.mock import patch
from pathlib import Path
import v48_guarded_live_install as deploy
from v48_build_anywhere_preview import apply_preview

def main():
    src={
        "version":123,
        "GeneralData":{"disableBaseDamage":False},
        "PlayerData":{"spawnGearPresetFiles":["custom/kit.json"],"StaminaData":{"sprintStaminaModifierErc":0}},
        "WorldsData":{"objectSpawnersArr":["custom/live-spawner.json"]},
        "BaseBuildingData":{
          "HologramData":{
            "disableIsCollidingBBoxCheck":False,
            "disableIsBaseViableCheck":False,
            "disableIsCollidingAngleCheck":False,
            "disableHeightPlacementCheck":False
          },
          "ConstructionData":{"disableIsCollidingCheck":False}
        },
        "MapData":{"displayPlayerPosition":True}
    }
    raw=json.dumps(src,indent=2).encode()
    new,changes=apply_preview(raw,"balanced")
    assert len(changes)==5
    assert deploy.exact_semantics(new,json.dumps(json.loads(new),separators=(",",":")).encode())
    assert not deploy.exact_semantics(raw,new)
    assert deploy.REL=="cfggameplay.json"
    assert deploy.known_player_count(0)
    assert deploy.known_player_count(1)
    assert deploy.known_player_count(10)
    assert not deploy.known_player_count(None)
    assert not deploy.known_player_count(True)
    assert not deploy.known_player_count(-1)
    with patch.dict(os.environ, {"BEILEYS47_V48_ALLOW_PLAYER_INTERRUPTION":"yes"}):
        assert deploy.player_restart_authorized()
    with patch.dict(os.environ, {"BEILEYS47_V48_ALLOW_PLAYER_INTERRUPTION":"no"}):
        assert not deploy.player_restart_authorized()
    with patch.dict(os.environ, {"BEILEYS47_V48_ALLOW_PLAYER_INTERRUPTION":""}):
        assert not deploy.player_restart_authorized()
    deploy.make_backup(raw)
    with zipfile.ZipFile(deploy.BACKUP) as z:
        assert z.testzip() is None
        copy=z.read("dayzOffline.enoch/cfggameplay.json")
        assert copy==raw
        assert hashlib.sha256(copy).hexdigest() in z.read("SHA256.txt").decode()
    deploy.BACKUP.unlink()
    print("V48 forced restart authorization + offline backup guards PASS; no Nitrado calls")
if __name__=="__main__":main()
