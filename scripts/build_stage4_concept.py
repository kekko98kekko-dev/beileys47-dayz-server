#!/usr/bin/env python3
"""Validate and visualize Stage 4 ZONA 47 (DESIGN ONLY, NOT GAME FILES).

No Nitrado, network, DayZ launch, real world coordinates or deployment.
Creates a conceptual SVG, JSON audit report and deliberately non-installable ZIP.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import zipfile
from collections import Counter, deque
from pathlib import Path

from zip_deterministic import add_bytes
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "config/stage4_zone47_blueprint.json"
MICRO = ROOT / "config/stage4_zone47_micro_layout.json"
OUT = ROOT / "dist/stage4"
ZIP = OUT / "beileys47-zone47-design-only.zip"

def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def two_separate_routes(graph: dict[str, set[str]], source: str, target: str) -> bool:
    """Find two paths with no shared INTERMEDIATE nodes (excluding endpoints)."""
    routes: list[list[str]] = []
    stack = [(source, [source])]
    while stack:
        node, path = stack.pop()
        if node == target:
            routes.append(path)
            continue
        for nxt in sorted(graph[node]):
            if nxt not in path:
                stack.append((nxt, path + [nxt]))
    for a, b in itertools.combinations(routes, 2):
        if not set(a[1:-1]) & set(b[1:-1]):
            return True
    return False

def validate(bp: dict, micro: dict) -> dict:
    check(bp["stage"] == 4 and micro["stage"] == 4, "Wrong stage")
    check(bp["codename"] == micro["codename"] == "ZONA 47", "Wrong codename")
    check(bp["status"] == "DESIGN_ONLY_NOT_INSTALLABLE", "Unsafe blueprint status")
    check(micro["status"] == "SCHEMATIC_ONLY_NOT_OBJECT_SPAWNER_JSON", "Unsafe micro status")
    check(bp["map"] == "Livonia" and set(bp["platforms"]) == {"PS4", "PS5"}, "Wrong map/platform")
    g = bp["coordinate_system"]
    check(g["unit"] == "local_metres_xz" and not g["terrain_surveyed"], "Real terrain claims are forbidden")
    check(all(g[k] is None for k in ("world_x","world_y","world_z","yaw_degrees")), "World anchor must be null")
    check(micro["selected_map_anchor"] is None and not micro["ground_elevations_known"], "Unsurveyed location cannot export")

    zones = bp["zones"]
    ids = [z["id"] for z in zones]
    check(len(ids) == 8 and len(set(ids)) == 8, "8 distinct playable zones required")
    check({"checkpoint","woods","service","barracks","logistics","hq","ridge","secret"} == set(ids), "Unexpected zones")
    targets = bp["objectives"]
    budget = sum(z["object_budget"] for z in zones)
    planned = sum(z["prototype_count"] for z in zones)
    check(20 <= planned <= 30 and targets["first_micro_prototype_min"] <= planned <= targets["first_micro_prototype_max"], "Micro budget invalid")
    check(budget <= targets["max_visual_entities_soft"] <= 100, "Visual object soft budget exceeded")
    check(targets["real_console_fps_threshold"] is None, "FPS not measured")
    check(all(z["object_budget"] >= z["prototype_count"] >= 1 for z in zones), "Invalid zone object budgets")
    check(all(0 <= z["x"] <= g["width"] and 0 <= z["z"] <= g["height"] for z in zones), "Zone outside concept bounds")
    entrances = bp["entrances"]
    entrance_ids = [x["id"] for x in entrances]
    check(len(entrance_ids) == len(set(entrance_ids)) == 3, "Three distinct access routes required")
    check(all(x["to"] in ids and 0 <= x["x"] <= g["width"] and 0 <= x["z"] <= g["height"] for x in entrances), "Invalid entry")
    graph: dict[str,set[str]] = {i: set() for i in ids+entrance_ids}
    check(len(graph) == 11, "Zone and entrance IDs overlap")
    edge_seen = set()
    for a,b in bp["links"]:
        check(a in graph and b in graph and a != b, "Bad link")
        edge = tuple(sorted((a,b)))
        check(edge not in edge_seen, "Duplicate link")
        edge_seen.add(edge)
        graph[a].add(b)
        graph[b].add(a)
    check(all(len(graph[x]) == 1 and graph[x] == {next(e["to"] for e in entrances if e["id"]==x)} for x in entrance_ids), "Entrance must have one intuitive approach")
    check(all(len(graph[z]) >= 2 for z in ids), "No isolated/dead-end playable zone allowed")
    for e in entrances:
        check(two_separate_routes(graph, e["to"], "hq"), f"Single predictable route from {e['id']} to HQ")
    check(bp["balance"]["dominant_position"] == "ridge", "Dominant vantage requires explicit counterplay")
    visible = set(bp["balance"]["visible_zones"])
    counters = set(bp["balance"]["countered_from"])
    check(len(visible) <= bp["balance"]["max_visible_playable_zones"] <= 3, "Overpowered vantage")
    check(counters <= set(ids) and len(counters) >= 2 and "ridge" not in counters, "Ridge must have counterplay")
    check(not any(bp["balance"][k] for k in ("raid_windows_implemented","scripted_quests_implemented","spawned_loot_implemented","objects_spawner_implemented")), "No feature may be claimed installed")
    check(bp["balance"]["no_pay_to_win"] and bp["balance"]["no_rare_gear_spam"], "Balance safeguards must remain")

    props = micro["asset_placements"]
    check(len(props) == planned, "Micro list and zone budgets diverge")
    check(len({p["id"] for p in props}) == len(props), "Duplicate prop IDs")
    counts = Counter(p["zone"] for p in props)
    check(all(counts[z["id"]] == z["prototype_count"] for z in zones), "Wrong objects per subzone")
    centers = {z["id"]:(z["x"],z["z"]) for z in zones}
    all_coords = set()
    for p in props:
        check(p["zone"] in centers, f"Invalid zone for {p['id']}")
        check(all(p[k] is None for k in ("class_name","world_pos","yaw_pitch_roll","scale")), f"Unverified renderable content: {p['id']}")
        check(p["verified_model"] is False and p["placement_checked_on_console"] is False, "Unsupported verification claim")
        check(isinstance(p["visual_role"], str) and len(p["visual_role"]) >= 5, "Missing placement purpose")
        x,z = p["local_x"],p["local_z"]
        check(0 <= x <= g["width"] and 0 <= z <= g["height"], "Object outside layout")
        check(math.dist((x,z),centers[p["zone"]]) <= 25, "Prop too far from subzone")
        check((x,z) not in all_coords, "Exact duplicate object points")
        all_coords.add((x,z))
    return {
        "status":"DESIGN_ONLY_VALIDATED_NOT_PLAYSTATION",
        "map":bp["map"], "stage":4, "candidate_area_selected":False,
        "real_world_coordinates_present":False,
        "object_spawner_exported":False,
        "object_budget_soft":budget,
        "micro_prototype_symbols":len(props),
        "routes":len(bp["links"]),
        "entrances":len(entrances),
        "counterplay":"2 internally disjoint routes from each entrance sector to HQ; ridge has >=2 counters",
        "tests":["JSON structure","entity count","graph connectivity","counterplay","placeholder safety"],
        "untested":["actual asset compatibility","DayZ world location","vertical terrain heights","collisions","PS4 FPS","PS5 FPS","Nitrado deployment"]
    }

def render_svg(bp: dict, micro: dict) -> str:
    W, H = bp["coordinate_system"]["width"],bp["coordinate_system"]["height"]
    sx = lambda x: round(120 + x * 3.15, 1)
    sy = lambda z: round(780 - z * 3.10, 1)
    zones = {z["id"]:z for z in bp["zones"]}
    entries = {e["id"]:e for e in bp["entrances"]}
    nodes = {**zones,**entries}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 940" width="1000" height="940">',
        '<rect width="1000" height="940" fill="#111b20"/>',
        '<rect x="112" y="89" width="772" height="713" fill="#18262b" stroke="#5e7773" stroke-width="2" rx="22"/>',
        '<text x="120" y="49" fill="#f1e9d7" font-size="30" font-family="sans-serif" font-weight="bold">ZONA 47 — TACTICAL LAYOUT V0.1</text>',
        '<text x="122" y="74" fill="#adbbbd" font-size="14" font-family="sans-serif">ILLUSTRATIVE ONLY • LOCAL METRES • NOT A REAL DAYZ POSITION</text>',
        '<path d="M 128 770 L 853 770" stroke="#31504d" stroke-width="4" stroke-dasharray="8,12"/>'
    ]
    for a,b in bp["links"]:
        x1,y1=sx(nodes[a]["x"]),sy(nodes[a]["z"])
        x2,y2=sx(nodes[b]["x"]),sy(nodes[b]["z"])
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#587d74" stroke-width="7" opacity="0.5" stroke-linecap="round"/>')
    for o in micro["asset_placements"]:
        parts.append(f'<circle cx="{sx(o["local_x"])}" cy="{sy(o["local_z"])}" r="4" fill="#a1b2a2" opacity="0.75"/>')
    for z in bp["zones"]:
        x,y=sx(z["x"]),sy(z["z"])
        main = z["id"] == "hq"
        ridge = z["id"] == "ridge"
        col="#e4a35d" if main else "#ae7777" if ridge else "#86b0a0"
        parts += [
            f'<rect x="{x-67}" y="{y-23}" width="134" height="46" rx="13" fill="#24383b" stroke="{col}" stroke-width="2.5"/>',
            f'<text x="{x}" y="{y-2}" fill="#f8f7ed" font-size="15" font-family="sans-serif" font-weight="bold" text-anchor="middle">{escape(z["name"])}</text>',
            f'<text x="{x}" y="{y+14}" fill="#b5cbc3" font-size="11" font-family="sans-serif" text-anchor="middle">{z["prototype_count"]} prop markers</text>',
        ]
    for e in bp["entrances"]:
        x,y=sx(e["x"]),sy(e["z"])
        parts += [
            f'<circle cx="{x}" cy="{y}" r="17" fill="#cfb879" stroke="#fff2cc" stroke-width="2"/>',
            f'<text x="{x}" y="{y+5}" fill="#172225" font-size="15" font-family="sans-serif" text-anchor="middle" font-weight="bold">{e["id"][0].upper()}</text>',
        ]
    parts += [
        '<text x="125" y="829" fill="#d9e6da" font-size="15" font-family="sans-serif">3 approaches  •  8 playable sectors  •  26 symbolic prototype placements</text>',
        '<text x="125" y="855" fill="#b6c6c4" font-size="13" font-family="sans-serif">Lines = navigational routes, not confirmed pathways. No terrain surveyed.</text>',
        '<text x="125" y="881" fill="#e7b27a" font-size="13" font-family="sans-serif">IMPORTANT: NOT a mission map, Object Spawner file, or FPS validation.</text>',
        '</svg>'
    ]
    return "\n".join(parts) + "\n"

def build() -> None:
    bp=json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    micro=json.loads(MICRO.read_text(encoding="utf-8"))
    report=validate(bp,micro)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"zone47_layout.svg").write_text(render_svg(bp,micro),encoding="utf-8")
    (OUT/"concept_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    warning="""BEILEYS47 | ZONA 47 - PAPER DESIGN ONLY

