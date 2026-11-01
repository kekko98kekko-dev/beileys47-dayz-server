#!/usr/bin/env python3
"""BEILEYS47 V15: guarded, idempotent, no-wipe Nitrado DayZ PlayStation deployment.

This automation is EXPLICITLY authorized by server owner (November 1 2026).
It refuses deployment if the service reports players, unknown status,
unexpected current file hashes, or invalid config changes.
No persistence wipe, database clear, reinstallation or player data edits.
"""
import base64
import copy
import hashlib
import json
import os
import posixpath
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

from nitrado_snapshot import API, SERVICE_ID, NitradoError, resolve_mission, download_one, call_api

REPO_ROOT = Path(__file__).resolve().parent.parent
VEHICLE_DATA = REPO_ROOT / "deploy/v15/vehicle_changes_b64.txt"
SNAPSHOT_HASHES = {
    "cfgspawnabletypes.xml": "137f8b8df4e437c49c021e545b8c515c75913696385cba6bfe84254e4e474fd7",
    "cfgweather.xml": "8f7eb6e8d6cd46e49d777f04b024e2ecf9f19264dfc010efda61a242bf6d2b30",
    "cfgeventspawns.xml": "3d2ff517094ece47040b2c306594c0a42681de5d23a52e2b853138082ebabcad",
    "mapgrouppos.xml": "407fb3aad267bae9d039106dc4aad4ede3ad32797138c25f6f720b0c1698350d",
    "db/events.xml": "cb105cfb4102a9c65f45ef4f2095dad5edb6f9deaf901e212fa600dc0954594a",
    "db/types.xml": "9e33b8d8f91004ef3fae4fabfcc88102a87547849fc8681f0ba07cd9b748ffa2",
    "custom/beileys47_dolnik_military_base_v9.json": "b83c64b3f632ce34130d3d9a1941d9bc652522cc3b0b82c4fffd95b7ad578164"
}
TRUCK_EVENT = "VehicleBEILEYS47DolnikTest"
SPAWN = (11574.92, 374.01, 177.83)
TENT_MED = ("Land_Medical_Tent_Big", 11508.31640625, 441.74154663)
TENT_MIL = ("Land_Mil_Tent_Big2_4", 11476.400390625, 456.8460083)
REPORT_PATH = REPO_ROOT / "deploy/v15/deploy_result.json"

def report(**fields):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(fields, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def require(ok, message):
    if not ok:
        raise NitradoError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def xml_load(data):
    return ET.fromstring(data, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))

