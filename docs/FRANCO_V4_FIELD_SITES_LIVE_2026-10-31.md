# Franco V4 — field outposts deployed, October 31 2026

**Status:** two Nitrado Object Spawner files were edited by the owner's connected authenticated TinyFish agent. Both were saved in the native Nitrado editor. The server was normally stopped and restarted with 0/10 players; agent reported RUNNING afterward and no `Object spawner failed to spawn` in its latest RPT inspection. This is evidence of configuration loading, **not of physically visiting/seeing the two areas on PS5**.

## Actual sites and classes (not the original blueprint)

| Name of existing filename | Real sourced field position | Objects | Notes |
| --- | --- | ---: | --- |
| `custom/beileys47_hotspot_zone47.json` | X ≈ 7101, Z ≈ 6963, near Radunin | 9 | A well pump, 1 military tent, 4 tables, 3 sidewalk props |
| `custom/beileys47_hotspot_southwest.json` | X ≈ 11440, Z ≈ 560, Dolnik southeast | 9 | 2 fortified nests, 2 police wrecks, 1 watchtower, 4 truck wrecks |

**Important:** these existing filenames are historical labels and are **geographically misleading**. These 18 props are **NOT** the intended full-scale outpost around X 9000 / Z 7800 or the original southwest blueprint around X 4500 / Z 4000. Do not claim that the 26-placement bespoke ZONA 47, bunker, fridge, lootable keyed shipping containers, private PvP mechanics, or custom event scripts were implemented.

The two JSON configurations as prepared from the selected positions appear in `mission/franco_v4_field_sites/`. They were reconstructed from verified source and the agent's edit request; **they have not been independently byte-by-byte downloaded back from Nitrado**.

## Sources / authorship

Adapted subsets of published historical DayZ Livonia field layouts from **scalespeeder**:
- [DayZ Console Livonia Custom Admin Spawn Base With Gear and Truck](https://github.com/scalespeeder/DayZ-Console-Livonia-Custom-Admin-Spawn-Base-With-Gear-and-Truck) — northern field positions, historically tested on older game versions.
- [DayZ Livonia Military Base at Dolnik](https://github.com/scalespeeder/DayZ-Livonia-Military-Base-At-Dolnik-Custom-Location-JSON-and-XML-Loot-Snippets) — southern field positions, historically limited PC testing in DayZ 1.15.

No invented ground Y; the values came from the source. No guarantee that older layouts have good collisions, geometry or FPS on PlayStation 1.30. Bohemia official [Object Spawner](https://community.bistudio.com/wiki/DayZ:Object_Spawner) warns that numerous items can affect performance.

## Protection and rollout

- 0 players verified before normal stop; **no wipe, resetmission, reinstall, or storage deletion**.
- `cfggameplay.json` had both `custom/` references already and `enableCfgGameplayFile` was reported enabled in the live panel.
- Automated post-restart check reported Nitrado service RUNNING, no fatal XML/JSON/CE errors, no `Object spawner failed to spawn` in inspected RPT.
- No full-world backup is available in Nitrado Restore Backup UI. The conversation-generated `BEILEYS47_CONFIG_V4_18_OGGETTI_20261031.zip` is only a **configuration reconstruction**, not a player/bases/vehicles backup.
- If actual objects appear underground, obstruct roads, prevent safe movement or create serious stuttering, stop further deployment and restore each custom Object Spawner file to `{"Objects":[]}` while 0 players and server stopped normally, then start normally. This does not restore the world state itself.

## Still to test to claim completion

1. PS5 visual rendering and collision at both site coordinates; client-side performance and safe entrances/exits.
2. Fresh-spawn loot changes, events, case/keys and persistence. An error-free startup is insufficient.
3. Any additional props, bunker, interactive fridge, locked shipping containers or alternative PvP sites **only if supported**; they remain research/concept work until verified on PlayStation.
4. Provider-supported world backup / recovery before high-risk changes.

**Final safety decision:** stop changing the live public server after verified successful start, instead of adding untested elements indefinitely without a rollback of persistence.
