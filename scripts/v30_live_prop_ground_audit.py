#!/usr/bin/env python3
"""BEILEYS47 V30: read-only compare actual live V16 placed objects vs Livonia heightfield.

This is a TERRAIN-ORIGIN diagnostic, not proof objects are visually floating:
model origins/foundations may be offset intentionally. No live edits or restarts.
"""
from __future__ import annotations
import io,json,math,os,posixpath
from pathlib import Path
import numpy as np
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from v27_zone47_real_heights import get,interp,RASTER,WORLD
from deploy_beileys47_v15 import game_state,game_status
OUT=Path("deploy/v30/LIVE_PROP_HEIGHT_DIAGNOSTIC.json")
FILES=["custom/beileys47_v16_three_hotspots.json","custom/beileys47_v29_zone47_p1_guardbox.json"]
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Nitrado secret unavailable")
    mission=resolve_mission(token)
    grid=np.load(io.BytesIO(get(RASTER)),allow_pickle=False)
    assert grid.shape==(2048,2048)
    factor=(grid.shape[0]-1)/WORLD
    report={"source":"DZPage Livonia 2048² terrain raster + current Nitrado spawner JSON",
      "calibration":"matched against 1100 official static Livonia groups in V27",
      "read_only":True,"changes_to_Nitrado":0,
      "model_pivot_offsets_unknown":True,"console_contact_verified":False,
      "server_status":game_status(game_state(token)),"scenes":[]}
    for f in FILES:
        payload=json.loads(download_one(token,posixpath.join(mission,f)))
        objects=payload.get("Objects")
        if not isinstance(objects,list):raise ValueError("Invalid live objects JSON")
        surveyed=[]
        for i,o in enumerate(objects):
            pos=o.get("pos")
            if not isinstance(pos,list) or len(pos)!=3:
                raise ValueError("Malformed world pos")
            x,y,z=map(float,pos)
            assert all(map(math.isfinite,(x,y,z)))
            height=float(interp(grid,x,z,("zx",False,False),factor))
            difference=y-height
            surveyed.append({"index":i,"name":o.get("name"),
              "x":round(x,3),"z":round(z,3),"object_origin_y":round(y,3),
              "terrain_y":round(height,3),
              "origin_minus_ground_m":round(difference,3),
              "needs_visual_check":abs(difference)>1.5,
              "extreme_difference_over_6m":abs(difference)>6.0})
        report["scenes"].append({
          "name":f,"total":len(surveyed),
          "median_abs_origin_ground_delta":round(float(np.median([abs(o["origin_minus_ground_m"]) for o in surveyed])),3),
          "gt_1_5m":sum(x["needs_visual_check"] for x in surveyed),
          "gt_6m":sum(x["extreme_difference_over_6m"] for x in surveyed),
          "objects":surveyed})
    assert report["scenes"][0]["total"]==32 and report["scenes"][1]["total"]==1
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