def xml_out(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def find(root, tag, name):
    obj = root.find(f"{tag}[@name='{name}']")
    require(obj is not None, "Missing expected element " + tag + " " + name)
    return obj

def build_config(old):
    """All 7 target files come from fresh Nitrado downloads, not vanilla examples."""
    for name, expected in SNAPSHOT_HASHES.items():
        require(digest(old[name]) == expected, "Live changed since approved snapshot: " + name +
                ". No deployment; refresh and review the diff first.")

    output = {}
    vehicle_patches = json.loads(zlib.decompress(base64.b64decode(
        VEHICLE_DATA.read_text(encoding="ascii").strip()
    )).decode("utf-8"))
    require(len(vehicle_patches) == 17, "Expected exactly 17 vehicle-class patches")
    root = xml_load(old["cfgspawnabletypes.xml"])
    for name, fragment in vehicle_patches.items():
        target = find(root, "type", name)
        index = list(root).index(target)
        replacement = xml_load(fragment.encode())
        require(replacement.get("name") == name, "Invalid vehicle patch name")
        # Keep only cargo items supported by the current DayZ console types.
        for cargo in list(replacement.findall("cargo")):
            if any(item.get("name") == "JerryCan" for item in cargo.findall("item")):
                replacement.remove(cargo)
        root.remove(target)
        root.insert(index, replacement)
    for name in ("Truck_01_Covered", "Truck_01_Covered_Blue", "Truck_01_Covered_Orange"):
        truck = find(root, "type", name)
        amounts = [item.get("name") for item in truck.findall(".//cargo/item")]
        require(amounts.count("NailBox") == 10, "NailBox not exactly ten in " + name)
        require(all(x in amounts for x in ("Rope", "Hammer", "WoodAxe", "BarbedWire",
                    "MetalWire", "GunCaseKeys_Blue", "ScientificBriefcase")),
                "Construction/special cargo incomplete: " + name)
    output["cfgspawnabletypes.xml"] = xml_out(root)

    weather = xml_load(old["cfgweather.xml"])
    weather.set("reset", "1")
    fog = weather.find("fog")
    require(fog is not None, "Missing weather fog tag")
    fog.find("current").set("actual", "0.0")
    for tag in ("limits", "changelimits"):
        el = fog.find(tag)
        require(el is not None, "Missing fog " + tag)
        el.set("min", "0.0")
        el.set("max", "0.0")
    require(weather.find("rain").find("limits").get("max") != "0.0", "Rain must remain enabled")
    output["cfgweather.xml"] = xml_out(weather)

    scene = json.loads(old["custom/beileys47_dolnik_military_base_v9.json"])
    objects = scene.get("Objects")
    require(isinstance(objects, list) and len(objects) == 29,
            "Unexpected Dolnik live scene")
    def keep_tent(item):
        return any(item.get("name") == target[0] and
                   abs(item["pos"][0] - target[1]) < 0.1 and
                   abs(item["pos"][2] - target[2]) < 0.1
                   for target in (TENT_MED, TENT_MIL))
    slim = [obj for obj in objects
            if "Tent" not in obj.get("name", "") or keep_tent(obj)]
    require(len(slim) == 18 and sum("Tent" in x["name"] for x in slim) == 2,
            "Dolnik tent removal did not yield two tents + 16 other structures")
    scene["Objects"] = slim
    output["custom/beileys47_dolnik_military_base_v9.json"] = (
        json.dumps(scene, indent=2, ensure_ascii=False) + "\n").encode()

    mapgroups = xml_load(old["mapgrouppos.xml"])
    removed = []
    kept = []
    for group in list(mapgroups):
        pos = group.get("pos") or ""
        if group.tag != "group" or "Tent" not in (group.get("name") or ""):
            continue
        try:
            x, y, z = map(float, pos.split())
        except ValueError:
            continue
        if not (11400 < x < 11650 and 350 < z < 540):
            continue
        g = {"name": group.get("name"), "pos": [x,y,z]}
        if keep_tent(g):
            kept.append(g)
        else:
            removed.append(g)
            mapgroups.remove(group)
    require(len(removed) == 11 and len(kept) == 2,
            "Map CE group count mismatch. Refuse removing unrelated structures.")
    output["mapgrouppos.xml"] = xml_out(mapgroups)

    events = xml_load(old["db/events.xml"])
    require(events.find(f"event[@name='{TRUCK_EVENT}']") is None,
            "Custom Dolnik truck event already exists; refuses duplicate")
    truck = find(events, "event", "VehicleTruck01")
    for tag, value in (("nominal","10"),("min","6"),("max","12")):
        find_tag = truck.find(tag)
        require(find_tag is not None, "Missing truck event parameter " + tag)
        find_tag.text = value
    for name, amount in (("StaticHeliCrash","5"),("StaticMilitaryConvoy","5")):
        find(events, "event", name).find("nominal").text = amount
    custom_event = ET.fromstring(f"""<event name="{TRUCK_EVENT}">
        <nominal>1</nominal><min>1</min><max>1</max>
        <lifetime>300</lifetime><restock>0</restock>
        <saferadius>150</saferadius><distanceradius>100</distanceradius>
        <cleanupradius>100</cleanupradius>
        <flags deletable="0" init_random="0" remove_damaged="1"/>
        <position>fixed</position><limit>mixed</limit><active>1</active>
        <children><child lootmax="0" lootmin="0" max="1" min="1" type="Truck_01_Covered"/></children>
        </event>""")
    events.append(custom_event)
    output["db/events.xml"] = xml_out(events)

    eventspawns = xml_load(old["cfgeventspawns.xml"])
    spawn_trucks = find(eventspawns, "event", "VehicleTruck01")
    candidates = [p for p in spawn_trucks.findall("pos") if
        abs(float(p.get("x"))-SPAWN[0])<0.10 and
        abs(float(p.get("z"))-SPAWN[1])<0.10]
    require(len(candidates) == 1, "Official Dolnik truck point not unique")
    spawn_trucks.remove(candidates[0])
    new_eventpos = ET.SubElement(eventspawns,"event",name=TRUCK_EVENT)
    ET.SubElement(new_eventpos,"pos",
                  x=f"{SPAWN[0]:.2f}", z=f"{SPAWN[1]:.2f}", a=f"{SPAWN[2]:.2f}")
    output["cfgeventspawns.xml"] = xml_out(eventspawns)

    types = xml_load(old["db/types.xml"])
    pile = find(types,"type","PileOfWoodenPlanks")
    require(pile.find("quantmin") is not None and pile.find("quantmax") is not None,
            "PileOfWoodenPlanks quantity tags missing")
    pile.find("quantmin").text = "100"
    pile.find("quantmax").text = "100"
    output["db/types.xml"] = xml_out(types)

    for name, blob in output.items():
        if name.endswith(".xml"):
            xml_load(blob)
        elif name.endswith(".json"):
            json.loads(blob)
        require(len(blob) > 50, "Generated file too small: " + name)
    # Confirm every cargo classname from V13 exists in the live CE types.
    valid = {x.get("name") for x in types.findall("type")}
    for vehicle_name in vehicle_patches:
        vehicle = find(root, "type", vehicle_name)
        for cargo in vehicle.findall(".//cargo/item"):
            require(cargo.get("name") in valid, "Unknown console cargo type " + str(cargo.get("name")))
    return output

def game_state(token):
    info = call_api(token, f"/services/{SERVICE_ID}/gameservers")
    gs = info.get("gameserver")
    require(isinstance(gs, dict), "Nitrado game state unavailable")
    return gs

def players(gs):
    query = gs.get("query") if isinstance(gs.get("query"), dict) else {}
    for value in (query.get("player_current"), gs.get("player_current")):
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None

def game_status(gs):
    return str(gs.get("status") or "").lower()

def request_api_post(token, endpoint, form=None):
    encoded = urllib.parse.urlencode(form or {}).encode()
    req = urllib.request.Request(API + endpoint, data=encoded, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "User-Agent": "BEILEYS47-controlled-deployment/1.0"
    },method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body = response.read(256 * 1024)
            reply = json.loads(body)
    except urllib.error.HTTPError as exc:
        raise NitradoError("API POST HTTP " + str(exc.code) + " at " + endpoint) from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise NitradoError("API POST connection or response failed at " + endpoint) from None
    require(reply.get("status")=="success", "Nitrado API rejected " + endpoint)
    return reply.get("data", {})

def wait_status(token, wanted, attempts=36):
    for _ in range(attempts):
        gs = game_state(token)
        if game_status(gs) in wanted:
            return gs
        time.sleep(5)
    raise NitradoError("Server state did not reach " + ",".join(sorted(wanted)))

def upload_file(token, remote, blob):
    folder, name = posixpath.split(remote)
    reply = request_api_post(token,
             f"/services/{SERVICE_ID}/gameservers/file_server/upload",
             {"path": folder, "file": name})
    ticket = reply.get("token") if isinstance(reply, dict) else None
    require(isinstance(ticket, dict) and ticket.get("token") and ticket.get("url"),
            "Nitrado did not issue an upload ticket")
    url = ticket["url"]
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username,
            "Untrusted upload address returned by Nitrado")
    req = urllib.request.Request(url, data=blob, headers={
        "token": ticket["token"], "content-type": "application/binary",
        "User-Agent": "BEILEYS47-controlled-deployment/1.0"
    },method="POST")
    try:
        with urllib.request.urlopen(req,timeout=100) as response:
            response.read(256*1024)
    except urllib.error.HTTPError as exc:
        raise NitradoError("File upload rejected HTTP " + str(exc.code) + " for " + name) from None
    except (urllib.error.URLError, TimeoutError):
        raise NitradoError("File upload network failure for " + name) from None

