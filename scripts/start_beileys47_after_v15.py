#!/usr/bin/env python3
"""One-shot, guarded Nitrado start following the verified BEILEYS47 V15 upload.

Only administrative action: POST /gameservers/restart if the server is stopped.
No configuration writes, player-data access, persistence wipe, or reinstall.
"""
import json
import os
import sys
import time
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, NitradoError
from deploy_beileys47_v15 import game_state, game_status, request_api_post

ROOT = Path(__file__).resolve().parents[1]
DEPLOY_STATUS = ROOT / "deploy/v15/DEPLOY_RESULT.json"
START_STATUS = ROOT / "deploy/v15/START_RESULT.json"
SUCCESS = False

def save(**values):
    START_STATUS.parent.mkdir(parents=True, exist_ok=True)
    data={"service_id": SERVICE_ID, "version": "V15", "ps5_runtime_tested": False,
          "wipe_performed": False, **values}
    START_STATUS.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")

def run():
    data=json.loads(DEPLOY_STATUS.read_text(encoding="utf-8"))
    if data.get("service_id") != SERVICE_ID or not data.get("deployment_confirmed_by_workflow"):
        raise NitradoError("V15 file uploads not confirmed; refusing to start.")
    token=os.getenv("NITRADO_API_TOKEN","").strip()
    if not token:
        raise NitradoError("GitHub secret NITRADO_API_TOKEN missing.")
    if os.getenv("BEILEYS47_START_APPROVED") != "yes":
        raise NitradoError("Owner approval not configured.")

    before=game_status(game_state(token))
    print("DayZ service before start:", before, flush=True)
    if before in {"started","running"}:
        save(status="already_running", final_state=before, restart_requested=False,
             running_confirmed=True)
        print("Game already running. No restart performed.",flush=True)
        return
    if before != "stopped":
        raise NitradoError("Unexpected DayZ service status; no restart: "+before)

    print("V15 uploads verified and service is stopped. Requesting Nitrado restart/start.",flush=True)
    request_api_post(token, f"/services/{SERVICE_ID}/gameservers/restart")
    save(status="restart_requested", restart_requested=True, running_confirmed=False)
    for step in range(30):
        time.sleep(6)
        current=game_status(game_state(token))
        if current in {"started","running"}:
            save(status="running", final_state=current,
                 restart_requested=True, running_confirmed=True)
            print("NITRADO STATUS CONFIRMED:",current,flush=True)
            return
        if step in {0, 5, 10, 20, 29}:
            print("Nitrado reports:",current,flush=True)
    raise NitradoError("Nitrado accepted restart but running state not confirmed in polling window.")

if __name__=="__main__":
    try:
        run()
    except Exception as exc:
        print("START CHECK ERROR:",str(exc)[:240],file=sys.stderr)
        # Keep the restart-requested report if a POST was accepted.
        if not START_STATUS.exists():
            save(status="failed_before_restart", error=type(exc).__name__,
                 restart_requested=False, running_confirmed=False)
        sys.exit(1)
