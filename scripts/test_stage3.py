#!/usr/bin/env python3
"""Regression, source-scope and ZIP safety tests for Stage 3 PREVIEW.

This validates file content and intended changes; not engine behavior.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from build_stage2 import STAGE2_FILES
from build_stage3 import STAGE3_FILES, STATUS, upstream
from build_mission import UPSTREAM_COMMIT

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
S3 = DIST / "stage3/dayzOffline.enoch"
ZIP = DIST / "stage3/beileys47-livonia-stage3-preview.zip"

def canonical(root: ET.Element) -> str:
    return ET.canonicalize(ET.tostring(root, encoding="unicode"))

def main() -> None:
    rules = json.loads((ROOT / "config/stage3_rules.json").read_text(encoding="utf-8"))
    report = json.loads((DIST / "stage3/change_report.json").read_text(encoding="utf-8"))
    assert report["status"] == STATUS and report["stage"] == 3
    assert report["pinned_commit"] == UPSTREAM_COMMIT

    # Inherited Stage 2 files must be perfectly identical (not reserialized).
    for path in STAGE2_FILES:
        original = (DIST / "stage2/dayzOffline.enoch" / path).read_bytes()
        inherited = (S3 / path).read_bytes()
        assert inherited == original, f"Unexpected Stage 2 change in {path}"

    actual = ET.parse(S3 / "db/events.xml").getroot()
    expected = ET.fromstring(upstream("db/events.xml", None))
    names = [x.get("name") for x in actual.findall("event")]
    assert len(names) == len(set(names))
    lookup = {x.get("name"): x for x in expected.findall("event")}
    assert set(rules["events"]) == {"StaticHeliCrash", "StaticMilitaryConvoy"}
    for name, params in rules["events"].items():
        item = lookup[name]
        assert int(item.findtext("nominal")) == params["vanilla_nominal"]
        assert item.findtext("active") == "1"
        item.find("nominal").text = str(params["target_nominal"])
        if name == "StaticHeliCrash":
            children = item.findall("./children/child")
            assert len(children) == 1
            child = children[0]
            assert child.get("type") == "Wreck_Mi8_Crashed"
            assert int(child.get("max")) == params["vanilla_child_max"]
            child.set("max", str(params["target_child_max"]))
    assert canonical(actual) == canonical(expected), "Unexpected event changes"

    # Official spawn coordinate pool is untouched because the preview does
    # not contain cfgeventspawns.xml.
    assert "cfgeventspawns.xml" not in STAGE3_FILES
    assert len(report["event_changes"]) == 2

    actual_msgs = ET.parse(S3 / "db/messages.xml").getroot()
    base_msgs = ET.fromstring(upstream("db/messages.xml", None))
    assert base_msgs.tag == "messages" and not base_msgs.findall("message")
    assert actual_msgs.tag == "messages"
    items = actual_msgs.findall("message")
    assert len(items) == len(rules["messages"]) == 3
    for node, rule in zip(items, rules["messages"]):
        assert node.findtext("text") == rule["text"]
        assert len(rule["text"]) <= 160
        assert node.findtext("shutdown") == "0"
        assert node.findtext("deadline") == "0"
        assert int(node.findtext("repeat")) == rule["repeat"]
        assert int(node.findtext("delay")) == rule["delay"]
        assert int(node.findtext("onconnect")) == rule["onconnect"]
    assert sum(int(m.findtext("onconnect")) for m in items) == 1
    assert all(int(m.findtext("repeat")) >= 30 for m in items[1:])

    allowed = {f"dayzOffline.enoch/{p}" for p in STAGE3_FILES} | {"change_report.json"}
    with zipfile.ZipFile(ZIP) as archive:
        infos = archive.infolist()
        names = [x.filename for x in infos]
        assert len(names) == len(allowed) and set(names) == allowed
        assert archive.testzip() is None
        assert all(not x.is_dir() and x.file_size <= 3_000_000 for x in infos)
        assert sum(x.file_size for x in infos) <= 6_000_000
        assert all(".." not in Path(x.filename).parts and "\\" not in x.filename for x in infos)
        for path in STAGE3_FILES:
            assert archive.read(f"dayzOffline.enoch/{path}") == (S3 / path).read_bytes()
        assert json.loads(archive.read("change_report.json")) == report

    print("PASS: Stage 3 baseline diff scope, Stage 2 inheritance and ZIP safety.")
    print("NOT tested: console event behavior, message display, Nitrado or PvP balance.")

if __name__ == "__main__":
    main()
