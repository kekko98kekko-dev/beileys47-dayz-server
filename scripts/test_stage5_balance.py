#!/usr/bin/env python3
"""Adversarial offline Stage 5 balance checks with only synthetic tampering."""
from __future__ import annotations

import json
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build_stage5_balance import DIST, build


def reject(action, phrase: str) -> None:
    try:
        action()
    except ValueError as err:
        assert phrase in str(err), (phrase, str(err))
    else:
        raise AssertionError("Stage 5 unsafe data accepted: " + phrase)


def test() -> None:
    # Real Stage1→2→3 generated outputs, still without actual game execution.
    with tempfile.TemporaryDirectory(prefix="beileys47-stage5-") as folder:
        tmp = Path(folder)
        for stage in ("stage1", "stage2", "stage3"):
            source = DIST / stage
            dest = tmp / stage
            (dest / "dayzOffline.enoch/db").mkdir(parents=True, exist_ok=True)
            for filename in ("change_report.json",):
                shutil.copyfile(source / filename, dest / filename)
            shutil.copyfile(source / "dayzOffline.enoch/db/types.xml",
                            dest / "dayzOffline.enoch/db/types.xml")
        result_path = tmp / "balance.json"
        report = build(tmp, result_path)
        assert json.loads(result_path.read_text(encoding="utf-8")) == report
        assert report["stage"] == 5
        assert report["stage3_types_byte_equal_stage2"] is True
        assert report["every_unselected_ce_class_unchanged_stage1_to_stage2"] is True
        assert report["in_game_spawn_rates_verified"] is False
        assert report["deployment_allowed"] is False
        assert report["nitrado_server_accessed"] is False
        assert report["object_spawner_included"] is False
        assert report["stage2_change_count"] == len(report["stage2_changed_classes"])
        assert report["stage2_change_count"] >= 5
        assert report["stage2_nominal_sum_delta"] >= 0

        stage2_xml = tmp / "stage2/dayzOffline.enoch/db/types.xml"
        original_xml = stage2_xml.read_bytes()
        tree = ET.parse(stage2_xml)
        root = tree.getroot()
        approved = {item["class"] for item in report["stage2_changed_classes"]}
        target = next(x for x in root.findall("type")
                      if x.get("name") not in approved and x.get("name") != "UndergroundStash")
        target.find("nominal").text = str(int(target.findtext("nominal")) + 1)
        tree.write(stage2_xml, encoding="utf-8", xml_declaration=True)
        # Must never write or replace a report for rejected data.
        result_path.unlink()
        reject(lambda: build(tmp, result_path), "Unauthorized Stage 2 CE change")
        assert not result_path.exists()
        stage2_xml.write_bytes(original_xml)

        stage3_xml = tmp / "stage3/dayzOffline.enoch/db/types.xml"
        original_stage3 = stage3_xml.read_bytes()
        stage3_xml.write_bytes(original_stage3 + b"\n")
        reject(lambda: build(tmp, result_path), "Stage 3 must inherit Stage 2")
        assert not result_path.exists()
        stage3_xml.write_bytes(original_stage3)

        ledger_path = tmp / "stage2/change_report.json"
        original_ledger = ledger_path.read_bytes()
        bad = json.loads(original_ledger)
        bad["additional_loot_and_stash_changes"][0]["nominal"][1] += 2
        ledger_path.write_text(json.dumps(bad), encoding="utf-8")
        reject(lambda: build(tmp, result_path), "ledger does not match XML")
        assert not result_path.exists()
        ledger_path.write_bytes(original_ledger)

        # A positive test again after all adversarial edits are removed.
        report2 = build(tmp, result_path)
        assert report2 == report

    print("PASS: Stage 5 exact inventory, no unapproved loot changes and fake ledger rejected.")
    print("NO in-game spawn rate, PS5 compatibility, Nitrado access or public deploy implied.")


if __name__ == "__main__":
    test()
