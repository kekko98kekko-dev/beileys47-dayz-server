#!/usr/bin/env python3
"""Build Stage 3 Livonia encounter/identity PREVIEW, without Nitrado access.

Adds only two constrained edits to existing vanilla dynamic events and
non-shutdown messages.xml. All Stage 2 files are copied byte-for-byte.
This is NOT a console compatibility test.
"""
from __future__ import annotations

import argparse
import json
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from build_mission import UPSTREAM_BASE, UPSTREAM_COMMIT
from build_stage2 import STAGE2_FILES, build as build_stage2

ROOT = Path(__file__).resolve().parents[1]
EXTRA_FILES = ("db/events.xml", "db/messages.xml")
STAGE3_FILES = STAGE2_FILES + EXTRA_FILES
STATUS = "PREVIEW ONLY - NO NITRADO DEPLOY / NO PLAYSTATION TEST"


def upstream(path: str, source_dir: Path | None) -> bytes:
    if path not in EXTRA_FILES:
        raise ValueError(f"Unapproved upstream file {path}")
    if source_dir is not None:
        data = (source_dir / path).read_bytes()
    else:
        req = urllib.request.Request(
            UPSTREAM_BASE + path,
            headers={"User-Agent": "BEILEYS47-DayZ-Stage3-Preview/1.0"}
        )
        with urllib.request.urlopen(req, timeout=45) as res:
            data = res.read(3_000_001)
    if len(data) > 3_000_000:
        raise ValueError(f"Unexpected upstream size for {path}")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError(f"Disallowed XML DTD/entities: {path}")
    return data


def modify_events(root: ET.Element, rules: dict) -> list[dict]:
    if root.tag != "events":
        raise ValueError("Unexpected events.xml root")
    nodes = root.findall("event")
    index = {node.get("name"): node for node in nodes}
    if len(index) != len(nodes) or None in index:
        raise ValueError("Duplicated or missing event names")
    if set(rules["events"]) != {"StaticHeliCrash", "StaticMilitaryConvoy"}:
        raise ValueError("Stage 3 only allows two explicitly approved events")
    report = []
    for name, options in rules["events"].items():
        if name not in index:
            raise ValueError(f"Official event absent: {name}")
        node = index[name]
        if node.findtext("active") != "1" or node.findtext("position") != "fixed":
            raise ValueError(f"Official event no longer active/fixed: {name}")
        nominal = node.find("nominal")
        if nominal is None or int(nominal.text) != options["vanilla_nominal"]:
            raise ValueError(f"Unexpected official event nominal: {name}")
        target = options["target_nominal"]
        if not isinstance(target, int) or not 1 <= target <= 5:
            raise ValueError(f"Unsafe event count: {name}")
        nominal.text = str(target)
        item = {"event": name, "vanilla_nominal": options["vanilla_nominal"], "target_nominal": target}

        if name == "StaticHeliCrash":
            children = node.findall("./children/child")
            child = next((x for x in children if x.get("type") == options["child_type"]), None)
            if child is None or len(children) != 1:
                raise ValueError("Unexpected vanilla helicopter crash child configuration")
            if int(child.get("max", "-1")) != options["vanilla_child_max"]:
                raise ValueError("Helicopter child cap changed in official baseline")
            if not 1 <= options["target_child_max"] <= 5:
                raise ValueError("Helicopter crash child cap unsafe")
            child.set("max", str(options["target_child_max"]))
            item["child_max"] = [options["vanilla_child_max"], options["target_child_max"]]
        report.append(item)
    return report


def make_messages(root: ET.Element, rules: dict) -> list[dict]:
    if root.tag != "messages":
        raise ValueError("Unexpected messages.xml root")
    if root.findall("message"):
        raise ValueError("Upstream has active messages; refusing to override")
    messages = rules["messages"]
    if len(messages) != 3:
        raise ValueError("Exactly three brand messages required")
    report = []
    seen_kinds = set()
    for spec in messages:
        kind = spec["kind"]
        text = spec["text"]
        if kind in seen_kinds or not isinstance(text, str) or not 1 <= len(text) <= 160:
            raise ValueError(f"Duplicated kind or invalid message length: {kind}")
        if any(s in text for s in ("#tmin", "\n", "\r")):
            raise ValueError("Messages cannot contain countdowns or newlines")
        delay = spec["delay"]
        repeat = spec["repeat"]
        onconnect = spec["onconnect"]
        if type(delay) is not int or type(repeat) is not int or type(onconnect) is not int:
            raise ValueError("Messages require integer timings")
        if delay < 0 or onconnect not in (0, 1) or (repeat and repeat < 30):
            raise ValueError("Message timings must be conservative")
        if repeat == 0 and onconnect != 1:
            raise ValueError("Nonrepeating messages must be on-connect")
        node = ET.SubElement(root, "message")
        for tag, value in (
            ("delay", delay), ("repeat", repeat), ("deadline", 0),
            ("onconnect", onconnect), ("shutdown", 0), ("text", text)
        ):
            ET.SubElement(node, tag).text = str(value)
        seen_kinds.add(kind)
        report.append({"kind": kind, "repeat_minutes": repeat, "onconnect": bool(onconnect)})
    if seen_kinds != {"welcome", "survival_hint", "community_rule"}:
        raise ValueError("Unexpected message kinds")
    return report


def build(output: Path, source_dir: Path | None) -> None:
    stage2 = output / "stage2/dayzOffline.enoch"
    if not all((stage2 / p).is_file() for p in STAGE2_FILES):
        build_stage2(output, source_dir)
    if not all((stage2 / p).is_file() for p in STAGE2_FILES):
        raise ValueError("Stage 2 build must be present")
    rules = json.loads((ROOT / "config/stage3_rules.json").read_text(encoding="utf-8"))
    if rules.get("stage") != 3:
        raise ValueError("Stage 3 rules require stage=3")
    dest = output / "stage3/dayzOffline.enoch"
    for path in STAGE2_FILES:
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage2 / path, target)

    events = ET.fromstring(upstream("db/events.xml", source_dir))
    changes = modify_events(events, rules)
    messages = ET.fromstring(upstream("db/messages.xml", source_dir))
    brands = make_messages(messages, rules)
    for path, root in (("db/events.xml", events), ("db/messages.xml", messages)):
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
        ET.parse(target)

    report = {
        "stage": 3,
        "source": "BohemiaInteractive/DayZ-Central-Economy",
        "pinned_commit": UPSTREAM_COMMIT,
        "status": STATUS,
        "inherited_from": "STAGE2_BYTE_FOR_BYTE",
        "event_changes": changes,
        "messages": brands,
        "notes": rules["disclaimer"],
    }
    outdir = output / "stage3"
    report_path = outdir / "change_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = outdir / "beileys47-livonia-stage3-preview.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
        for path in STAGE3_FILES:
            zipped.write(dest / path, arcname=f"dayzOffline.enoch/{path}")
        zipped.write(report_path, arcname="change_report.json")
    print(f"Stage 3 PREVIEW: {archive}")
    print("Changed only 2 dynamic events + 3 non-shutdown announcements.")
    print("NO runtime tests; NO Nitrado access or deployment.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--source-dir", type=Path, default=None)
    args = parser.parse_args()
    build(args.output, args.source_dir)
