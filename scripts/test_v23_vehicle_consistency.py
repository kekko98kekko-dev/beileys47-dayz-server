#!/usr/bin/env python3
"""Pure, Nitrado-free tests of one-field motorcycle CE correction."""
from v23_vehicle_consistency import patch,NitradoError
from xml.etree import ElementTree as ET
def base():
    return (b'<events><event name="VehicleMotorbike"><nominal>12</nominal><min>5</min><max>11</max>'
            b'<children><child type="Motorbike_01"/></children></event>'
            b'<event name="VehicleTruck01"><nominal>10</nominal><min>6</min><max>12</max></event></events>')
def reject(blob):
    try:patch(blob)
    except (NitradoError,ValueError,ET.ParseError):pass
    else:raise AssertionError("Invalid motorcycle event accepted")
def main():
    old=base();new=patch(old)
    assert len(new)==len(old)
    assert new.count(b'<nominal>11</nominal>')==1
    assert new.replace(b'<nominal>11</nominal>',b'<nominal>12</nominal>',1)==old
    assert ET.fromstring(new).find("event[@name='VehicleTruck01']/nominal").text=="10"
    reject(new) # idempotence must fail
    reject(old.replace(b'<max>11</max>',b'<max>12</max>'))
    reject(old.replace(b'<min>5</min>',b'<min>0</min>'))
    reject(old.replace(b'</events>',b'<event name="VehicleMotorbike"><nominal>12</nominal></event></events>'))
    print("PASS V23: exactly one CE field corrected, no silent change, strict stop on mismatches")
if __name__=="__main__":main()
