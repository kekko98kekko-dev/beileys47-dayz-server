#!/usr/bin/env python3
"""Create a private-survey worksheet for Stage 4; contains NO real game coordinates."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/stage4/zone47_survey_template.json"

def build() -> None:
    micro=json.loads((ROOT/"config/stage4_zone47_micro_layout.json").read_text(encoding="utf-8"))
    candidates=json.loads((ROOT/"config/stage4_asset_candidates.json").read_text(encoding="utf-8"))
    assert micro["status"]=="SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON"
    survey={
        "status":"INCOMPLETE_SURVEY_TEMPLATE_DO_NOT_DEPLOY",
        "project":"BEILEYS47 | ZONA 47",
        "map":"Livonia",
        "version":"1.0",
        "confirmations":{
            "actual_livonia_site_surveyed":False,
            "terrain_heights_recorded_for_each_prop":False,
            "game_asset_classes_checked_against_current_playstation_version":False,
            "exact_current_game_version_matched":False
        },
        "site":{"world_origin_x":None,"world_origin_z":None,"rotation_degrees":None,"game_version":None,"survey_notes":None},
        "candidate_classnames":[c["name"] for c in candidates["models"]],
        "placements":[
            {"id":p["id"],"classname":None,"height_y":None,"yaw_degrees":None,
             "pitch_degrees":0,"roll_degrees":0,"scale":1.0,
             "asset_verified_in_target_version":False,"terrain_height_measured":False}
            for p in micro["asset_placements"]
        ],
        "warning":"Worksheet only. Do not publish live credentials; keep completed surveys under private/ or outside the repository. No provider deployment is ever performed."
    }
    assert all(survey["site"][key] is None for key in ("world_origin_x","world_origin_z","rotation_degrees"))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(survey,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PASS: survey template with {len(survey['placements'])} placeholders (ZERO real game coordinates): {OUT}")

if __name__=="__main__":build()
