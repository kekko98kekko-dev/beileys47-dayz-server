#!/usr/bin/env python3
"""Offline invariant check for 26 source slots and no duplicate P1 in new spawner."""
from v31_full_zone47_dryrun import build,FALLBACK,P1
def main():
    scene,a=build()
    assert len(scene["Objects"])==25
    assert len(FALLBACK)==17
    assert a["requested_scene_slots"]==26
    assert a["existing_live_p1_slots"]==1
    assert a["new_offline_scene_objects"]==25
    assert a["deployment_allowed"] is False
    assert a["independently_verified_ps5_model_count"]==0
    assert a["model_origin_y_verified_count"]==0
    assert a["Nitrado_write_actions"]==0
    assert P1 in a["placed_roles"]
    assert all(o["name"].startswith("Land_") and len(o["pos"])==3 for o in scene["Objects"])
    assert all(o["enableCEPersistency"] is False for o in scene["Objects"])
    assert all(o["pos"]!=a["placed_roles"][P1]["scene"]["pos"] for o in scene["Objects"])
    assert len(a["visual_clearance_conflicts"])==a["detected_visual_clearance_pairs_below_2_5m"]
    print("PASS V31: 26 planned roles, 25 new nonduplicate props, no false runtime/collision/deploy assertions")
if __name__=="__main__":main()
