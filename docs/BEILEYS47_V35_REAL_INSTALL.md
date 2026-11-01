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
