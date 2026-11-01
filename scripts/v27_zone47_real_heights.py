#!/usr/bin/env python3
"""V27: calibrated, read-only Livonia heightmap sampling for 26 ZONA 47 candidates.

Fetch PUBLIC DZPage NPY terrain and vanilla Bohemia Livonia world object positions.
Fit row/column orientation and metre-to-grid scale against official static-object
world Y. No Nitrado calls, no player/world modifications, no automatic deployment.
"""
from __future__ import annotations
import io,json,math,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=Path("deploy/v27/ZONE47_REAL_ELEVATION_CANDIDATES.json")
WORLD=12800.
RASTER="https://dzpage.com/map3d-data/enoch/heightmap_gz.bin?v=18"
BOHEMIA="https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/master/dayzOffline.enoch/mapgrouppos.xml"
CATALOG="https://dzpage.com/map-editor-data/catalog.json?v=3"

def get(url,limit=30_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"BEILEYS47 elevation validation / noncommercial, read-only"})
    with urllib.request.urlopen(req,timeout=45) as response:
        data=response.read(limit+1)
    if len(data)>limit:raise ValueError("Source exceeds safe max size "+url)
    return data

def xyz(world_x,world_z,orientation,grid_factor,shape):
    axis,flr,flc=orientation
    r,c=(world_z,world_x) if axis=="zx" else (world_x,world_z)
    if flr:r=WORLD-r
    if flc:c=WORLD-c
    return (np.clip(np.asarray(r,dtype=float)*grid_factor,0,shape[0]-1),
            np.clip(np.asarray(c,dtype=float)*grid_factor,0,shape[1]-1))

def interp(grid,world_x,world_z,orientation,factor):
    row,col=xyz(world_x,world_z,orientation,factor,grid.shape)
    r0=np.floor(row).astype(np.intp);c0=np.floor(col).astype(np.intp)
    r1=np.minimum(r0+1,grid.shape[0]-1);c1=np.minimum(c0+1,grid.shape[1]-1)
    fr=row-r0;fc=col-c0
    return (grid[r0,c0]*(1-fr)*(1-fc)
          + grid[r1,c0]*fr*(1-fc)
          + grid[r0,c1]*(1-fr)*fc
          + grid[r1,c1]*fr*fc)

def inspect_catalog(raw,classes):
    obj=json.loads(raw)
    keys=set()
    def visit(o,d=0):
        if d>12:return
        if isinstance(o,dict):
            for k,v in o.items():
                if isinstance(v,str) and (v.startswith("Land_") or v.startswith("Static")):
                    keys.add(v)
                elif isinstance(v,(dict,list)):visit(v,d+1)
        elif isinstance(o,list):
            for v in o:visit(v,d+1)
    visit(obj)
    return {"total_detected_class_strings":len(keys),
      "candidate_matches":{c:c in keys for c in sorted(set(classes))},
      "catalog_json_type":type(obj).__name__,
      "catalog_note":"Class appearing in third-party catalogue is not PS5 runtime spawn proof"}

