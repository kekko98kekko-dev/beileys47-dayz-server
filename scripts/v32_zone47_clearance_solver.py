#!/usr/bin/env python3
"""V32 move 17 subordinate ZONA47 props, preserving 9 candidate landmark structures.

Reads live-compatible public DayZ Livonia 2048² ground heights, resamples
shifted positions, and eliminates all known conservative VISUAL footprint
conflicts. No Nitrado writes. Cannot prove PS5 collisions, interactability
or model-origin Y. Do not conflate 0 visual circles conflicts with final quality.
"""
from __future__ import annotations
import io,json,math
from pathlib import Path
import numpy as np
from v31_full_zone47_dryrun import build as preliminary,FALLBACK,MIN_WALKWAY,P1
from v27_zone47_real_heights import RASTER,get,interp,WORLD

OUT=Path("dist/v32")
CENTER=(9000,7800)
ROTATION=120
MAX_SHIFT=38.0
RESOLUTION=2.0

def planar_distance(a,b):
 return math.hypot(a["scene"]["pos"][0]-b["scene"]["pos"][0],
                   a["scene"]["pos"][2]-b["scene"]["pos"][2])
def clearance(a,b):
 return planar_distance(a,b)-a["bbox_origin_radius_m"]-b["bbox_origin_radius_m"]
def inside(x,z,radius):
 angle=math.radians(ROTATION);c=math.cos(angle);s=math.sin(angle)
 dx,dz=x-CENTER[0],z-CENTER[1]
 local_x=c*dx+s*dz
 local_z=-s*dx+c*dz
 return abs(local_x)<=120-radius-1 and abs(local_z)<=110-radius-1
def sorted_offsets():
 values=[]
 for ix in range(-19,20):
  for iz in range(-19,20):
   dx=ix*RESOLUTION;dz=iz*RESOLUTION
   dd=math.hypot(dx,dz)
   if dd<=MAX_SHIFT:
    values.append((dd,dx,dz))
 return sorted(values,key=lambda e:(e[0],abs(e[1])+abs(e[2]),e[1],e[2]))
def sampled_ground(grid,x,z):
 return float(interp(grid,x,z,("zx",False,False),(grid.shape[0]-1)/WORLD))
def sampled_relief(grid,x,z):
 hs=[sampled_ground(grid,x+dx,z+dz) for dx,dz in
     [(-6,-6),(-6,0),(-6,6),(0,-6),(0,0),(0,6),(6,-6),(6,0),(6,6)]]
 return max(hs)-min(hs)
def build():
 preview,audit=preliminary()
 grid=np.load(io.BytesIO(get(RASTER)),allow_pickle=False)
 if grid.shape!=(2048,2048):raise ValueError("Unexpected terrain grid")
 props=json.loads(json.dumps(audit["placed_roles"]))
 ids=list(props)
 original={k:tuple(v["scene"]["pos"]) for k,v in props.items()}
 # Fixed structures retain original exact ground heights, role, orientation.
 fixed=[props[k] for k in ids if k not in FALLBACK]
 if len(fixed)!=9 or props[P1] not in fixed:raise ValueError("Changed fixed object set")
 for i,a in enumerate(fixed):
    for b in fixed[i+1:]:
       if clearance(a,b)<MIN_WALKWAY:
          raise ValueError("Landmark structures overlap; cannot relocate them automatically")
 placed=list(fixed)
 moves=[]
 for id in ids:
  if id not in FALLBACK:continue
  slot=props[id];x0,y0,z0=original[id]
  selected=None
  for dist,dx,dz in sorted_offsets():
    x=x0+dx;z=z0+dz
    if not inside(x,z,slot["bbox_origin_radius_m"]):continue
    candidate=json.loads(json.dumps(slot))
    candidate["scene"]["pos"][0]=round(x,4)
    candidate["scene"]["pos"][2]=round(z,4)
    if any(clearance(candidate,a)<MIN_WALKWAY for a in placed):continue
    ground=sampled_ground(grid,x,z)
    relief=sampled_relief(grid,x,z)
    if not math.isfinite(ground) or not 200<ground<400 or relief>3.0:
      continue
    candidate["scene"]["pos"][1]=round(ground,4)
    candidate["sampled_local_12m_relief_m"]=round(relief,3)
    candidate["relocated_m"]=round(dist,2)
    selected=candidate;break
  if selected is None:
    raise ValueError("No nonoverlap zone within 38 metres for "+id)
  props[id]=selected
  placed.append(selected)
  if selected["relocated_m"]:
   moves.append({"id":id,"old_pos":original[id],
                 "new_pos":selected["scene"]["pos"],
                 "shift_m":selected["relocated_m"],
                 "new_relief_m":selected["sampled_local_12m_relief_m"]})
 # Pairwise invariant: 0 conservative visual overlaps.
 warnings=[]
 for i,a in enumerate(ids):
  for b in ids[i+1:]:
   gap=clearance(props[a],props[b])
   if gap < MIN_WALKWAY-0.005:
     warnings.append({"a":a,"b":b,"visual_gap":gap})
 if warnings:raise ValueError("Remaining visual conflicts: "+str(warnings[:5]))
 # Check original P1 has NOT moved even by 0.001m.
 if tuple(props[P1]["scene"]["pos"])!=original[P1]:
  raise ValueError("Existing live P1 moved; stop")
 # Ground values on all 26 positions originate from calibrated map.
 scene={"Objects":[props[k]["scene"] for k in ids if k!=P1]}
 if len(scene["Objects"])!=25:raise ValueError("Incorrect P1-excluded count")
 all_positions=[p["scene"]["pos"] for p in props.values()]
 xs=[p[0] for p in all_positions];zs=[p[2] for p in all_positions]
 report={
   "stage":"V32","purpose":"geometric layout resolution, not console acceptance",
   "site_center":[9000,7800],"footprint_metres":[240,220],
   "p1_preserved":True,"existing_live_p1_count":1,
   "candidate_new_objects":25,"visual_clearance_conflicts":0,
   "unresolved_original_v31_conflicts":7,
   "subordinate_props_relodged":len(moves),
   "relocations":moves,
   "max_subordinate_shift_m":max([p["shift_m"] for p in moves],default=0),
   "bbox_x_span_m":round(max(xs)-min(xs),2),
   "bbox_z_span_m":round(max(zs)-min(zs),2),
   "all_26_classnames_assigned":True,
   "actual_terrain_y_per_position":True,
   "PS4_PS5_model_footprint_validated":False,
   "traversable_routes_checked":False,
   "vanilla_map_collision_checked":False,
   "full_world_backup_tested":False,
   "deployment_allowed":False,
   "nitrado_api_calls":0,
   "reason_no_auto_deploy":"P1 still lacks PS5 model contact/physics evidence; interior and large structures may not match visual circles"
 }
 return scene,report
def main():
 scene,report=build()
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"ZONE47_25_EXPERIMENTAL_RELOCATED.json").write_text(
   json.dumps(scene,indent=2)+"\n")
 (OUT/"ZERO_VISUAL_COLLISIONS_NOT_PS5_PROOF.json").write_text(
   json.dumps(report,indent=2)+"\n")
 print("V32 PASS: 26 ground-referenced props including existing P1; 25 offline candidates;",
   len(report["relocations"]),"secondary positions changed, 0 conservative visual collisions.",
   "No Nitrado edits or PS5-runtime proof.")
if __name__=="__main__":main()
