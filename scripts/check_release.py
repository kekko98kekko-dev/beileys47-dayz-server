#!/usr/bin/env python3
"""Static deployment guard for DayZ PS4/PS5 mission preview ZIPs.

Read-only: does not upload files or contact a provider.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET

ALLOWED = {
    "dayzOffline.enoch/db/types.xml",
    "dayzOffline.enoch/cfgplayerspawnpoints.xml",
    "dayzOffline.enoch/cfgspawnabletypes.xml",
    "dayzOffline.enoch/cfggameplay.json",
    "change_report.json",
}
REQUIRED = set(ALLOWED)


def verify(filename: str) -> None:
    with zipfile.ZipFile(filename, "r") as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if set(names) != REQUIRED or len(names) != len(REQUIRED):
            raise ValueError(f"Unexpected or missing archive entries: {set(names) ^ REQUIRED}")
        if any(
            i.is_dir() or "\\" in i.filename or
            ".." in PurePosixPath(i.filename).parts or
            i.file_size > 3_000_000
            for i in infos
        ):
            raise ValueError("Unsafe paths or sizes inside ZIP")
        if sum(i.file_size for i in infos) > 5_000_000:
            raise ValueError("Unexpectedly large ZIP payload")
        for name in names:
            raw = archive.read(name)
            if name.endswith(".xml"):
                if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                    raise ValueError(f"XML DTD/entities not allowed: {name}")
                ET.fromstring(raw)
            elif name.endswith(".json"):
                json.loads(raw.decode("utf-8-sig"))
        report = json.loads(archive.read("change_report.json"))
        if report.get("stage") != 2:
            raise ValueError("This verifier accepts Stage 2 previews only")
        if report.get("status") != "PREVIEW ONLY - NO NITRADO DEPLOY / NO PLAYSTATION TEST":
            raise ValueError("Unexpected stage status")
    print("PASS: Stage 2 archive contents, allowed paths, sizes, XML/JSON syntax.")
    print("NOT verified: DayZ engine semantics, server version, in-game performance or Nitrado permissions.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/check_release.py path/to/stage2-preview.zip")
    verify(sys.argv[1])
