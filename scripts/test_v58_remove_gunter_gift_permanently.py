#!/usr/bin/env python3
from __future__ import annotations
import xml.etree.ElementTree as ET
from test_v53_gunter_gift import sample
from v53_gunter_gift import patch as create_gift,parse,data,FILES,EVENT,CAR
from v58_remove_gunter_gift_permanently import prune_config,verify_removed

def main():
    original,types=sample()
    live,details=create_gift(original,types)
    ev=parse(live[FILES[0]])
    ev.find(f"event[@name='{EVENT}']").find("restock").text="2147483647"
    live[FILES[0]]=data(ev)
    edited=prune_config(live,original,types)
    verify_removed(edited,original)
    assert all(edited[f]!=live[f] for f in FILES)
    assert parse(edited[FILES[0]]).find(f"event[@name='{EVENT}']") is None
    assert parse(edited[FILES[1]]).find(f"event[@name='{EVENT}']") is None
    assert ET.tostring(parse(edited[FILES[2]]).find(f"type[@name='{CAR}']"))==ET.tostring(parse(original[FILES[2]]).find(f"type[@name='{CAR}']"))
    assert parse(edited[FILES[0]]).find("event[@name='VehicleOther']") is not None
    assert parse(edited[FILES[2]]).find("type[@name='Truck_01_Covered']") is not None
    try:
        prune_config(edited,original,types)
        raise AssertionError("already removed config accepted")
    except Exception as e:
        assert "a gift source/point" in str(e).lower() or "gift source/point" in str(e).lower() or "gift" in str(e).lower()
    print("V58 PASS: exact original black-Gunter profile restored, custom event/point deleted")
    print("V58 PASS: unrelated vehicle event and truck profile unchanged, no wipe/persistence edits")
if __name__=="__main__":main()
