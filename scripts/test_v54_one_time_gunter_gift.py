#!/usr/bin/env python3
"""V54 strictly offline one-time vehicle lifecycle regression checks."""
from __future__ import annotations
import xml.etree.ElementTree as ET
from test_v53_gunter_gift import sample
from v54_one_time_gunter_gift import arm,disarm,EVENT,FILES,RESTOCK_SECONDS,parse
from v53_gunter_gift import CARGO,CAR,patch_for_postread

def main():
    original,types=sample()
    pending,details=arm(original,types)
    assert pending is not None
    assert details["configured_cargo_entries"]==10
    live_e=parse(pending[FILES[0]]).find(f"event[@name='{EVENT}']")
    assert live_e.findtext("restock")==str(RESTOCK_SECONDS)
    assert live_e.findtext("active")=="1"
    assert live_e.findtext("saferadius")=="0"
    assert patch_for_postread(pending)[0] is True
    disabled=disarm(pending,original)
    e=parse(disabled[FILES[0]]).find(f"event[@name='{EVENT}']")
    assert all(e.findtext(k)=="0" for k in ("active","nominal","min","max"))
    assert disabled[FILES[2]]==original[FILES[2]]
    assert disabled[FILES[1]]==pending[FILES[1]]
    assert parse(disabled[FILES[0]]).find("event[@name='VehicleOther']") is not None
    assert parse(disabled[FILES[2]]).find("type[@name='Truck_01_Covered']") is not None
    # Disabling is mandatory, not an optional deferred state for final success.
    assert patch_for_postread(disabled)[0] is False
    # Reapplying same live gift should not silently create duplicates.
    from v53_gunter_gift import patch
    try:
        patch(disabled,types)
        raise AssertionError("V54 disabled event re-armed unexpectedly")
    except Exception as exc:
        assert "Existing V53 event" in str(exc)
    print("V54 PASS: 1 new fixed-event, temporary black-car cargo, 7-day restock safety,")
    print("V54 PASS: then active/nominal/min/max=0, global car profile bytes restored, no unrelated edits.")
    print("V54 NOTE: physical vehicle and fuel levels require console field test.")

if __name__=="__main__":main()