def main():
    token = os.environ.get("NITRADO_API_TOKEN","").strip()
    require(token, "Missing GitHub NITRADO_API_TOKEN secret")
    require(os.environ.get("BEILEYS47_V15_APPROVED") == "yes",
            "V15 not explicitly approved in workflow")
    mission = resolve_mission(token)
    files = {}
    print("Reading seven current Nitrado configurations for guarded V15 deployment.",flush=True)
    for rel in SNAPSHOT_HASHES:
        files[rel] = download_one(token, posixpath.join(mission,rel))
        print("Read:", rel, flush=True)
    output = build_config(files)
    print("V15 seven-file static validation passed; Dolnik two tents; no wipe.",flush=True)
    if os.environ.get("BEILEYS47_V15_MODE") == "validate":
        report(status="preflight_validated", file_sha256={key:digest(value) for key,value in output.items()},
               wipe=False, file_changes_live=False, ps5_tested=False)
        print("PREFLIGHT ONLY: seven files validated locally; Nitrado untouched.",flush=True)
        return
    require(os.environ.get("BEILEYS47_V15_MODE") == "deploy",
            "Invalid mode: must be validate or deploy")
    gs = game_state(token)
    count = players(gs)
    status = game_status(gs)
    require(status in {"started","running","stopped"}, "Unexpected server status: " + status)
    if status != "stopped":
        require(count == 0, "Player count unknown or nonzero: NO DEPLOY")
    else:
        print("Server is already stopped; no players can be connected.", flush=True)
    stopped_by_us = status != "stopped"
    modified = []
    try:
        if stopped_by_us:
            print("0 players confirmed; requesting normal Nitrado stop.",flush=True)
            request_api_post(token,f"/services/{SERVICE_ID}/gameservers/stop")
            wait_status(token, {"stopped"}, attempts=36)
        # A second check ensures nobody remained connected before writes.
        print("Nitrado server stopped; uploading seven validated config files.",flush=True)
        for rel,blob in output.items():
            remote = posixpath.join(mission,rel)
            upload_file(token,remote,blob)
            modified.append(rel)
            result = download_one(token,remote)
            require(digest(result) == digest(blob), "Post-upload SHA mismatch: " + rel)
            print("VERIFIED:",rel,flush=True)
        report(status="file_uploads_verified", files=modified,
               service_id=SERVICE_ID, wipe=False, ps5_tested=False)
    except Exception as error:
        print("Deployment failed; attempt in-memory rollback of changed files.",flush=True)
        for rel in reversed(modified):
            try:
                upload_file(token,posixpath.join(mission,rel),files[rel])
                print("ROLLED BACK:",rel,flush=True)
            except Exception:
                print("ROLLBACK ERROR:",rel,flush=True)
        report(status="deploy_error", files_modified_before_error=modified,
               error=type(error).__name__, wipe=False)
        raise
    finally:
        # After a successful upload, request start even when the game server
        # was already stopped before the workflow began.
        if modified and len(modified) == len(output):
            try:
                request_api_post(token,f"/services/{SERVICE_ID}/gameservers/restart")
                print("Nitrado restart/start requested after verified upload.",flush=True)
            except Exception:
                print("WARNING: automatic restart request failed; check Nitrado panel.",flush=True)
    print("V15 file verification complete. PS5 gameplay verification is still required.",flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("DEPLOY ERROR:",str(exc)[:240],file=sys.stderr)
        sys.exit(1)
