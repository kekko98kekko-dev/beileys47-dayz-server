#!/usr/bin/env python3
"""Generate a NOT-RUNTIME-TESTED Enforce Script example to query real DayZ SurfaceY.

The .c snippet must be placed/invoked by a legitimate PC DayZ scripting
environment. It is NOT a PS5 mod and not a Nitrado mission file.
"""
from __future__ import annotations

import json
from pathlib import Path

from prepare_stage4_height_capture import OUT

def build()->Path:
    data=json.loads((OUT/"central_surfaceY_empty.json").read_text(encoding="utf-8"))
    assert data["status"]=="UNMEASURED_CAPTURE_TEMPLATE" and len(data["points"])==182
    lines=[
      "// BEILEYS47 ZONA 47 / PC DayZ SurfaceY CAPTURE EXAMPLE ONLY",
      "// NOT TESTED IN DAYZ RUNTIME. NOT INSTALLABLE IN NITRADO CONSOLE.",
      "// Runs only when an authorized PC DayZ script/missions environment calls it.",
      "// This only logs terrain height, NOT roads, bridges, collisions or line of sight.",
      "void Z47CaptureSurfaceY_Example()",
      "{",
    ]
    for p in data["points"]:
        assert p["kind"] in ("GRID","PROP")
        assert "|" not in p["id"]
        x,z=p["x"],p["z"]
        # DayZ Enforce string.Format uses %1, not printf %f.
        tag=f'Z47_ALT|{p["kind"]}|{p["id"]}|{x:.3f}|{z:.3f}|%1'
        lines.append(f'    Print(string.Format("{tag}", GetGame().SurfaceY({x:.3f}, {z:.3f})));')
    lines+=["}",""]
    dest=OUT/"central_surfaceY_pc_runtime_example.c"
    dest.write_text("\n".join(lines),encoding="utf-8")
    assert dest.read_text().count("GetGame().SurfaceY(")==182
    print("PASS: generated 182-line source sampling example; NOT executed or compiled in DayZ.")
    return dest

if __name__=="__main__":build()
