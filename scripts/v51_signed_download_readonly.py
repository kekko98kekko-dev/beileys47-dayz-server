#!/usr/bin/env python3
"""V51: read-only Nitrado signed download diagnostic with longer 180s timeout.

No uploads, restarts, wipes, persistence reads, token logging, signed URL logging.
Compare one problem XML with known readable JSON only if XML succeeds. 1 attempt
per file so a hung provider cannot cause unbounded retries.
"""
from __future__ import annotations
import datetime
import hashlib
import json
import os
import posixpath
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, call_api, resolve_mission, entries_at, entry_name, NitradoError

MAX_BYTES=16*1024*1024
LONG_TIMEOUT_SECONDS=180
OUT=Path("deploy/v51/NITRADO_DOWNLOAD_DIAGNOSIS.json")
TARGETS=("env/zombie_territories.xml","cfggameplay.json")

def validate_address(address, ephemeral_token):
    if not isinstance(address,str) or not isinstance(ephemeral_token,str) or not ephemeral_token:
        raise NitradoError("Missing signed download address or ephemeral token")
    parsed=urllib.parse.urlsplit(address)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        raise NitradoError("Nitrado returned unsafe signed download address")
    query=urllib.parse.parse_qsl(parsed.query,keep_blank_values=True)
    query.append(("token",ephemeral_token))
    return urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,parsed.path,
        urllib.parse.urlencode(query),parsed.fragment))

def download_probe(token, remote):
    started=time.monotonic()
    ticket=call_api(token,f"/services/{SERVICE_ID}/gameservers/file_server/download",{"file":remote}).get("token") or {}
    ticket_seconds=round(time.monotonic()-started,2)
    url=validate_address(ticket.get("url"),ticket.get("token"))
    request=urllib.request.Request(url,headers={
        "User-Agent":"BEILEYS47-V51-readonly-download-diagnostics/1.0",
        "Accept":"application/octet-stream"})
    fetch_started=time.monotonic()
    info={"token_ticket_seconds":ticket_seconds,"timeout_seconds":LONG_TIMEOUT_SECONDS}
    try:
        with urllib.request.urlopen(request,timeout=LONG_TIMEOUT_SECONDS) as resp:
            info["time_to_headers_seconds"]=round(time.monotonic()-fetch_started,2)
            data=resp.read(MAX_BYTES+1)
            info["total_download_seconds"]=round(time.monotonic()-fetch_started,2)
        if len(data)>MAX_BYTES:
            raise NitradoError("Payload exceeded 16MB maximum")
        info.update(status="success",bytes_downloaded=len(data),
                    sha256=hashlib.sha256(data).hexdigest())
    except urllib.error.HTTPError as exc:
        info.update(status="http_error",http_status=exc.code,
                    elapsed_seconds=round(time.monotonic()-fetch_started,2))
    except (urllib.error.URLError, TimeoutError) as exc:
        info.update(status="connection_error",
                    error_class=type(exc).__name__,
                    elapsed_seconds=round(time.monotonic()-fetch_started,2))
    except NitradoError as exc:
        info.update(status="payload_too_large",elapsed_seconds=round(time.monotonic()-fetch_started,2))
    return info

def file_metadata(token, mission, rel):
    try:
        folder,name=posixpath.split(posixpath.join(mission,rel))
        entry=next((v for v in entries_at(token,folder) if entry_name(v)==name),None)
        if not entry:
            return {"listed":False,"size_bytes":None}
        for key in ("size","size_bytes","filesize"):
            size=entry.get(key)
            if isinstance(size,(int,float)) and not isinstance(size,bool) and 0<=size<10000000000:
                return {"listed":True,"size_bytes":int(size)}
        return {"listed":True,"size_bytes":None}
    except Exception:
        return {"listed":"unavailable","size_bytes":None}

def main():
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    if not token:
        raise NitradoError("Nitrado API secret not available in Actions")
    result={"stage":"V51","mode":"GET_ONLY","file_operations":["list","download"],
       "remote_changes":False,"restart":False,"wipe":False,"player_storage_read":False,
       "seconds_per_file_timeout":LONG_TIMEOUT_SECONDS,
       "started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "files":{}}
    try:
        mission=resolve_mission(token)
        print("V51 mission located by authenticated metadata; no token/URLs printed",flush=True)
        for rel in TARGETS:
            result["files"][rel]={"metadata":file_metadata(token,mission,rel)}
            print("V51 attempting signed download",rel,"size metadata",
                  result["files"][rel]["metadata"]["size_bytes"],flush=True)
            result["files"][rel]["download"]=download_probe(token,posixpath.join(mission,rel))
            result["files"][rel]["download"]["token_ticket_seconds"]=result["files"][rel]["download"].get("token_ticket_seconds")
            status=result["files"][rel]["download"]["status"]
            print("V51 result",rel,status,
                  "elapsed_seconds",result["files"][rel]["download"].get("elapsed_seconds",
                                            result["files"][rel]["download"].get("total_download_seconds")),flush=True)
            # First failed XML test is sufficient evidence of link failure; no second 180s hang.
            if status!="success":break
    except Exception as exc:
        result["probe_error"]={"class":type(exc).__name__}
        print("V51 read-only diagnostic failed before successful transfer:",type(exc).__name__,flush=True)
    finally:
        result["completed_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if len(result["files"])==2 and all(
       item.get("download",{}).get("status")=="success" for item in result["files"].values()):
        print("V51 GOOD: both signed file transfers succeeded at <=180s timeout",flush=True)
    else:
        print("V51 CHECK REQUIRED: download did not complete. No Nitrado writes were attempted.",flush=True)
if __name__=="__main__":main()
