#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from v37_zone47_infected_patches import patch,already_installed,NitradoError
def base():
    return b'''<?xml version="1.0" encoding="UTF-8"?>
<territory-type><territory color="12">
<zone name="InfectedArmy" x="7100.0" z="6965.0" r="95" dmin="12" dmax="18"/>
<zone name="InfectedArmy" x="9022.5" z="7457.9" r="85" dmin="10" dmax="14"/>
<zone name="InfectedMedic" x="11490.0" z="461.0" r="75" dmin="6" dmax="10"/>
</territory></territory-type>'''
def events():return b'<events><event name="InfectedArmy"/><event name="InfectedMedic"/></events>'
def reject(old,ev):
    try:patch(old,ev)
    except (NitradoError,ET.ParseError,ValueError):return
    raise AssertionError("Unsafe XML accepted")
def main():
    old=base();new,count=patch(old,events())
    assert count==3
    assert len(ET.fromstring(new).findall(".//zone"))==5
    assert new.startswith(old[:50])
    assert b'</territory-type>' in new
    assert b'x="8960.0" z="7810.0"' in new
    assert b'x="9040.0" z="7730.0"' in new
    assert not already_installed(old)
    assert already_installed(new)
    reject(new,events())
    reject(old,b"<events></events>")
    reject(old.replace(b'9022.5',b'9022.6'),events())
    reject(old.replace(b'</territory></territory-type>',
      b'<zone name="InfectedArmy" x="8955.0" z="7810.0"/></territory></territory-type>'),events())
    try: already_installed(new.replace(b'dmin="5"',b'dmin="4"',1))
    except NitradoError: pass
    else: raise AssertionError("Wrong settings in already-installed zone accepted")
    print("PASS V37: 2 moderate vanilla patrol zones, prior zones preserved, XML fail-closed")
if __name__=="__main__":main()
