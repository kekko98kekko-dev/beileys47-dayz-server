#!/usr/bin/env python3
"""Import PC DayZ SurfaceY text into a PRIVATE Stage 4.5 observation file.

Reject malformed, duplicate, missing and oversized measurements. No deployment.
User-supplied elevations and metadata must never be written to this public repo.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from audit_stage4_height_samples import ROOT, analyze

OUT = ROOT / "dist/stage4_height_capture"
MAX_LOG_BYTES = 8_000_000
MAX_LOG_LINES = 100_000
MAX_LINE_CHARS = 4096

# Engine logs may prepend a timestamp and optionally quote the Print value.
# Crucially, reject partial Y readings such as "200.0garbage" or a second tag.
LOG_LINE = re.compile(
    r"(?<![A-Za-z0-9_])Z47_ALT\|(GRID|PROP)\|([A-Za-z0-9_-]+)"
    r"\|([0-9]+(?:\.[0-9]+)?)\|([0-9]+(?:\.[0-9]+)?)"
    r"\|([-+]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+))(?:[\"'])?\s*$"
)


def read_log_lines(log: Path) -> list[str]:
    if not log.is_file():
        raise ValueError("Missing SurfaceY input log")
    with log.open("rb") as stream:
        raw = stream.read(MAX_LOG_BYTES + 1)
    if len(raw) > MAX_LOG_BYTES or b"\x00" in raw:
        raise ValueError("Oversized or binary SurfaceY input log")
    lines = raw.decode("utf-8", errors="replace").splitlines()
    if len(lines) > MAX_LOG_LINES:
        raise ValueError("Too many SurfaceY log lines")
    return lines


def convert(log: Path, template: Path, output: Path,
            game_build: str, utc: str, evidence: str) -> dict:
    # Reject public output even under dist/ or hidden subfolders: this is
    # potentially identifying real server data, not a synthetic CI fixture.
    if output.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Private SurfaceY capture cannot be written inside public repository")
    if output.exists() or output.is_symlink():
        raise ValueError("Output file already exists; refusing to overwrite")
    data = json.loads(template.read_text(encoding="utf-8"))
    ref = json.loads((ROOT / "dist/stage4_terrain_survey/terrain_survey_grid.json").read_text(encoding="utf-8"))
    expect = {(p["kind"], p["id"]): p for p in data["points"]}
    seen = {}
    for line in read_log_lines(log):
        if "Z47_ALT|" not in line:
            continue
        if len(line) > MAX_LINE_CHARS or line.count("Z47_ALT|") != 1:
            raise ValueError("Invalid SurfaceY record line")
        match = LOG_LINE.search(line)
        if match is None:
            raise ValueError("Malformed or truncated SurfaceY reading")
        kind, sid, x, z, y = match.groups()
        key = (kind, sid)
        if key not in expect:
            raise ValueError("Unknown logged point " + str(key))
        if key in seen:
            raise ValueError("Duplicate logged point " + str(key))
        px, pz = expect[key]["x"], expect[key]["z"]
        if abs(float(x) - px) >= 0.01 or abs(float(z) - pz) >= 0.01:
            raise ValueError("Coordinate mismatch " + str(key))
        seen[key] = float(y)
    if len(seen) != len(expect):
        raise ValueError(f"Incomplete capture: {len(seen)} of {len(expect)} terrain points")
    data["status"] = "USER_SUPPLIED_SURFACEY_LOG_UNVERIFIED"
    data["measurement"].update({
        "method": "DayZ_CGame_SurfaceY",
        "dayz_game_build": game_build,
        "captured_utc": utc,
        "evidence_reference": evidence
    })
    for p in data["points"]:
        p["ground_y"] = seen[(p["kind"], p["id"])]
    report = analyze(data, ref, data["region"])
    if report["provided_y_count"] != 182 or not report["provenance_complete"]:
        raise ValueError("Measurement report lacks values or provenance")
    if report["status"] == "BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE":
        raise ValueError("Height audit remains blocked")
    output.parent.mkdir(parents=True, exist_ok=True)
    # The 'x' mode makes refusal to overwrite safe against a late-created file.
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Parsed {len(seen)} private SurfaceY measurements into {output}")
    print("WARNING: not independently authenticated; do not publish or deploy.")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--template", type=Path, default=OUT / "central_surfaceY_empty.json")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--game-build", required=True)
    p.add_argument("--captured-utc", required=True)
    p.add_argument("--evidence", required=True)
    v = p.parse_args()
    convert(v.log, v.template, v.output, v.game_build, v.captured_utc, v.evidence)
