#!/usr/bin/env python3
"""V56 regressions: only the V55 Gunter gift restock tag may change."""
from __future__ import annotations
from test_v53_gunter_gift import sample
from v53_gunter_gift import EVENT, FILES, patch as v53_patch,parse,data
from v56_gunter_max_safe_restock import patch, OLD, NEW, inspected_event

def test():
    before,types=sample()
    armed,_=v53_patch(before,types)
    root=parse(armed[FILES[0]])
    ev=root.find(f"event[@name='{EVENT}']")
    ev.find("restock").text=str(OLD)
    blob=data(root)
    point=armed[FILES[1]]
    updated,already=patch(blob,point)
    assert not already
    assert updated!=blob
    assert inspected_event(updated).findtext("restock")==str(NEW)
    assert updated.replace(str(NEW).encode(),str(OLD).encode(),1)==blob
    same,already2=patch(updated,point)
    assert already2 and same==updated
    assert b'event name="VehicleOther"' in same
    # Unexpected operator values must never be silently replaced.
    rogue=blob.replace(str(OLD).encode(),b"900",1)
    try:
        patch(rogue,point)
        raise AssertionError("Unknown restock was accepted")
    except Exception as ex:assert "not V55 expected" in str(ex)
    # Must not update if someone removed/replaced the gift point.
    missing=point.replace(EVENT.encode(),b"OtherEvent")
    try:
        patch(blob,missing)
        raise AssertionError("Position drift was accepted")
    except Exception as ex:assert "point disappeared" in str(ex)
    assert NEW <= 2**31-1
    assert 100*365*86400 > 2**31-1
    print("V56 PASS: only one tag changed byte-for-byte; max safe signed int32")
    print("V56 PASS: existing event, exact location, idempotency, drift fail-closed")
if __name__=="__main__":test()
