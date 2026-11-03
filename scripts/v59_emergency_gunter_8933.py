#!/usr/bin/env python3
"""V59: user-requested ONE fixed Gunter 2 rescue at Livonia 8933.20 / 7211.91.

Fail closed. Reuse V53's backup, zero-player gate, post-upload checks,
rollback protection and server restart. Never touch storage_1 or wipe.
A DayZ console CE spawn request does NOT guarantee physical car presence,
actual tank fuel, or coolant fill. Verify on PS5 after deployment.
"""
from __future__ import annotations
import os
import posixpath
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import v53_gunter_gift as legacy
from nitrado_snapshot import resolve_mission, download_one

EVENT = "VehicleBEILEYS47GunterRescueV59"
X = 8933.20
Z = 7211.91

# These are alternative *vanilla* classnames, resolved against the LIVE
# Livonia db/types.xml. Missing essential groups abort before any write.
REQUIRED = {
    "rifle": ("AKM",),
    "75_round_mag": ("Mag_AKM_Drum75Rnd",),
    "ballistic_vest": ("PlateCarrierVest_Black", "PlateCarrierVest_Green", "PlateCarrierVest"),
    "helmet": ("CombatHelmet_Black", "GorkaHelmet_Black", "Mich2001Helmet", "GorkaHelmet"),
    "jacket": ("GorkaEJacket_Black", "GorkaEJacket_Summer", "GorkaEJacket_Autumn", "BDUJacket"),
    "pants": ("GorkaPants_Black", "GorkaPants_Summer", "CargoPants_Black", "BDUPants"),
    "boots": ("MilitaryBoots_Black", "CombatBoots_Black", "JungleBoots_Black"),
    "gloves": ("TacticalGloves_Black", "TacticalGloves_Green", "WorkingGloves_Black"),
    "backpack": ("AliceBag_Black", "AliceBag_Green", "AssaultBag_Black"),
}
OPTIONAL = {
    "face_cover": ("BalaclavaMask_Black", "SkiMask_Black", "BandanaMask_Black"),
    "night_vision": ("NVGoggles",),
    "nv_mount": ("NVGHeadstrap",),
    "battery": ("Battery9V",),
    "vest_pouches": ("PlateCarrierPouches",),
    "vest_holster": ("PlateCarrierHolster",),
    "rifle_suppressor": ("AK_Suppressor",),
    "rifle_scope": ("PSO1Optic", "KobraOptic"),
    "cleaning_kit": ("WeaponCleaningKit",),
    "medical": ("BandageDressing",),
    "ammo": ("Ammo_762x39",),
    "canteen": ("Canteen",),
    "fuel": ("CanisterGasoline",),
    "tyre_kit": ("TireRepairKit",),
    "spare_radiator": ("CarRadiator",),
    "spare_sparkplug": ("SparkPlug",),
}
EXTRA_COUNTS = {
    "75_round_mag": 2,
    "ammo": 3,
    "medical": 2,
    "canteen": 2,
}
ORIGINAL_PATCH = legacy.patch


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def choose(available, possibilities):
    return next((name for name in possibilities if name in available), None)


def configure():
    require(os.getenv("BEILEYS47_V59_APPROVED") == "yes",
            "V59 owner approval env missing")
    token = os.getenv("NITRADO_API_TOKEN", "").strip()
    require(bool(token), "Nitrado secret missing")
    mission = resolve_mission(token)
    events = legacy.parse(download_one(token, posixpath.join(mission, "db/events.xml")))
    positions = legacy.parse(download_one(token, posixpath.join(mission, "cfgeventspawns.xml")))
    require(events.find("event[@name='VehicleBEILEYS47GunterGiftV53']") is None
            and positions.find("event[@name='VehicleBEILEYS47GunterGiftV53']") is None,
            "Old removed Gunter gift config unexpectedly present; no duplicate")
    require(events.find(f"event[@name='{EVENT}']") is None
            and positions.find(f"event[@name='{EVENT}']") is None,
            "V59 already configured; never run deployment twice")
    live_types = legacy.parse(download_one(token, posixpath.join(mission, "db/types.xml")))
    available = {x.get("name") for x in live_types.findall("type")}
    selected = {}
    for group, candidates in REQUIRED.items():
        found = choose(available, candidates)
        require(found is not None, "Missing essential Livonia kit group: " + group)
        selected[group] = found
    for group, candidates in OPTIONAL.items():
        found = choose(available, candidates)
        if found:
            selected[group] = found

    # Cap in-car item entries; all changes are scoped to one spawnable
    # classname. DayZ cfgspawnabletypes.xml is per-class, NOT per-event.
    cargo = {}
    for group, classname in selected.items():
        cargo[classname] = cargo.get(classname, 0) + EXTRA_COUNTS.get(group, 1)
    require(all(x in available for x in cargo), "Selected cargo contains unknown class")
    require(sum(cargo.values()) <= 35, "Too many rescue items")
    legacy.EVENT = EVENT
    legacy.X = X
    legacy.Z = Z
    legacy.YAW = 0.0
    legacy.CARGO = cargo
    legacy.OUT = Path("deploy/v59/GUNTER_8933_DEPLOY_RESULT.json")
    legacy.ARCH = Path("deploy/v59/PRIVATE_ORIGINAL_3XML.zip")
    legacy.patch = add_quantity_and_long_restock
    # This is the same explicit operator approval, passed to the extensively
    # exercised V53 upload/restart transaction rather than bypassing checks.
    os.environ["BEILEYS47_V53_APPROVED"] = "yes"
    print("V59 selected kit:", sorted(selected.items()), flush=True)


def add_quantity_and_long_restock(before, live_types):
    changed, details = ORIGINAL_PATCH(before, live_types)
    if changed is None:
        raise RuntimeError("Unexpected already-configured rescue event")
    events = legacy.parse(changed[legacy.FILES[0]])
    ev = events.find(f"event[@name='{EVENT}']")
    require(ev is not None, "Rescue event absent")
    ev.find("restock").text = "31536000"  # One year; still not never-respawn guarantee
    ev.find("saferadius").text = "0"  # Owner may stand nearby on first restart
    changed[legacy.FILES[0]] = legacy.data(events)

    spawns = legacy.parse(changed[legacy.FILES[2]])
    car = spawns.find(f"type[@name='{legacy.CAR}']")
    require(car is not None, "Gunter class profile missing")
    for item in car.findall("./cargo/item"):
        if item.get("name") in {"Mag_AKM_Drum75Rnd", "CanisterGasoline", "Canteen"}:
            item.set("quantmin", "100")
            item.set("quantmax", "100")
    changed[legacy.FILES[2]] = legacy.data(spawns)
    good, _ = legacy.patch_for_postread(changed)
    require(good, "Rescue loadout failed post-patch check")
    return changed, details


if __name__ == "__main__":
    try:
        configure()
        legacy.main()
    except Exception as e:
        print("V59 ERROR", type(e).__name__, str(e)[:210], file=sys.stderr)
        raise SystemExit(1)
