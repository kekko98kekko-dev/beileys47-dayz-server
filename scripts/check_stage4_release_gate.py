#!/usr/bin/env python3
"""Read-only monitor for DayZ public CE release tag and source drift.

Only proves source provenance; no provider/Game API access and no deployment.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/stage4_release_gate.json"
OUTPUT=ROOT/"dist/compatibility/stage4_release_gate_report.json"
API="https://api.github.com/repos/BohemiaInteractive/DayZ-Central-Economy/"

def get_json(url:str)->dict:
    if not url.startswith(API):raise ValueError("Only approved official CE API is allowed")
    headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"BEILEYS47-DayZ-ReadOnly-Baseline-Gate/1.0",
        "X-GitHub-Api-Version":"2022-11-28"
    }
    # GitHub Actions supplies its ephemeral, read-only token. Never print,
    # persist or publish it; the unauthenticated API limit is much lower.
    token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=45) as response:
            raw=response.read(1000001)
    except urllib.error.HTTPError as exc:
        if exc.code in (403,429):
            raise RuntimeError(
                "GitHub official CE API rate limited; source check NOT verified. "
                "Provide an ephemeral GITHUB_TOKEN through the CI environment."
            ) from None
        raise
    if len(raw)>1000000:raise ValueError("Oversized official API response")
    return json.loads(raw)

def build() -> dict:
    config_bytes=CONFIG.read_bytes()
    cfg=json.loads(config_bytes)
    assert cfg["kind"]=="OFFICIAL_MISSION_BASELINE_MONITOR"
    assert cfg["official_ce_repository"]=="BohemiaInteractive/DayZ-Central-Economy"
    assert cfg["official_baseline_release_tag"]=="DZ_130"
    assert cfg["stage"]==4 and cfg["map"]=="Livonia"
    assert cfg["target_game_build_verified_live"] is False
    assert cfg["platform_runtime_compatibility_confirmed"] is False
    assert cfg["nitrado_mission_files_verified"] is False and cfg["allow_install"] is False

    tag=get_json(API+"git/ref/tags/DZ_130")
    master=get_json(API+"commits/master")
    rel=get_json(API+"releases/tags/DZ_130")
    tag_sha=tag["object"]["sha"]
    current_sha=master["sha"]
    pinned=cfg["pinned_ce_commit"]
    if tag_sha != pinned:
        raise ValueError("OFFICIAL TAG DRIFT: current DZ_130 target changed; manual review required")
    if rel["tag_name"]!="DZ_130":
        raise ValueError("Unexpected official release tag")
    if rel["name"]!="Stable Update 1.30":
        raise ValueError("Official release label changed; manual review required")
    report={
      "stage":4,"kind":"SOURCE_PROVENANCE_ONLY_NO_RUNTIME_COMPATIBILITY",
      "status":"CURRENT_OFFICIAL_CE_STABLE_TAG_MATCHES_PINNED" if current_sha==pinned else "OFFICIAL_CE_MASTER_MOVED_REVIEW_REQUIRED",
      "pinned_ce_commit":pinned,
      "official_stable_tag":"DZ_130",
      "official_tag_commit_sha":tag_sha,
      "official_master_commit_sha":current_sha,
      "master_equal_to_pinned_tag":current_sha==pinned,
      "official_release_name":rel["name"],
      "official_release_published_at":rel.get("published_at"),
      "playstation_stable_version_from_manual_review":cfg["latest_official_playstation_stable_known_at_review"],
      "playstation_stable_release_date_from_manual_review":cfg["latest_official_playstation_stable_release_date"],
      "last_manual_review_date":cfg["review_date"],
      "project_gate_config_sha256":hashlib.sha256(config_bytes).hexdigest(),
      "actual_nitrado_server_version_checked":False,
      "live_ps4_ps5_compatibility_checked":False,
      "release_ready":False,
      "deploy_allowed":False,
      "human_checks_required":[
        "Compare exact Nitrado-hosted mission files after purchasing test capacity.",
        "Confirm actual server and PlayStation stable build currently running.",
        "Perform live gameplay tests including saving and restarting.",
        "Review changes if official master moved; never auto-upgrade pinned CE files."
      ]
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Official CE stable DZ_130={tag_sha}, master={current_sha}")
    print(f"PASS: version tag provenance. Deployment READY? {report['release_ready']}. Console runtime tested? NO.")
    if current_sha!=pinned:print("WARNING: official master has moved; review mission XML before any future release.")
    return report

if __name__=="__main__":build()
