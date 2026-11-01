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
    """Resolve the REAL mission by verifying its contents, not just its name.

    Nitrado may return a successful empty file listing for a nonexistent path.
    Never accept that as proof that a game mission exists.
    """
    roots = ["/", "/games", "/dayzps_missions", "/games/dayzps_missions"]
    candidate_missions = []
    metadata_found = False
    bookmarks_count = 0
    username_ok = False

    def add_candidate(p):
        if (isinstance(p, str) and p.startswith("/") and ".." not in p
                and len(p) < 512):
            p = posixpath.normpath(p)
            if posixpath.basename(p) == MISSION:
                candidate_missions.append(p)
            else:
                roots.append(p)

    def add_base(base):
        if not isinstance(base, str) or not base.startswith("/") or ".." in base:
            return
        base = posixpath.normpath(base)
        add_candidate(base)
        add_candidate(base + "/dayzps_missions")
        add_candidate(base + "/dayzps_missions/" + MISSION)
        add_candidate(base + "/" + MISSION)

    try:
        info = call_api(token, f"/services/{SERVICE_ID}/gameservers")
        gs = info.get("gameserver") or {}
        if isinstance(gs, dict):
            metadata_found = True
            username = gs.get("username")
            if (isinstance(username, str) and username.isascii()
                    and username.replace("_", "").replace("-", "").isalnum()):
                username_ok = True
                add_base(f"/games/{username}")
                add_base(f"/games/{username}/noftp")
                add_base(f"/games/{username}/ftproot")
            gsdata = gs.get("game_specific") or {}
            if isinstance(gsdata, dict):
                gp = gsdata.get("path")
                if isinstance(gp, str) and gp.startswith("/"):
                    add_base(gp)
                    add_base(posixpath.dirname(gp.rstrip("/")))
    except NitradoError as exc:
        print("Diagnostic: gameserver metadata access:", str(exc), flush=True)

    try:
        raw = call_api(token, f"/services/{SERVICE_ID}/gameservers/file_server/bookmarks")
        bookmarks = raw.get("bookmarks", [])
        if isinstance(bookmarks, dict):
            bookmarks = list(bookmarks.values())
        for bm in bookmarks if isinstance(bookmarks, list) else []:
            bp = bm if isinstance(bm, str) else (
                bm.get("path") if isinstance(bm, dict) else None
            )
            if isinstance(bp, str) and bp.startswith("/"):
                bookmarks_count += 1
                add_base(bp)
    except NitradoError as exc:
        print("Diagnostic: bookmarks access:", str(exc), flush=True)

    candidate_missions = list(dict.fromkeys(candidate_missions))
    # Stage A: verify likely full mission paths from metadata/bookmarks.
    # Keep logs credential-free: do not print server username, full path or token.
    listing_ok = 0
    listing_empty = 0
    listing_fail = 0
    token_issue_codes = {}
    checked = set()

    def check_candidate(path):
        nonlocal listing_ok, listing_empty, listing_fail
        if path in checked:
            return False
        checked.add(path)
        try:
            entries = entries_at(token, path)
            names = {entry_name(x) for x in entries}
            if "cfggameplay.json" in names and "cfgweather.xml" in names:
                listing_ok += 1
                return True
            listing_empty += 1
        except NitradoError:
            listing_fail += 1
        # Some Nitrado servers return an empty listing even for a real directory.
        # Try a read-only download token for the exact known configuration path.
        try:
            payload = download_one(token, posixpath.join(path, "cfggameplay.json"))
            data = json.loads(payload.decode("utf-8-sig"))
            if isinstance(data, dict) and "WorldsData" in data and "PlayerData" in data:
                print("Diagnostic: mission confirmed by valid JSON download.", flush=True)
                return True
        except (NitradoError, ValueError, UnicodeError) as exc:
            # No signed URLs or access tokens are ever logged.
            kind = str(exc) if isinstance(exc, NitradoError) else type(exc).__name__
            code = (kind[:100] if "HTTP " in kind else type(exc).__name__)
            token_issue_codes[code] = token_issue_codes.get(code, 0) + 1
        return False

    for path in candidate_missions:
        if check_candidate(path):
            print("Diagnostic: verified mission from metadata/bookmarks.", flush=True)
            return path

    # Stage B: traverse only directory entries exposed by Nitrado. No player
    # persistence, server logs or unnecessary backup directories are opened.
    pending = [(x, 0) for x in dict.fromkeys(roots)]
    walked = set()
    listed_nonempty = 0
    while pending and len(walked) < 130:
        parent, depth = pending.pop(0)
        if (parent in walked or depth > 7 or
                not isinstance(parent, str) or not parent.startswith("/")):
            continue
        walked.add(parent)
        if posixpath.basename(parent.rstrip("/")) == MISSION:
            if check_candidate(parent):
                print("Diagnostic: verified mission from directory traversal.", flush=True)
                return parent
            continue
        try:
            entries = entries_at(token, parent)
        except NitradoError:
            listing_fail += 1
            continue
        if entries:
            listed_nonempty += 1
        for e in entries:
            name = entry_name(e)
            if not name or name in (".", "..") or "/" in name:
                continue
            if name == MISSION:
                sub = e.get("path") or posixpath.join(parent, name)
                if check_candidate(str(sub)):
                    print("Diagnostic: verified mission from directory listing.", flush=True)
                    return str(sub)
            elif is_dir(e) and (
                    name.lower() in {"games", "game", "noftp", "ftproot",
                                     "dayzps_missions", "missions", "dayz", "server"}
                    or (parent.rstrip("/") == "/games" and depth < 3)
                    or (depth < 3 and name.lower().startswith("dayz"))
            ):
                pending.append((str(e.get("path") or posixpath.join(parent, name)), depth + 1))

    print("Diagnostic: metadata available:", metadata_found,
          "; valid username:", username_ok,
          "; bookmarks:", bookmarks_count,
          "; candidate paths checked:", len(checked),
          "; candidate directory listings nonempty:", listing_ok,
          "; candidate empty or incorrect:", listing_empty,
          "; listings rejected:", listing_fail,
          "; navigable directory listings:", listed_nonempty,
          "; download failures:", token_issue_codes,
          flush=True)
    raise NitradoError(
        "Cannot identify a real DayZ mission with readable cfggameplay.json. "
        "Probe did not confirm download access. No files were modified."
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
    print("Nitrado mission verified by real configuration content.")
    print("Mission folder resolved (remote path deliberately hidden in logs).")
    print("No file downloaded or changed in probe mode.")

def snapshot(token, output):
    mission_root = resolve_mission(token)
    # Verify that the folder returned by the API really contains DayZ config files.
    # A valid HTTP 200 on an empty/nonexistent directory is not sufficient.
    try:
        base_entries = entries_at(token, mission_root)
        base_names = {entry_name(entry) for entry in base_entries}
        expected = {"cfggameplay.json", "cfgweather.xml", "cfgeconomycore.xml"}
        print("Diagnostic: mission listing contains", len(base_entries), "entries; "
              "expected config files present:", len(expected & base_names), "/", len(expected))
        if not expected & base_names:
            raise NitradoError("The discovered mission folder does not list any core config file; "
                               "no download attempted. Verify the Nitrado bookmark/mission path.")
    except NitradoError as exc:
        print("Diagnostic: mission listing failed:", str(exc))
        raise
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
            # Errors are constructed locally and never expose token, URL, response body
            # or other credentials. Show actionable cause in GitHub Actions logs.
            print("MISSING/ERROR:", rel, "-", str(exc))
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
    # Regression: an empty Nitrado listing must NEVER be treated as
    # a valid mission even when the folder basename appears correct.
    from unittest.mock import patch
    from contextlib import redirect_stdout
    from io import StringIO
    simulated_api = lambda token, endpoint, params=None: (
        {"gameserver": {"username": "test_account", "game_specific": {}}}
        if endpoint.endswith("/gameservers") else {"bookmarks": []}
    )
    with (patch(__name__ + ".call_api", side_effect=simulated_api),
          patch(__name__ + ".entries_at", return_value=[]),
          patch(__name__ + ".download_one",
                side_effect=NitradoError("download blocked")),
          redirect_stdout(StringIO())):
        try:
            resolve_mission("test-token")
            raise AssertionError("False positive: empty mission accepted")
        except NitradoError:
            pass
    # Regression: an actual directory listing with both core config
    # filenames is accepted, without needing to download any files.
    def fake_entries(token, directory):
        if directory.endswith("/dayzOffline.enoch"):
            return [{"name": "cfggameplay.json", "type": "file"},
                    {"name": "cfgweather.xml", "type": "file"}]
        return []
    with (patch(__name__ + ".call_api", side_effect=simulated_api),
          patch(__name__ + ".entries_at", side_effect=fake_entries),
          patch(__name__ + ".download_one",
                side_effect=NitradoError("Not needed")),
          redirect_stdout(StringIO())):
        assert resolve_mission("test-token").endswith("/dayzOffline.enoch")
    print("Local safety + directory resolution regression tests passed. No network used.")

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
