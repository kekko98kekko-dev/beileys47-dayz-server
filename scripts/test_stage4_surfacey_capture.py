#!/usr/bin/env python3
"""Prove log-format conversion is mechanical; no live DayZ call made."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from build_stage4_surfacey_snippet import build
from import_stage4_surfacey_log import convert, MAX_LOG_BYTES
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
        # A valid-looking sample prefix must not be accepted if its numeric
        # suffix is truncated or polluted with extra text.
        def invalid_capture(label:str, changed:str, expected:str)->None:
            hostile=dir/(label+".txt")
            hostile.write_text("\n".join([changed]+lines[1:]),encoding="utf-8")
            dest=dir/(label+".json")
            try:
                convert(hostile,OUT/"central_surfaceY_empty.json",dest,
                        "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
            except ValueError as exc:
                assert expected in str(exc),(expected,str(exc))
                assert not dest.exists()
            else:
                raise AssertionError("Malformed log was accepted: "+label)
        invalid_capture("trailing_junk",lines[0]+"corrupted",
                        "Malformed or truncated")
        invalid_capture("double_marker",lines[0]+" "+lines[0],
                        "Invalid SurfaceY record line")
        invalid_capture("broken_coordinate",lines[0].replace("Z47_ALT|","Z47_ALT|GRID|"),
                        "Malformed or truncated")

        # Previously completed private captures must not be silently replaced.
        try:
            convert(log,OUT/"central_surfaceY_empty.json",out,
                    "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        except ValueError as exc: assert "already exists" in str(exc)
        else: raise AssertionError("Existing capture overwritten")

        # A real or synthetic populated dataset MUST NOT be saved in this
        # public repository (including ignored dist/).
        leaked=OUT/"private_reality_must_not_exist.json"
        try:
            convert(log,OUT/"central_surfaceY_empty.json",leaked,
                    "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        except ValueError as exc: assert "inside public repository" in str(exc)
        else: raise AssertionError("Private capture was permitted into repository")
        assert not leaked.exists()

        huge=dir/"oversized.txt"
        huge.write_bytes(b"X"*(MAX_LOG_BYTES+1))
        try:
            convert(huge,OUT/"central_surfaceY_empty.json",dir/"huge.json",
                    "SYNTHETIC_TEST_ONLY","2026-10-30T00:00:00Z","UNIT_TEST_NOT_REAL_DAYZ")
        except ValueError as exc: assert "Oversized" in str(exc)
        else: raise AssertionError("Oversized SurfaceY log accepted")
    print("PASS: optional 182-point PC runtime snippet and synthetic log importer.")
    print("NO DayZ runtime executed and NO fabricated height files published.")

if __name__=="__main__":test()
