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

## Addendum — Nitrado live recheck and fresh RPT smoke test (2026-10-31)

A second Nitrado TinyFish read-only audit observed:
- `db/types.xml`: `GunCase_Black`, `GunCase_White`, `GunCaseKeys_Blue`, `GunCaseKeys_Red` each `nominal=2`, `min=1`, military use. No file modified.
- `db/events.xml`: `StaticHeliCrash` and `StaticMilitaryConvoy` each `nominal=4`, heli Mi8 child `max=4`, active events. No file modified.
- Actual `custom/beileys47_freshspawn_v6.json` has the four canonical preset keys, NOT the prior agent's invented spawn coordinates/ammunition.
- `cfggameplay.json` contains V6 kit reference and both V4 outpost object spawner paths.

An RPT captured during the earlier deployment window (`DAYZSERVER_PS4_X64_2026-10-31_15-29-01.RPT`) contained a `JSON ERROR: The document root must not be followed by other values` for `$mission:cfggameplay.json`. **A subsequent full live editor recheck reported a clean single-root JSON and no changed fields except V6 kit**, so no replacement was performed. A syntax-validated recovery candidate was committed at `mission/franco_v6/cfggameplay_v6_validated_repair.json` for future emergency recovery, not auto-applied.

**Decisive follow-up smoke test:** at 0/10 players, a normal Nitrado restart without wipe was performed, and the fresh log `DayZServer_PS4_x64_2026-10-31_16-08-35.RPT` was inspected. The agent reported:
- no `JSON ERROR`, no `Object spawner failed to spawn` in the new log;
- Central Economy initialized; `16:09:10.611 Player connect enabled`;
- Nitrado dashboard `RUNNING`, 0/10 players after restart;
- hostname `BEILEYS47 | SURVIVAL WAR | LIVONIA | NO SCHEDULED WIPES`.

TinyFish audit: https://agent.tinyfish.ai/runs/9dadb3be-c061-4a14-843f-168c6503d870
Editor recheck: https://agent.tinyfish.ai/runs/dcd4030b-94e8-4bb0-accf-34228935d538
Fresh RPT: https://agent.tinyfish.ai/runs/741fbdac-01ca-458f-b08e-53af54ec2fec

### Accurate release gate
**Live server healthy on the new restart; cannot guarantee specific runtime gear or scenery without PlayStation in-game testing.** Both V4 sites remain 9+9 static props, not the original large 26-prop ZONA47 design. The bespoke underground bunker has not been installed. Weekly *scripted* award delivery and powered refrigeration cannot be promised on stock console without mods; shipping key items alone don't create matching functional locked container events in Livonia. Wipe is neither required for starter gear nor a solution to missing scripts/terrain Y.
