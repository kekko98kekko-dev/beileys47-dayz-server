#!/usr/bin/env python3
"""Prepare a purchase-day handoff from the already audited Livonia Stage 3 preview.

This is a REVIEW CANDIDATE, never a confirmed console release. No upload,
network access, passwords, actual world heights, or ZONA47 Object Spawner.
"""
from __future__ import annotations

import hashlib
import json
import stat
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

from build_mission import UPSTREAM_COMMIT
from build_stage3 import STAGE3_FILES
from build_stage4_13_console_pilot import PROTOCOL

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"dist/stage3/beileys47-livonia-stage3-preview.zip"
OUT=ROOT/"dist/prepurchase"
PACKAGE=OUT/"beileys47-livonia-mission-review-candidate.zip"
REPORT=OUT/"purchase_day_gate.json"
EXPECTED=set("dayzOffline.enoch/"+p for p in STAGE3_FILES)
MAX_SINGLE_BYTES=3_000_000

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def clean_archive(z:zipfile.ZipFile,source:bool)->dict[str,bytes]:
    infos=z.infolist()
    members=[i.filename for i in infos]
    expected=EXPECTED|({"change_report.json"} if source else set())
    if len(members)!=len(set(members)) or set(members)!=expected:
        raise ValueError("Unexpected, duplicate or missing Stage 3 mission members")
    data={}
    for inf in infos:
        path=PurePosixPath(inf.filename)
        if inf.is_dir() or path.is_absolute() or ".." in path.parts or "\\" in inf.filename:
            raise ValueError("Unsafe mission archive path")
        if (inf.external_attr >> 16)&0o170000==stat.S_IFLNK:
            raise ValueError("ZIP symlinks forbidden")
        if inf.file_size>MAX_SINGLE_BYTES:
            raise ValueError("Oversized mission file")
        raw=z.read(inf)
        if len(raw)!=inf.file_size:
            raise ValueError("Truncated mission member")
        if inf.filename.endswith(".xml"):
            if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                raise ValueError("XML entities/DTD forbidden")
            ET.fromstring(raw)
        if inf.filename.endswith(".json"):
            json.loads(raw.decode("utf-8-sig"))
        data[inf.filename]=raw
    return data

def validate_payload(source_members:dict[str,bytes])->dict:
    if set(source_members)!=EXPECTED|{"change_report.json"}:
        raise ValueError("Stage 3 preview membership changed")
    report=json.loads(source_members["change_report.json"])
    if report.get("stage")!=3 or report.get("pinned_commit")!=UPSTREAM_COMMIT:
        raise ValueError("Wrong DayZ stage or Bohemia pinned version")
    if report.get("status")!="PREVIEW ONLY - NO NITRADO DEPLOY / NO PLAYSTATION TEST":
        raise ValueError("Dangerous preview claim")
    gameplay=json.loads(source_members["dayzOffline.enoch/cfggameplay.json"])
    worlds=gameplay.get("WorldsData")
    if not isinstance(worlds,dict) or worlds.get("objectSpawnersArr")!=[]:
        raise ValueError("ZONA47 must remain disabled: objectSpawnersArr must be empty")
    if gameplay["GeneralData"]["disableBaseDamage"] is not False:
        raise ValueError("Unreviewed base invulnerability")
    if gameplay["GeneralData"]["disableContainerDamage"] is not False:
        raise ValueError("Unreviewed container invulnerability")
    if "base" not in str(report.get("notes","")).lower() and not report.get("event_changes"):
        raise ValueError("Stage 3 report missing changes")
    return report

