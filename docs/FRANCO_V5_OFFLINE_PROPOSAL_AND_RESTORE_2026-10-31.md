# Franco V5 — loot balance and starter gear: OFFLINE ONLY (31 Oct 2026)

## Live verified facts

- Server PS5 Livonia, version 1.30, confirmed **running** after automation cleanup. V4 two field-site JSON files with 9 objects each remain configured.
- Attempted to add a starter-gear preset automatically through Nitrado. Nitrado's browser **created a folder named `custom/beileys47_startkit.json` instead of a JSON file**. The initial automation inserted an invalid reference into `cfggameplay.json`.
- A subsequent dedicated cleanup automation **removed the `PlayerData.spawnGearPresetFiles` property**, saved the JSON, and verified both existing Object Spawner paths and all other config settings unchanged. The server was confirmed **RUNNING** afterward. The accidentally named folder remains inert; do not interpret it as a working preset.
- Therefore **there is no active custom starter kit**; fresh players are on current mission's default starting gear. Existing surviving characters retain their persisted state.
- No verified full-world backup is available through Nitrado's Restore Backup UI. Avoid an unsafe mass upload or unverified static structure.

## Offline V5 build completed

A downloadable conversation ZIP named `BEILEYS47_V5_PREPARAZIONE_NON_INSTALLATA_20261031.zip` contains:
- `types.xml`: surgical edits to **20** item types from the owner-provided V2 baseline (8 survival resources, 11 moderate gear/repair targets, metal plates). Every non-target type and non-scalar field preserved. **Not uploaded to live Nitrado**. The original V2 baseline may differ from the live XML (e.g., earlier manual metal-plate quantity edits), so never upload it blindly.
- `custom/beileys47_startkit.json`: preset for **new characters only**, preserving character selection; clothing plus bandage, light and a food can. **Not uploaded live**.
- `cfggameplay.json`: refers to that preset and preserves two original Object Spawner references. **Not uploaded live**, must never be used unless the real preset JSON file exists (not a folder).
- SHA-256 manifest, precise change list, offline tests and warnings.

This ZIP is NOT a world backup or proof of console behavior. No attempt was made to run unsigned scripts on PlayStation.

## Buildings and bunker

The current 18 static objects are small scenery checkpoints at historical source sites (Radunin area and Dolnik). They are **not** the 26-piece original ZONA 47 target at X 9000/Z 7800 or original Southwest. No PS5 on-site visual/collision check has been reported yet.

The popular community-built underground Livonia layout from scalespeeder explicitly warns players cannot climb out normally (must relog), so it was **excluded** from the live server. The **vanilla Dambog bunker** already offers a real end-game underground keycard experience on Livonia; it's available without modifying scenery.

A new original large bunker and working fridge or shipping container locking are not certified achievable through vanilla PlayStation Object Spawner alone. Avoid promising native scripted features based on a prop's visual model.

## Events

Increased crash-helicopter/convoy vanilla nominal targets are live as owner-reported. A weekly scripted PvP tournament with automatic rewards and scheduled in-game mission logic is **not** created by `events.xml` or `messages.xml`; it would require external management and/or unsupported scripting. The English messages are configured and PS5 welcome was previously observed.

## Release decision

- V4 public server: **active and playable**.
- V5 loot + starter kit: **prepared offline, not installed**.
- Custom ZONA 47 large site and bunker: **not installed**.
- New risky live edits: **blocked** pending a provider-supported world backup or an explicit plan accepting persistence loss, and real in-game verification of current 18 objects.
- Never wipe, resetmission, reinstall or delete `storage_*` to force new loot.