def main():
    report={"source_heightmap":RASTER,"official_group_source":BOHEMIA,
      "world":"DayZ Livonia", "read_only":True,"nitrado_modified":False,
      "server_wipe":False,"ps5_placement_tested":False,"all_features_complete":False}
    try:
        grid=np.load(io.BytesIO(get(RASTER)),allow_pickle=False)
        if grid.ndim!=2 or grid.shape[0]!=grid.shape[1] or grid.shape[0]<1000:
            raise ValueError("Unexpected Livonia heightmap array dimensions")
        if not np.isfinite(grid).all():raise ValueError("Nonfinite terrain values")
        report["raster"]={"shape":list(grid.shape),"dtype":str(grid.dtype),
            "min_y":round(float(np.min(grid)),3),"max_y":round(float(np.max(grid)),3)}
        xml=ET.fromstring(get(BOHEMIA,limit=5_000_000))
        known=[]
        for g in xml.findall("group"):
            a=g.get("pos","").split()
            if len(a)!=3:continue
            x,y,z=map(float,a)
            if 0<=x<=WORLD and 0<=z<=WORLD and math.isfinite(y):
                known.append((x,y,z))
        # deterministic fixed sample; buildings are elevated above ground by
        # a nonuniform foundation amount, so compare lower quantile AND median.
        known=known[::max(1,len(known)//1100)][:1100]
        x=np.array([p[0] for p in known]); z=np.array([p[2] for p in known])
        y=np.array([p[1] for p in known])
        comparisons=[]
        for orientation in (("zx",False,False),("zx",True,False),
             ("zx",False,True),("zx",True,True),
             ("xz",False,False),("xz",True,False),
             ("xz",False,True),("xz",True,True)):
            for factor_label,factor in (("N_over_world",grid.shape[0]/WORLD),
                          ("Nminus1_over_world",(grid.shape[0]-1)/WORLD)):
                h=interp(grid,x,z,orientation,factor)
                difference=np.abs(y-h)
                comparisons.append({"axis":orientation[0],"flip_row":orientation[1],
                  "flip_col":orientation[2],"factor_type":factor_label,
                  "median_abs_metres":round(float(np.median(difference)),3),
                  "p25_abs_metres":round(float(np.quantile(difference,.25)),3),
                  "p90_abs_metres":round(float(np.quantile(difference,.9)),3),
                  "mean_difference_y_minus_height":round(float(np.mean(y-h)),3)})
        comparisons.sort(key=lambda r:(r["p25_abs_metres"],r["median_abs_metres"]))
        report["calibration_top_6"]=comparisons[:6]
        report["vanilla_groups_compared"]=len(known)
        best=comparisons[0]
        # Need a robust separation from second most plausible physical axis,
        # rather than falsely claiming precision based on buildings' y.
        other=next((i for i in comparisons if
             (i["axis"],i["flip_row"],i["flip_col"])!=(best["axis"],best["flip_row"],best["flip_col"])),None)
        separation=other["median_abs_metres"]/max(.001,best["median_abs_metres"]) if other else 0
        report["orientation_separation_ratio"]=round(separation,2)
        report["orientation_confirmed_from_vanilla_objects"]=bool(separation>=2 and best["median_abs_metres"]<8.0)
        if not report["orientation_confirmed_from_vanilla_objects"]:
            raise ValueError("Terrain orientation not reliably calibrated to official object positions")
        orientation=(best["axis"],best["flip_row"],best["flip_col"])
        factor=grid.shape[0]/WORLD if best["factor_type"]=="N_over_world" else (grid.shape[0]-1)/WORLD
        layout=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text())
        roles=json.loads((ROOT/"config/stage4_10_placement_roles.json").read_text())["placement_options"]
        candidates=json.loads((ROOT/"config/stage4_centered_export_contract.json").read_text())["candidates"]
        layout_width=240
        layout_depth=220
        out=[]
        for site in candidates:
            cx,cz,angle=site["world_center_x"],site["world_center_z"],site["screened_orientation_degrees"]
            ct,st=math.cos(math.radians(angle)),math.sin(math.radians(angle))
            placements=[]
            for item in layout["asset_placements"]:
                dx=item["local_x"]-layout_width/2;dz=item["local_z"]-layout_depth/2
                xx=cx+ct*dx-st*dz;zz=cz+st*dx+ct*dz
                if xx<0 or xx>WORLD or zz<0 or zz>WORLD:raise ValueError("Candidate outside Livonia")
                ground=float(interp(grid,xx,zz,orientation,factor))
                # ±6 metre surrounding terrain sampled only to inform slope risk.
                heights=np.array([float(interp(grid,xx+dx,zz+dz,orientation,factor))
                  for dx,dz in [(-6,-6),(-6,0),(-6,6),(0,-6),(0,0),(0,6),(6,-6),(6,0),(6,6)]])
                role=roles.get(item["id"],{})
                placements.append({"id":item["id"],"visual_role":item["visual_role"],
                  "class_candidate_unverified":role.get("proposed_visual_model_classname"),
                  "x":round(xx,4),"terrain_y":round(ground,4),"z":round(zz,4),
                  "local_12m_ground_relief_m":round(float(np.max(heights)-np.min(heights)),3),
                  "ground_y_source":"DZPage public Livonia 2048² float32 game-derived raster",
                  "object_origin_y_not_determined":True,"ready_for_PS5_spawn":False})
            out.append({"region":site["region"],"center_x":cx,"center_z":cz,
                "rotation_degrees":angle,"placements":placements,
                "max_local_relief_12m":max(v["local_12m_ground_relief_m"] for v in placements),
                "median_local_relief_12m":round(float(np.median([v["local_12m_ground_relief_m"] for v in placements])),3),
                "terrain_only":True})
        report["candidate_sites"]=out
        names=[v["class_candidate_unverified"] for item in out[:1]
               for v in item["placements"] if v["class_candidate_unverified"]]
        try:report["dzpage_catalog_verification"]=inspect_catalog(get(CATALOG),names)
        except Exception as e:report["dzpage_catalog_error"]=str(e)[:230]
        report["exact_terrain_elevation_samples_count"]=sum(len(x["placements"]) for x in out)
        report["has_surface_y_samples"]=True
        report["site_ready_for_live_deploy"]=False
        report["remaining_reasons"]=[
         "Only 9/26 roles have candidate classnames; some may not be spawnable on PlayStation",
         "Object model origin/footprint and collision not proven by terrain Y",
         "Actual server still needs PS5 PS4 render and entrance/exit/performance tests",
         "Provider full persistence backup availability/recovery not verified"]
    except Exception as e:report["fatal_error"]=str(e)[:450]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    summary={k:v for k,v in report.items() if k!="candidate_sites"}
    if "candidate_sites" in report:
      summary["candidate_sites"]=[{k:v for k,v in s.items() if k!="placements"} for s in report["candidate_sites"]]
      summary["main_center_first_4"]=report["candidate_sites"][0]["placements"][:4]
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if "fatal_error" in report:raise SystemExit(1)
if __name__=="__main__":main()
