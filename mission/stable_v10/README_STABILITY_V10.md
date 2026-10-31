# BEILEYS47 | Stability V10 candidate — NEVER CLAIMED LIVE

**State: READY FOR DEPLOYMENT ONLY; NOT DEPLOYED, NOT PS5-CERTIFIED.** The server was previously reported as running, and the owner reported using the V9 installer; this directory does not reflect a fresh byte-for-byte read of Nitrado.

## Conservative bug fix

1. **Fix V8/V9 spawn collision by restoring Bohemia's ORIGINAL Livonia 1.30 spawnpoint file**. The old V8 zone X11405 Z586 overlaps **6 V9 base objects** within its 80m×80m grid. The newly staged official spawnpoint file from Bohemia tag `DZ_130` contains 151 positions, all **at least 7865.0 meters** from the closest V9 base object (center-to-center 2D distance); official grid widths and hop/travel behavior remain unchanged. The same official file is on current master; blob SHA `13a6b2e3cbeeb1eb23e09af81bc36ba4d53871b5`.
2. Keep V8 gear preset and MapData map access. Every one of the 81 V8 cargo variants contains 2 fruits, 2 cans, CombatKnife, 2 BandageDressing and ChernarusMap; a TaloonBag_Blue attachment is defined. **Inventory in PS5 is not runtime verified**.
3. Keep the complete V9 Dolnik military base (29 source-authored objects) and Radunin area; the config's spawner references exclude the old V7 test and duplicate southwest hotspot.
4. **Known tradeoff:** spawning returns to official Livonia locations distributed around the map. It no longer forces every new player to spawn by Dolnik. This is deliberate to prevent spawn trapping, not an unnoticed regression.
5. Custom Dolnik models from 2021 may still have geometry/height clipping. **Do not claim scenery is flawless.** The 29 `mapgrouppos` group lines must be present on the actual Nitrado mission for loot; this cannot be certified by a project file alone.

## Exact staged files

- `cfgplayerspawnpoints.xml`: identical Bohemia official `dayzOffline.enoch/cfgplayerspawnpoints.xml` at `DZ_130`. Only safe spawn file; players/hop/travel retain vanilla rules.
- `cfggameplay.json`: full V9 candidate copy, contains V8 kit and MapData and only two world spawners. If actual live config differs, **do not replace it blindly** — update the specific fields while preserving all other live settings.

## No-risk deployment gate

No person or automation is authorized to overwrite live Nitrado without first confirming current 0 players, stopping the server, and saving/download-verifying: `cfggameplay.json`, `cfgplayerspawnpoints.xml`, `mapgrouppos.xml`, current custom JSON files **and** a provider-supported world persistence backup if available. Never delete storage/players, never wipe.

When authorized computer control is available, compare actual live XML/JSON byte-by-byte to the project, replace ONLY `cfgplayerspawnpoints.xml` to remove the known overlap, and fix the spawner list only if V9 is missing. Before enabling world, validate integrity, ensure reference files exist, and check logs; after startup test PS5 spawn, kit, map, scenery and loot. If read-only/permission-limited, stop rather than fabricating a deployment success.

## Current limitations

No Nitrado write access in the current chat: browser connector is READ-ONLY; TinyFish automation out of credit; local container has no external DNS/FTP. **Not possible to truthfully certify deployment, absence of bugs or in-game outcomes here.**

Official reference: https://github.com/BohemiaInteractive/DayZ-Central-Economy/blob/DZ_130/dayzOffline.enoch/cfgplayerspawnpoints.xml ; official player spawning spec: https://community.bohemia.net/wiki/DayZ:Player_Spawning_Configuration
