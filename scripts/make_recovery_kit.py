#!/usr/bin/env python3
"""Produce a portable, static disaster-recovery ZIP for BEILEYS47.

Contains the complete versioned source needed to rebuild previews and the
current preview builds. No Nitrado access, no credentials, no live game saves.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "beileys47-recovery-kit.zip"

SOURCE_PATHS = [
    ".github/workflows/validate.yml",
    ".github/workflows/recovery-release.yml",
    ".gitignore",
    "README.md",
    "NEXT_STEPS.md",
    "config/profile.json",
    "config/stage1_rules.json",
    "config/stage2_rules.json",
    "config/stage3_rules.json",
    "config/stage4_zone47_blueprint.json",
    "config/stage4_site_screening_rules.json",
    "config/stage4_footprint_rules.json",
    "config/stage4_release_gate.json",
    "config/stage4_centered_export_contract.json",
    "config/stage4_asset_candidates.json",
    "config/stage4_zone47_micro_layout.json",
    "docs/OPERATIONS.md",
    "docs/STAGE1.md",
    "docs/STAGE2.md",
    "docs/STAGE3.md",
    "docs/STAGE4_ZONE47.md",
    "docs/STAGE4_SITE_SCREEN.md",
    "docs/STAGE4_FOOTPRINT.md",
    "docs/STAGE4_RELEASE_COMPATIBILITY.md",
    "docs/STAGE4_TERRAIN_SURVEY.md",
    "docs/STAGE4_REAL_ALTITUDE.md",
    "docs/STAGE4_6_SPAWNER_PREFLIGHT.md",
    "docs/STAGE4_SITE_SHORTLIST.md",
    "docs/ZONE47_QA_PROTOCOL.md",
    "docs/RECOVERY_KIT.md",
    "docs/RELEASE_SNAPSHOT.md",
    "mission/README.md",
    "scripts/audit_stage2.py",
    "scripts/build_mission.py",
    "scripts/build_stage2.py",
    "scripts/build_stage3.py",
    "scripts/build_stage4_concept.py",
    "scripts/scan_stage4_sites.py",
    "scripts/test_stage4_sites.py",
    "scripts/assess_stage4_footprints.py",
    "scripts/test_stage4_footprints.py",
    "scripts/build_stage4_terrain_survey_grid.py",
    "scripts/test_stage4_terrain_grid.py",
    "scripts/prepare_stage4_height_capture.py",
    "scripts/audit_stage4_height_samples.py",
    "scripts/test_stage4_height_samples.py",
    "scripts/build_stage4_surfacey_snippet.py",
    "scripts/import_stage4_surfacey_log.py",
    "scripts/test_stage4_surfacey_capture.py",
    "scripts/build_stage4_6_pilot_preflight.py",
    "scripts/test_stage4_6_pilot_preflight.py",
    "scripts/check_stage4_release_gate.py",
    "scripts/test_stage4_release_gate.py",
    "scripts/audit_stage4_assets.py",
    "scripts/prepare_zone47_survey.py",
    "scripts/export_zone47_spawner.py",
    "scripts/test_zone47_export_safety.py",
    "scripts/check_release.py",
    "scripts/make_recovery_kit.py",
    "scripts/plan_nitrado.py",
    "scripts/test_stage2.py",
    "scripts/test_stage3.py",
    "scripts/validate.py",
]
PREVIEW_PATHS = [
    "dist/stage1/beileys47-livonia-stage1.zip",
    "dist/stage1/change_report.json",
    "dist/stage2/beileys47-livonia-stage2-preview.zip",
    "dist/stage2/change_report.json",
    "dist/stage2/nitrado_dry_run_plan.json",
    "dist/stage3/beileys47-livonia-stage3-preview.zip",
    "dist/stage3/change_report.json",
    "dist/stage4/beileys47-zone47-design-only.zip",
    "dist/stage4/zone47_layout.svg",
    "dist/stage4/concept_audit.json",
    "dist/stage4/asset_evidence.json",
    "dist/stage4/zone47_survey_template.json",
    "dist/stage4_site_screening/site_screen_report.json",
    "dist/stage4_site_screening/site_screen_scatter.svg",
    "dist/stage4_site_screening/beileys47-zone47-site-screen-only.zip",
    "dist/stage4_footprint/footprint_report.json",
    "dist/stage4_footprint/footprint_rectangles.svg",
    "dist/stage4_footprint/beileys47-zone47-footprint-screen-only.zip",
    "dist/compatibility/stage4_release_gate_report.json",
    "dist/stage4_terrain_survey/terrain_survey_grid.json",
    "dist/stage4_terrain_survey/central_empty_Y_grid.csv",
    "dist/stage4_terrain_survey/southern_west_empty_Y_grid.csv",
    "dist/stage4_terrain_survey/southern_east_empty_Y_grid.csv",
    "dist/stage4_terrain_survey/central_xz_survey.svg",
    "dist/stage4_terrain_survey/beileys47-zone47-terrain-survey-worksheet-only.zip",
    "dist/stage4_height_capture/central_surfaceY_empty.json",
    "dist/stage4_height_capture/southern_west_surfaceY_empty.json",
    "dist/stage4_height_capture/southern_east_surfaceY_empty.json",
    "dist/stage4_height_capture/terrain_height_audit.json",
    "dist/stage4_height_capture/central_surfaceY_pc_runtime_example.c",
    "dist/stage4_height_capture/beileys47-zone47-height-capture-templates-only.zip",
    "dist/stage4_6_preflight/zone47_micro_pilot_plan.json",
    "dist/stage4_6_preflight/beileys47-micro-pilot-plan-only.zip",
]
README = """BEILEYS47 | DAYZ SURVIVAL WAR - OFFLINE RECOVERY KIT

