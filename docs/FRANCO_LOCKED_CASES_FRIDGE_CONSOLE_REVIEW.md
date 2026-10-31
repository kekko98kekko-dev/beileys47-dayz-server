# Franco V1 — Keyed containers and unusual props feasibility (DayZ PlayStation 1.30)

**Status: reference-source verified / PlayStation runtime unverified / NOT DEPLOYED.** The user authorized research and intended installation, but no Nitrado world backup, authenticated write-capable browser, or in-game validation exists.

## Two DIFFERENT key systems — do not confuse them

### A. Rifle cases + red/blue case keys
The official `DayZ-Central-Economy` pinned Livonia `db/types.xml` includes these classnames (all `nominal=0`, `min=0`, so they do not spawn ordinarily):

- `GunCase_Black` ↔ `GunCaseKeys_Blue`.
- `GunCase_White` ↔ `GunCaseKeys_Red`.
- Also `GunCase_Orange` ↔ `GunCaseKeys_Orange`.

`cfgspawnabletypes.xml` already defines a cargo group that may place the corresponding key **inside** each case. This is not a completed treasure hunt: test whether the case is initially locked, whether the key inside is accessible, and how loot is obtained before enabling them. The built-in OpenGunCase recipe maps the black case to blue key, white case to red key, orange case to orange key.

**Optional experiment (NOT part of Franco V1 release):** in a separate, reversible change to real `db/types.xml`, consider `nominal=2 min=1` for black/white cases and separately `nominal=2 min=1` for blue/red keys. Do not deploy if keys and cases cannot be linked/used on PS5 or if the random economy does not find eligible Military locations. Verify type availability and game DLC gates; no unlock success is promised. Add reasonable prizes manually only after confirming the vanilla mechanism.

### B. Blue/red shipping-container lock keys
`ShippingContainerKeys_Blue` and `ShippingContainerKeys_Orange` are in Livonia's official `types.xml` at nominal zero. The native beached locked-container activity is associated with Sakhal; merely enabling a key **does not** cause a container to appear in Livonia. Need a supported vanilla object class, proper lock behavior, position/rotation/height, loot association, and PS5 tests before any Object Spawner experiment. Do not install desktop Steam mods (e.g. DNA_Keycards) on console.

## Fridges and unusual objects
The string `Refridgerator` is found in public 1.30 item data, but **not** in our pinned Livonia `db/types.xml` or `cfgspawnabletypes.xml`. The presence of `StaticFridgeTest` in `db/events.xml` is NOT evidence of a working refrigerator: that event is inactive (`nominal=0`, `active=0`, no children).

Vanilla **decorative** props may be added via Object Spawner from `cfggameplay.json` -> `WorldsData.objectSpawnersArr` with a file in mission `custom/`. For *each* prop, confirm a supported class, real X/Y/Z ground height, visual appearance, collisions and PS5 stability. Decorative world props do not automatically provide cold storage, crafting or interactive containers.

## User-requested public launch
The user wants the password removed and server public. On Nitrado PlayStation that requires a write-capable authenticated panel session (General settings) and confirmation that the server actually starts and accepts unauthenticated community connections. Until Franco V1 changes and key/fridge experiments are actually installed/validated, keep English hostname and the truthful pre-launch description. Do NOT claim deployed features, public access or no lag. Do NOT publish external public links to expose administration interfaces or FTP credentials.

**Provider gate:** Nitrado backup UI last displayed "Nessun backup disponibile / Per questo gioco non è necessario alcun backup". No world restore point is verified. Read-only Chrome connector cannot change server state. Do not treat prior saved GitHub Recovery Kit as backup of players, bases, loot economy storage or vehicles.

References: official pinned Bohemia CE (1.30) `dayzOffline.enoch/db/types.xml`, `cfgspawnabletypes.xml`, `db/events.xml`; Bohemia DayZ gameplay/Object Spawner specification; Nitrado console support.
