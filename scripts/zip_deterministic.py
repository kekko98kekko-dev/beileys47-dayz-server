#!/usr/bin/env python3
"""Canonical ZIP member serialization for pinned CE preview artifacts.

The old zipfile.write() included local file mtimes, making repeated builds
from identical source bytes produce different release checksums.
"""
from __future__ import annotations

import zipfile
from pathlib import PurePosixPath

FIXED_ZIP_TIME=(2026,10,30,0,0,0)

def add_bytes(archive:zipfile.ZipFile,name:str,payload:bytes)->None:
    path=PurePosixPath(name)
    if not name or path.is_absolute() or "\\" in name or ".." in path.parts or name.endswith("/"):
        raise ValueError(f"Unsafe archive name: {name!r}")
    if type(payload) is not bytes:
        raise TypeError("Archive content must be immutable bytes")
    info=zipfile.ZipInfo(name,date_time=FIXED_ZIP_TIME)
    info.compress_type=zipfile.ZIP_DEFLATED
    info.create_system=3
    info.external_attr=0o644<<16
    archive.writestr(info,payload)
