# BEILEYS47 V48 — Build Anywhere (offline candidate, not deployed)

**Scope:** PS4/PS5, DayZ Livonia 1.30. **No Nitrado writes or restarts**. Because V46 reported a raw SHA mismatch in `db/types.xml`, do not automate further writes before verifying fresh backups and remote readback. V47 was a GET-only semantic verification of truck and loot XML, **not** an inspection of the live `cfggameplay.json` BaseBuildingData.

## What the player asked
- Easier placement of a second `FenceKit` above an existing built fence, enabling taller multi-level bases where engine geometry permits.
- Ability to stack `WoodenCrate` and barrels, as previously experienced.

These are **different subsystems**. `cfggameplay.json` has supported placement/construction checks but is **not** a guaranteed crate/barrel stacking switch. Stacking may depend on the game's inventory/physics/collision rules and client update, not on server-base-building switches. Nothing in this preview guarantees stackability or the ability to place another complete fence kit on top of one fence.

## Profiles
- `balanced` (recommended first): set `true` for `HologramData.disableIsCollidingBBoxCheck`, `disableIsBaseViableCheck`, `disableIsCollidingAngleCheck`, `disableHeightPlacementCheck`; and `ConstructionData.disableIsCollidingCheck`.
- `extended` (only if balanced fails and after PvP exploitation assessment): additionally set `HologramData.disableIsClippingRoofCheck`, `disableIsPlacementPermittedCheck`; and `ConstructionData.disablePerformRoofCheck`. **This could permit clipped or unfair/inaccessible PvP bases.**
- Both profiles preserve `disableIsUnderwaterCheck`, underground disallowed types, `disableIsInTerrainCheck`, all gameplay, spawner references, loadouts, stamina, UI, vehicles and persistence untouched.

## Offline preview procedure
1. Obtain an up-to-date **read-only** copy of the live Livonia `cfggameplay.json` and a separate verified SHA-256 backup; do not use the historical V9 candidate as live baseline.
2. Run `python scripts/v48_build_anywhere_preview.py cfggameplay_live.json cfggameplay_V48_BALANCED_CANDIDATE.json` on a local machine; it refuses to overwrite input/output and performs no remote actions.
3. Compare resulting JSON changes with the original, then test on a non-public PS5 session. Check fence on fence, wall against building, garage doors, terrain clipping, watchtower, flag, and restart persistence. Separately test 2 crates and 2 barrels. Do not assume success based on JSON syntax alone.
4. **Only after the V46 drift problem is understood:** schedule an authorized, player-free maintenance window, verified backup and rollback, upload only the audited JSON, restart and validate PS5 behaviour. No such deploy exists in V48.

Official setting definitions: https://community.bistudio.com/wiki/DayZ:Gameplay_Settings