This ZIP contains versioned project sources, the Stage 1, Stage 2 and Stage 3
PREVIEW ZIP files, reports and Stage 4 non-deployable design archive. See docs/RECOVERY_KIT.md.

IMPORTANT:
* It does NOT contain live Nitrado data, characters, bases, vehicles, or
  the world persistence database.
* Its official Bohemia baseline is pinned to October 16, 2026; you MUST
  verify compatibility with the currently installed DayZ game version.
* These files were NOT tested on PS5/PS4 and were NOT deployed.
* Do not upload the recovery ZIP to Nitrado. Extract only the reviewed
  mission XML/JSON files, individually, after backing up server files.
* Keep a separate private local copy of live Nitrado files/backup if
  available, and never commit passwords or tokens to the public repo.
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def zipinfo(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 30, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info


def build() -> None:
    entries = {"README_RECOVERY.txt": README.encode("utf-8")}
    for rel in SOURCE_PATHS:
        entries["repository/" + rel] = (ROOT / rel).read_bytes()
    for rel in PREVIEW_PATHS:
        entries["previews/" + rel.removeprefix("dist/")] = (ROOT / rel).read_bytes()

    manifest = {
        "project": "BEILEYS47 | DAYZ SURVIVAL WAR",
        "kind": "OFFLINE PREVIEW RECOVERY ONLY - NOT A LIVE SERVER BACKUP",
        "baseline": "BohemiaInteractive/DayZ-Central-Economy@f220b2918b1d79a5055b1ee9be70c0ec1516e876",
        "files": {
            name: {"sha256": sha256(payload), "bytes": len(payload)}
            for name, payload in sorted(entries.items())
        },
    }
    entries["MANIFEST_SHA256.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w") as archive:
        for name, content in sorted(entries.items()):
            archive.writestr(zipinfo(name), content)

    # Verify written data, exact file list and every saved hash.
    with zipfile.ZipFile(OUT, "r") as archive:
        archive.testzip_result = archive.testzip()
        if archive.testzip_result is not None:
            raise AssertionError(f"Corrupt ZIP member: {archive.testzip_result}")
        if set(archive.namelist()) != set(entries):
            raise AssertionError("Unexpected recovery ZIP file list")
        saved = json.loads(archive.read("MANIFEST_SHA256.json"))
        if saved != manifest:
            raise AssertionError("Recovery manifest was changed")
        for name, meta in saved["files"].items():
            data = archive.read(name)
            if sha256(data) != meta["sha256"] or len(data) != meta["bytes"]:
                raise AssertionError(f"Recovery hash/size mismatch for {name}")
    print(f"PASS: recovery kit with {len(entries)} entries and SHA-256 manifest: {OUT}")
    print("NOTE: not a copy of Nitrado game saves and NOT a PlayStation runtime test.")


if __name__ == "__main__":
    build()
