#!/usr/bin/env python3
"""Audit every nested Recovery ZIP and repeated same-input package builds.

This catches a subtle prior issue: deterministic OUTER archive ZIP can still
contain nondeterministic STAGE4 inner ZIPs or purchase-day review ZIP bytes.
No server files, logs, or gameplay data are needed for these static tests.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile

from zip_deterministic import FIXED_ZIP_TIME
from make_recovery_kit import ROOT,OUT,PREVIEW_PATHS,build as build_recovery
from build_prepurchase_bundle import PACKAGE,build as build_review

def digest(path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test()->None:
    assert len(PREVIEW_PATHS)>15
    inner=[r for r in PREVIEW_PATHS if r.lower().endswith(".zip")]
    assert len(inner)>=10,"Recovery Kit lost embedded stage archives"
    for rel in inner:
        path=ROOT/rel
        assert path.exists(),f"Missing generated artifact {rel}"
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None,rel
            names=archive.namelist()
            assert names and len(names)==len(set(names)),rel
            assert all(archive.getinfo(name).date_time==FIXED_ZIP_TIME for name in names),(
                f"Non-reproducible ZIP member timestamp: {rel}"
            )
    before_review=digest(PACKAGE)
    review=build_review()
    assert review["ready_to_deploy"] is False
    assert digest(PACKAGE)==before_review,"Six-file master archive changed across same-input runs"
    before_recovery=digest(OUT)
    build_recovery()
    assert digest(OUT)==before_recovery,"Recovery Kit changed across same-input builds"
    with zipfile.ZipFile(OUT) as recovery:
        assert recovery.testzip() is None
        assert recovery.getinfo("MANIFEST_SHA256.json").date_time==FIXED_ZIP_TIME
        manifest=json.loads(recovery.read("MANIFEST_SHA256.json"))
        for rel in inner:
            name="previews/"+rel.removeprefix("dist/")
            raw=recovery.read(name)
            assert hashlib.sha256(raw).hexdigest()==manifest["files"][name]["sha256"]
            assert raw==(ROOT/rel).read_bytes()
            with zipfile.ZipFile(io.BytesIO(raw)) as nested:
                assert nested.testzip() is None
                assert all(i.date_time==FIXED_ZIP_TIME for i in nested.infolist())
    print(f"PASS: {len(inner)} nested Stage 1–4 ZIPs have fixed timestamps and valid SHA-256.")
    print("PASS: duplicate master handoff and Recovery Kit builds produce identical bytes.")
    print("NO server connection, Nitrado backup or PlayStation tests were performed.")

if __name__=="__main__":test()
