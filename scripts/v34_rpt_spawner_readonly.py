#!/usr/bin/env python3
"""V34: read-only privacy-safe search for DayZ Object Spawner engine failures in RPT.

Never returns raw log lines, player identities or addresses. ADM is forbidden.
No RPT found means UNKNOWN, not proof that models spawned on PlayStation.
"""
from __future__ import annotations
import json,os,posixpath,re
from pathlib import Path
from nitrado_snapshot import SERVICE_ID,call_api,entries_at,is_dir,entry_name,download_one,NitradoError
OUT=Path("deploy/v34/RPT_ERROR_COUNTS_ONLY.json")
KNOWN=("Land_Mil_GuardBox_Green","Land_Mil_Barracks6_Old",
       "Land_Mil_GuardHouse3","Land_Container_1Bo",
       "Land_Mil_Fortified_Nest_Small")
def roots(token):
    meta=call_api(token,f"/services/{SERVICE_ID}/gameservers").get("gameserver",{})
    user=meta.get("username")
    if not isinstance(user,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,60}",user):
        raise NitradoError("Valid Nitrado path metadata not available")
    base=f"/games/{user}"
    return [base+"/ftproot/dayzps/logs",base+"/noftp/logs",
            base+"/ftproot/dayzps/config",base+"/ftproot/logs",
            base+"/ftproot/dayzstandalone/logs"]
def main():
    token=os.environ.get("NITRADO_API_TOKEN","").strip()
    if not token:raise NitradoError("Missing access token")
    result={"mode":"RPT_READ_ONLY_AGGREGATE","server_edits":0,
      "players_accessed":False,"adm_accessed":False,"raw_logs_published":False,
      "PS5_visual_tested":False,"rpt_files_scanned":0,"object_spawn_failures":0,
      "class_failure_mentions":{k:0 for k in KNOWN}}
    for base in roots(token):
        try:entries=entries_at(token,base)
        except NitradoError:continue
        rpt=[]
        for e in entries:
            if is_dir(e):continue
            n=entry_name(e)
            if re.fullmatch(r"[A-Za-z0-9_.-]{1,128}\.RPT",n,re.I):
                rpt.append(n)
        for name in sorted(set(rpt),reverse=True)[:2]:
            try:content=download_one(token,posixpath.join(base,name))
            except NitradoError:continue
            result["rpt_files_scanned"]+=1
            for line in content.decode("utf-8","replace").splitlines():
                if re.search(r"Object\s+spawner\s+failed\s+to\s+spawn",line,re.I):
                    result["object_spawn_failures"]+=1
                    for c in KNOWN:
                        if c.casefold() in line.casefold():result["class_failure_mentions"][c]+=1
        if result["rpt_files_scanned"]:break
    result["interpretation"]=(
        "Engine failures counted, NOT visual proof"
        if result["rpt_files_scanned"] else
        "No accessible RPT; object runtime status remains UNKNOWN")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
