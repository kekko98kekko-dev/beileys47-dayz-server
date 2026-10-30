#!/usr/bin/env python3
"""Stage 4 exporter safety tests. Synthetic fixtures only; no console survey."""
from __future__ import annotations
import copy
import json
import tempfile
from pathlib import Path

from export_zone47_spawner import export, STAGE3_GAMEPLAY
from prepare_zone47_survey import OUT as SURVEY_TEMPLATE, build as make_template

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
            "world_origin_x":5000,"world_origin_z":5000,
            "rotation_degrees":35.0,
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

        # Fully specified fixture exercises only local JSON composition.
        synthetic_out=work/"synthetic_export"
        survey=work/"synthetic.json"
        survey.write_text(json.dumps(sample),encoding="utf-8")
        report=export(survey,STAGE3_GAMEPLAY,synthetic_out)
        objects=json.loads((synthetic_out/"zone47_objects.json").read_text(encoding="utf-8"))
        assert len(objects["Objects"])==26
        assert all(len(o["pos"])==3 and len(o["ypr"])==3 for o in objects["Objects"])
        assert all(o["enableCEPersistency"] is False for o in objects["Objects"])
        original_game=json.loads(STAGE3_GAMEPLAY.read_text(encoding="utf-8"))
        revised=json.loads((synthetic_out/"cfggameplay.json").read_text(encoding="utf-8"))
        assert revised["WorldsData"]["objectSpawnersArr"] == original_game["WorldsData"]["objectSpawnersArr"]+["zone47_objects.json"]
        revised["WorldsData"]["objectSpawnersArr"]=original_game["WorldsData"]["objectSpawnersArr"]
        assert revised==original_game, "Unrelated DayZ gameplay setting mutated"
        assert report["no_live_deployment"] is True
    print("PASS: Stage 4 exporter blocks incomplete/unverified surveys, transforms synthetic coordinates and preserves gameplay.")
    print("All synthetic output deleted. No real site, game launch or Nitrado access.")

if __name__=="__main__":run()
