#!/usr/bin/env python3
from v32_zone47_clearance_solver import build,MIN_WALKWAY
from v31_full_zone47_dryrun import P1,FALLBACK
def main():
  scene,report=build()
  assert len(scene["Objects"])==25
  assert report["p1_preserved"] is True
  assert report["visual_clearance_conflicts"]==0
  assert report["actual_terrain_y_per_position"] is True
  assert report["deployment_allowed"] is False
  assert report["nitrado_api_calls"]==0
  assert report["max_subordinate_shift_m"]<=38
  assert all(x["id"] in FALLBACK for x in report["relocations"])
  assert all(0<=o["pos"][0]<=12800 and 0<=o["pos"][2]<=12800 for o in scene["Objects"])
  assert all(o["name"].startswith("Land_") and o["enableCEPersistency"] is False for o in scene["Objects"])
  print("PASS V32: 25 new objects, P1 unmodified, zero visual circle intersections, no bogus PS5 verification")
if __name__=="__main__":main()
