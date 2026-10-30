#!/usr/bin/env python3
"""Prove log-format conversion is mechanical; no live DayZ call made."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from build_stage4_surfacey_snippet import build
from import_stage4_surfacey_log import convert
from prepare_stage4_height_capture import OUT

def test()->None:
    path=build()
    script=path.read_text(encoding="utf-8")
    assert script.count("GetGame().SurfaceY(")==182
    assert "NOT TESTED IN DAYZ RUNTIME" in script
    data=json.loads((OUT/"central_surfaceY_empty.json").read_text(encoding="utf-8"))
    lines=[]
    for p in data["points"]:
        # A mathematical fixture. This is NEVER real terrain data.
        y=200+0.01*(p["x"]-9000)+0.01*(p["z"]-7800)
        lines.append(f'2026-10-30 LOG Z47_ALT|{p["kind"]}|{p["id"]}|{p["x"]:.3f}|{p["z"]:.3f}|{y:.6f}')
    with tempfile.TemporaryDirectory(prefix="beileys47-synthetic-heights-") as dirname:
        dir=Path(dirname)
        log=dir/"synthetic_dayz_log.txt"
        out=dir/"synthetic_capture.json"
        log.write_text("\n".join(lines),encoding="utf-8")
        report=convert(log,OUT/"central_surfaceY_empty.json",out,
            "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        assert report["status"]=="MEASUREMENTS_COMPLETE_REQUIRE_MANUAL_VERIFICATION"
        assert report["deployment_allowed"] is False
        assert len(json.loads(out.read_text())["points"])==182
        bad=dir/"duplicate_log.txt"
        bad.write_text("\n".join(lines+[lines[0]]),encoding="utf-8")
        try:convert(bad,OUT/"central_surfaceY_empty.json",dir/"bad.json",
            "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        except ValueError as exc:assert "Duplicate" in str(exc)
        else:raise AssertionError("Duplicate log accepted")
        missing=dir/"missing_log.txt"
        missing.write_text("\n".join(lines[:-1]),encoding="utf-8")
        try:convert(missing,OUT/"central_surfaceY_empty.json",dir/"bad2.json",
            "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        except ValueError as exc:assert "Incomplete" in str(exc)
        else:raise AssertionError("Incomplete log accepted")
    print("PASS: optional 182-point PC runtime snippet and synthetic log importer.")
    print("NO DayZ runtime executed and NO fabricated height files published.")

if __name__=="__main__":test()
