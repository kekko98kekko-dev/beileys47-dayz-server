#!/usr/bin/env python3
"""Stage 7: audit and illustrate a ZONA47 bunker GRAPH, not world geometry.

Graph-theoretic redundancy is not proof of walkable DayZ corridors, doors,
terrain, collision, AI, performance or PlayStation compatibility.
"""
from __future__ import annotations

import json
import math
from collections import deque
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/stage7_bunker_layout.json"
BLUEPRINT = ROOT / "config/stage4_zone47_blueprint.json"
SIX = ROOT / "config/stage6_special_zones.json"
PILOT = ROOT / "config/stage4_13_pilot_protocol.json"
OUTPUT = ROOT / "dist/stage7_bunker"
ENTRANCES = {"west_entry", "south_entry", "east_entry"}
ALLOWED_ROLES = {"entrance", "utility", "flank", "junction", "objective"}


def require(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError("STAGE7_BLOCKED: " + detail)


def read(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(type(data) is dict, "document must be JSON object")
    return data


def reachable(graph: dict[str, set[str]], start: str, goal: str, removed: str | None = None) -> bool:
    if start == removed or goal == removed:
        return False
    q = deque([start])
    seen = {start}
    while q:
        node = q.popleft()
        if node == goal:
            return True
        for nxt in graph[node]:
            if nxt != removed and nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


def disjoint_entrance_routes(graph: dict[str, set[str]], entrances: set[str], goal: str) -> int:
    """Node splitting: max internally vertex-disjoint paths using distinct entrances."""
    source, target = ("@", "source"), (goal, "out")
    residual: dict[tuple, dict[tuple, int]] = {}

    def add(u: tuple, v: tuple, capacity: int) -> None:
        residual.setdefault(u, {})
        residual.setdefault(v, {})
        residual[u][v] = residual[u].get(v, 0) + capacity
        residual[v].setdefault(u, 0)

    for node in graph:
        add((node, "in"), (node, "out"), len(entrances) if node == goal else 1)
    for node, peers in graph.items():
        for nxt in peers:
            # Bidirectional paper routes; network flow still limits each room to
            # one path unless it's the shared objective.
            add((node, "out"), (nxt, "in"), 1)
    for entry in entrances:
        add(source, (entry, "in"), 1)

    count = 0
    while True:
        parent = {source: None}
        q = deque([source])
        while q and target not in parent:
            current = q.popleft()
            for nxt, cap in residual[current].items():
                if cap > 0 and nxt not in parent:
                    parent[nxt] = current
                    q.append(nxt)
        if target not in parent:
            break
        cur = target
        while parent[cur] is not None:
            prev = parent[cur]
            residual[prev][cur] -= 1
            residual[cur][prev] += 1
            cur = prev
        count += 1
    return count


def audit(data: dict, blueprint: dict, six: dict, pilot: dict) -> dict:
    require(data.get("stage") == 7 and data.get("status") ==
            "SCHEMATIC_TOPOLOGY_NOT_OBJECT_SPAWNER", "unsafe stage/state")
    require(data.get("map") == "Livonia" and
            data.get("target_platform") == "PlayStation 4 / PlayStation 5", "map/platform")
    require(data.get("coordinate_system") == "zone47_blueprint_local_xz_only_not_world_meters_proven",
            "coordinates mistakenly treated as world")
    require(data.get("deployment_allowed") is False, "deployment flag")
    require(data.get("blueprint_source") == "config/stage4_zone47_blueprint.json" and
            data.get("stage6_source") == "config/stage6_special_zones.json" and
            data.get("pilot_source") == "config/stage4_13_pilot_protocol.json",
            "source provenance")
    require(blueprint.get("status") == "DESIGN_ONLY_NOT_INSTALLABLE" and
            blueprint.get("coordinate_system", {}).get("terrain_surveyed") is False and
            blueprint.get("balance", {}).get("objects_spawner_implemented") is False,
            "ZONA47 blueprint not an untested design")
    hq = next((r for r in blueprint.get("zones", []) if r.get("id") == "hq"), None)
    require(hq is not None, "missing existing HQ")
    require(six.get("stage") == 6 and six.get("deployment_allowed") is False and
            any(z.get("id") == "hidden_bunker" and z.get("blueprint_zone") == "hq" and
                z.get("loot_status") == "NOT_CONFIGURED"
                for z in six.get("proposed_zones", [])), "Stage 6 bunker not an untested concept")
    require(pilot.get("status") == "CONSOLE_PILOT_PROTOCOL_ONLY_NO_RUNTIME_TRIAL" and
            pilot.get("safety", {}).get("automatic_deployment_allowed") is False and
            [x.get("object_count") for x in pilot["rollout"]] == [1, 3, 5],
            "pilot must remain 1→3→5 and disabled")

    bounds = data.get("footprint")
    require(type(bounds) is dict and set(bounds) == {"min_x", "max_x", "min_z", "max_z"},
            "footprint keys")
    require(all(type(v) in (int, float) and math.isfinite(v) for v in bounds.values()),
            "nonfinite footprint")
    require(0 < bounds["min_x"] < bounds["max_x"] < blueprint["coordinate_system"]["width"] and
            0 < bounds["min_z"] < bounds["max_z"] < blueprint["coordinate_system"]["height"],
            "footprint outside schematic")
    require(bounds["min_x"] < hq["x"] < bounds["max_x"] and
            bounds["min_z"] < hq["z"] < bounds["max_z"], "footprint does not enclose HQ")
    require(bounds["max_x"] - bounds["min_x"] <= 70 and
            bounds["max_z"] - bounds["min_z"] <= 60, "unreviewed oversized bunker concept")

    room_specs = data.get("rooms")
    require(type(room_specs) is list and 8 <= len(room_specs) <= 15, "bunker room count")
    rooms = {}
    for spec in room_specs:
        require(type(spec) is dict and
                set(spec) == {"id", "label", "local_x", "local_z", "role",
                              "ground_y", "object_classname", "collision_verified", "console_verified"},
                "room schema contains unreviewed fields")
        nid = spec["id"]
        require(type(nid) is str and nid.isascii() and nid.replace("_", "").isalnum()
                and nid not in rooms, "invalid or duplicate room")
        require(type(spec["label"]) is str and 3 <= len(spec["label"]) <= 40,
                "room label")
        require(type(spec["role"]) is str and spec["role"] in ALLOWED_ROLES, "unknown room role")
        require(all(type(spec[k]) in (float, int) and math.isfinite(spec[k])
                    for k in ("local_x", "local_z")), "invalid room coordinate")
        require(bounds["min_x"] <= spec["local_x"] <= bounds["max_x"] and
                bounds["min_z"] <= spec["local_z"] <= bounds["max_z"],
                "room outside schematic HQ footprint")
        require(spec["ground_y"] is None and spec["object_classname"] is None and
                spec["collision_verified"] is False and spec["console_verified"] is False,
                "unverified object or ground claimed real")
        rooms[nid] = spec
    entrances = data.get("entrances")
    objective = data.get("objective")
    require(type(entrances) is list and len(entrances) == 3 and
            len(set(entrances)) == 3 and set(entrances) == ENTRANCES,
            "three distinct paper entrances required")
    require(all(rooms[e]["role"] == "entrance" for e in entrances),
            "entrances must refer to entrance nodes")
    require(objective == "vault" and rooms[objective]["role"] == "objective",
            "one verified design-only objective")
    require({x for x in rooms if rooms[x]["role"] == "entrance"} == set(entrances),
            "hidden entrances are not approved")
    require(sum(x["role"] == "objective" for x in rooms.values()) == 1,
            "extra or missing reward objective")
    require(len({(v["local_x"], v["local_z"]) for v in rooms.values()}) == len(rooms),
            "overlapping room symbols")
    links = data.get("links")
    require(type(links) is list and len(links) <= 32, "unbounded or missing links")
    graph: dict[str, set[str]] = {x: set() for x in rooms}
    pairs = set()
    for link in links:
        require(type(link) is list and len(link) == 2 and
                all(type(v) is str and v in rooms for v in link) and
                link[0] != link[1], "invalid link")
        a, b = link
        pair = tuple(sorted((a, b)))
        require(pair not in pairs, "duplicate corridor concept")
        pairs.add(pair)
        graph[a].add(b)
        graph[b].add(a)
    require(all(len(graph[n]) >= 2 for n in rooms), "dead-end/isolated route in concept")
    require(len(graph[objective]) >= 3, "objective has too few alternatives")
    reachable_entries = [e for e in entrances if reachable(graph, e, objective)]
    require(len(reachable_entries) == 3, "not all entrances reach objective")
    alternate_count = disjoint_entrance_routes(graph, set(entrances), objective)
    minimum = data.get("rules", {}).get("minimum_internally_vertex_disjoint_routes_to_objective")
    require(type(minimum) is int and minimum == 2, "route target cannot change silently")
    require(alternate_count >= minimum, "one corridor dominates the entire bunker")
    # Simulate blocking any one internal room. At least two independently placed
    # exterior approaches must still connect to the objective on the paper graph.
    blocked = {}
    for node in sorted(set(rooms) - set(entrances) - {objective}):
        remaining = [e for e in entrances if reachable(graph, e, objective, removed=node)]
        blocked[node] = len(remaining)
        require(len(remaining) >= 2, f"single-room lockout: {node}")

    require(data.get("rules") == {
        "minimum_internally_vertex_disjoint_routes_to_objective": 2,
        "one_access_cannot_hold_all_approaches": True,
        "no_one_way_doors_claimed": True,
        "no_functioning_lock_mechanics_claimed": True,
        "no_zombie_scripted_ai": True,
        "no_guaranteed_loot": True,
        "first_pilot_remains_one_three_five_props": True,
    }, "unreviewed gameplay promise")
    unresolved = data.get("unresolved")
    require(type(unresolved) is dict and set(unresolved) == {
        "real_ground_y_all_rooms", "actual_walkable_bunker_structures",
        "console_classnames", "door_and_stair_behaviors",
        "local_terrain_obstructions", "navigation_and_evacuation",
        "loot_spawn_points", "ps5_collision_and_performance",
    } and all(v is True for v in unresolved.values()),
            "real console gates misrepresented")
    require(data.get("artifacts") == {
        "world_positions_generated": False,
        "object_spawner_json_generated": False,
        "mission_xml_modified": False,
        "ready_for_nitrado": False,
    }, "unsafe installable output claim")

    return {
        "stage": 7, "status": "PAPER_BUNKER_GRAPH_APPROVED_NOT_PHYSICAL",
        "room_count": len(rooms), "paper_corridor_count": len(pairs),
        "entrance_count": len(entrances), "objective": objective,
        "vertex_disjoint_entry_to_objective_routes": alternate_count,
        "minimum_accesses_after_each_single_interior_node_block":
            min(blocked.values()),
        "single_room_lockout_checks": blocked,
        "real_bunker_or_tunnel_constructibility_verified": False,
        "real_doors_and_passage_collision_tested": False,
        "real_Y_and_classnames_known": False, "loot_spawning_verified": False,
        "ps4_ps5_performance_tested": False, "world_coordinates_emitted": False,
        "deployment_allowed": False,
        "critical_limitations": [
            "Connections are abstract graph edges, not doors, corridors, ladders, portals, collision, or navigable surfaces.",
            "Local X/Z is a drawing reference, not measured Livonia world elevation; underground access is unverified.",
            "Graph redundancy cannot prove line of sight fairness, no camping, absence of exploits or playable performance.",
            "The 1→3→5 object-spawner pilot remains the only approved future testing progression.",
        ]
    }


def svg(data: dict) -> str:
    rooms = {r["id"]: r for r in data["rooms"]}
    bounds = data["footprint"]
    # Fixed-size illustration. SVG is NOT a world object export, map placement
    # confirmation or an asset/class name manifest.
    w, h = 780, 650
    px = lambda x: 70 + (x - bounds["min_x"]) * (635 / (bounds["max_x"] - bounds["min_x"]))
    pz = lambda z: 90 + (z - bounds["min_z"]) * (485 / (bounds["max_z"] - bounds["min_z"]))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<rect width="780" height="650" fill="#0b1421"/>',
           '<text x="65" y="40" font-size="25" font-family="Arial" fill="#ecf4ff">ZONA 47 — BUNKER / STAGE 7</text>',
           '<text x="65" y="65" font-size="13" font-family="Arial" fill="#b9c7d5">SCHEMATIC ROUTE GRAPH · NOT A REAL DAYZ STRUCTURE OR MAP</text>',
           '<rect x="50" y="80" width="680" height="510" rx="12" fill="#122235" stroke="#4c6781" stroke-width="2"/>']
    for a, b in data["links"]:
        u, v = rooms[a], rooms[b]
        out.append(f'<line x1="{px(u["local_x"]):.1f}" y1="{pz(u["local_z"]):.1f}" x2="{px(v["local_x"]):.1f}" y2="{pz(v["local_z"]):.1f}" stroke="#728ba5" stroke-width="6" opacity=".72"/>')
    palette = {"entrance": "#38c9b7", "utility": "#d3b568",
               "flank": "#72a4ed", "junction": "#b2a3ec", "objective": "#e88871"}
    for node in data["rooms"]:
        x, y = px(node["local_x"]), pz(node["local_z"])
        c = palette[node["role"]]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{c}" stroke="#edf6ff" stroke-width="2"/>')
        out.append(f'<text x="{x:.1f}" y="{y - 18:.1f}" text-anchor="middle" font-size="12" font-weight="bold" font-family="Arial" fill="#edf6ff">{escape(node["label"])}</text>')
    out.append('<text x="65" y="620" font-family="Arial" font-size="13" fill="#d8e5f5">Entrances (teal) · Utility (gold) · Routes (blue) · Objective (coral) · NO WORLD Y</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def build(output: Path = OUTPUT) -> dict:
    data = read(CONFIG)
    result = audit(data, read(BLUEPRINT), read(SIX), read(PILOT))
    output.mkdir(parents=True, exist_ok=True)
    (output / "bunker_topology_report.json").write_text(json.dumps(
        result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "bunker_topology.svg").write_text(svg(data), encoding="utf-8")
    print("PASS: stage 7 schematic bunker routes; no real ground, objects or loot.")
    print("No Object Spawner generated; NO Nitrado deployment.")
    return result


if __name__ == "__main__":
    build()
