# V35 — ACTUAL NITRADO DEPLOY OF THE 25 ZONA47 WORLD PROPS

**Purpose:** Install the full 26-marker ZONA 47 experimental scene in Livonia (original V29 P1 + 25 new props). Previous V31/V32/V33 stages created only offline files; V35 now **attempts an actual live Nitrado upload and activation** when explicit safety gates pass.

The owner expressly authorized the installation and an optional wipe in this conversation. **No wipe is needed or performed.** Existing player database and storage, loot economy, V20 unlimited sprint, V16 Radunin/Bunker/Dolnik scenes, V21 messages, weather and vehicle changes must remain untouched.

## Preconditions and automatic protection

- Verify Nitrado is the actual Livonia mission, original V29 P1, V16, Dolnik are still registered, V20 stamina and movement unchanged, and exactly 25 new objects appear in the source.
- Confirm the final V32 conservative visual geometry report says zero visible circular footprint collisions. This is **not** proof of actual collision in the game.
- Read and ZIP the *live* `cfggameplay.json` plus existing spawner files. Verify ZIP bytes/hash before any update. This backup is **config-only**, not a full save/database backup.
- Two independent zero-player checks. If someone is online or count is unknown, fail without interruption.
- Reject uploads if the target new filename already exists; never replace another scene. Recheck all original file hashes after stopping.
- Only add one new JSON scene file `custom/beileys47_v35_zone47_full_25.json` and append its reference to `WorldsData.objectSpawnersArr` inside `cfggameplay.json`.
- Re-read hashes of both files, perform normal restart, re-read and verify registered scenes. Original `cfggameplay.json` can be restored from private artifact on any error.

## What a success confirms

Exactly 25 additional Object Spawner entries are stored in Nitrado and the reference is activated in the server configuration alongside P1; **26 planned positions** exist as config.

What success does **not** prove: all 25 assets physically render on PlayStation, exact model-ground contact, NPC/chest interaction, traversable bunker entrances, PS4 framerate, or original 12 priorities at 100%. A wipe would not prove those things either.

## Reference

- [Public official Bohemia DayZ Object Spawner](https://community.bistudio.com/wiki/DayZ:Object_Spawner)
- `config/v33/BEILEYS47_ZONE47_25_NOT_LIVE.json` is source design, but after V35 installer succeeds the **new** file is live on Nitrado.
- The V35 workflow produces `deploy/v35/LIVE_DEPLOY_RESULT.json` and private rollback archive. Consult the specific run for verified status.
- Console runtime visual acceptance remains a separate check.

## VERIFIED LIVE RESULT — 1 November 2026

- [V35 actual Nitrado installation GitHub run 41309552433](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41309552433) **SUCCESS**, including protected live-install job. The log explicitly states: `V35 INSTALL SUCCESS: 25 new ZONA47 objects registered, P1 retained, no wipe`.
- [Independent read-only V35/V29/V21/V20 audit run 41309830380](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41309830380) **SUCCESS**:
  - Nitrado status `started`
  - V35 file **registered** in current gameplay spawner list.
  - New V35 scene **25 objects**, byte-decoded JSON **exactly matches reviewed versioned 25-object file**.
  - Old V29 P1 retained: **26 total ZONA47 objects** represented in installed registered scenes.
  - V16 scenery, Dolnik tents, special economy, weather and events still verified.
  - V20 unlimited sprint configured and enabled; 6 V21 in-game notices present.
- [Private backup artifact 13084193435](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41309552433/artifacts/13084193435) from installation; configuration files only, retained seven days. **Not a full Nitrado world-persistence backup.**
- No wipe or manipulation of player storage performed by V35.
- **Runtime still unverified:** even after both remote checks, whether all 26 objects appear with correct ground pivot, doors, collisions and acceptable PS4/PS5 frame-rate must be tested in game. The experimental design has no automated gameplay acceptance. Do not claim 100% project completion until these and other remaining game features are verified.

