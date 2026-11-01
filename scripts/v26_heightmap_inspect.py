#!/usr/bin/env python3
"""Read only: investigate public Livonia terrain heightmap file encoding.

No Nitrado APIs, game server write, credentials, player data or distribution of
raw proprietary heightfield. Persist numeric diagnostics only.
"""
from __future__ import annotations
import gzip,io,json,math,struct,urllib.request,zlib
from pathlib import Path

URL="https://dzpage.com/map3d-data/enoch/heightmap_gz.bin?v=18"
CHUNKS="https://dzpage.com/map3d-data/enoch/chunks.json?v=18"
OUT=Path("deploy/v26/HEIGHT_ENCODING_DIAGNOSTIC.json")
MAX=200_000_000
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"BEILEYS47 terrain-research / read-only"})
    with urllib.request.urlopen(req,timeout=40) as f:
        raw=f.read(MAX+1)
    if len(raw)>MAX:raise ValueError("Public raster too large for safe inspection")
    return raw
def summarize(raw):
    r={"raw_bytes":len(raw),"raw_head_hex":raw[:48].hex(),
       "gzip_header":raw[:2]==b"\x1f\x8b"}
    for typ,fn in (("gzip",gzip.decompress),("zlib",zlib.decompress)):
        try:
            b=fn(raw)
            if len(b)>MAX:raise ValueError("Decompressed binary too large")
            r.update({"decode":typ,"decompressed_bytes":len(b),
              "decompressed_first_64_hex":b[:64].hex(),
              "decompressed_first_64_text":"".join(chr(x) if 32<=x<127 else "." for x in b[:64])})
            for num in (1,2,4,8,12,16,32,64):
                size=(len(b)-num)
                for unit in (2,4,8):
                    side=round(math.sqrt(size/unit)) if size>=0 else 0
                    if abs(side*side*unit-size)<64:
                        r.setdefault("possible_grids",[]).append({
                          "header_bytes":num,"bytes_per_sample":unit,"side":side,
                          "remainder":size-side*side*unit})
            if len(b)>=32:
                r["first_8_u32_le"]=list(struct.unpack("<8I",b[:32]))
                r["first_8_f32_le"]=[
                  round(x,5) if math.isfinite(x) else str(x)
                  for x in struct.unpack("<8f",b[:32])]
            # deterministic sparse test of candidate float32 sample plausibility
            for offset in (0,4,8,12,16,32,64):
                count=(len(b)-offset)//4
                if count<1024:continue
                indices=[(count-1)*i//31 for i in range(32)]
                vals=[struct.unpack_from("<f",b,offset+i*4)[0] for i in indices]
                plausible=[v for v in vals if math.isfinite(v) and -500<v<1500]
                r.setdefault("float32_plausibility",[]).append({
                 "header":offset,"fraction":round(len(plausible)/len(vals),3),
                 "min":round(min(plausible),3) if plausible else None,
                 "max":round(max(plausible),3) if plausible else None})
            return r
        except Exception as e:r[typ+"_decode_error"]=str(e)[:120]
    r["decode"]="none"
    return r
def main():
    out={"source":"DZPage public Livonia Enoch game map heightmap",
      "nitrado_modified":False,"source_url":URL,
      "validated_26_height_samples":False,"elevations_claimed":False}
    try:out["raster"]=summarize(get(URL))
    except Exception as e:out["raster_error"]=str(e)[:280]
    try:
        c=json.loads(get(CHUNKS))
        out["chunk_manifest_type"]=type(c).__name__
        if isinstance(c,dict):
            out["chunk_manifest_keys"]=list(c)[:35]
            out["chunk_manifest_preview"]={k:str(v)[:350] for k,v in list(c.items())[:8]}
        elif isinstance(c,list):
            out["chunk_manifest_list_length"]=len(c)
            out["chunk_manifest_preview"]=str(c[:2])[:800]
    except Exception as e:out["chunks_error"]=str(e)[:180]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
