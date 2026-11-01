#!/usr/bin/env python3
"""Read extra DayZ PS files for V16 using Nitrado API, never writes to game server."""
import os,zipfile,json,hashlib
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,resolve_mission,download_one,NitradoError,call_api
extra = ["env/zombie_territories.xml","db/globals.xml","db/messages.xml",
         "cfgplayerspawnpoints.xml","cfgundergroundtriggers.json",
         "cfgeventgroups.xml","cfgEffectArea.json"]
token=os.getenv("NITRADO_API_TOKEN","").strip()
if not token:raise NitradoError("Nitrado secret missing")
root=resolve_mission(token)
out=Path("v16_extra/BEILEYS47_V16_EXTRA.zip")
out.parent.mkdir(parents=True,exist_ok=True)
manifest={"service":SERVICE_ID,"downloaded":[],"missing":[]}
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
  for rel in extra:
    try:
      data=download_one(token,root.rstrip("/")+"/"+rel)
      z.writestr("dayzOffline.enoch/"+rel,data)
      manifest["downloaded"].append({"file":rel,"size":len(data),"sha256":hashlib.sha256(data).hexdigest()})
      print("READ:",rel,len(data),"bytes")
    except NitradoError:
      manifest["missing"].append(rel)
      print("NOT FOUND:",rel)
  z.writestr("MANIFEST.json",json.dumps(manifest,indent=2))
assert any(x["file"]=="env/zombie_territories.xml" for x in manifest["downloaded"]), "Zombie territory data unavailable"
print("EXTRA V16 CONFIGS READY",len(manifest["downloaded"]))
