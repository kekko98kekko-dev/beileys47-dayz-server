#!/usr/bin/env python3
"""Stage 4 exporter safety tests. Synthetic fixtures only; no console survey."""
from __future__ import annotations
import copy
import json
import tempfile
from pathlib import Path

from export_zone47_spawner import export, STAGE3_GAMEPLAY
from prepare_zone47_survey import OUT as SURVEY_TEMPLATE, build as make_template
from build_stage4_terrain_survey_grid import local_to_world

def must_block(data:dict, work:Path, label:str) -> None:
    survey=work/f"{label}.json"
    out=work/f"blocked_{label}"
    survey.write_text(json.dumps(data),encoding="utf-8")
    try:
        export(survey,STAGE3_GAMEPLAY,out)
    except ValueError as exc:
        assert "EXPORT BLOCKED" in str(exc), str(exc)
        assert not out.exists(), f"{label} improperly created output"
    else:
        raise AssertionError(f"Unsafe survey accepted: {label}")

def run() -> None:
    make_template()
    original=json.loads(SURVEY_TEMPLATE.read_text(encoding="utf-8"))
    assert original["status"]=="INCOMPLETE_SURVEY_TEMPLATE_DO_NOT_DEPLOY"
    assert len(original["placements"])==26
    with tempfile.TemporaryDirectory(prefix="zone47-static-test-") as dirname:
        work=Path(dirname)
        must_block(original,work,"all_missing")
        sample=copy.deepcopy(original)
        sample["status"]="SURVEY_DATA_REVIEWED_FOR_OFFLINE_EXPORT"
        sample["confirmations"]={k:True for k in sample["confirmations"]}
        sample["site"].update({
            "source_site_candidate":"central",
            "world_center_x":9000,"world_center_z":7800,
            "rotation_degrees":120.0,
            "game_version":"SYNTHETIC TEST ONLY",
            "survey_notes":"SYNTHETIC fixture: coordinates are NOT from DayZ; they are used only to test transformations."
        })
        for p in sample["placements"]:
            p.update({"classname":sample["candidate_classnames"][0],
                      "height_y":150.0,"yaw_degrees":45.0,
                      "asset_verified_in_target_version":True,
                      "terrain_height_measured":True})
        # Show that an unverified prop fails, even after other fields are provided.
        broken=copy.deepcopy(sample)
        broken["placements"][3]["asset_verified_in_target_version"]=False
        must_block(broken,work,"unchecked_asset")
        broken=copy.deepcopy(sample)
        broken["placements"][4]["height_y"]=None
        must_block(broken,work,"missing_height")
        broken=copy.deepcopy(sample)
        broken["placements"][0]["classname"]="MadeUp_UnknownObject"
        must_block(broken,work,"unknown_class")

        old_version=copy.deepcopy(sample)
        old_version["version"]="1.0"
        must_block(old_version,work,"deprecated_v1_origin")
        wrong_origin=copy.deepcopy(sample)
        wrong_origin["site"]["world_origin_x"]=9000
        must_block(wrong_origin,work,"ambiguous_old_origin_field")
        shifted=copy.deepcopy(sample)
        shifted["site"]["world_center_x"]=9100
        must_block(shifted,work,"unreviewed_site_center")
        wrong_rotation=copy.deepcopy(sample)
        wrong_rotation["site"]["rotation_degrees"]=35.0
        must_block(wrong_rotation,work,"unreviewed_orientation")

        # Fully specified fixture exercises only local JSON composition.
        synthetic_out=work/"synthetic_export"
        survey=work/"synthetic.json"
        survey.write_text(json.dumps(sample),encoding="utf-8")
        report=export(survey,STAGE3_GAMEPLAY,synthetic_out)
        objects=json.loads((synthetic_out/"zone47_objects.json").read_text(encoding="utf-8"))
        assert len(objects["Objects"])==26
        assert all(len(o["pos"])==3 and len(o["ypr"])==3 for o in objects["Objects"])
        assert all(o["enableCEPersistency"] is False for o in objects["Objects"])
        assert all(set(o)=={"name","pos","ypr","scale","enableCEPersistency"} for o in objects["Objects"])
        assert all(o["scale"]==1.0 and len(o["pos"])==3 and len(o["ypr"])==3 for o in objects["Objects"])
        micro=json.loads((SURVEY_TEMPLATE.parents[2]/"config/stage4_zone47_micro_layout.json").read_text())
        ordered={p["id"]:p for p in micro["asset_placements"]}
        for source,entry in zip(sample["placements"],objects["Objects"]):
            local=ordered[source["id"]]
            x,z=local_to_world(local["local_x"],local["local_z"],9000,7800,240,220,120)
            assert abs(x-entry["pos"][0])<0.0001 and abs(z-entry["pos"][2])<0.0001
        assert report["coordinate_reference"]=="WORLD_CENTER_OF_BLUEPRINT"
        assert report["world_center_x"]==9000 and report["world_center_z"]==7800
        assert report["runtime_verified"] is False and report["site_is_provisional"] is True
        original_game=json.loads(STAGE3_GAMEPLAY.read_text(encoding="utf-8"))
        revised=json.loads((synthetic_out/"cfggameplay.json").read_text(encoding="utf-8"))
        assert revised["WorldsData"]["objectSpawnersArr"] == original_game["WorldsData"]["objectSpawnersArr"]+["zone47_objects.json"]
        revised["WorldsData"]["objectSpawnersArr"]=original_game["WorldsData"]["objectSpawnersArr"]
        assert revised==original_game, "Unrelated DayZ gameplay setting mutated"
        assert report["no_live_deployment"] is True
    print("PASS: Stage 4 exporter blocks incomplete/unverified surveys, transforms synthetic coordinates and preserves gameplay.")
    print("All synthetic output deleted. No real site, game launch or Nitrado access.")

if __name__=="__main__":run()
