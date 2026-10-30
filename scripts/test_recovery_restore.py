#!/usr/bin/env python3
"""Adversarial offline round-trip restore tests (zero Nitrado access)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from make_recovery_kit import OUT
from restore_recovery_kit import restore, verify_archive, mapped_path


def reject(action, expected: str, absent: Path | None = None) -> None:
    try:
        action()
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
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
        checksum = work / "release.zip.sha256"
        checksum.write_text(hashlib.sha256(OUT.read_bytes()).hexdigest()
                            + "  dist/beileys47-recovery-kit.zip\n", encoding="utf-8")
        result = restore(OUT, restored, checksum)
        assert result["status"] == "OFFLINE_RECOVERY_VERIFIED_AND_EXTRACTED"
        assert result["not_a_live_nitrado_backup"] is True
        assert result["external_release_checksum_verified"] is True
        assert result["restored_file_count"] == len(contents)
        assert (restored / "scripts/restore_recovery_kit.py").is_file()
        assert (restored / "dist/stage3/beileys47-livonia-stage3-preview.zip").is_file()
        assert (restored / "dist/prepurchase/beileys47-livonia-mission-review-candidate.zip").is_file()
        for rel, original in contents.items():
            assert (restored / rel).read_bytes() == original, str(rel)
        reject(lambda: restore(OUT, restored), "NEW")
        assert (restored / "README.md").is_file()
        # Simulate a competing process creating the destination precisely
        # AFTER our initial exists() check, during exclusive reservation.
        raced = work / "raced"
        original_mkdir = Path.mkdir
        def occupy_destination(path, *args, **kwargs):
            if path == raced:
                original_mkdir(path, *args, **kwargs)
                (path / "SENTINEL").write_text("preserve", encoding="utf-8")
                raise FileExistsError("Simulated rival directory creation")
            return original_mkdir(path, *args, **kwargs)
        with patch.object(Path, "mkdir", occupy_destination):
            reject(lambda: restore(OUT, raced), "NEW")
        assert (raced / "SENTINEL").read_text(encoding="utf-8") == "preserve"

        # A late I/O error must remove a partially populated destination.
        interrupted = work / "interrupted"
        original_rename = Path.rename
        def fail_transfer(path, target):
            if Path(target).parent == interrupted:
                raise OSError("Synthetic transfer failure")
            return original_rename(path, target)
        with patch.object(Path, "rename", fail_transfer):
            reject(lambda: restore(OUT, interrupted), "Synthetic transfer failure", interrupted)
        wrong_checksum = work / "wrong.sha256"
        wrong_checksum.write_text("0" * 64 + "  beileys47-recovery-kit.zip\n", encoding="utf-8")
        reject(lambda: restore(OUT, work / "external-mismatch", wrong_checksum),
               "External GitHub Release SHA-256 mismatch", work / "external-mismatch")
        wrong_name = work / "wrong-name.sha256"
        wrong_name.write_text("0" * 64 + "  unrelated.zip\n", encoding="utf-8")
        reject(lambda: restore(OUT, work / "external-name", wrong_name),
               "Invalid or mismatched external Release SHA-256 entry", work / "external-name")

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
        for unsafe in ("repository/C:/outside.txt", "repository/CON.txt",
                       "repository/sub/file. ", "repository/sub/AUX",
                       "repository/LPT1.txt"):
            reject(lambda name=unsafe: mapped_path(name), "Unsafe ZIP member")
        case_collision = forged("windows-case", extra=("repository/readme.md", b"bad"))
        reject(lambda: restore(case_collision, work / "case-collision"),
               "Colliding recovery output path", work / "case-collision")

    print("PASS: all Recovery Kit files round-trip exactly; corrupt, traversal, duplicate and incomplete archives rejected.")
    print("PASS: no overwrite and no partial destination after failed verification; NO Nitrado access.")


if __name__ == "__main__":
    test()
