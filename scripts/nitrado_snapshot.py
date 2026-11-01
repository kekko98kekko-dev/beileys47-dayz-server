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
    """Discover the mission using authenticated Nitrado metadata, never passwords."""
    # Nitrado usually places console missions under /games/<account>/noftp/.
    # API root "/" may be inaccessible even with a valid service-scope token.
    roots = ["/", "/games", "/dayzps_missions", "/games/dayzps_missions"]
    metadata_found = False
    try:
        info = call_api(token, f"/services/{SERVICE_ID}/gameservers")
        game = info.get("gameserver", {})
        if isinstance(game, dict):
            metadata_found = True
            username = game.get("username")
            if isinstance(username, str) and username.isascii() and (
                    username.replace("_", "").replace("-", "").isalnum()):
                for base in (f"/games/{username}/noftp", f"/games/{username}/ftproot",
                             f"/games/{username}"):
                    roots.extend([base, base + "/dayzps_missions",
                                  base + "/dayzps_missions/" + MISSION])
            specific = game.get("game_specific") or {}
            gamepath = specific.get("path") if isinstance(specific, dict) else None
            if isinstance(gamepath, str) and gamepath.startswith("/games/") and ".." not in gamepath:
                base = gamepath.rstrip("/")
                roots.extend([base, base + "/dayzps_missions",
                              base + "/dayzps_missions/" + MISSION,
                              posixpath.dirname(base) + "/dayzps_missions",
                              posixpath.dirname(base) + "/dayzps_missions/" + MISSION])
    except NitradoError as exc:
        # Only an HTTP error number is printed; never a token or private path.
        print("Diagnostic: gameserver metadata not accessible:", str(exc))

    bookmarks_count = 0
    try:
        bookmarks = call_api(
            token, f"/services/{SERVICE_ID}/gameservers/file_server/bookmarks"
        ).get("bookmarks", [])
        if isinstance(bookmarks, dict):
            bookmarks = list(bookmarks.values())
        for bk in bookmarks if isinstance(bookmarks, list) else []:
            if isinstance(bk, dict):
                p = bk.get("path")
                if isinstance(p, str) and p.startswith("/"):
                    bookmarks_count += 1
                    roots.extend([p, p.rstrip("/") + "/dayzps_missions",
                                  p.rstrip("/") + "/dayzps_missions/" + MISSION])
            elif isinstance(bk, str) and bk.startswith("/"):
                bookmarks_count += 1
                roots.append(bk)
    except NitradoError as exc:
        print("Diagnostic: bookmarks not accessible:", str(exc))

    pending = [(r, 0) for r in dict.fromkeys(roots)]
    seen = set()
    success_lists = 0
    failed_lists = 0
    directory_entries = 0
    file_entries = 0
    last_api_error = None
    while pending and len(seen) < 140:
        here, depth = pending.pop(0)
        if here in seen or depth > 7 or not here.startswith("/"):
            continue
        seen.add(here)
        try:
            entries = entries_at(token, here)
            success_lists += 1
        except NitradoError as exc:
            failed_lists += 1
            last_api_error = str(exc)
            continue
        # Avoid accepting an empty/nonexistent path just because its basename is correct.
        if posixpath.basename(here.rstrip("/")) == MISSION:
            print("Diagnostic: mission found; API metadata:",
                  metadata_found, "bookmarks:", bookmarks_count)
            return here
        for entry in entries:
            name = entry_name(entry)
            if name == MISSION and is_dir(entry):
                resolved = entry.get("path") or safe_dir(here, name)
                print("Diagnostic: mission found; directory listings:", success_lists)
                return str(resolved)
            if is_dir(entry):
                directory_entries += 1
                if name in {"games", "game", "noftp", "ftproot", "dayzps_missions",
                            "missions", "dayz", "server"} or (
                    here.rstrip("/") == "/games" and depth < 2
                ) or (depth < 3 and name.lower().startswith("dayz")):
                    sub = entry.get("path") or safe_dir(here, name)
                    pending.append((str(sub), depth + 1))
            else:
                file_entries += 1

    print("Diagnostic: metadata_available=", metadata_found,
          "bookmark_paths=", bookmarks_count,
          "directory_list_successes=", success_lists,
          "directory_list_failures=", failed_lists,
          "directories_seen=", directory_entries,
          "non_directories_seen=", file_entries)
    if last_api_error:
        print("Diagnostic: last list API error:", last_api_error)
    raise NitradoError(
        "Mission directory dayzOffline.enoch not found with current API access. "
        "No server file was modified. Check diagnostics above."
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