def build(source_zip:Path=SOURCE,output:Path=PACKAGE)->dict:
    with zipfile.ZipFile(source_zip,"r") as z:
        source_members=clean_archive(z,True)
    stage_report=validate_payload(source_members)
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if protocol["stage"]!="4.13" or protocol["safety"]["automatic_deployment_allowed"] is not False:
        raise ValueError("Pilot gate must remain disabled")
    rawfiles={k:v for k,v in source_members.items() if k!="change_report.json"}
    files=[{
        "mission_relative_path":p.removeprefix("dayzOffline.enoch/"),
        "sha256":sha(rawfiles[p]),
        "size_bytes":len(rawfiles[p]),
        "action":"REVIEW_VERSION_AND_BACKUP_BEFORE_OPTIONAL_MANUAL_UPLOAD"
    } for p in sorted(rawfiles)]
    assert len(files)==6 and len({x["mission_relative_path"] for x in files})==6
    report={
        "project":"BEILEYS47 | DAYZ SURVIVAL WAR",
        "stage":"PREPURCHASE-MASTER",
        "status":"REVIEWED_OFFLINE_FILES_NOT_CONSOLE_VERIFIED",
        "target_map":"Livonia","target_platform":"PlayStation",
        "source_stage":3,"source_baseline_commit":UPSTREAM_COMMIT,
        "source_preview_sha256":sha(source_zip.read_bytes()),
        "mission_relative_paths_are_NOT_verified_Nitrado_paths":True,
        "mission_file_count":len(files),
        "mission_files":files,
        "contains_ZONA47_object_spawner":False,
        "has_real_world_terrain_y":False,
        "has_console_runtime_test":False,
        "live_server_build_match":False,
        "provider_backup_availability_verified":False,
        "console_classes_verified":False,
        "server_mission_root":None,
        "install_or_upload_performed":False,
        "ready_to_deploy":False,
        "provisional_install_order":[
            "A. Vanilla: start original Livonia server; establish console connectivity",
            "B. Snapshot: verify available provider backup and download original six mission files privately",
            "C. Verify build and changes; test Stage 1 first, then Stage 2, then Stage 3",
            "D. For each stage: stop server, replace ONLY reviewed file paths, enable cfggameplay if needed, restart, inspect gameplay and persistence",
            "E. Stage 4/ZONA47 separate: must acquire real Y, valid spawner classnames, collision and PS5 evidence; NEVER install this planning material"
        ],
        "manual_go_no_go":[
            "Owner approved server maintenance and chose exact Livonia mission root",
            "Current console and pinned Bohemia CE baseline compatibility checked",
            "Downloaded real target files and kept independent private backups",
            "Nitrado Tools > Restore Backup shows an actual usable prior backup",
            "Understand restore can roll back player progress and may change IP",
            "Server stopped, no players online, mission file modification rights confirmed",
            "cfggameplay.json enabled in Nitrado General settings for Stage 2/3",
            "Stage 1 and Stage 2 actual PS5 smoke tests passed before Stage 3",
            "Errors/log observations and rollback plan recorded privately"
        ],
        "source_reference_docs":[
            "https://community.bistudio.com/wiki/DayZ:Gameplay_Settings",
            "https://community.bistudio.com/wiki/DayZ:Object_Spawner",
            "https://server.nitrado.net/en-US/guides/settings-dayz-console/",
            "https://server.nitrado.net/en-US/guides/backup%20restore%20on%20dayz"
        ],
        "warning":"OFFLINE ZIP CONTENTS ONLY. It is NOT a DayZ modpack, not a console-validated deployment, not a live server backup and NOT an automatically installable package."
    }
    package_readme=(
        "BEILEYS47 LIVONIA -- PURCHASE-DAY FILE REVIEW CANDIDATE\n\n"
        "MISSION-FILES/ contains exactly SIX candidate Stage 3 mission files built from pinned Bohemia CE.\n"
        "DO NOT UPLOAD THIS ZIP: only transfer individual files to matching paths AFTER VERSION REVIEW,\n"
        "BACKUP, APPROVAL and staged PS5 tests. This package has NO ZONA47 spawner or real terrain Y.\n"
        "Stage 1 and Stage 2 previews should be installed and tested before Stage 3, not all at once.\n"
        "The root server mission folder depends on what Nitrado actually exposes: VERIFY IT.\n"
        "Do NOT replace mission files with an unreviewed game version or touch world persistence.\n"
        "Opening the generated JSON manifest does not authorize uploading anything.\n"
    ).encode("utf-8")
    entries={
        "READ_FIRST_NOT_INSTALLABLE.txt":package_readme,
        "purchase_day_gate.json":(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    }
    for name,raw in rawfiles.items():
        entries["MISSION_FILES_REVIEW_ONLY/"+name]=raw
    checksum={name:{"sha256":sha(raw),"bytes":len(raw)} for name,raw in sorted(entries.items())}
    entries["SHA256_MANIFEST.json"]=(json.dumps(checksum,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as z:
        for name,payload in sorted(entries.items()):z.writestr(name,payload)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None and set(z.namelist())==set(entries)
        verify=json.loads(z.read("SHA256_MANIFEST.json"))
        for name,detail in verify.items():
            raw=z.read(name)
            assert sha(raw)==detail["sha256"] and len(raw)==detail["bytes"]
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PASS: six exact Stage 3 candidate mission files, no ZONA 47 objects, no auto-install.")
    print("Status: NOT console verified. Manual version check and staged testing still mandatory.")
    return report

if __name__=="__main__":build()
