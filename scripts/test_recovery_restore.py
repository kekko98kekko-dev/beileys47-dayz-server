#!/usr/bin/env python3
"""Adversarial offline round-trip restore tests (zero Nitrado access)."""
from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

from make_recovery_kit import OUT
from restore_recovery_kit import restore, verify_archive, mapped_path


def reject(action, expected: str, absent: Path | None = None) -> None:
    try:
        action()
    except (ValueError, zipfile.BadZipFile) as exc:
        assert expected in str(exc), (expected, str(exc))
    else:
        raise AssertionError("Unsafe recovery action accepted: " + expected)
    if absent is not None:
        assert not absent.exists(), "Corrupt ZIP created a partial destination"


def test() -> None:
    contents, manifest = verify_archive(OUT)
    assert len(contents) >= 70
    assert len(manifest["files"]) == len(contents)
    with tempfile.TemporaryDirectory(prefix="beileys47-restore-regression-") as root:
        work = Path(root)
        restored = work / "fresh"
        result = restore(OUT, restored)
        assert result["status"] == "OFFLINE_RECOVERY_VERIFIED_AND_EXTRACTED"
        assert result["not_a_live_nitrado_backup"] is True
        assert result["restored_file_count"] == len(contents)
        assert (restored / "scripts/restore_recovery_kit.py").is_file()
        assert (restored / "dist/stage3/beileys47-livonia-stage3-preview.zip").is_file()
        assert (restored / "dist/prepurchase/beileys47-livonia-mission-review-candidate.zip").is_file()
        for rel, original in contents.items():
            assert (restored / rel).read_bytes() == original, str(rel)
        reject(lambda: restore(OUT, restored), "NEW")
        assert (restored / "README.md").is_file()

        with zipfile.ZipFile(OUT) as source:
            entries = [(item.filename, source.read(item)) for item in source.infolist()]

        def forged(name: str, replacement: bytes | None = None,
                   extra: tuple[str, bytes] | None = None,
                   omit: str | None = None) -> Path:
            dest = work / (name.replace("/", "_") + ".zip")
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as out:
                for member, raw in entries:
                    if member == omit:
                        continue
                    out.writestr(member, replacement if member == name and replacement is not None else raw)
                if extra:
                    out.writestr(*extra)
            return dest

        # Well-formed archive with modified payload must fail SHA-256 before any write.
        tampered = forged("repository/README.md", replacement=b"UNAUTHORIZED CONTENT")
        reject(lambda: restore(tampered, work / "corrupted"),
               "checksum mismatch", work / "corrupted")
        absent = forged("missing-manifest", omit="MANIFEST_SHA256.json")
        reject(lambda: restore(absent, work / "missing"),
               "missing required", work / "missing")
        traversal = forged("path-escape", extra=("../outside.txt", b"bad"))
        reject(lambda: restore(traversal, work / "escape"),
               "Unsafe ZIP member", work / "escape")
        assert not (work / "outside.txt").exists()
        duplicate = forged("duplicated", extra=("repository/README.md", b"wrong"))
        reject(lambda: restore(duplicate, work / "duplicated-output"),
               "Duplicate", work / "duplicated-output")
        extra = forged("unknown-namespace", extra=("other/passwords.txt", b"bad"))
        reject(lambda: restore(extra, work / "wrong"),
               "Unexpected Recovery Kit member namespace", work / "wrong")
        reject(lambda: mapped_path("repository" + chr(92) + "malicious.txt"),
               "Unsafe ZIP member")

    print("PASS: all Recovery Kit files round-trip exactly; corrupt, traversal, duplicate and incomplete archives rejected.")
    print("PASS: no overwrite and no partial destination after failed verification; NO Nitrado access.")


if __name__ == "__main__":
    test()
