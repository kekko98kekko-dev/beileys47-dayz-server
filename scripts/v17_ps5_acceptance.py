#!/usr/bin/env python3
"""V17 offline PS5 acceptance gate. NEVER connects to Nitrado or modifies a server."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKS = {
    "ps5_connect": "Connect to Livonia from PS5/PS4 community list",
    "zona47_visual": "ZONA47: no floating or buried props; pathways and lines of fire usable",
    "bunker_access": "Existing bunker: outside fortification leaves a safe way in and out",
    "dolnik_two_tents": "Dolnik: exactly two intended medical/military tents visible",
    "loot_zona47": "ZONA47: economy-based loot observed in appropriate locations",
    "loot_bunker": "Bunker: economy-based loot observed in appropriate locations",
    "loot_dolnik": "Dolnik: medical and military loot observed after legitimate CE cycle",
    "infected_zona47": "ZONA47: local infected spawn and interact as intended",
    "infected_bunker": "Bunker: local infected spawn and interact as intended",
    "infected_dolnik": "Dolnik: local infected spawn and interact as intended",
    "night_cycle": "One full night sampled: accelerated nights, normal playable day",
    "surface_stash_persistence": "Surface container survives a planned safe restart",
    "buried_stash_persistence": "Buried stash survives a planned safe restart",
    "vehicle_persistence": "Vehicle position and fuel/inventory survive a planned safe restart",
    "performance": "No severe client stutter or server instability in actual multiplayer play",
}

# Feature gaps that cannot be inferred away from XML/JSON, even if every test passes.
UNDELIVERED = (
    "New underground scripted bunker interior",
    "Confirmed functioning red/blue-key locked shipping containers",
    "Script-controlled mobile infected hordes",
    "Automated in-game winner tracking and prize allocation",
    "Guaranteed immediate vehicle replacement after a truck drives away",
    "Exact calendar-day 15 replenishment of persistent plank piles",
)

def assess(document: dict) -> dict:
    """Conservatively infer a *playability test* outcome from explicit PS5 evidence."""
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("Expected schema_version 1")
    checks = document.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(CHECKS):
        missing = sorted(set(CHECKS) - set(checks or {})) if isinstance(checks, dict) else sorted(CHECKS)
        extra = sorted(set(checks) - set(CHECKS)) if isinstance(checks, dict) else []
        raise ValueError(f"Check IDs must match V17 exactly; missing={missing}; extra={extra}")

    normalized = {}
    for cid, label in CHECKS.items():
        item = checks[cid]
        if not isinstance(item, dict):
            raise ValueError(f"{cid}: expected object")
        state = item.get("result")
        if state not in {"passed", "failed", "not_tested"}:
            raise ValueError(f"{cid}: result must be passed, failed or not_tested")
        note = item.get("observation", "")
        if not isinstance(note, str):
            raise ValueError(f"{cid}: observation must be text")
        proof = item.get("evidence_ref", "")
        if not isinstance(proof, str):
            raise ValueError(f"{cid}: evidence_ref must be text")
        if state in {"passed", "failed"} and (len(note.strip()) < 10 or len(proof.strip()) < 3):
            raise ValueError(f"{cid}: recorded result requires observation and private evidence reference")
        normalized[cid] = {"label": label, "result": state}
    passed = sorted(k for k, v in normalized.items() if v["result"] == "passed")
    failed = sorted(k for k, v in normalized.items() if v["result"] == "failed")
    untested = sorted(k for k, v in normalized.items() if v["result"] == "not_tested")
    status = "failed" if failed else "not_verified" if untested else "accepted_on_recorded_ps5_evidence"
    return {
        "version": "V17-PS5-GATE",
        "scope": "manual PS5 gameplay evidence only; not a live Nitrado readback",
        "ps5_acceptance": status,
        "counts": {"passed": len(passed), "failed": len(failed), "not_tested": len(untested)},
        "failed": failed,
        "not_tested": untested,
        "all_requested_features_complete": False,
        "unavailable_or_unverified_advanced_features": list(UNDELIVERED),
        "no_wipe_verified": False,
        "note": "File uploads alone cannot prove persistence/no wipe, world collisions, key mechanics or game performance.",
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("evidence", type=Path, help="LOCAL private JSON evidence file; do not commit private data")
    args = ap.parse_args()
    try:
        record = json.loads(args.evidence.read_text(encoding="utf-8"))
        report = assess(record)
    except (OSError, ValueError, json.JSONDecodeError) as ex:
        print("V17 FAIL CLOSED:", str(ex), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["ps5_acceptance"] == "failed" else 0

if __name__ == "__main__":
    raise SystemExit(main())
