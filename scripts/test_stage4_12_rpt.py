#!/usr/bin/env python3
"""Stage 4.12: synthetic RPT failures and privacy regression tests."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from triage_stage4_12_rpt import (
    ROOT, OUTPUT, analyze_lines, analyze_file, known_candidates, run
)

def must_fail(fn,substring:str)->None:
    try:fn()
    except (ValueError,AssertionError) as e:
        assert substring in str(e),(substring,str(e))
    else:raise AssertionError("Expected failure: "+substring)

def test()->None:
    names=known_candidates()
    assert len(names)==13 and "Land_Mil_GuardBox_Green" in names
    blank=run(None,OUTPUT)
    assert blank["stage"]=="4.12"
    assert blank["status"]=="NO_REAL_LOG_AVAILABLE"
    assert blank["evidence_kind"]=="NO_LOG_PROVIDED"
    assert blank["official_object_spawner_failure_lines"]==0
    assert blank["actual_successfully_spawned_objects_count"] is None
    assert blank["candidate_console_spawnability_confirmed_count"]==0
    assert blank["deployment_allowed"] is False
    assert json.loads(OUTPUT.read_text(encoding="utf-8"))==blank

    # Synthetic fixture (NEVER real player data). Inject a known candidate,
    # unknown arbitrary object, and a similar but non-identical classname.
    private_marker="SYNTHETIC_IP_192_0_2_5_DO_NOT_INCLUDE"
    lines=[
        "Starting synthetic test log",
        f"20:00:00 Object spawner failed to spawn Land_Mil_GuardBox_Green {private_marker}",
        "Object Spawner Failed To Spawn 'Land_Ghost_Object'",
        "Object spawner failed to spawn Land_Mil_GuardBox_Green_extra",
        "Loaded cfggameplay.json (synthetic text: not evidence of actual load)",
        "objectSpawnersArr: fake/example",
        "Object spawner: startup (no proof of spawn)",
        private_marker,
    ]
    report=analyze_lines(lines,names,"USER_SUPPLIED_PRIVATE_RPT")
    assert report["official_object_spawner_failure_lines"]==3
    assert report["official_failure_lines_with_no_recognized_candidate"]==2
    assert report["source_known_candidate_mentions_on_failure_lines"]=={"Land_Mil_GuardBox_Green":1}
    assert report["heuristic_keyword_line_counts_NOT_ERRORS"]["OBJECT_SPAWNER_REFERENCE"]==1
    assert report["heuristic_keyword_line_counts_NOT_ERRORS"]["CFG_GAMEPLAY_REFERENCE"]==1
    assert report["inspected_line_count"]==len(lines)
    assert report["actual_successfully_spawned_objects_count"] is None
    assert report["deployment_allowed"] is False
    assert report["missing_error_is_NOT_proof_of_success"] is True
    assert report["known_names_are_NOT_certified_to_spawn"] is True
    assert report["raw_log_contents_in_report"] is False
    rendered=json.dumps(report)
    assert private_marker not in rendered
    assert "Land_Ghost_Object" not in rendered
    assert "Land_Mil_GuardBox_Green_extra" not in rendered
    assert report["diagnostic_examples_NO_RAW_TEXT"][0]["line_number"]==2
    assert len(report["diagnostic_examples_NO_RAW_TEXT"])==3

    empty=analyze_lines(["No errors shown in incomplete synthetic file"],names,"USER_SUPPLIED_PRIVATE_RPT")
    assert empty["official_object_spawner_failure_lines"]==0
    assert empty["actual_successfully_spawned_objects_count"] is None
    assert empty["PS4_PS5_runtime_approved"] is False

    must_fail(lambda:analyze_lines(["Object spawner failed to spawn"],names,"NO_LOG_PROVIDED"),
              "Unprovided log")
    must_fail(lambda:analyze_lines(["A"*200_001],names,"USER_SUPPLIED_PRIVATE_RPT"),
              "line exceeds")
    with tempfile.TemporaryDirectory(prefix="z47-private-test-not-upload-") as temp:
        base=Path(temp)
        fake=base/"fake_dayz.RPT"
        fake.write_text("\n".join(lines),encoding="utf-8")
        parsed=analyze_file(fake,names)
        assert parsed==report
        output=base/"private_summary.json"
        safe=run(fake,output)
        assert safe==report
        assert json.loads(output.read_text(encoding="utf-8"))==report
        assert private_marker not in output.read_text(encoding="utf-8")
        must_fail(lambda:run(fake,ROOT/"dist/stage4_12_rpt_diagnostics/private_bad.json"),
                  "Private log reports cannot be written")
        utf16=base/"utf16.RPT"
        utf16.write_bytes(b"A\x00B\x00")
        must_fail(lambda:analyze_file(utf16,names),"Unsupported binary")
    assert OUTPUT.exists()
    assert private_marker not in OUTPUT.read_text(encoding="utf-8")
    print("PASS: Stage 4.12 exact official RPT marker, false-positive, unknown class and privacy tests.")
    print("NO real server logs used; only an intentionally EMPTY audit is published.")

if __name__=="__main__":test()
