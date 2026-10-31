#!/usr/bin/env python3
"""Validate English public identity and Stage 3 language policy, offline only."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
profile=json.loads((ROOT/"config/server_identity_en.json").read_text(encoding="utf-8"))
rules=json.loads((ROOT/"config/stage3_rules.json").read_text(encoding="utf-8"))
assert profile["language"]=="en" and rules["audience_language"]=="en"
assert profile["map"]=="dayzOffline.enoch"
name=profile["server_hostname"]
description=profile["server_description"]
assert 10<len(name)<=100 and 10<len(description)<=200
assert "BEILEYS47" in name and "LIVONIA" in name and "NO SCHEDULED WIPES" in name
assert "International" in description and "All players welcome" in description
assert name.isascii() and description.isascii()
for flag in ("live_hostname_applied","live_description_applied","stage3_messages_enabled_on_live_server"):
    assert profile[flag] is False, "Never claim live activation before panel/console verification"
assert len(rules["messages"])==3
assert [m["kind"] for m in rules["messages"]]==["welcome","survival_hint","community_rule"]
for m in rules["messages"]:
    assert isinstance(m["text"],str) and m["text"].isascii() and 1<=len(m["text"])<=160
    assert m["text"].startswith(("Welcome to BEILEYS47","SURVIVAL WAR |"))
    assert m["delay"]==0 and m["repeat"] in (0,35,60)
    assert m["onconnect"] in (0,1)
assert [(m["repeat"],m["onconnect"]) for m in rules["messages"]]==[(0,1),(35,0),(60,0)]
assert not any("coming soon" in m["text"].lower() or "restart" in m["text"].lower() for m in rules["messages"])
print("PASS: International server identity and Stage 3 English announcement source. No live changes.")
