# BEILEYS47 V7 — Test Kit + Showcase (NOT DEPLOYED)

**Current status:** Offline candidate only. Do not claim these files are on Nitrado or that a wipe has been executed.

## Candidate
- `beileys47_freshspawn_v7.json`: clothing inherited from V6; every fresh character gets 2 independently random fruit (Apple/Pear/Plum), 2 independently random canned foods (PeachesCan/SpaghettiCan/BakedBeansCan), and one CombatKnife; 81 weighted cargo combinations. The previous V6 bandage and chemlight are deliberately omitted per V7 requested items. Test actual free inventory in PS5.
- `beileys47_test_showcase_v7.json`: 1 military tent, 4 roadblock tables, 16 representative pickup classnames (food, firearm, magazine/ammo, tools, medical, clothing/parts). **Not all game items.** Terrain Y for new structure is approximate extrapolation from existing Dolnik V4 objects, not measured. Tabletop item heights, collision and pickup ability unverified: MUST field-test before deploying to public server.
- `cfgplayerspawnpoints_v7_candidate.xml`: model based on Bohemia Interactive's upstream Livonia `cfgplayerspawnpoints.xml`, with sole fresh spawn bubble x=11405, z=586 near existing V4 southeast field site (Dolnik). The live Nitrado file is not yet available in full; **do not replace without byte-/semantic-comparison, backup and live spawn test.** `hop` and `travel` were preserved from the upstream file, not necessarily from the user's current live file. An exact location cannot be guaranteed by a generator bubble.
- `cfggameplay_v7_candidate.json`: V6 settings preserved + registered V7 kit and test showcase spawner, leaving both prior spawners untouched. **Prepared, not installed**.

## Safety-critical observations
- Earlier proposal to spawn near Radunin was REJECTED: Radunin is a **permanent toxic gas zone**. Do not put unprotected freshspawns there.
- Original Livonia bunker is accessible with a Punched Card at Dambog, and lower puzzle areas generally require two people; NO custom bunker installed.
- Small test area can validate a *sample* of vanilla item classes, not every item in DayZ (many special items/vehicle/AI mechanics need different systems).
- Object Spawner pickup items may despawn or become persistent depending on `enableCEPersistency`; test and remove trial area after QA.
- Never wipe before confirming a current recoverable provider backup, exporting or documenting the mission files, verifying item classnames and obtaining a fresh clean RPT. No player data reset has been performed.

## Install gate
1. Obtain live `cfgplayerspawnpoints.xml` full text & validate correct changes (no missing custom settings); backup on provider.
2. Upload exact V7 kit and test spawner JSON as FILES under mission `custom/`, not folders; verify saved and reopened.
3. Apply V7 merged `cfggameplay.json`; selectively patch live `cfgplayerspawnpoints.xml` fresh bubbles.
4. Restart with 0 players, read new RPT. If errors, rollback immediately without wiping.
5. Connect to PS5 as a fresh character. Verify no poison gas, no obstructions, no clipping, correct 5 items (plus clothing), and pickup of all representative samples.
6. Only after those pass, consider the user-approved player+world persistence wipe with a recoverable backup.

Upstream XML: https://github.com/BohemiaInteractive/DayZ-Central-Economy/blob/master/dayzOffline.enoch/cfgplayerspawnpoints.xml

## Installation attempt and exact stopping point (2026-10-31)

Agent run: https://agent.tinyfish.ai/runs/3ff498ac-017a-4be3-b745-288124a8b8be

Nitrado editor opened; `beileys47_freshspawn_v7.json` was created as a file in mission `custom/` and the GitHub preset was pasted into the **unsaved editor**. Agent ran out of wallet budget before clicking Save or reopening. Hence **V7 is NOT ACTIVE**, `cfggameplay.json` remains V6, no server restart, showcase and spawn XML untouched, no wipe. The pasted editor state may be lost after closing session; do not assume the V7 file has content. Never point `cfggameplay.json` to the V7 file until its saved content is verified. Remaining TinyFish balance observed after run approximately $0.184; a full automated installation requires renewed funding or a supported alternative.

Last successful Nitrado smoke test remains the clean V6 restart; no new V7 verification.