Not deployable to DayZ. DO NOT UPLOAD THIS ARCHIVE TO NITRADO.
NO real world coordinates, elevations, rotations, verified asset class
names, collision surveys or PS4/PS5 performance measurements exist yet.
The 26 circles shown are DESIGN PLACEHOLDERS ONLY, NOT GAME OBJECTS.
This archive is intended for review, future implementation and history.
"""
    files={
        "DO_NOT_UPLOAD_TO_NITRADO.txt":warning.encode(),
        "design/stage4_zone47_blueprint.json":BLUEPRINT.read_bytes(),
        "design/stage4_zone47_micro_layout.json":MICRO.read_bytes(),
        "design/zone47_layout.svg":(OUT/"zone47_layout.svg").read_bytes(),
        "design/concept_audit.json":(OUT/"concept_audit.json").read_bytes(),
        "design/asset_evidence.json":(OUT/"asset_evidence.json").read_bytes(),
        "design/zone47_survey_template.json":(OUT/"zone47_survey_template.json").read_bytes()
    }
    manifest={name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}
    files["SHA256_MANIFEST.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    with zipfile.ZipFile(ZIP,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            add_bytes(archive,name,data)
    with zipfile.ZipFile(ZIP) as archive:
        check(archive.testzip() is None, "ZIP corrupted")
        check(set(archive.namelist())==set(files), "Unexpected ZIP entries")
        check(all("dayzOffline" not in name and not name.endswith("spawnerData.json") for name in archive.namelist()), "Unsafe deploy path")
        for name,digest in manifest.items():
            check(hashlib.sha256(archive.read(name)).hexdigest()==digest, f"Manifest mismatch {name}")
    print(f"PASS: ZONA 47 design validated ({report['micro_prototype_symbols']} symbolic markers, {report['routes']} routes).")
    print(f"PASS: schematic SVG and verified non-deployable concept archive at {ZIP}")
    print("NOT done: asset placement, Nitrado deploy, real terrain survey, PS4/PS5 validation.")

if __name__=="__main__":
    build()
