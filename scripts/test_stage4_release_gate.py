#!/usr/bin/env python3
"""Tests for DayZ CE stable-tag provenance (not PlayStation runtime)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"dist/compatibility/stage4_release_gate_report.json"
CFG=ROOT/"config/stage4_release_gate.json"

def main()->None:
    r=json.loads(REPORT.read_text(encoding="utf-8"))
    cfg_bytes=CFG.read_bytes()
    cfg=json.loads(cfg_bytes)
    assert r["kind"]=="SOURCE_PROVENANCE_ONLY_NO_RUNTIME_COMPATIBILITY"
    assert r["stage"]==4
    assert r["official_stable_tag"]==cfg["official_baseline_release_tag"]
    assert r["pinned_ce_commit"]==cfg["pinned_ce_commit"]
    assert r["official_tag_commit_sha"]==r["pinned_ce_commit"]
    assert len(r["pinned_ce_commit"])==40
    assert r["master_equal_to_pinned_tag"] == (r["official_master_commit_sha"]==r["pinned_ce_commit"])
    if r["master_equal_to_pinned_tag"]:
        assert r["status"]=="CURRENT_OFFICIAL_CE_STABLE_TAG_MATCHES_PINNED"
    else:
        assert r["status"]=="OFFICIAL_CE_MASTER_MOVED_REVIEW_REQUIRED"
    assert r["project_gate_config_sha256"]==hashlib.sha256(cfg_bytes).hexdigest()
    assert r["actual_nitrado_server_version_checked"] is False
    assert r["live_ps4_ps5_compatibility_checked"] is False
    assert r["deploy_allowed"] is False and r["release_ready"] is False
    assert len(r["human_checks_required"])>=4
    print("PASS: stable-tag source provenance data consistent; NO PS5/Nitrado compatibility claim.")

if __name__=="__main__":main()
