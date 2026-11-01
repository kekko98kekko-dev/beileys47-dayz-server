#!/usr/bin/env python3
"""V24 public terrain-data discovery. No Nitrado, no account, no browser automation.

Read-only scans first party DZPage public HTML/JS asset references and reports
whether an elevation raster can be fetched via documented/public URL.
Does not pretend that a JS config key supplies a verified elevation sample.
"""
from __future__ import annotations
import html.parser,json,re,urllib.parse,urllib.request
from pathlib import Path

BASE="https://dzpage.com/en/map-editor"
OUT=Path("deploy/v24/PUBLIC_TERRAIN_SOURCE_PROBE.json")
MAX_BYTES=3500000
class Scripts(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="script" and d.get("src"):self.scripts.append(d["src"])
        if tag=="link" and d.get("href") and (d.get("rel","") in ("preload","modulepreload") or "script" in d.get("as","")):
            self.links.append(d["href"])

def fetch(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!="dzpage.com":
        raise ValueError("Only first-party public dzpage.com assets allowed")
    req=urllib.request.Request(url,headers={"User-Agent":"BEILEYS47-Research/1.0 (public map metadata; read-only)"})
    with urllib.request.urlopen(req,timeout=18) as resp:
        return resp.read(MAX_BYTES+1)[:MAX_BYTES]

def main():
    result={"scope":"public_dzpage_assets_only","game_world_modified":False,
      "nitrado_called":False,"exact_terrain_elevation_samples_collected":0,
      "verified_complete_site_survey":False,
      "source_url":BASE,"scripts":[],"possible_height_data_urls":[],"errors":[]}
    try:
        raw=fetch(BASE)
        if len(raw)>=MAX_BYTES:raise ValueError("HTML truncated")
        parser=Scripts()
        parser.feed(raw.decode("utf-8","replace"))
        paths=list(dict.fromkeys(parser.scripts+parser.links))
        result["html_bytes"]=len(raw)
        result["script_paths_found"]=len(paths)
        for rel in paths[:25]:
            url=urllib.parse.urljoin(BASE,rel)
            if urllib.parse.urlsplit(url).hostname!="dzpage.com":continue
            item={"path":urllib.parse.urlsplit(url).path}
            try:
                data=fetch(url)
                item["downloaded_bytes"]=len(data)
                text=data.decode("utf-8","replace")
                keywords=["heightmap","terrainheight","heightdata","surfacey","enoch","livonia","heighttile","terrain.bin","height.bin"]
                item["keyword_counts"]={k:len(re.findall(k,text,re.I)) for k in keywords if re.search(k,text,re.I)}
                item["keyword_context"]={}
                for key in ("heightmap","surfacey","enoch","terrainheight","livonia"):
                    hits=list(re.finditer(key,text,re.I))[:4]
                    if hits:
                        item["keyword_context"][key]=[
                          text[max(0,m.start()-95):min(len(text),m.end()+140)].replace("\\n"," ") for m in hits
                        ]
                # Only public, first-party filenames for height/terrain assets.
                item["candidate_network_paths"]=[
                    x for x in dict.fromkeys(re.findall(r'/[A-Za-z0-9_./-]{6,110}',text))
                    if any(z in x.lower() for z in ("height","enoch","terrain","livonia"))][:20]
                # Do not copy source JS; record candidate URL-shaped strings only.
                candidates=re.findall(r'["\x27]([^"\x27]{4,200}(?:height|terrain|enoch|livonia)[^"\x27]{0,100})["\x27]',text,re.I)
                item["candidate_asset_strings"]=[s for s in dict.fromkeys(candidates) if
                    (s.startswith("/") or s.startswith("https://dzpage.com/")) and len(s)<130][:20]
                for candidate in item["candidate_asset_strings"]:
                    if "height" in candidate.lower() or "terrain" in candidate.lower():
                        result["possible_height_data_urls"].append(candidate)
            except Exception as exc:
                item["error"]=str(exc)[:150]
            result["scripts"].append(item)
    except Exception as exc:
        result["errors"].append(str(exc)[:220])
    result["possible_height_data_urls"]=list(dict.fromkeys(result["possible_height_data_urls"]))[:30]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
