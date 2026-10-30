#!/usr/bin/env python3
"""Regression: Stage 3 MUST refresh Stage 2 even if its files already exist.

All upstream XML is synthetic and kept in a temporary test directory; no
network access, real console data or user saves.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

from build_stage3 import STAGE2_FILES, build, ROOT

def synthetic_ce(source:Path)->None:
    rules=json.loads((ROOT/"config/stage3_rules.json").read_text(encoding="utf-8"))
    events=ET.Element("events")
    for name,opts in rules["events"].items():
        ev=ET.SubElement(events,"event",name=name)
        for tag,value in (("active","1"),("position","fixed"),("nominal",str(opts["vanilla_nominal"]))):
            ET.SubElement(ev,tag).text=value
        if name=="StaticHeliCrash":
            children=ET.SubElement(ev,"children")
            ET.SubElement(children,"child",type=opts["child_type"],max=str(opts["vanilla_child_max"]))
    (source/"db").mkdir(parents=True)
    ET.ElementTree(events).write(source/"db/events.xml",encoding="utf-8")
    ET.ElementTree(ET.Element("messages")).write(source/"db/messages.xml",encoding="utf-8")

def test()->None:
    with tempfile.TemporaryDirectory(prefix="beileys-stage3-refresh-") as folder:
        work=Path(folder)
        source=work/"source"
        synthetic_ce(source)
        output=work/"output"
        stage2=output/"stage2/dayzOffline.enoch"
        stage2.mkdir(parents=True)
        # Simulates an earlier build (for example, from yesterday's rules).
        for rel in STAGE2_FILES:
            p=stage2/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(b"STALE_OLD_STAGE2_SHOULD_NEVER_SHIP")
        builds=[]
        def regenerate(dest:Path,src:Path|None)->None:
            assert dest==output and src==source
            builds.append(len(builds)+1)
            for rel in STAGE2_FILES:
                p=dest/"stage2/dayzOffline.enoch"/rel
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(f"SYNTHETIC_REFRESH_{builds[-1]}_{rel}".encode())
        with patch("build_stage3.build_stage2",side_effect=regenerate):
            build(output,source)
            assert builds==[1], "Stage 3 reused stale Stage 2 dependencies"
            for rel in STAGE2_FILES:
                assert (output/"stage3/dayzOffline.enoch"/rel).read_bytes()==f"SYNTHETIC_REFRESH_1_{rel}".encode()
            assert b"STALE_OLD_STAGE2_SHOULD_NEVER_SHIP" not in (
                output/"stage3/dayzOffline.enoch/db/types.xml").read_bytes()
            build(output,source)
            assert builds==[1,2], "A second Stage 3 run must refresh Stage 2 again"
            with zipfile.ZipFile(output/"stage3/beileys47-livonia-stage3-preview.zip") as z:
                assert z.testzip() is None
                for rel in STAGE2_FILES:
                    assert z.read("dayzOffline.enoch/"+rel)==f"SYNTHETIC_REFRESH_2_{rel}".encode()
                assert z.read("dayzOffline.enoch/db/events.xml")
                assert z.read("dayzOffline.enoch/db/messages.xml")
        print("PASS: stale Stage 2 source cannot persist through Stage 3 build, even on repeat invocation.")
        print("All tests used mock content; no DayZ/Nitrado server was accessed.")

if __name__=="__main__":test()
