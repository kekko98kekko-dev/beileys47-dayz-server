#!/usr/bin/env python3
"""Pure offline tests for V19, no GitHub write and no Nitrado access."""
import datetime as dt
from v19_plank_maintenance import ANCHOR,EXPIRY,PREFIX,due_date,planned_issue

def main():
    assert ANCHOR==dt.date(2026,10,31)
    assert EXPIRY==dt.date(2026,11,30)
    days=[ANCHOR+dt.timedelta(days=i) for i in range(0,40)
          if due_date(ANCHOR+dt.timedelta(days=i))]
    assert days==[dt.date(2026,11,15),dt.date(2026,11,30)],days
    assert not due_date(dt.date(2026,10,31))
    assert not due_date(dt.date(2026,11,29))
    assert not due_date(dt.date(2026,12,15))
    issue=planned_issue(days[0],set())
    assert issue and issue[0]==PREFIX+"2026-11-15"
    assert "NOT AN IN-GAME AUTOMATIC REFILL" in issue[1]
    assert "does not access Nitrado" in issue[1]
    assert planned_issue(days[0],{issue[0]}) is None
    assert planned_issue(days[0]+dt.timedelta(days=1),set()) is None
    print("PASS V19: 15-day reminders only Nov 15/30, no duplicates, no false in-game refill claims")
if __name__=="__main__":main()
