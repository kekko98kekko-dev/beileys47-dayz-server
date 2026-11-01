#!/usr/bin/env python3
"""Produce a portable, static disaster-recovery ZIP for BEILEYS47.

Contains the complete versioned source needed to rebuild previews and the
current preview builds. No Nitrado access, no credentials, no live game saves.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
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
    "config/server_identity_en.json",
    "config/franco_v1_preview.json",
    "config/franco_v1_messages_after_deploy.xml",
    "config/stage4_zone47_blueprint.json",
    "config/stage4_site_screening_rules.json",
    "config/stage4_footprint_rules.json",
    "config/stage4_release_gate.json",
    "config/stage4_centered_export_contract.json",
    "config/stage4_9_p3d_bbox_evidence.json",
    "config/stage4_10_placement_roles.json",
    "config/stage4_11_p3d_role_candidates.json",
    "config/stage4_13_pilot_protocol.json",
    "config/stage4_asset_candidates.json",
    "config/stage4_zone47_micro_layout.json",
    "config/stage6_special_zones.json",
    "config/stage7_bunker_layout.json",
    "config/stage8_bunker_feasibility.json",
    "config/stage9_hq_structure_pilot.json",
    "docs/OPERATIONS.md",
    "docs/STAGE1.md",
    "docs/STAGE2.md",
    "docs/STAGE3.md",
    "docs/SERVER_IDENTITY_EN.md",
    "docs/LIVE_ACTIVATION_2026-10-31.md",
    "docs/FRANCO_V1_PREDEPLOY.md",
    "docs/FRANCO_LOCKED_CASES_FRIDGE_CONSOLE_REVIEW.md",
    "docs/STAGE5_GAMEPLAY_BALANCE.md",
    "docs/STAGE6_SPECIAL_ZONES.md",
    "docs/STAGE7_BUNKER_TOPOLOGY.md",
    "docs/STAGE8_BUNKER_FEASIBILITY.md",
    "docs/STAGE9_HQ_STRUCTURE_PILOT.md",
    "docs/STAGE4_ZONE47.md",
    "docs/STAGE4_SITE_SCREEN.md",
    "docs/STAGE4_FOOTPRINT.md",
    "docs/STAGE4_RELEASE_COMPATIBILITY.md",
    "docs/STAGE4_TERRAIN_SURVEY.md",
    "docs/STAGE4_REAL_ALTITUDE.md",
    "docs/STAGE4_6_SPAWNER_PREFLIGHT.md",
    "docs/STAGE4_7_PVP_ROUTE_STRESS.md",
    "docs/STAGE4_8_FIELD_RECON.md",
    "docs/STAGE4_9_MODEL_VISUAL_BOUNDS.md",
    "docs/STAGE4_10_FULL_LAYOUT.md",
    "docs/STAGE4_11_ROLE_MATCHED_MODELS.md",
    "docs/STAGE4_12_RPT_AND_SPAWNER_PROVENANCE.md",
    "docs/STAGE4_13_CONSOLE_PILOT.md",
    "docs/PREPURCHASE_MASTER.md",
    "docs/PREPURCHASE_CODE_AUDIT.md",
    "docs/STAGE4_SITE_SHORTLIST.md",
    "docs/ZONE47_QA_PROTOCOL.md",
    "docs/RECOVERY_KIT.md",
    "docs/RELEASE_SNAPSHOT.md",
    "mission/README.md",
    "scripts/audit_stage2.py",
    "scripts/build_mission.py",
    "scripts/zip_deterministic.py",
    "scripts/test_zip_reproducibility.py",
    "scripts/test_all_nested_zip_reproducibility.py",
    "scripts/test_stage3_dependency_refresh.py",
    "scripts/test_ce_input_guards.py",
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
    "scripts/stress_test_stage4_pvp_routes.py",
    "scripts/test_stage4_pvp_routes.py",
    "scripts/build_stage4_8_field_recon.py",
    "scripts/test_stage4_8_field_recon.py",
    "scripts/assess_stage4_9_visual_envelopes.py",
    "scripts/test_stage4_9_visual_envelopes.py",
    "scripts/audit_stage4_10_all_placements.py",
    "scripts/test_stage4_10_all_placements.py",
    "scripts/assess_stage4_11_role_model_options.py",
    "scripts/test_stage4_11_role_model_options.py",
    "scripts/triage_stage4_12_rpt.py",
    "scripts/build_stage4_12_evidence.py",
    "scripts/test_stage4_12_rpt.py",
    "scripts/test_stage4_12_evidence.py",
    "scripts/build_stage4_13_console_pilot.py",
    "scripts/audit_stage4_13_console_pilot.py",
    "scripts/test_stage4_13_console_pilot.py",
    "scripts/build_prepurchase_bundle.py",
    "scripts/test_prepurchase_bundle.py",
    "scripts/check_stage4_release_gate.py",
    "scripts/test_stage4_release_gate.py",
    "scripts/audit_stage4_assets.py",
    "scripts/prepare_zone47_survey.py",
    "scripts/export_zone47_spawner.py",
    "scripts/test_zone47_export_safety.py",
    "scripts/check_release.py",
    "scripts/make_recovery_kit.py",
    "scripts/restore_recovery_kit.py",
    "scripts/test_recovery_restore.py",
    "scripts/plan_nitrado.py",
    "scripts/test_stage2.py",
    "scripts/test_stage3.py",
    "scripts/test_server_identity.py",
    "scripts/build_stage5_balance.py",
    "scripts/test_stage5_balance.py",
    "scripts/build_stage6_special_zones.py",
    "scripts/test_stage6_special_zones.py",
    "scripts/build_stage7_bunker.py",
    "scripts/test_stage7_bunker.py",
    "scripts/build_stage8_feasibility.py",
    "scripts/test_stage8_feasibility.py",
    "scripts/build_stage9_hq_structure.py",
    "scripts/test_stage9_hq_structure.py",
    "scripts/validate.py",
    "docs/BEILEYS47_AUDIT_V8_V9_2026-10-31.md",
    "docs/FRANCO_V3_VERIFIED_LIVE_2026-10-31.md",
    "docs/FRANCO_V4_FIELD_SITES_LIVE_2026-10-31.md",
    "docs/FRANCO_V5_OFFLINE_PROPOSAL_AND_RESTORE_2026-10-31.md",
    "docs/FRANCO_V6_STARTER_KIT_PANEL_REPORT_2026-10-31.md",
    "docs/FRANCO_V7_TEST_SPAWN_AND_SHOWCASE_CANDIDATE_2026-10-31.md",
    "mission/bunker_v10/MANIFEST_BUNKER_V10.json",
    "mission/bunker_v10/README_RICERCA_E_CONDIZIONI.md",
    "mission/dolnik_replacement_v9/README_INSTALLAZIONE.md",
    "mission/dolnik_replacement_v9/SPAWN_LOCATION_REVIEW.md",
    "mission/dolnik_replacement_v9/beileys47_dolnik_military_base_v9.json",
    "mission/dolnik_replacement_v9/cfggameplay_V9_CANDIDATE.json",
    "mission/dolnik_replacement_v9/cfgplayerspawnpoints_v9_SAFEZONE_CANDIDATE.xml",
    "mission/dolnik_replacement_v9/dolnik_mapgrouppos_additions_ONLY.xml",
    "mission/franco_v4_field_sites/beileys47_hotspot_southwest.json",
    "mission/franco_v4_field_sites/beileys47_hotspot_zone47.json",
    "mission/franco_v6/beileys47_freshspawn_v6.json",
    "mission/franco_v6/cfggameplay_v6_validated_repair.json",
    "mission/franco_v7/beileys47_freshspawn_v7.json",
    "mission/franco_v7/beileys47_test_showcase_v7.json",
    "mission/franco_v7/cfggameplay_v7_candidate.json",
    "mission/franco_v7/cfgplayerspawnpoints_v7_candidate.xml",
    "mission/franco_v8/beileys47_freshspawn_v8.json",
    "mission/franco_v8/cfggameplay.json",
    "mission/franco_v8/cfgplayerspawnpoints.xml",
    "mission/stable_v10/README_STABILITY_V10.md",
    "mission/stable_v10/cfggameplay.json",
    "mission/stable_v10/cfgplayerspawnpoints.xml",
    "scripts/audit_stable_v10.py",
    "scripts/test_stable_v10.py",
    "mission/v11_gameplay/README_GESTIONE_RICHIESTE.md",
    "mission/v11_gameplay/TEST_ITEMS_POSITIONS_AND_LIMITATIONS.md",
    "mission/v11_gameplay/beileys47_test_items_v11.json",
    "mission/v11_gameplay/beileys47_vehicle_loadouts_v11.xml",
    "mission/v11_gameplay/cfgeconomycore_V11_REFERENCE_DO_NOT_OVERWRITE.xml",
    "mission/v11_gameplay/cfgeventspawns_truck12_FRAGMENT.xml",
    "mission/v11_gameplay/cfgweather_SUNNY_V11.xml",
    "mission/v11_gameplay/db_event_VehicleTruck01_FRAGMENT.xml",
    "mission/v11_gameplay/db_types_PileOfWoodenPlanks_FRAGMENT.xml",
    "scripts/test_v11_gameplay.py",
    ".github/workflows/nitrado-readonly.yml",
    ".github/workflows/v15-deploy.yml",
    ".github/workflows/v15-preflight.yml",
    ".github/workflows/v15-start.yml",
    ".github/workflows/v16-deploy.yml",
    ".github/workflows/v16-extra.yml",
    ".github/workflows/v16-live-audit.yml",
    ".github/workflows/v16-night.yml",
    ".github/workflows/v17-ps5-offline-tests.yml",
    ".github/workflows/weekly-community-events.yml",
    "deploy/v15/DEPLOY_RESULT.json",
    "deploy/v15/GO_LIVE.txt",
    "deploy/v15/START_SERVER_NOW.txt",
    "deploy/v15/START_WORKFLOW_RESULT.json",
    "deploy/v15/vehicle_changes_b64.txt",
    "deploy/v16/EXTRA_RUN.json",
    "deploy/v16/GO_LIVE.txt",
    "deploy/v16/LIVE_AUDIT_WORKFLOW.json",
    "deploy/v16/NIGHT_WORKFLOW.json",
    "deploy/v16/WORKFLOW_RESULT.json",
    "deploy/v17/PS5_ACCEPTANCE.template.json",
    "docs/BEILEYS47_V15_LIVE_STATUS.md",
    "docs/BEILEYS47_V16_VERIFIED_AND_LIMITATIONS.md",
    "docs/BEILEYS47_V17_PS5_ACCEPTANCE.md",
    "docs/NITRADO_API_SETUP_BEILEYS47.md",
    "mission/v14_dolnik_clean/beileys47_dolnik_2_tende_v14.json",
    "scripts/deploy_beileys47_v15.py",
    "scripts/deploy_beileys47_v16.py",
    "scripts/nitrado_snapshot.py",
    "scripts/start_beileys47_after_v15.py",
    "scripts/test_v17_ps5_acceptance.py",
    "scripts/v16_audit_live.py",
    "scripts/v16_night.py",
    "scripts/v16_read_extra.py",
    "scripts/v17_ps5_acceptance.py",
    ".github/workflows/v18-preflight.yml",
    "docs/BEILEYS47_V18_READONLY_PREFLIGHT.md",
    "scripts/v18_live_preflight.py",
    ".github/workflows/v18-orange-keys.yml",
    "docs/BEILEYS47_V18_ORANGE_KEY_CHANGE.md",
    "scripts/test_v18_orange_key_fix.py",
    "scripts/v18_orange_key_fix.py",
    ".github/workflows/v19-plank-inspection.yml",
    ".github/workflows/v19-release-evidence.yml",
    "docs/BEILEYS47_V19_ALL_NINE_FEATURES.md",
    "scripts/test_v19_plank_maintenance.py",
    "scripts/test_v19_release_gate.py",
    "scripts/v19_plank_maintenance.py",
    "scripts/v19_release_gate.py",
    ".github/workflows/v20-sprint.yml",
    "docs/BEILEYS47_V20_SPRINT.md",
    "scripts/test_v20_unlimited_sprint.py",
    "scripts/v20_unlimited_sprint.py",
    ".github/workflows/v21-daily-health.yml",
    ".github/workflows/v21-hotspot-notices.yml",
    "docs/BEILEYS47_V21_PREMIUM_LAUNCH.md",
    "scripts/test_v21_safe_discovery_messages.py",
    "scripts/v21_safe_discovery_messages.py",
    "scripts/v22_economy_readonly.py",
    ".github/workflows/v22-live-economy-readonly.yml",
    "scripts/v23_vehicle_consistency.py",
    "scripts/test_v23_vehicle_consistency.py",
    ".github/workflows/v23-vehicle-ce.yml",
    "scripts/v24_elevation_source_probe.py",
    ".github/workflows/v24-elevation-probe.yml",
    "scripts/v25_dzpage_network_probe.mjs",
    ".github/workflows/v25-livonia-browser.yml",
    ".github/workflows/v26-heightmap-inspect.yml",
    ".github/workflows/v27-terrain-survey.yml",
    ".github/workflows/v28-save-terrain-survey.yml",
    "config/stage4_14_public_terrain_survey.json",
    "scripts/v26_heightmap_inspect.py",
    "scripts/v27_zone47_real_heights.py",
    ".github/workflows/v29-zone47-p1.yml",
    "docs/BEILEYS47_V29_P1_GUARDBOX.md",
    "scripts/test_v29_zone47_p1_pilot.py",
    "scripts/v29_zone47_p1_pilot.py",
    ".github/workflows/v30-live-terrain-audit.yml",
    "scripts/v30_live_prop_ground_audit.py",
    "docs/BEILEYS47_V30_HEIGHT_DIFF_AND_NEXT_TESTS.md",
    ".github/workflows/v31-zone47-full-preview.yml",
    "docs/BEILEYS47_V31_FULL_ZONE47_RELEASE_GATE.md",
    "scripts/test_v31_full_zone47_dryrun.py",
    "scripts/v31_full_zone47_dryrun.py",
    ".github/workflows/v32-zone47-clearance.yml",
    "docs/BEILEYS47_V32_RELOCATED_ZONE47.md",
    "scripts/test_v32_zone47_clearance_solver.py",
    "scripts/v32_zone47_clearance_solver.py",
    ".github/workflows/v33-persist-zone47-plan.yml",
    ".github/workflows/v34-rpt-readonly.yml",
    "config/v33/BEILEYS47_ZONE47_25_NOT_LIVE.json",
    "config/v33/QUALITY_GATES_NOT_PS5_TESTED.json",
    "scripts/v34_rpt_spawner_readonly.py",
    ".github/workflows/v35-install-25-zone47.yml",
    "docs/BEILEYS47_V35_REAL_INSTALL.md",
    "scripts/test_v35_install_25_zone47.py",
    "scripts/v35_install_25_zone47.py",
    ".github/workflows/v36-provider-backups-readonly.yml",
    "scripts/test_v36_nitrado_backups_readonly.py",
    "scripts/v36_nitrado_backups_readonly.py",
    ".github/workflows/v37-zone47-infected.yml",
    "docs/BEILEYS47_V37_VANILLA_ALTERNATIVES.md",
    "scripts/test_v37_zone47_infected_patches.py",
    "scripts/v37_zone47_infected_patches.py",
    ".github/workflows/v39-truck-audit.yml",
    "scripts/v39_truck_live_audit.py",
    ".github/workflows/v40-dolnik-full-truck.yml",
    "docs/BEILEYS47_V40_DOLNIK_TRUCK.md",
    "scripts/test_v40_dolnik_truck_rescue.py",
    "scripts/v40_dolnik_truck_rescue.py",
    ".github/workflows/v41-operator-truck-restart-once.yml",
    "docs/BEILEYS47_V41_OWNER_APPROVED_RESTART.md",
    ".github/workflows/v42-full-m3s-lumber.yml",
    "docs/BEILEYS47_V42_FULL_LOGS_PLANKS.md",
    "scripts/test_v42_full_m3s_lumber_racks.py",
    "scripts/v42_full_m3s_lumber_racks.py",
    ".github/workflows/v43-dolnik-readonly.yml",
    "scripts/v43_dolnik_readonly_audit.py",
    ".github/workflows/v44-single-dolnik-truck.yml",
    "docs/BEILEYS47_V44_ONE_ORIGINAL_M3S_REALITY.md",
    "scripts/test_v44_single_original_dolnik_truck.py",
    "scripts/v44_single_original_dolnik_truck.py",
    ".github/workflows/v45-ground-clutter-ttl.yml",
    "docs/BEILEYS47_V45_SAFE_GROUND_CLEANUP.md",
    "scripts/test_v45_safe_loot_ttl.py",
    "scripts/v45_safe_loot_ttl.py",
    ".github/workflows/v46-one-off-dolnik-and-loot.yml",
    "docs/BEILEYS47_V46_ONE_RESTART_SAFETY.md",
    "scripts/test_v46_one_off_truck_and_loot_restart.py",
    "scripts/v46_one_off_truck_and_loot_restart.py",
]
PREVIEW_PATHS = [
    "dist/stage1/beileys47-livonia-stage1.zip",
    "dist/stage1/change_report.json",
    "dist/stage2/beileys47-livonia-stage2-preview.zip",
    "dist/stage2/change_report.json",
    "dist/stage2/nitrado_dry_run_plan.json",
    "dist/stage3/beileys47-livonia-stage3-preview.zip",
    "dist/stage3/change_report.json",
    "dist/stage5_gameplay/ce_balance_scorecard.json",
    "dist/stage6_special_zones/concept_review.json",
    "dist/stage7_bunker/bunker_topology_report.json",
    "dist/stage7_bunker/bunker_topology.svg",
    "dist/stage8_bunker_feasibility/feasibility_review.json",
    "dist/stage9_hq_structure/hq_structure_review.json",
    "dist/stage9_hq_structure/hq_structure_checklist.csv",
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
    "dist/stage4_7_route_balance/pvp_route_stress_report.json",
    "dist/stage4_7_route_balance/sector_lockout_matrix.csv",
    "dist/stage4_7_route_balance/beileys47-route-stress-design-only.zip",
    "dist/stage4_8_field_recon/central_field_recon.json",
    "dist/stage4_8_field_recon/central_waypoints.csv",
    "dist/stage4_8_field_recon/central_route_links.csv",
    "dist/stage4_8_field_recon/beileys47-world-xz-field-guide-only.zip",
    "dist/stage4_9_visual_envelopes/pilot_visual_clearance_report.json",
    "dist/stage4_9_visual_envelopes/beileys47-visual-clearance-not-deployable.zip",
    "dist/stage4_10_full_layout/full_26_layout_risk_report.json",
    "dist/stage4_10_full_layout/all_26_placement_review.csv",
    "dist/stage4_10_full_layout/all_325_pair_review.csv",
    "dist/stage4_10_full_layout/beileys47-full-layout-paper-audit-only.zip",
    "dist/stage4_11_role_catalog/candidate_26_visual_fit_report.json",
    "dist/stage4_11_role_catalog/all_26_visual_candidate_sizes.csv",
    "dist/stage4_11_role_catalog/reference_pair_warnings.csv",
    "dist/stage4_11_role_catalog/beileys47-stage411-visual-role-options-not-deployable.zip",
    "dist/stage4_12_rpt_diagnostics/class_evidence_no_runtime.json",
    "dist/stage4_12_rpt_diagnostics/rpt_triage_no_logs.json",
    "dist/stage4_12_rpt_diagnostics/beileys47-spawner-log-preflight-only.zip",
    "dist/stage4_13_console_pilot/blank_1_3_5_console_trial.json",
    "dist/stage4_13_console_pilot/console_pilot_no_evidence_audit.json",
    "dist/stage4_13_console_pilot/beileys47-console-pilot-templates-only.zip",
    "dist/prepurchase/beileys47-livonia-mission-review-candidate.zip",
    "dist/prepurchase/purchase_day_gate.json",
]
README = """BEILEYS47 | DAYZ SURVIVAL WAR - OFFLINE RECOVERY KIT

