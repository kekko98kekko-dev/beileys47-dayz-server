#!/usr/bin/env python3
"""Static evidence check for proposed ZONA 47 *candidate* asset names.

A name appearing in mapgrouppos.xml does NOT prove it is spawnable through
Object Spawner on console, collision-safe, or performant. No game upload.
"""
from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/stage4_asset_candidates.json"
OUT = ROOT / "dist/stage4/asset_evidence.json"
COMMIT = "f220b2918b1d79a5055b1ee9be70c0ec1516e876"
URL = (
    "https://raw.githubusercontent.com/BohemiaInteractive/"
    f"DayZ-Central-Economy/{COMMIT}/dayzOffline.enoch/mapgrouppos.xml"
)

def audit() -> None:
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    assert cfg["status"]=="CANDIDATE_CLASS_NAMES_ONLY_NOT_RUNTIME_VERIFIED"
    assert cfg["pinned_commit"]==COMMIT
    assert cfg["stage"]==4 and cfg["codename"]=="ZONA 47"
    models=cfg["models"]
    assert 5<=len(models)<=40
    assert len({model["name"] for model in models})==len(models)
    assert all(model["object_spawner_confirmed"] is False and model["ps4_ps5_runtime_confirmed"] is False for model in models)
    assert all(model["ground_elevation_known"] is False for model in models)

    req=urllib.request.Request(URL,headers={"User-Agent":"BEILEYS47-ZONA47-Audit/1.0"})
    with urllib.request.urlopen(req,timeout=45) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000 or b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("Unsafe official map groups document")
    root=ET.fromstring(raw)
    assert root.tag=="map"
    counts=Counter(node.get("name") for node in root.findall("group"))
    missing=sorted(m["name"] for m in models if m["name"] not in counts)
    if missing:
        raise AssertionError(f"Candidate classes absent from pinned Livonia mapgrouppos.xml: {missing}")
    report={
        "stage":4,
        "status":"SOURCE_NAME_PRESENCE_ONLY_NOT_OBJECT_SPAWNER_CERTIFICATION",
        "origin":cfg["source"],
        "commit":COMMIT,
        "candidates": [
            {"name":m["name"],"source_map_group_instances":counts[m["name"]],"runtime_verified":False}
            for m in models
        ],
        "limitations":[
            "No proof of console Object Spawner compatibility.",
            "No world anchor/terrain-height or slope verification.",
            "No in-game collision, visibility or FPS tests.",
            "Existing map placement is not permission to reuse a class on Nitrado."
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"PASS: {len(models)} candidate identifiers found in pinned official Livonia map groups.")
    print("NOT VERIFIED: Object Spawner support, PlayStation runtime, terrain fit or FPS.")

if __name__=="__main__":
    audit()
