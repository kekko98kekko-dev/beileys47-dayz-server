#!/usr/bin/env python3
"""V47 independent, privacy-safe, GET-only examination after V46 rollback alert."""
import hashlib,json,os,posixpath,xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import resolve_mission,download_one,NitradoError
from deploy_beileys47_v15 import game_state,game_status,players
from v44_single_original_dolnik_truck import installed as truck_installed
from v45_safe_loot_ttl import patch as remaining_ttl_patch
FILES=("db/events.xml","cfgeventspawns.xml","cfgspawnabletypes.xml","db/types.xml")
OUT=Path("deploy/v47/POST_FAILURE_READONLY_STATE.json")
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 token=os.environ.get("NITRADO_API_TOKEN","").strip()
 if not token:raise NitradoError("Nitrado access not available")
 mission=resolve_mission(token)
 blobs={p:download_one(token,posixpath.join(mission,p)) for p in FILES}
 s=game_state(token)
 remote_ttl=sha(blobs["db/types.xml"])
 expected_original="3f329b028b49024a6f0dc42bd0d8f57a6628e23660ff8683a33e4edcf6086480"
 expected_modified="558998879030a36c183120f2dd0c8928b7d1d71ffaecf00f896f69bd9670a1a1"
 _,pending=remaining_ttl_patch(blobs["db/types.xml"])
 report={
  "mode":"V47 GET_ONLY_NO_CHANGES","server_status":game_status(s),
  "players_online":players(s),"mission_files":{p:{"sha256":sha(v),"size":len(v)} for p,v in blobs.items()},
  "v44_single_original_dolnik_ce_event_configured":truck_installed(blobs),
  "v45_ordinary_loot_items_still_eligible_for_4h_cap":len(pending),
  "v45_some_ordinary_loot_already_capped":len(pending)==0,
  "types_equals_pre_v46_backup":remote_ttl==expected_original,
  "types_equals_intended_v46_patched_bytes":remote_ttl==expected_modified,
  "world_vehicles_selectively_deleted":False,"actual_world_vehicle_count_unknown":True,
  "ps5_cargo_checked":False,"any_server_edit":False}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