This ZIP contains versioned project sources, the Stage 1, Stage 2 and Stage 3
PREVIEW ZIP files, reports and Stage 4 non-deployable design archive. See docs/RECOVERY_KIT.md.

IMPORTANT:
* It does NOT contain live Nitrado data, characters, bases, vehicles, or
  the world persistence database.
* Its official Bohemia baseline is pinned to October 16, 2026; you MUST
  verify compatibility with the currently installed DayZ game version.
* Some historical sources powered live V15/V16 deployment, but this ZIP is NOT\n  a readback of current live Nitrado mission/persistence. PS5 runtime remains untested.
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


def validate_source_inventory(tracked: set[str] | None = None) -> None:
    """Fail closed if a future tracked source file is missing from backups.

    Git is available in GitHub Actions and the repository checkout. Ignore
    untracked dist/ build outputs; all versioned project files must be saved.
    """
    if tracked is None:
        output = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout
        tracked = {path.decode("utf-8") for path in output.split(b"\0") if path}
    included = set(SOURCE_PATHS)
    if len(included) != len(SOURCE_PATHS):
        raise ValueError("Duplicate source paths in Recovery Kit inventory")
    missing = sorted(tracked - included)
    stale = sorted(included - tracked)
    if missing or stale:
        raise ValueError(
            f"Recovery source inventory out of sync: missing={missing}, stale={stale}"
        )
    for rel in included:
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Recovery source is missing or is a symlink: {rel}")


def build() -> None:
    validate_source_inventory()
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
