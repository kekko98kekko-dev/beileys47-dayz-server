#!/usr/bin/env python3
"""Verify and restore a BEILEYS47 Recovery Kit into a NEW directory.

Strictly offline, never touches Nitrado and never overwrites an existing tree.
Restores repository/* to the chosen root and previews/* into root/dist/*.
This is NOT a restoration of DayZ characters or server persistence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 8_000_000
MAX_TOTAL_BYTES = 50_000_000
REQUIRED = {
    "README_RECOVERY.txt",
    "repository/README.md",
    "repository/scripts/make_recovery_kit.py",
    "previews/stage3/beileys47-livonia-stage3-preview.zip",
    "previews/prepurchase/beileys47-livonia-mission-review-candidate.zip",
}
MANIFEST = "MANIFEST_SHA256.json"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def mapped_path(name: str) -> Path | None:
    if name == MANIFEST:
        return None
    if name == "README_RECOVERY.txt":
        return Path("README_RECOVERY.txt")
    path = PurePosixPath(name)
    if (not name or "\\\\" in name or path.is_absolute()
            or path.as_posix() != name or
            any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError(f"Unsafe ZIP member path: {name!r}")
    if name.startswith("repository/"):
        parts = name.split("/")[1:]
        if not parts:
            raise ValueError("Empty repository member")
        return Path(*parts)
    if name.startswith("previews/"):
        parts = name.split("/")[1:]
        if not parts:
            raise ValueError("Empty preview member")
        return Path("dist", *parts)
    raise ValueError(f"Unexpected Recovery Kit member namespace: {name!r}")


def verify_archive(archive_path: Path) -> tuple[dict[Path, bytes], dict]:
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate Recovery Kit ZIP entries")
        if not REQUIRED.issubset(names) or MANIFEST not in names:
            raise ValueError("Recovery Kit is missing required files")
        if len(names) < 70:
            raise ValueError("Unexpectedly small/incomplete Recovery Kit")
        total = 0
        paths: dict[str, Path | None] = {}
        destinations: set[Path] = set()
        for info in infos:
            name = info.filename
            if info.is_dir() or info.file_size > MAX_FILE_BYTES or info.file_size < 0:
                raise ValueError(f"Invalid ZIP entry type/size: {name!r}")
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError(f"ZIP symlink or special file forbidden: {name!r}")
            dest = mapped_path(name)
            if dest is not None:
                if dest in destinations:
                    raise ValueError(f"Colliding recovery output path: {dest}")
                destinations.add(dest)
            paths[name] = dest
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("Recovery Kit uncompressed payload too large")
        manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
        if (not isinstance(manifest, dict) or
                manifest.get("project") != "BEILEYS47 | DAYZ SURVIVAL WAR" or
                manifest.get("kind") != "OFFLINE PREVIEW RECOVERY ONLY - NOT A LIVE SERVER BACKUP"):
            raise ValueError("Wrong Recovery Kit manifest identity")
        files = manifest.get("files")
        if not isinstance(files, dict) or set(files) != set(names) - {MANIFEST}:
            raise ValueError("Manifest does not cover exactly every ZIP payload")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC verification failed")
        recovered: dict[Path, bytes] = {}
        for info in infos:
            name = info.filename
            if name == MANIFEST:
                continue
            meta = files[name]
            if (not isinstance(meta, dict) or
                    type(meta.get("bytes")) is not int or
                    not isinstance(meta.get("sha256"), str) or
                    re.fullmatch(r"[0-9a-f]{64}", meta["sha256"]) is None):
                raise ValueError(f"Invalid SHA256 manifest entry: {name}")
            raw = archive.read(info)
            if len(raw) != meta["bytes"] or sha256(raw) != meta["sha256"]:
                raise ValueError(f"Recovery Kit checksum mismatch: {name}")
            recovered[paths[name]] = raw
        return recovered, manifest


def restore(archive_path: Path, destination: Path) -> dict:
    """All ZIP validation happens BEFORE any destination is created."""
    if destination.exists() or destination.is_symlink():
        raise ValueError("Restoration requires a NEW, nonexistent destination directory")
    if not destination.parent.is_dir():
        raise ValueError("Restoration parent directory does not exist")
    contents, manifest = verify_archive(archive_path)
    # Write to temporary sibling and rename only when every write succeeded.
    temp = Path(tempfile.mkdtemp(prefix=".beileys47-restore-", dir=destination.parent))
    try:
        for rel, raw in contents.items():
            target = temp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        # Refuse to overwrite even if a different process created the path
        # after our initial check.
        if destination.exists() or destination.is_symlink():
            raise ValueError("Restoration destination appeared during verification")
        temp.rename(destination)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {
        "status": "OFFLINE_RECOVERY_VERIFIED_AND_EXTRACTED",
        "restored_file_count": len(contents),
        "baseline": manifest["baseline"],
        "destination": str(destination),
        "not_a_live_nitrado_backup": True,
        "nitrado_connection_or_gameplay_test": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    report = restore(args.archive, args.destination)
    print(json.dumps(report, indent=2))
    print("No Nitrado saves, console runtime evidence or player persistence are included.")


if __name__ == "__main__":
    main()
