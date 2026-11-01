#!/usr/bin/env python3
"""V19 safe maintenance schedule: creates GitHub reminders, NEVER edits DayZ/Nitrado."""
from __future__ import annotations
import argparse,datetime as dt,json,os,urllib.error,urllib.request
from typing import Iterable
ANCHOR=dt.date(2026,10,31)
EXPIRY=dt.date(2026,11,30)
PREFIX="BEILEYS47 PLANK INSPECTION "
INTERVAL_DAYS=15

def due_date(today:dt.date,anchor:dt.date=ANCHOR,expiry:dt.date=EXPIRY)->bool:
    delta=(today-anchor).days
    return 0<delta and delta%INTERVAL_DAYS==0 and today<=expiry

def planned_issue(today:dt.date,existing_titles:Iterable[str]):
    if not due_date(today):return None
    title=PREFIX+today.isoformat()
    if title in existing_titles:return None
    body=f"""# BEILEYS47 | 15-day wooden-plank inspection

**Scheduled review:** {today.isoformat()} (15-day cadence from 31 October 2026).
**Map:** Livonia (PS5 / PS4).

**THIS IS A MAINTENANCE REMINDER, NOT AN IN-GAME AUTOMATIC REFILL.**

- Check existing wooden-plank piles in game before making any edits.
- Record location, remaining quantity and whether the pile is a new CE spawn or an existing persistent one.
- Existing V15/V18 types.xml requests 100% quantity only on **newly created** piles; it does NOT replenish persistent depleted piles to 252/252 on a calendar date.
- If stock is low, plan a supported manual admin replenishment or game-world maintenance (only with actual world/player safety and owner approval). Never wipe for this.
- Confirm real backup capability, whether players are connected, and any impact on bases and vehicles before any Nitrado operation.

**Important:** this GitHub workflow does not access Nitrado, change loot quantities, restart the server or identify player inventories. Only a person can verify the physical in-game pile stock on PS5.
"""
    return title,body

def request_json(url:str,token:str,method:str="GET",payload:dict|None=None):
    headers={"Accept":"application/vnd.github+json","Authorization":"Bearer "+token,
             "User-Agent":"BEILEYS47-v19-ops","X-GitHub-Api-Version":"2022-11-28"}
    data=None if payload is None else json.dumps(payload).encode("utf-8")
    if data is not None:headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,headers=headers,method=method,data=data)
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date",help="UTC calendar date YYYY-MM-DD; defaults to today")
    p.add_argument("--post",action="store_true",help="Create a reminder GitHub Issue, never changes Nitrado")
    args=p.parse_args()
    today=dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone.utc).date()
    if not due_date(today):
        print(json.dumps({"date":today.isoformat(),"due":False,"kind":"informational_only"}))
        return
    if not args.post:
        title,_=planned_issue(today,())
        print(json.dumps({"date":today.isoformat(),"due":True,"would_create":title,
                          "nitrado_changes":False,"in_game_refill":False}))
        return
    token=os.environ.get("GITHUB_TOKEN","")
    repo=os.environ.get("GITHUB_REPOSITORY","")
    if not token or not repo or "/" not in repo:
        raise ValueError("GITHUB_TOKEN and GITHUB_REPOSITORY required")
    api="https://api.github.com/repos/"+repo+"/issues"
    # Exact-date deduplication (schedule is at most one event per day), pagination.
    existing=set()
    for page in range(1,11):
        arr=request_json(api+f"?state=all&per_page=100&page={page}",token)
        if not isinstance(arr,list):raise ValueError("Unexpected issues response")
        existing.update(str(x.get("title","")) for x in arr if isinstance(x,dict))
        if len(arr)<100:break
    else:
        raise ValueError("Issue listing too large; fail closed rather than duplicate")
    issue=planned_issue(today,existing)
    if issue is None:
        print(json.dumps({"date":today.isoformat(),"due":True,"created":False,"reason":"already_exists"}))
        return
    title,body=issue
    created=request_json(api,token,method="POST",payload={"title":title,"body":body})
    print(json.dumps({"created":True,"url":created.get("html_url"),
                      "nitrado_changes":False,"in_game_refill":False}))

if __name__=="__main__":
    main()
