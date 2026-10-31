# BEILEYS47 | Military Base Dolnik V9 | STAGING ONLY — NOT INSTALLED

Status: Prepared and checked structurally in GitHub. **NOT installed on Nitrado; NOT field-tested on PS5 in 2026.**

## Origin and limitations

Original work: Scalespeeder, 2021 (DayZ 1.15, limited tests on PC Livonia). Source: https://github.com/scalespeeder/DayZ-Livonia-Military-Base-At-Dolnik-Custom-Location-JSON-and-XML-Loot-Snippets . See original readme/terms there; imported JSON object positions and group entries remain unchanged.

There are **29** objects in the complete Dolnik base. Our existing `custom/beileys47_hotspot_southwest.json` has **9** of these EXACT same objects, so enabling both creates 9 duplicate structures. Our badly positioned test `custom/beileys47_test_showcase_v7.json` has 21 more nearby objects including an intersecting tent and tables: do NOT enable it alongside the base.

The current spawn V8 is at X11405, Z586, with an 80x80 generator grid. The new base's closest object is **26.87 m** from its center, and falls INSIDE that generator's range, so spawning among objects is possible. Verify that the spawn site is clear BEFORE deploying to a public server; the candidate does **not** alter this XML.

## Planned replacement (after a full recoverable backup; 0 players; server STOPPED)

1. Back up/download LIVE `cfggameplay.json`, `cfgplayerspawnpoints.xml`, `mapgrouppos.xml` and current `custom` contents. Do not wipe persistence/players.
2. Upload the staged `beileys47_dolnik_military_base_v9.json` to Livonia: `dayzps_missions/dayzOffline.enoch/custom/`.
3. In LIVE `cfggameplay.json` change ONLY `WorldsData.objectSpawnersArr` to:

```json
"objectSpawnersArr": [
  "custom/beileys47_hotspot_zone47.json",
  "custom/beileys47_dolnik_military_base_v9.json"
]```

This RETIRES the old southwest hotspot and the test showcase from active loading. Keep the actual files for rollback; do not delete them. All V8 spawn-gear and map settings remain untouched. For convenience a full candidate `cfggameplay_V9_CANDIDATE.json` is supplied, but copying only the array is SAFER if LIVE settings have changed.

4. For loot in the new structures: back up LIVE `mapgrouppos.xml` and insert the 29 `<group />` lines from `dolnik_mapgrouppos_additions_ONLY.xml` inside the pre-existing `<map>` root. Do NOT replace the original XML with the snippet. Ensure no already-identical group positions are present or duplicates result. This updates CE group references; loot quantities/usage are still governed by CE economy files.
5. Start the server, check the latest RPT for `Object spawner failed to spawn` or XML/JSON errors. On PS5 inspect at Dolnik: no overlapping objects, tents not buried, loot over time, and spawn safety. Only then mark the base as accepted. Old 2021 PC positioning is not proof of console 2026 fit.

## Rollback

Stop server. Restore backed-up LIVE `cfggameplay.json` and `mapgrouppos.xml`; leave `cfgplayerspawnpoints.xml` unchanged. Restart. No wipe necessary.

## Pending

A PS5 tester must confirm ground/collision; movement of the V8 spawn bubble if it intersects the base; a bunker site and usable entrance/exit. No custom bunker, new currency shop or automatic events are included in this package.
