#!/usr/bin/env python3
"""Check Stage 1/2/3 archives reproduce byte-for-byte independent of mtime."""
from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from pathlib import Path

from zip_deterministic import FIXED_ZIP_TIME,add_bytes

ROOT=Path(__file__).resolve().parents[1]
PREVIEWS=(
  ROOT/"dist/stage1/beileys47-livonia-stage1.zip",
  ROOT/"dist/stage2/beileys47-livonia-stage2-preview.zip",
  ROOT/"dist/stage3/beileys47-livonia-stage3-preview.zip"
)
def test()->None:
    for path in PREVIEWS:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            names=z.namelist()
            assert names and len(set(names))==len(names)
            assert all(z.getinfo(name).date_time==FIXED_ZIP_TIME for name in names),(
                f"ZIP contains non-reproducible filesystem mtimes: {path}"
            )
            assert all(z.getinfo(name).create_system==3 for name in names)
    with tempfile.TemporaryDirectory(prefix="z47-zip-repeat-") as work:
        p=Path(work)/"payload.xml"
        p.write_bytes(b"<types><type name='synthetic'/></types>")
        a=Path(work)/"A.zip";b=Path(work)/"B.zip"
        for time,output in ((1_600_000_000,a),(1_900_000_000,b)):
            os.utime(p,(time,time))
            with zipfile.ZipFile(output,"w") as archive:
                add_bytes(archive,"dayzOffline.enoch/db/types.xml",p.read_bytes())
        assert a.read_bytes()==b.read_bytes()
        assert hashlib.sha256(a.read_bytes()).hexdigest()==hashlib.sha256(b.read_bytes()).hexdigest()
        with zipfile.ZipFile(a) as z:
            assert z.getinfo("dayzOffline.enoch/db/types.xml").date_time==FIXED_ZIP_TIME
        try:
            with zipfile.ZipFile(Path(work)/"invalid.zip","w") as z:
                add_bytes(z,"../server.cfg",b"not safe")
        except ValueError:
            pass
        else:raise AssertionError("Unsafe ZIP traversal accepted")
    print("PASS: Stage 1/2/3 archives have canonical member timestamps.")
    print("PASS: identical data + different filesystem mtimes => identical archive SHA-256.")

if __name__=="__main__":test()
