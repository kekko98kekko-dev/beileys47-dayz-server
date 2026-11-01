# BEILEYS47 V47 — Independent live state after V46 restart

**Date:** 1 November 2026. Independent Nitrado read-only workflow: https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41337667223 — SUCCESS.

## Real server state verified
- Status **started**, zero players at read-only inspection.
- V44: two old CE event sources `VehicleBEILEYS47DolnikTest` and `VehicleBEILEYS47DolnikRescueV40` both `nominal=min=max=0`, `active=0`. They retain their XML position history but no longer generate new trucks.
- New `VehicleBEILEYS47DolnikUltimateV43` is `nominal=min=max=1`, `active=1` at **X11574.92, Z374.01, heading177.83°**.
- `Truck_01_Covered` profile: 25 attachment groups, all chance=1; 4 barrel slots, 4 WoodenCrate slots, truck parts 100%, WoodenLog/WoodenPlank/MetalPlate quantity percent 100.
- New loadout has 112 cargo entries including `TerritoryFlagKit`, `TerritoryFlag`, 32 stones, 6 nail boxes, complete repair and vehicle spares, Field Backpack 64, premium weapons, medical gear, two filled-class fuel canister spawn entries, with *no weapon cases/scientific briefcases* in this new truck profile.
- V45: the same read-only XML pass identifies zero **still-eligible** ordinary loot entries for the 4h cap (i.e. its desired lifetime rules are already present). Zero-player state post-restart.

## Explain V46 failure honestly

The combined push workflow https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41336984226 returned **failure** due post-restart raw SHA mismatch for `db/types.xml` after successful upload. Rollback returned a manual-recovery-required report. It is not safe to ignore this. A follow-up GET-only probe found the server live, complete V44 event change, and zero remaining eligible V45 entries. The exact remote types.xml bytes differ from the original SHA and the locally predicted fully reserialized SHA. Most likely a provider-side transformation or concurrent rewrite, but **cause not confirmed**. The independent semantic checks—not the failed workflow—support current configuration.

Backup original four mission files available privately in GitHub V46 artifact `13095931457` for only 7 days. Preserve for manual recovery. This is a CONFIG archive, not a world save.

## What has NOT been established
- Not possible to confirm that the 2 old **persisted truck entities** were deleted: disabling CE events cannot surgically delete individual stored world instances. **Do NOT wipe `storage_1/data` to try it**, because that deletes bases, crates and all other vehicles.
- The single new CE event is **not proof exactly one truck currently exists in the world** nor that the engine spawned it at that coordinate. A player needs to go in-game.
- 112 cargo entries with chance=1 are not proof all items fit physically inside the engine's 600 inventory slots; four attached crates and barrels are not guaranteed filled themselves.
- Fuel canisters in inventory do not automatically fill the truck fuel tank.
- The 4-hour lifetime cap is wallclock, NOT exactly after two restarts and intentionally excludes persistent construction/storage/vehicles and special drops.

## Safety after failure
Scheduled Nitrado write workflows have been temporarily paused to avoid overwriting files while investigating raw hash drift. A GET-only audit is allowed. Restore schedules selectively after a controlled review. 
