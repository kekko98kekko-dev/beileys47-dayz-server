#!/usr/bin/env python3
"""Offline V21 tests; never access GitHub/Nitrado network."""
from v21_safe_discovery_messages import patch,MESSAGES,NitradoError
from xml.etree import ElementTree as ET
def sample(count=4):
    root=ET.Element("messages")
    for i in range(count):
        m=ET.SubElement(root,"message")
        for k,v in [("delay","0"),("repeat",str(30+i*10)),("deadline","0"),
                    ("onconnect","0"),("shutdown","0"),("text","Existing greeting "+str(i))]:
            ET.SubElement(m,k).text=v
    return b'<?xml version="1.0"?><messages>'+b''.join(ET.tostring(x) for x in root)+b'</messages>'
def must_fail(data):
    try: patch(data)
    except (ValueError,NitradoError,ET.ParseError):return
    raise AssertionError("Unsafe XML unexpectedly accepted")
def main():
    old=sample()
    new=patch(old)
    assert new.startswith(old[:20]) and new!=old
    root=ET.fromstring(new)
    assert len(root.findall("message"))==6
    assert root.findall("message")[:4] and len(MESSAGES)==2
    assert [v.findtext("text") for v in root.findall("message")[:4]]==[
        "Existing greeting "+str(i) for i in range(4)]
    assert [v.findtext("text") for v in root.findall("message")[4:]]==[x[1] for x in MESSAGES]
    assert max(len(t[1]) for t in MESSAGES)<=160
    assert all(v.findtext("shutdown")=="0" for v in root.findall("message"))
    old_long=old.replace(b"Existing greeting 0",b"Existing greeting 0"+b"x"*180)
    new_long=patch(old_long)
    assert len(ET.fromstring(new_long).findall("message"))==6
    assert b"Existing greeting 0"+b"x"*180 in new_long
    must_fail(new)   # duplicate or changed source
    must_fail(sample(3))
    must_fail(sample(5))
    must_fail(old.replace(b'<shutdown>0</shutdown>',b'<shutdown>1</shutdown>',1))
    must_fail(b"<wrong></wrong>")
    print("PASS V21: 4 preexisting messages unchanged, 2 new messages, DayZ 160-char limit, fail closed")
if __name__=="__main__":main()
