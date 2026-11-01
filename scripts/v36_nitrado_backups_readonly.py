#!/usr/bin/env python3
"""BEILEYS47 V36: Nitrado provider-hosted *full* backup availability read-only audit.

GET /services/{id}/gameservers/backups
GET /services/{id}/gameservers/backups/restore_possible
No user data, no credentials or backup IDs printed. Never restores or creates
backups. A list is NOT evidence that actual restored world state was tested.
"""
from __future__ import annotations
import json,os,sys
from pathlib import Path
from nitrado_snapshot import call_api,SERVICE_ID,NitradoError
OUT=Path("deploy/v36/PROVIDER_BACKUP_AVAILABILITY.json")
def analyze(backups_data,restore_data):
    assert isinstance(backups_data,dict),"Backup endpoint response not structured"
    inventory=backups_data.get("backups")
    # Do not treat success with an absent backups key as a nonempty backup list.
    if isinstance(inventory,list):
        count=len(inventory)
        formats=sorted(set(type(x).__name__ for x in inventory))
    elif isinstance(inventory,dict):
        count=len(inventory)
        formats=["dict"]
    else:
        count=None
        formats=[]
    enabled=None
    if isinstance(restore_data,bool):
        enabled=restore_data
    if isinstance(restore_data,dict):
        for key in ("restore_possible","restorePossible","possible","available"):
            if type(restore_data.get(key)) is bool:
                enabled=restore_data[key]
                break
    return {
       "backup_endpoint_responded":True,
       "backup_list_present":count is not None,
       "backup_count":count,
       "backup_container_types":formats,
       "restore_possible_endpoint_supported":restore_data is not None,
       "restore_possible":enabled,
       "provider_backup_exists":bool(count and count>0),
       "full_dayz_world_restore_tested":False,
       "restoration_executed":False,
       "restore_reliability_certified":False
    }
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Nitrado secret missing")
    out={"service_type":"DayZ PlayStation Livonia","mode":"PROVIDER_BACKUP_API_READ_ONLY",
       "player_data_accessed":False,"server_changed":False,
       "provider_restore_initiated":False,"full_world_restore_verified":False}
    backup_data={}
    restore_data=None
    try:
        backup_data=call_api(token,f"/services/{SERVICE_ID}/gameservers/backups")
        out["backups_endpoint_status"]="success"
    except NitradoError as e:
        out["backups_endpoint_status"]="unsupported_or_error"
        out["backups_endpoint_error_category"]=str(e)[:110]
    try:
        restore_data=call_api(token,f"/services/{SERVICE_ID}/gameservers/backups/restore_possible")
        out["restore_possible_endpoint_status"]="success"
    except NitradoError as e:
        out["restore_possible_endpoint_status"]="unsupported_or_error"
        out["restore_possible_error_category"]=str(e)[:110]
    out.update(analyze(backup_data,restore_data))
    out["backup_endpoint_responded"]=out["backups_endpoint_status"]=="success"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))
    if not out["provider_backup_exists"]:
        print("WARNING: Nitrado complete world restore point NOT confirmed. See panel Tools > Restore Backup.",file=sys.stderr)
if __name__=="__main__":
    main()
