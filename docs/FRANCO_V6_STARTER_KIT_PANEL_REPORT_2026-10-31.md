# Franco V6 — Starter kit activated in Nitrado config (panel report, 2026-10-31)

## Scope and confirmed actions
- The owner manually uploaded `custom/beileys47_freshspawn_v6.json` on Nitrado PlayStation service 20113048 / Livonia `dayzOffline.enoch`.
- A TinyFish agent using the saved Nitrado profile reported finding a 2.39 KiB JSON **file**, not a directory.
- It reported editing the live `cfggameplay.json` conservatively by adding `PlayerData.spawnGearPresetFiles: ["custom/beileys47_freshspawn_v6.json"]`, without altering the prior `WorldsData.objectSpawnersArr` references.
- The agent reported reopening the edited configuration and seeing the saved entry, enabling `cfggameplay.json` in Nitrado General settings, and restarting the server normally **without a wipe**.
- TinyFish run URL: https://agent.tinyfish.ai/runs/ff03f26c-05fd-4ac4-aa36-64fc0b23e399

## Verification limits
**Nitrado config saved according to the automation, not yet independently validated in the PlayStation runtime.** A fresh PS5 character must be spawned to verify the clothing, bandage, chemlight and food; verify no unexpected default spawn items and inspect the newest RPT for loadout errors.

**Critical agent-report contradiction:** the final TinyFish narrative describes `mission_name`, `spawns`, `loot_settings`, `loot_tables` and ammunition in the 2.39 KiB starter JSON. That does **not match** the actual 2,444-byte `beileys47_freshspawn_v6.json` created earlier, which has the canonical `name`, `spawnWeight`, `attachmentSlotItemSets` and `discreteUnsortedItemSets` and only the lightweight survival kit. Treat those extra fields/loot claims as unreliable until the file is downloaded and compared byte-by-byte.

The same automated narrative labels the existing hotpots as the full large ZONA47 and supplies coordinates that contradict `docs/FRANCO_V4_FIELD_SITES_LIVE_2026-10-31.md`. The old field outposts remain **9+9 static objects**, not the 26-object original ZONA47. Do not overwrite them or claim full ZONA47 based on that report.

## Remaining work
- Verify Nitrado server RUNNING after restart and parse most recent RPT.
- Test fresh spawn on PS5. **No wipe is necessary for a starter kit**; already-living characters do not get the new preset.
- Compare live `db/types.xml` before applying any V5 targeted loot patch. Never replace it from a stale copy.
- Cases + keys are documented as research, not proven usable or placed in the world: `docs/FRANCO_LOCKED_CASES_FRIDGE_CONSOLE_REVIEW.md`.
- Custom 26-object ZONA47 requires actual terrain elevations (Y), classnames, collision and PlayStation smoke tests before install. See Stage 4 docs.
- A custom bunker should not be installed without a tested safe exit; one public design explicitly traps players in it.
- Scheduled automatic prize distribution via custom script and genuinely functioning refrigerators are not supported by stock DayZ PlayStation Nitrado configuration; no PC-only mods can be installed.
- This update is **not a backup of the DayZ world**, players, vehicles or `storage_*`.
