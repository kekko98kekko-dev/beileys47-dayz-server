#!/usr/bin/env python3
"""Negative tests for V8 overlap and corrupted release configuration."""
import copy
import audit_stable_v10 as a

def rejects(fn):
    try: fn()
    except AssertionError: return
    raise AssertionError("Bad input was not rejected!")

def main():
    objects=a.read_json(a.BASE)["Objects"]
    old=a.spawn_positions((a.MISSION/"franco_v8/cfgplayerspawnpoints.xml").read_text("utf-8-sig"))
    rejects(lambda:a.check_spawn_clear(old,objects))
    bad=copy.deepcopy(a.read_json(a.KIT))
    bad["discreteUnsortedItemSets"][0]["complexChildrenTypes"].pop()
    rejects(lambda:a.check_kit(bad))
    cfg=copy.deepcopy(a.read_json(a.CFG))
    cfg["WorldsData"]["objectSpawnersArr"].append("custom/beileys47_test_showcase_v7.json")
    rejects(lambda:a.check_cfg(cfg))
    print("PASS negative tests: V8 overlap, missing starter item, obsolete V7 scenery are detected.")

if __name__=="__main__":
    main()
