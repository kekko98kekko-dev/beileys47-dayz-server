#!/usr/bin/env python3
"""BEILEYS47 V31: complete 26-object ZONA 47 concept, honest offline collision gate.

Uses 26 calibrated ground coordinates, 9 class-matched options and 17
conservative vanilla prop substitutions. Does NOT assert that model origins
equal terrain heights, class exists as PS5 spawnable, or collisions are safe.
Does not call Nitrado. Generates a valid experimental Object Spawner JSON
for *inspection only*, plus a measured pairwise visual-clearance audit.
"""
from __future__ import annotations
import json,math,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SURVEY=ROOT/"config/stage4_14_public_terrain_survey.json"
EVIDENCE=ROOT/"config/stage4_9_p3d_bbox_evidence.json"
OUTPUT=ROOT/"dist/v31"
P1="checkpoint_03"
P1_CLASS="Land_Mil_GuardBox_Green"
# These are V16 existing live configuration classnames, not verified PS5 render.
FALLBACK={
 "checkpoint_01":"Land_Mil_Fortified_Nest_Small",
 "checkpoint_02":"Land_Mil_Fortified_Nest_Small",
 "woods_01":"Land_Roadblock_WoodenCrate",
 "woods_02":"Land_Roadblock_WoodenCrate",
 "service_01":"Land_Roadblock_WoodenCrate",
 "service_03":"Land_Roadblock_Table",
 "barracks_02":"Land_Roadblock_WoodenCrate",
 "barracks_03":"Land_Roadblock_WoodenCrate",
 "barracks_04":"Land_Roadblock_Table",
 "logistics_04":"Land_Roadblock_Table",
 "hq_02":"Land_Roadblock_WoodenCrate",
 "hq_03":"Land_Roadblock_WoodenCrate",
 "hq_04":"Land_Roadblock_Table",
 "hq_05":"Land_Roadblock_Table",
 "ridge_02":"Land_Mil_Fortified_Nest_Small",
 "secret_01":"Land_Roadblock_WoodenCrate",
 "secret_02":"Land_Roadblock_Table",
}
# Unknown models have intentionally oversized bounds. Needed because
# bounding boxes of V16 roadblocks are NOT independently verified.
UNVERIFIED_RADIUS={
 "Land_Roadblock_WoodenCrate":5.0,
 "Land_Roadblock_Table":5.0
}
MIN_WALKWAY=2.5
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def guard(ok,message):
 if not ok:raise ValueError(message)
def radius(model,meta):
 if model in UNVERIFIED_RADIUS:return UNVERIFIED_RADIUS[model],False
 source=meta.get(model)
 guard(source is not None,"No source visual metadata for "+model)
 a=source["bbox_min"];b=source["bbox_max"]
 return max(math.hypot(x,z) for x in (a["x"],b["x"]) for z in (a["z"],b["z"])),True
