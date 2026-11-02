#!/usr/bin/env python3
"""V48 protected installer OFFLINE regression checks; never calls Nitrado."""
import hashlib,json,zipfile
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
    deploy.make_backup(raw)
    with zipfile.ZipFile(deploy.BACKUP) as z:
        assert z.testzip() is None
        copy=z.read("dayzOffline.enoch/cfggameplay.json")
        assert copy==raw
        assert hashlib.sha256(copy).hexdigest() in z.read("SHA256.txt").decode()
    deploy.BACKUP.unlink()
    print("V48 installer OFFLINE guard tests PASS; no Nitrado calls")
if __name__=="__main__":main()
