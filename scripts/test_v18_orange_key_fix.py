#!/usr/bin/env python3
"""Offline V18 safety tests: never contacts Nitrado."""
from __future__ import annotations
from v18_orange_key_fix import patch,sha,NitradoError
import xml.etree.ElementTree as ET
def base():
    return ("""<?xml version="1.0"?><types>
<type name="GunCase_Orange"><nominal>2</nominal><min>1</min></type>
<type name="GunCase_Black"><nominal>4</nominal><min>2</min></type>
<type name="GunCase_White"><nominal>4</nominal><min>2</min></type>
<type name="GunCaseKeys_Blue"><nominal>2</nominal><min>1</min></type>
<type name="GunCaseKeys_Red"><nominal>2</nominal><min>1</min></type>
<type name="GunCaseKeys_Orange"><nominal>0</nominal><min>0</min><usage name="Military"/></type>
</types>""").encode()
def expect_blocked(blob):
    try:patch(blob)
    except (ValueError,NitradoError,ET.ParseError):pass
    else:raise AssertionError("Unsafe altered content was accepted")
def main():
    before=base()
    after,changed=patch(before)
    assert changed and len(after)>len(before)
    assert patch(after)==(after,False)
    assert sha(before)!=sha(after)
    assert b'<nominal>2</nominal><min>1</min><usage name="Military"/>' in after
    assert after.count(b'GunCaseKeys_Orange')==1
    assert after.replace(b'<nominal>2</nominal><min>1</min><usage name="Military"/>',
                         b'<nominal>0</nominal><min>0</min><usage name="Military"/>')==before
    expect_blocked(before.replace(b'<usage name="Military"/>',b''))
    expect_blocked(before.replace(b'<nominal>0</nominal><min>0</min><usage',
                                  b'<nominal>999</nominal><min>0</min><usage'))
    expect_blocked(before.replace(b'<nominal>2</nominal><min>1</min></type>',
                                  b'<nominal>0</nominal><min>0</min></type>',1))
    expect_blocked(before.replace(b'</types>',before.split(b'<type name="GunCaseKeys_Orange">')[1].split(b'</type>')[0]+b'</types>'))
    print("PASS: V18 orange key minimal byte patch, idempotency and fail-closed invariants")
if __name__=="__main__":main()