def build():
 s=load(SURVEY)
 assert not s["deployment_allowed"] and not s["ps4_ps5_tested"]
 central=[site for site in s["candidate_sites"] if site["region"]=="central"]
 guard(len(central)==1,"No unique calibrated central site")
 site=central[0]
 guard((site["center_x"],site["center_z"],site["rotation_degrees"])==(9000,7800,120),"Site drift")
 places=site["placements"]
 guard(len(places)==26 and len(set(x["id"] for x in places))==26,"Not exactly 26 unique placements")
 meta={m["candidate_dayz_terrain_classname"]:m for m in load(EVIDENCE)["models"]}
 planned={}
 for p in places:
    id=p["id"]
    mapped=p["class_candidate_unverified"]
    cls=mapped if mapped is not None else FALLBACK.get(id)
    guard(isinstance(cls,str) and cls.startswith("Land_"),"Unmapped class "+id)
    bounds,measured=radius(cls,meta)
    xyz=[float(p[k]) for k in ("x","terrain_y","z")]
    guard(all(math.isfinite(x) for x in xyz),"Invalid XY")
    guard(0<=xyz[0]<=12800 and 0<=xyz[2]<=12800,"Out of bounds")
    guard(200<xyz[1]<400,"Unexpected terrain Y")
    scene={"name":cls,"pos":[round(v,4) for v in xyz],
           "ypr":[site["rotation_degrees"],0,0],
           "scale":1.0,"enableCEPersistency":False}
    planned[id]={"source":"V28 calibrated terrain ground height",
           "role":p["visual_role"],"classname":cls,
           "candidate_not_tested_on_PS5":True,
           "fallback_substitution":mapped is None,
           "bbox_origin_radius_m":round(bounds,3),
           "bbox_radius_verified_by_third_party_p3d":measured,
           "local_12m_relief_m":p["local_12m_ground_relief_m"],
           "scene":scene}
 guard(set(planned)==(set(FALLBACK)|{p["id"] for p in places if p["class_candidate_unverified"] is not None}),
       "Model role map does not cover 26 slots")
 guard(planned[P1]["classname"]==P1_CLASS,"P1 model changed")
 collisions=[]
 ids=list(planned)
 for i,a in enumerate(ids):
    for b in ids[i+1:]:
      x=planned[a];y=planned[b]
      dx=x["scene"]["pos"][0]-y["scene"]["pos"][0]
      dz=x["scene"]["pos"][2]-y["scene"]["pos"][2]
      gap=math.hypot(dx,dz)-(x["bbox_origin_radius_m"]+y["bbox_origin_radius_m"])
      if gap<MIN_WALKWAY:
       collisions.append({"a":a,"b":b,"clearance_m":round(gap,3),
         "minimum_walkway_m":MIN_WALKWAY,
         "a_class":x["classname"],"b_class":y["classname"]})
 # P1 preexisting, its placement must NOT be duplicated in any second file.
 new=[planned[id]["scene"] for id in ids if id!=P1]
 guard(len(new)==25,"Second scene must have exactly 25 objects")
 # A valid file is still NOT a deployment approval.
 audit={"stage":"V31","project":"BEILEYS47 ZONA 47 240x220",
  "site_center":[9000,7800],"rotation_degrees":120,
  "requested_scene_slots":26,"existing_live_p1_slots":1,
  "new_offline_scene_objects":25,
  "fallback_visual_substitutions":len(FALLBACK),
  "independently_verified_ps5_model_count":0,
  "model_origin_y_verified_count":0,
  "persistence_backup_checked":False,
  "console_visual_collision_passed":False,
  "p3d_visual_clearance_only":True,"player_walkable_paths_tested":False,
  "Nitrado_write_actions":0,
  "deployment_allowed":False,
  "detected_visual_clearance_pairs_below_2_5m":len(collisions),
  "visual_clearance_conflicts":collisions,
  "highest_risk":sorted([{"id":k,"class":v["classname"],
          "radius":v["bbox_origin_radius_m"],"relief":v["local_12m_relief_m"]}
           for k,v in planned.items()],key=lambda v:-(v["radius"]+v["relief"]))[:10],
  "placed_roles":planned}
 return {"Objects":new},audit
def main():
 out,audit=build()
 OUTPUT.mkdir(parents=True,exist_ok=True)
 source=(json.dumps(out,indent=2,ensure_ascii=False)+"\n").encode()
 (OUTPUT/"BEILEYS47_ZONE47_25_EXPERIMENTAL_NOT_ACTIVE.json").write_bytes(source)
 audit["scene_sha256"]=hashlib.sha256(source).hexdigest()
 (OUTPUT/"GEOMETRY_AND_DEPLOY_GATE.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n")
 print("V31 generated 25 offline JSON objects; 1 existing P1; "
       +str(audit["detected_visual_clearance_pairs_below_2_5m"])+" visual clearance warnings.")
 print("NOTE: P3D bbox clearance is NOT collision/FPS proof. NO NITRADO DEPLOY.")
if __name__=="__main__":main()
