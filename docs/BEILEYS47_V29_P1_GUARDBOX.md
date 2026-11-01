# BEILEYS47 V29 — first ZONA 47 central-area physical pilot

**This is NOT a completed 240 × 220 m area.** It is one vanilla model for a field test. The existing V16 Radunin PvP hotspot is untouched.

- **Central candidate:** X 9000, Z 7800, orientation 120°
- **P1 selected:** checkpoint_03 at **X 9057.3275, terrain Y 302.7723, Z 7822.7058**
- **Proposed model:** `Land_Mil_GuardBox_Green`, originally identified in the official CE's terrain catalog and the third-party DZPage model catalog. **Actual Object Spawner compatibility remains unverified until PS5 RPT/visual test.**
- **Y is raw ground elevation at the object origin, not guaranteed collision-accurate pivot position.** The model may need a reversible Y adjustment after actual client test.
- Stage 4.14 supplies 26 terrain Y per candidate location, but 17 visual roles still lack an acceptable proposed classname, and no 3D PS5 test has been completed.

## What the guarded V29 installer will do

1. Refuse if live `cfggameplay.json` SHA differs from independent V21 audit baseline. It preserves all V20 gameplay, V16 scene, player gear, night, loot and world references.
2. Verify every existing Object Spawner scene and reject if any existing placed object is within 45 m of P1. Also reject any existing destination name to avoid overwrites.
3. Confirm cfgGameplay enabled and run two zero-player checks, otherwise STOP before changes.
4. Create an original `cfggameplay.json` ZIP/SHA backup. If server running, stop normally. Upload **only** `custom/beileys47_v29_zone47_p1_guardbox.json` with one prop and update `cfggameplay.json` to reference it.
5. SHA readback of both files and normal server restart, followed by final file checks. No wipe, no storage file changes, no CE edits, no vehicle changes.
6. On upload error, restore the original gameplay. A non-referenced new JSON file may be left behind, but it cannot spawn without its reference. Archive backup available for 7 days.

## Gameplay acceptance needed before P3/P5

A PS5 tester must visit approximately X9057 Z7823, observe whether the guard box appears, check height/ground contact, doors and collisions, whether passages are blocked, and whether client stutter is acceptable. PS4 performance must be checked separately before promising cross-generation stability. Check after two normal server restarts when safe. A GitHub green check is **not** gameplay proof.

**No automatic P3/P5 or full 26-structure deploy.** If P1 fails, remove only the newly appended JSON reference using the saved exact original gameplay; do not wipe world storage.

Official Bohemia Object Spawner: https://community.bistudio.com/wiki/DayZ:Object_Spawner
