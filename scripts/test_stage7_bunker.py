#!/usr/bin/env python3
"""Stage 7 negative tests: unsafe world claims and paper route chokepoints."""
from __future__ import annotations

import copy
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build_stage7_bunker import (
    BLUEPRINT, CONFIG, PILOT, SIX, audit, build,
    disjoint_entrance_routes, read, reachable
)


def reject(data: dict, blueprint: dict, six: dict, pilot: dict, reason: str) -> None:
    try:
        audit(data, blueprint, six, pilot)
    except ValueError as exc:
        assert reason in str(exc), (reason, str(exc))
    else:
        raise AssertionError("Rejected bunker change was accepted: " + reason)


def test() -> None:
    data, bp, six, pilot = read(CONFIG), read(BLUEPRINT), read(SIX), read(PILOT)
    with tempfile.TemporaryDirectory(prefix="stage7-bunker-") as folder:
        dst = Path(folder)
        result = build(dst)
        assert result == json.loads((dst / "bunker_topology_report.json").read_text())
        assert result["room_count"] == 10
        assert result["entrance_count"] == 3
        assert result["vertex_disjoint_entry_to_objective_routes"] >= 2
        assert result["minimum_accesses_after_each_single_interior_node_block"] >= 2
        assert result["deployment_allowed"] is False
        assert result["world_coordinates_emitted"] is False
        svg_bytes = (dst / "bunker_topology.svg").read_bytes()
        assert ET.fromstring(svg_bytes).tag.endswith("svg")
        assert b"NOT A REAL DAYZ STRUCTURE" in svg_bytes
        assert b"land_" not in svg_bytes.lower()

    corrupted = copy.deepcopy(data)
    corrupted["deployment_allowed"] = True
    reject(corrupted, bp, six, pilot, "deployment flag")
    corrupted = copy.deepcopy(data)
    corrupted["rooms"][0]["object_classname"] = "Land_Unverified_Bunker"
    reject(corrupted, bp, six, pilot, "unverified object")
    corrupted = copy.deepcopy(data)
    corrupted["rooms"][1]["ground_y"] = 100.0
    reject(corrupted, bp, six, pilot, "unverified object")
    corrupted = copy.deepcopy(data)
    corrupted["rooms"][0]["local_x"] = 450
    reject(corrupted, bp, six, pilot, "room outside")
    corrupted = copy.deepcopy(data)
    corrupted["rooms"][0]["id"] = corrupted["rooms"][1]["id"]
    reject(corrupted, bp, six, pilot, "duplicate room")
    corrupted = copy.deepcopy(data)
    corrupted["links"].append(list(data["links"][0][::-1]))
    reject(corrupted, bp, six, pilot, "duplicate corridor")
    corrupted = copy.deepcopy(data)
    corrupted["links"].append(["unknown", "vault"])
    reject(corrupted, bp, six, pilot, "invalid link")
    corrupted = copy.deepcopy(data)
    corrupted["artifacts"]["object_spawner_json_generated"] = True
    reject(corrupted, bp, six, pilot, "unsafe installable")
    corrupted = copy.deepcopy(data)
    corrupted["unresolved"]["real_ground_y_all_rooms"] = False
    reject(corrupted, bp, six, pilot, "real console gates")
    corrupted = copy.deepcopy(data)
    corrupted["rules"]["minimum_internally_vertex_disjoint_routes_to_objective"] = 1
    reject(corrupted, bp, six, pilot, "route target")
    corrupted = copy.deepcopy(data)
    corrupted["footprint"]["max_x"] = 999
    reject(corrupted, bp, six, pilot, "footprint outside")
    bp2 = copy.deepcopy(bp)
    bp2["coordinate_system"]["terrain_surveyed"] = True
    reject(data, bp2, six, pilot, "blueprint not an untested design")
    pilot2 = copy.deepcopy(pilot)
    pilot2["rollout"][-1]["object_count"] = 26
    reject(data, bp, six, pilot2, "pilot must remain")
    six2 = copy.deepcopy(six)
    six2["deployment_allowed"] = True
    reject(data, bp, six2, pilot, "Stage 6 bunker")

    # A direct isolated mathematical check is necessary. Schema validation
    # could block a degenerate dataset before the path algorithm is reached.
    bottleneck = {
        "a": {"hub"}, "b": {"hub"}, "c": {"hub"},
        "hub": {"a", "b", "c", "vault"}, "vault": {"hub"}
    }
    assert disjoint_entrance_routes(bottleneck, {"a", "b", "c"}, "vault") == 1
    assert not reachable(bottleneck, "a", "vault", removed="hub")
    graph = {r["id"]: set() for r in data["rooms"]}
    for a, b in data["links"]:
        graph[a].add(b)
        graph[b].add(a)
    assert disjoint_entrance_routes(graph, set(data["entrances"]), "vault") >= 2

    print("PASS: Stage 7 bunker topology, adversarial paths, XML-only SVG and safe release gates.")
    print("NOT verified: real bunker, doors, tunnels, Y, class names, collision or PS5 FPS.")


if __name__ == "__main__":
    test()
