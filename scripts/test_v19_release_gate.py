#!/usr/bin/env python3
"""Check V19 gates never mistake code/configuration for real game functionality."""
from __future__ import annotations
from v19_release_gate import build,FEATURES
def main():
    report=build()
    names=[x["id"] for x in report["features"]]
    assert len(names)==len(set(names))==9
    assert set(names)=={x[0] for x in FEATURES}
    assert report["full_100_percent_completion"] is False
    assert report["ps5_runtime_tested"] is False
    assert report["nitrado_world_changed_by_this_gate"] is False
    assert all(x["installed_and_runtime_proven"] is False for x in report["features"])
    assert report["zone47_geometry"]["radunin_v16_new_props_count"]==20
    assert report["zone47_geometry"]["radunin_v16_new_props_bbox_x_m"]<240
    assert report["zone47_geometry"]["radunin_v16_new_props_bbox_z_m"]<220
    assert all(x["status"] in ("engine_unavailable","not_delivered","not_verified","needs_field_evidence") for x in report["features"])
    print("PASS V19: nine requested features accounted for, real ZONA47 footprint limits and no false 100%")
if __name__=="__main__":main()
