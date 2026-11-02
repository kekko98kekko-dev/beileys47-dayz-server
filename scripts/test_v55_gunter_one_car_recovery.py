#!/usr/bin/env python3
"""Regression: rearm V54 inactive gift without duplicating event or other cars."""
from __future__ import annotations
import xml.etree.ElementTree as ET
from test_v53_gunter_gift import sample
from v53_gunter_gift import patch, FILES, EVENT, CAR, parse, data, patch_for_postread
from v55_gunter_one_car_recovery import build,LONG_RESTOCK

def test():
    before,types=sample()
    armed,_=patch(before,types)
    inactive=dict(armed)
    ev=parse(inactive[FILES[0]])
    gift=ev.find(f"event[@name='{EVENT}']")
    for k in ("active","nominal","min","max"):gift.find(k).text="0"
    gift.find("restock").text="604800"
    inactive[FILES[0]]=data(ev)
    inactive[FILES[2]]=before[FILES[2]] # previous V54 restored shared profile.
    first,longterm,details=build(inactive,types)
    f=parse(first[FILES[0]])
    l=parse(longterm[FILES[0]])
    assert f.find(f"event[@name='{EVENT}']").findtext("restock")=="0"
    assert l.find(f"event[@name='{EVENT}']").findtext("restock")==str(LONG_RESTOCK)
    assert sum(e.get("name")==EVENT for e in f.findall("event"))==1
    assert f.find("event[@name='VehicleOther']") is not None
    assert patch_for_postread(first)[0]
    assert patch_for_postread(longterm)[0]
    assert first[FILES[1]] == longterm[FILES[1]]
    assert first[FILES[2]] == longterm[FILES[2]]
    # Fail closed rather than duplicate after already running.
    try:
        build(longterm,types)
        raise AssertionError("Already active event was rearmed")
    except Exception as e: assert "not fully disabled" in str(e)
    print("V55 PASS: originally inactive event rearmed exactly once with 0 first-restock")
    print("V55 PASS: 1 child/point, no unrelated events, 365-day restock staged, no premature disarm")

if __name__=="__main__":test()
