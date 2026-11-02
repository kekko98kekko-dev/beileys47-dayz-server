#!/usr/bin/env python3
"""V49 one-shot closeout: install missing V37 military infected ZONA47 territories.

The owner authorizes ONE maintenance restart even with online players.
No wipe, no player/world-storage reads or writes, no types.xml edits.
No schedules/retries. Never equate a successful XML deploy with PS5 testing.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import posixpath
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from nitrado_snapshot import SERVICE_ID, resolve_mission, download_one, NitradoError, call_api
from deploy_beileys47_v15 import game_state, game_status, players, upload_file, request_api_post, wait_status
from v20_unlimited_sprint import setting_state
from v37_zone47_infected_patches import (
    FILE, EVENT, CFG, ZONES, PREVIOUS, patch, already_installed
)
from v48_build_anywhere_preview import BALANCED
from v36_nitrado_backups_readonly import analyze

OUT = Path("deploy/v49/LIVE_RESULT.json")
BACKUP = Path("deploy/v49/PRIVATE_ORIGINAL_INFECTED_ZONES.zip")
SPECIAL_SCENE = "custom/beileys47_v35_zone47_full_25.json"

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def need(test, error):
    if not test:
        raise NitradoError(error)

def emit(**kw):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "version": "V49", "platform": "DayZ PlayStation Livonia",
        "scope": "two vanilla infected territories ONLY",
        "world_storage_mutated": False, "wipe_performed": False,
        "types_xml_modified": False, "ps5_ai_tested": False,
        "scripted_roaming_hordes": False,
        **kw
    }
    OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("V49 status:", kw.get("status", "unknown"), flush=True)

def known_players(value):
    return type(value) is int and 0 <= value <= 10

def backup(original: bytes):
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BACKUP, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("dayzOffline.enoch/"+FILE, original)
        z.writestr("SHA256.txt", sha(original)+"  "+FILE+"\n")
    with zipfile.ZipFile(BACKUP) as z:
        need(z.testzip() is None and
             sha(z.read("dayzOffline.enoch/"+FILE)) == sha(original),
             "Original infected territories ZIP backup invalid")

def meaning(blob):
    def parse(node):
        return (node.tag, tuple(sorted(node.attrib.items())),
                (node.text or "").strip(), tuple(parse(x) for x in node))
    return parse(ET.fromstring(blob))

def world_feature_gate(gameplay):
    g = json.loads(gameplay)
    need(SPECIAL_SCENE in g.get("WorldsData", {}).get("objectSpawnersArr", []),
         "V35 25-prop ZONA47 scene missing")
    data = g.get("BaseBuildingData", {})
    for section, key in BALANCED:
        need(data.get(section, {}).get(key) is True,
             "V48 build permissions missing: "+section+"."+key)
    stamina = g.get("PlayerData",{}).get("StaminaData", {})
    for key in ("sprintStaminaModifierErc","sprintStaminaModifierCro",
                "staminaKgToStaminaPercentPenalty"):
        need(stamina.get(key) == 0, "V20 sprint config drift: "+key)
    return True

def provider_backups_available(token):
    """This is a presence check, NOT proof a restore would succeed."""
    inventory = call_api(token, f"/services/{SERVICE_ID}/gameservers/backups")
    available = call_api(token, f"/services/{SERVICE_ID}/gameservers/backups/restore_possible")
    status = analyze(inventory, available)
    need(status["provider_backup_exists"] and status["restore_possible"] is True,
         "Provider doesn't confirm existing restorable backup records")
    return status["backup_count"]

def server_state(token):
    gs = game_state(token)
    return game_status(gs), players(gs), setting_state(gs)

def main():
    token = os.getenv("NITRADO_API_TOKEN", "").strip()
    need(token and os.getenv("BEILEYS47_V49_APPROVED") == "yes"
         and os.getenv("BEILEYS47_V49_PLAYER_INTERRUPTION_APPROVED") == "yes",
         "Missing explicit owner approval / Nitrado secret")
    mission = resolve_mission(token)
    remote = posixpath.join(mission, FILE)
    original = download_one(token, remote)
    events = download_one(token, posixpath.join(mission, EVENT))
    gameplay = download_one(token, posixpath.join(mission, CFG))
    world_feature_gate(gameplay)
    if already_installed(original):
        emit(status="ALREADY_INSTALLED_NO_ACTION",
             original_sha=sha(original), no_restart=True)
        return
    candidate, before_count = patch(original, events)
    need(len(ZONES)==2 and len(ET.fromstring(candidate).findall(".//zone"))==before_count+2,
         "V37 patch shape invalid")
    need(not already_installed(original) and already_installed(candidate),
         "V37 idempotence gate failed")
    status, count, setting = server_state(token)
    if status not in ("started", "running") or not known_players(count) or setting!="enabled":
        emit(status="BLOCKED_STATE_NO_CHANGES",server_status=status,
             players_online=count,gameplay_enabled=setting)
        return
    # Ensure a known provider restore point is present; this is not a restore test.
    backup_count = provider_backups_available(token)
    time.sleep(2)
    again, second_count, second_setting = server_state(token)
    if again!=status or not known_players(second_count) or second_setting!="enabled":
        emit(status="BLOCKED_SECOND_STATUS_NO_CHANGES",
             server_status=again,players_online=second_count)
        return
    backup(original)
    emit(status="BACKUP_VERIFIED_PRE_STOP", original_sha=sha(original),
         proposed_sha=sha(candidate), provider_backup_records=backup_count,
         players_before_stop=second_count, player_interruption_authorized=True,
         previous_zone_count=before_count, proposed_new_zones=2)
    stopped = False
    restarted = False
    attempted_upload = False
    success = False
    try:
        request_api_post(token, f"/services/{SERVICE_ID}/gameservers/stop")
        stopped = True
        wait_status(token, {"stopped"}, attempts=55)
        # No concurrent edits to source or game feature baseline.
        need(sha(download_one(token,remote))==sha(original),
             "Infected zone source drift during stop")
        need(sha(download_one(token,posixpath.join(mission,CFG)))==sha(gameplay),
             "Gameplay changed during stop")
        attempted_upload=True
        upload_file(token,remote,candidate)
        uploaded = download_one(token,remote)
        need(meaning(uploaded)==meaning(candidate),
             "New infected XML did not survive upload semantically")
        request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
        wait_status(token,{"started","running"},attempts=55)
        restarted=True
        post=download_one(token,remote)
        need(meaning(post)==meaning(candidate),
             "Infected XML semantic drift after restart")
        need(already_installed(post),"Two V37 infected territories absent after restart")
        world_feature_gate(download_one(token,posixpath.join(mission,CFG)))
        need(game_status(game_state(token)) in ("started","running"),
             "Server did not return to online state")
        success=True
        emit(status="INSTALLED_AND_VERIFIED_POST_RESTART",
             original_sha=sha(original), live_sha=sha(post),
             new_sha=sha(candidate), raw_hash_equal=sha(post)==sha(candidate),
             original_zone_count=before_count,new_zone_count=2,
             added_zone_centers=[[v[1],v[2]] for v in ZONES],
             additional_dynamic_max=18,provider_backup_records=backup_count,
             server_status="started_or_running",players_before_stop=second_count,
             note="Game PS4/PS5 NavMesh and actual infected counts remain unverified")
    except Exception as problem:
        if attempted_upload and not success:
            try:
                current_status,current_count,_=server_state(token)
                if current_status in ("started","running"):
                    need(known_players(current_count),
                         "Unknown player count, no safe rollback")
                    request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
                    wait_status(token,{"stopped"},attempts=55)
                    stopped=True
                    restarted=False
                need(game_status(game_state(token))=="stopped",
                     "Unknown state; refuse rollback")
                current=download_one(token,remote)
                need(meaning(current)==meaning(candidate) or sha(current)==sha(original),
                     "Concurrent edits detected, refuse overwriting other administrator")
                if sha(current)!=sha(original):
                    upload_file(token,remote,original)
                    need(meaning(download_one(token,remote))==meaning(original),
                         "Rollback XML semantic mismatch")
                emit(status="ROLLED_BACK_AFTER_FAILURE",
                     original_sha=sha(original),error_type=type(problem).__name__)
            except Exception as recovery:
                emit(status="CRITICAL_MANUAL_RECOVERY_REQUIRED",
                     error_type=type(problem).__name__,
                     recovery_type=type(recovery).__name__)
                print("CRITICAL: verify Nitrado config, world and restart before editing.",flush=True)
        raise
    finally:
        if stopped and not restarted:
            try:
                request_api_post(token, f"/services/{SERVICE_ID}/gameservers/restart")
                wait_status(token, {"started","running"}, attempts=55)
                print("V49 safety restart confirmed",flush=True)
            except Exception:
                print("CRITICAL V49: restart confirmation missing, inspect Nitrado",flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("V49 ERROR",type(e).__name__,str(e)[:180],file=sys.stderr)
        if not OUT.exists():emit(status="FAILED_PRE_DEPLOYMENT")
        raise SystemExit(1)
