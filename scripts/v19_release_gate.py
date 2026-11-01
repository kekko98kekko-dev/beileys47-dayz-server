#!/usr/bin/env python3
"""Honest offline V19 project-completion gate, no Nitrado/PS5 access."""
from __future__ import annotations
import json
from pathlib import Path
from deploy_beileys47_v16 import build_scenes

ROOT=Path(__file__).resolve().parents[1]
FEATURES=(
("zona47_240x220","needs_field_evidence","26-object original blueprint is not the installed V16 Radunin extension"),
("underground_custom_bunker","not_delivered","V16 fortifies the exterior of a vanilla bunker; no new tested underground interior"),
("red_blue_shipping_container_lock","not_verified","rifle case/key economy is NOT a tested lockable shipping-container activity on Livonia"),
("mobile_scripted_hordes","engine_unavailable","no custom server-side scripting in stock DayZ PlayStation mission XML/JSON"),
("automatic_in_game_winner_prizes","engine_unavailable","weekly GitHub announcement cannot award inventory to named PSN winners"),
("instant_truck_replacement","engine_unavailable","CE counts a vehicle that is simply driven away as a live vehicle"),
("plank_quantity_full_every_15_days","engine_unavailable","new-object full quantity does not change depleted persistent instances on a calendar date"),
("interactive_refrigerator","not_delivered","no proven working vanilla PS5 fridge storage or cooling mechanics configured"),
("ps5_full_playability_acceptance","needs_field_evidence","15 real PS5 acceptance observations and persistence tests are missing"),
)
def build():
    objs=build_scenes()
    rad=[o for o in objs if 7000<o["pos"][0]<7200]
    assert len(objs)==32 and len(rad)==20
    xs=[o["pos"][0] for o in rad]; zs=[o["pos"][2] for o in rad]
    footprint={"radunin_v16_new_props_count":len(rad),
      "radunin_v16_new_props_bbox_x_m":round(max(xs)-min(xs),2),
      "radunin_v16_new_props_bbox_z_m":round(max(zs)-min(zs),2),
      "requested_original_blueprint_m":[240,220],
      "original_blueprint_terrain_surveyed":False,
      "note":"V16 additions' bounding box is NOT the footprint of the full original site."}
    return {"project":"BEILEYS47","version":"V19","source":"GitHub code and documented V18 Nitrado readback",
      "game_server_live_version_last_verified":"V18 orange-key economy; V16 world props",
      "full_100_percent_completion":False,
      "ps5_runtime_tested":False,
      "nitrado_world_changed_by_this_gate":False,
      "zone47_geometry":footprint,
      "features":[{"id":id,"status":status,"reason":reason,"installed_and_runtime_proven":False}
                  for id,status,reason in FEATURES],
      "delivered_this_branch":"safe GitHub maintenance reminders, clear release truthfulness, no fictitious game features"}
def main():
    result=build()
    out=ROOT/"deploy/v19/FEATURE_GATE.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V19 truthfulness check:",len(result["features"]),
          "requested features, not falsely marked 100%.")
    print("V16 Radunin newly added scenery span:",
          result["zone47_geometry"]["radunin_v16_new_props_bbox_x_m"],"x",
          result["zone47_geometry"]["radunin_v16_new_props_bbox_z_m"],"m.")
if __name__=="__main__":
    main()
