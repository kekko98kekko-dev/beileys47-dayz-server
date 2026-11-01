# BEILEYS47 — V16 installed: final verified status (2026-11-01)

## Evidence from Nitrado + GitHub
- [V16 guarded live deploy (run 41295681527)](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41295681527): preflight SUCCESS; 8 uploaded and SHA256 read-back verified; Nitrado stopped only at zero connected players; restart confirmed STARTED.
- [V16 deployment report](../deploy/v16/WORKFLOW_RESULT.json): preflight success / install success, no wipe, PS5 runtime not tested.
- [Night settings run 41296018095](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41296018095): `config.serverNightTimeAcceleration` 4 -> 8, Nitrado API read-back verified.
- [Final live audit run 41296206351](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41296206351): SUCCESS. Nitrado status STARTED, V16 spawner listed, 32 static objects, exactly 2 Dolnik tents, medical tent lootmax 10, military tent lootmax 8, three new infected zones present, no fog, V15 truck event intact, night multiplier 8.
- No persistence wipe performed.
- [Automated event issue #40: Dolnik Survival Rescue](https://github.com/kekko98kekko-dev/beileys47-dayz-server/issues/40).
- Weekly GitHub Actions [weekly-community-events.yml](../.github/workflows/weekly-community-events.yml): Sundays 19:00 UTC. Rotates three venues, avoids duplicate ISO-week posts; creates GitHub announcement issues, NOT in-game payout.

## What V16 really changed
1. **Dolnik**: V15 already reduced from 13 tents to 2; V16 raised spawn slot limit from medical 8 to 10, military 5 to 8; retained the pre-existing Medicine/Military point definitions and added some external crates/table proxies.
2. **ZONA47 near 7100,6965**: 20 new props around existing Radunin 9-prop site (fortifications, military containers, tables, roadblocks, wrecks).
3. **Bunker area near 9022,7458**: fortified an **existing** Bohemia bunker with 9 props. NOT a new interior, scripted door, or true underground player-made bunker.
4. **Dolnik**: 3 small props outside the two tents and unchanged V15 truck-testing event.
5. **Loot**: 16 new CE mapgrouppos positions for containers/wooden-crate proxies at these three areas, increased medical/military tent slot limits, globally modest increased BandageDressing/Morphine/ammo supply, and rare gun cases + chance-based case contents. Existing categories and vanilla loot types maintained. Placement and content must be inspected on PS5; coordinates' Y values are estimated.
6. **Infetti**: three new CE zone entries (Radunin 12–18 military, bunker 10–14 military, Dolnik 6–10 medical). The active count is affected by proximity, AI limits, NavMesh and server performance. They are not script-driven moving hordes.
7. **Events**: server periodic announcement of challenge locations; GitHub weekly challenge announcements on Sundays. Additional prizes require manual admins or off-game automation.
8. **Nights**: Nitrado general setting night acceleration increased from 4 to 8; daytime multiplier unchanged.
9. **Meteo**: V15 dynamic rain/clouds/wind/storms retained, fog kept at zero.

## Still not actually delivered and why
- **Custom lockable container with red/blue key puzzle:** colored gun cases/keys and military containers exist, but functional shipping-container access-control mechanics were not implemented or tested. Generic `Land_Container_1Mo` is not automatically lockable.
- **New custom underground bunker interior:** only the existing bunker perimeter is fortified. No tested underground scripted passage.
- **Automatic weekly prize to winning players:** pure DayZ PlayStation XML/JSON offers no winner-identification or server-side code/mod to award player items. Weekly GitHub event notices exist; in-game prize delivery is not automated.
- **Guaranteed 252/252 on the 15th day:** `PileOfWoodenPlanks` has `quantmin=100` and `quantmax=100` (percentage for newly created items) from V15, but nominal is 0 in the vanilla types.xml and this does not replenish existing persistent piles. No reliable exact day-15 refill can be asserted without supported persistence editing/admin integration and rollback.
- **Instant truck replacement when driven away:** CE counts existing live trucks, including driven-away vehicles; higher nominal does not guarantee instant replacement. Extra Nitrado-local automation would need game state telemetry to do this correctly.
- **Truck fully loaded to physical capacity, gasoline liquid identity:** only validated user gameplay can prove inventory fit and real gasoline content; the XML alone does not.
- **All scenery visually perfect/no floating items:** no PS5 gameplay access; elevation near objects is approximate and may require correction.
- **No wipes:** no files under persistence/storage were cleared; world assets and players retained.

## Reliable deployment safety
All new files V16 were written only when Nitrado showed zero players connected, then read back and compared cryptographic hashes. Status was checked after normal restart.
Do not trigger old V15/V16 `GO_LIVE` markers accidentally, because those workflows are not idempotent on already-updated files. Future adjustments should start from fresh Nitrado reads and diff-validate.

Status: **V16 technically installed, Nitrado STARTED, PS5 runtime untested, requested project NOT 100% complete due listed native console limits**.
