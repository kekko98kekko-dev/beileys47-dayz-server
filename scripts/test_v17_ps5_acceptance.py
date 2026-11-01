#!/usr/bin/env python3
"""Adversarial, Nitrado-free tests for the V17 PS5 acceptance gate."""
from __future__ import annotations

import copy
from v17_ps5_acceptance import CHECKS, assess

def run() -> None:
    base = {"schema_version": 1, "checks": {
        key: {"result": "not_tested", "observation": "", "evidence_ref": ""} for key in CHECKS
    }}
    empty = assess(base)
    assert empty["ps5_acceptance"] == "not_verified" and empty["counts"]["not_tested"] == len(CHECKS)
    assert empty["all_requested_features_complete"] is False
    assert empty["no_wipe_verified"] is False

    validated = copy.deepcopy(base)
    for v in validated["checks"].values():
        v.update(result="passed", observation="Observed directly on PS5, with recording.", evidence_ref="private/local.mp4")
    fully_passed = assess(validated)
    assert fully_passed["ps5_acceptance"] == "accepted_on_recorded_ps5_evidence"
    assert fully_passed["all_requested_features_complete"] is False
    assert fully_passed["no_wipe_verified"] is False
    failed = copy.deepcopy(validated)
    failed["checks"]["bunker_access"]["result"] = "failed"
    assert assess(failed)["ps5_acceptance"] == "failed"

    invalid = []
    sample = copy.deepcopy(base); del sample["checks"]["bunker_access"]; invalid.append(sample)
    sample = copy.deepcopy(base); sample["checks"]["typo"] = {"result": "passed"}; invalid.append(sample)
    sample = copy.deepcopy(base); sample["checks"]["night_cycle"]["result"] = "passed"; invalid.append(sample)
    sample = copy.deepcopy(base); sample["checks"]["night_cycle"]["result"] = "true"; invalid.append(sample)
    sample = copy.deepcopy(base); sample["schema_version"] = 99; invalid.append(sample)
    sample = copy.deepcopy(base); sample["schema_version"] = True; invalid.append(sample)
    for doc in invalid:
        try: assess(doc)
        except ValueError: pass
        else: raise AssertionError("Invalid report unexpectedly accepted")
    print(f"PASS V17: {len(CHECKS)} critical checks, fail-closed evidence, no unsupported claims")

if __name__ == "__main__":
    run()
