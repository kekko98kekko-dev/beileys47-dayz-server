#!/usr/bin/env python3
from v60_correct_stale_server_messages import REPLACE,patch,fields
def main():
    msgs=[("Keep one unchanged.",15),("Another unchanged.",30),
          ("Third remains.",45)]+[(old,75) for old in REPLACE]
    original=("<messages>"+''.join(
       "<message><delay>0</delay><repeat>"+str(delay)+"</repeat>"
       "<deadline>0</deadline><onconnect>0</onconnect><shutdown>0</shutdown>"
       "<text>"+msg+"</text></message>" for msg,delay in msgs)+"</messages>").encode()
    updated,already=patch(original)
    assert not already
    same,done=patch(updated)
    assert done and same==updated
    a=[m.findtext("text") for m in fields(updated)[1]]
    assert a[:3]==[m for m,_ in msgs[:3]]
    assert a[3:]==list(REPLACE.values())
    assert len(fields(updated)[1])==6
    assert original!=updated
    print("V60 PASS: 3 exact obsolete announcements updated; times, fields, other 3 remain unchanged")
if __name__=="__main__":main()
