#!/usr/bin/env python3
"""Adversarial checks for the six-file pre-purchase DayZ handoff.

Does NOT prove console compatibility or upload anything.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from build_prepurchase_bundle import ROOT,SOURCE,PACKAGE,REPORT,EXPECTED,clean_archive,validate_payload,build

def deny(fn,fragment:str)->None:
    try:fn()
    except (AssertionError,ValueError) as exc:
        assert fragment in str(exc),(fragment,str(exc))
    else:raise AssertionError("A prohibited preview was accepted: "+fragment)

def temp_zip(path:Path,entries:list[tuple[str,bytes]])->None:
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        for name,data in entries:z.writestr(name,data)

def test()->None:
    with zipfile.ZipFile(SOURCE) as z:
        correct=clean_archive(z,True)
        assert set(correct)==EXPECTED|{"change_report.json"}
        original=[(n,correct[n]) for n in sorted(correct)]
    report=build()
    assert report["mission_file_count"]==6
    assert report["source_stage"]==3
    assert report["has_console_runtime_test"] is False
    assert report["live_server_build_match"] is False
    assert report["provider_backup_availability_verified"] is False
    assert report["ready_to_deploy"] is False
    assert report["install_or_upload_performed"] is False
    assert report["contains_ZONA47_object_spawner"] is False
    assert len({p["mission_relative_path"] for p in report["mission_files"]})==6
    assert json.loads(REPORT.read_text(encoding="utf-8"))==report

    with zipfile.ZipFile(PACKAGE) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        assert len(names)==9 # 6 mission, README, report, SHA256
        assert "zone47_objects.json" not in names
        assert all(not n.endswith((".p3d",".RPT",".adm")) for n in names)
        assert len([n for n in names if n.startswith("MISSION_FILES_REVIEW_ONLY/")])==6
        assert b"DO NOT UPLOAD THIS ZIP" in z.read("READ_FIRST_NOT_INSTALLABLE.txt")
        manifest=json.loads(z.read("SHA256_MANIFEST.json"))
        assert set(manifest)==names-{"SHA256_MANIFEST.json"}
        for name,details in manifest.items():
            raw=z.read(name)
            assert hashlib.sha256(raw).hexdigest()==details["sha256"]
            assert len(raw)==details["bytes"]
        for original_name in EXPECTED:
            assert z.read("MISSION_FILES_REVIEW_ONLY/"+original_name)==correct[original_name]

    with tempfile.TemporaryDirectory(prefix="z47-prepurchase-fixture-") as tmp:
        d=Path(tmp)
        bad=dict(correct)
        gameplay=json.loads(bad["dayzOffline.enoch/cfggameplay.json"])
        gameplay["WorldsData"]["objectSpawnersArr"]=["custom/FAKE_zone47_objects.json"]
        bad["dayzOffline.enoch/cfggameplay.json"]=json.dumps(gameplay).encode()
        deny(lambda:validate_payload(bad),"objectSpawnersArr")
        wrong=dict(correct)
        parsed=json.loads(wrong["change_report.json"])
        parsed["stage"]=4
        wrong["change_report.json"]=json.dumps(parsed).encode()
        deny(lambda:validate_payload(wrong),"Wrong DayZ stage")
        duplicate=d/"duplicate.zip"
        temp_zip(duplicate,original+[original[0]])
        with zipfile.ZipFile(duplicate) as z:
            deny(lambda:clean_archive(z,True),"Unexpected, duplicate")
        traversal=d/"traversal.zip"
        temp_zip(traversal,original+[("../exploit.xml",b"<x/>")])
        with zipfile.ZipFile(traversal) as z:
            deny(lambda:clean_archive(z,True),"Unexpected, duplicate")
        malicious=dict(correct)
        malicious["dayzOffline.enoch/db/events.xml"]=b'<!DOCTYPE events [<!ENTITY data "inject">]><events/>'
        xml=d/"entities.zip"
        temp_zip(xml,list(malicious.items()))
        with zipfile.ZipFile(xml) as z:
            deny(lambda:clean_archive(z,True),"XML entities/DTD")
        paths=dict(correct)
        paths["arbitrary.json"]=b"{}"
        deny(lambda:validate_payload(paths),"Stage 3 preview membership")

    print("PASS: exact 6-file Stage 3 candidate bundle, no live spawner, no unsafe ZIP paths.")
    print("NO console, Nitrado, actual terrain height or release authorization asserted.")

if __name__=="__main__":test()
