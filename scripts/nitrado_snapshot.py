#!/usr/bin/env python3
"""BEILEYS47: read-only snapshot of DayZ PS Nitrado mission configurations.
No upload, restart, stop, delete or write operations are implemented here.
Requires a Nitrado long-life token in NITRADO_API_TOKEN (GitHub Actions secret).
"""
import argparse
import hashlib
import json
import os
import posixpath
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.nitrado.net"
SERVICE_ID = 20113048
MISSION = "dayzOffline.enoch"
MAX_FILE_BYTES = 16 * 1024 * 1024
TARGETS = [
    "cfggameplay.json",
    "cfgeconomycore.xml",
    "cfgspawnabletypes.xml",
    "cfgweather.xml",
    "cfgeventspawns.xml",
    "mapgrouppos.xml",
    "mapgroupproto.xml",
    "db/events.xml",
    "db/types.xml",
    "custom/beileys47_dolnik_military_base_v9.json",
]
class NitradoError(Exception):
    pass

def safe_dir(parent, child):
    if not isinstance(child, str) or child in ("", ".", "..") or "/" in child or "\\" in child:
        raise NitradoError("Unsafe directory entry returned by API")
    return posixpath.join(parent.rstrip("/"), child) if parent != "/" else "/" + child

def call_api(token, endpoint, params=None):
    url = API + endpoint
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "User-Agent": "BEILEYS47-safe-config-snapshot/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read(24 * 1024 * 1024))
    except urllib.error.HTTPError as exc:
        # Never include the response body, headers or signed URL in logs.
        raise NitradoError("Nitrado API HTTP " + str(exc.code) + " on " + endpoint) from None
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        raise NitradoError("Nitrado API request failed (" + type(exc).__name__ + ")") from None
    if data.get("status") != "success" or not isinstance(data.get("data"), dict):
        raise NitradoError("Nitrado API did not return a successful response to " + endpoint)
    return data["data"]

def entries_at(token, path):
    endpoint = f"/services/{SERVICE_ID}/gameservers/file_server/list"
    data = call_api(token, endpoint, {"dir": path, "summarize_folders": 0})
    entries = data.get("entries", [])
    if isinstance(entries, dict):
        entries = list(entries.values())
    return [e for e in entries if isinstance(e, dict)]

def is_dir(entry):
    kind = str(entry.get("type", "")).lower()
    return kind in ("dir", "directory", "folder") or entry.get("is_dir") is True

def entry_name(entry):
    return str(entry.get("name") or posixpath.basename(str(entry.get("path", "")).rstrip("/")))

def resolve_mission(token):
    # We only list directories. Never enumerate storage_1, player data or logs.
    roots = ["/", "/games", "/dayzps_missions", "/games/dayzps_missions"]
    try:
        bookmarks = call_api(token, f"/services/{SERVICE_ID}/gameservers/file_server/bookmarks").get("bookmarks", [])
        if isinstance(bookmarks, dict):
            bookmarks = list(bookmarks.values())
        for b in bookmarks:
            if isinstance(b, dict) and isinstance(b.get("path"), str):
                roots.append(b["path"])
    except NitradoError:
        pass
    pending = [(r, 0) for r in roots]
    seen = set()
    tried = 0
    while pending and tried < 80:
        here, depth = pending.pop(0)
        if here in seen or depth > 6:
            continue
        seen.add(here)
        try:
            entries = entries_at(token, here)
            tried += 1
        except NitradoError:
            continue
        if posixpath.basename(here.rstrip("/")) == MISSION:
            return here
        for e in entries:
            name = entry_name(e)
            if not is_dir(e):
                continue
            if name == MISSION:
                return str(e.get("path") or safe_dir(here, name))
            # Only safe likely path ancestors; avoid player storage/backups/logs.
            allowed = (
                name.lower() in {"games", "game", "noftp", "dayzps_missions", "missions", "dayz", "server"}
                or (depth <= 2 and name.lower().startswith("dayz"))
                or (here.rstrip("/").lower() == "/games" and depth < 3
                    and name.lower() not in {"storage", "backups", "logs", "log"})
            )
            if allowed and depth < 6:
                sub = e.get("path") or safe_dir(here, name)
                pending.append((str(sub), depth + 1))
    raise NitradoError(
        "Mission folder not found via Nitrado API. Check API service scope and file_server/list access; "
        "no server files have been changed."
    )

