#!/usr/bin/env python3
"""Create a Nitrado *offline* installation preflight from a checked DayZ ZIP.

This script has NO networking and NO upload/restart/deletion capabilities.
It intentionally omits Nitrado host paths, credentials and API assumptions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from check_release import verify

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = ROOT / "dist/stage2/beileys47-livonia-stage2-preview.zip"
DEFAULT_OUT = ROOT / "dist/stage2/nitrado_dry_run_plan.json"
RELATIVE_FILES = (
    "db/types.xml",
    "cfgplayerspawnpoints.xml",
    "cfgspawnabletypes.xml",
    "cfggameplay.json",
)


def build_plan(preview_zip: Path, destination: Path) -> dict:
    verify(str(preview_zip))
    with zipfile.ZipFile(preview_zip) as archive:
        report = json.loads(archive.read("change_report.json"))
        if report["stage"] != 2 or "PREVIEW ONLY" not in report["status"]:
            raise ValueError("Not a valid Stage 2 preview")
        files = []
        for relative in RELATIVE_FILES:
            entry = "dayzOffline.enoch/" + relative
            raw = archive.read(entry)
            files.append({
                "mission_relative_path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
                "action": "replace_this_single_file_only_after_backup_and_authorization",
            })

    plan = {
        "project": "BEILEYS47 | DAYZ SURVIVAL WAR",
        "plan_type": "STATIC_OFFLINE_PREFLIGHT",
        "server_kind": "DayZ PlayStation PS4/PS5 (proposed; NOT verified)",
        "map": "Livonia",
        "target_slots": 10,
        "ready_to_deploy": False,
        "deployment_performed": False,
        "server_mission_root": None,
        "deployment_credentials": None,
        "official_baseline_commit": report["pinned_commit"],
        "files_for_potential_manual_upload": files,
        "never_upload": ["change_report.json", "nitrado_dry_run_plan.json"],
        "required_before_any_actual_deployment": [
            "Explicit owner approval for live deployment",
            "Purchased and running Nitrado PlayStation server on Livonia",
            "Verified exact server version against pinned Bohemia baseline",
            "Verified actual mission root inside the Nitrado console panel",
            "Reviewed original live files and created copies/backups",
            "Successful Stage 1 PS5 smoke test before introducing Stage 2",
            "Confirmed cfggameplay.json switch is available and enabled",
            "Planned maintenance window with no players online",
            "Documented manual rollback and checked backup availability",
        ],
        "warning": (
            "NOT A DEPLOYMENT SCRIPT. Do not use this plan as evidence of "
            "PlayStation compatibility, gameplay balance or persisted world backups."
        ),
    }
    if len(files) != 4 or not all(len(x["sha256"]) == 64 for x in files):
        raise AssertionError("Invalid installation manifest")
    if plan["ready_to_deploy"] or plan["server_mission_root"] is not None:
        raise AssertionError("Unsafe deployment state")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    # Read-back ensures all entries survived serialization.
    if json.loads(destination.read_text(encoding="utf-8")) != plan:
        raise AssertionError("Written plan differs from the validated plan")
    print(f"PASS: static, read-only Nitrado preflight created: {destination}")
    print("NO API requests, uploads, restarts, deletions or PS5 runtime tests.")
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    build_plan(args.zip, args.output)