def download_one(token, path):
    data = call_api(token, f"/services/{SERVICE_ID}/gameservers/file_server/download", {"file": path})
    tk = data.get("token") or {}
    address = tk.get("url")
    one_time_token = tk.get("token")
    if not isinstance(address, str) or not isinstance(one_time_token, str):
        raise NitradoError("Nitrado did not issue a file download token")
    parsed = urllib.parse.urlsplit(address)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise NitradoError("Nitrado issued an unsafe download URL (HTTPS is required)")
    params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    params.append(("token", one_time_token))
    url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                                 urllib.parse.urlencode(params), parsed.fragment))
    # Signed one-time token is used ONLY with the URL issued by Nitrado.
    request = urllib.request.Request(url, headers={"User-Agent": "BEILEYS47-safe-config-snapshot/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read(MAX_FILE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise NitradoError("Nitrado download HTTP " + str(exc.code) + " for remote configuration") from None
    except (urllib.error.URLError, TimeoutError):
        raise NitradoError("Nitrado download connection failed") from None
    if len(data) > MAX_FILE_BYTES:
        raise NitradoError("Configuration exceeded maximum allowed download size")
    return data

def probe(token):
    path = resolve_mission(token)
    print("Nitrado mission directory discovered and file-list API working.")
    print("Mission folder:", path)
    print("No file downloaded or changed in probe mode.")

def snapshot(token, output):
    mission_root = resolve_mission(token)
    result = {}
    failed = {}
    for rel in TARGETS:
        remote = posixpath.join(mission_root.rstrip("/"), rel)
        try:
            blob = download_one(token, remote)
            result[rel] = blob
            print("OK:", rel, "-", len(blob), "bytes")
        except NitradoError as exc:
            failed[rel] = str(exc)
            print("MISSING/ERROR:", rel, "-", type(exc).__name__)
    if len(result) < 8:
        raise NitradoError(
            f"Snapshot incomplete ({len(result)}/{len(TARGETS)}). No ZIP produced: "
            "inspect Nitrado file_server permissions and mission directory."
        )
    manifest = {
        "purpose": "CONFIGURATION SNAPSHOT ONLY. NOT world persistence / player backup",
        "service_id": SERVICE_ID,
        "mission": MISSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "files": {name: {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
                  for name, blob in result.items()},
        "missing_or_failed": list(failed),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel, blob in result.items():
            archive.writestr("dayzOffline.enoch/" + rel, blob)
        archive.writestr("MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise NitradoError("Archive integrity verification failed")
    print("Saved configuration-only snapshot (not live world persistence):", output)
    if failed:
        print("Optional missing files:", ", ".join(failed))

def self_test():
    assert safe_dir("/games", "dayzps_missions") == "/games/dayzps_missions"
    assert safe_dir("/", "games") == "/games"
    for unsafe in ("../oops", "..", "some/path", ""):
        try:
            safe_dir("/", unsafe)
            raise AssertionError("Unsafe path accepted")
        except NitradoError:
            pass
    assert len(TARGETS) == 10 and all("storage" not in t for t in TARGETS)
    print("Local safety checks passed. No network used.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("self-test", "probe", "snapshot"))
    parser.add_argument("--output", default="nitrado_snapshot/BEILEYS47_NITRADO_CONFIG.zip")
    args = parser.parse_args()
    if args.mode == "self-test":
        self_test()
        return
    token = os.environ.get("NITRADO_API_TOKEN", "").strip()
    if not token:
        raise NitradoError("Missing NITRADO_API_TOKEN GitHub Actions repository secret")
    if args.mode == "probe":
        probe(token)
    else:
        snapshot(token, Path(args.output))

if __name__ == "__main__":
    try:
        main()
    except NitradoError as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
