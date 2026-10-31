# BEILEYS47 — live state after October 31, 2026

This document supersedes older pre-installation claims in `docs/LIVE_ACTIVATION_2026-10-31.md`. It does **not** mark the experimental Stage 1–9 preview outputs as deployed.

## Observed live state

- Platform: **DayZ PlayStation** on Nitrado, 10 slots, mission `dayzOffline.enoch` (Livonia), build **1.30.164200**.
- Server was observed **running** on Oct 31 via an authenticated **read-only Nitrado browser session**. Two custom files were observed at `dayzOffline.enoch/custom/beileys47_hotspot_zone47.json` and `custom/beileys47_hotspot_southwest.json`.
- `enableCfgGameplayFile` was observed enabled in general settings.
- The owner previously reported success entering on PS5 without password and seeing the English welcome message.
- The Nitrado **Restore Backup** page showed **no available backups**. This means no verified recoverable full-world snapshot is currently held by the project.
- At the time of inspection, Nitrado showed no players connected. This is time-bound and must not be assumed true later.

## Configuration changes reported installed by the owner

Owner-reported completed uploads or settings saves (not independently downloaded byte-for-byte):

1. `db/types.xml`: metal plates quantity 100/100, and later rare black/white gun cases plus matching blue/red keys at nominal 2 / minimum 1.
2. `cfgspawnabletypes.xml`: six hatchback/offroad variants with improved chances for the first four wheels and basic engine parts.
3. `db/events.xml`: helicopter crashes and military convoys target 4 instead of 3; helicopter child maximum adjusted.
4. `cfgweather.xml`: already configured, left unchanged.
5. `db/messages.xml`: English welcome and recurring announcements; welcome observed in game.
6. Nitrado settings: public no-password access; appropriate English server identity; time acceleration day 4x and night 16x reported saved.
7. `cfggameplay.json`: two Object Spawner references, `enableCfgGameplayFile` on.

**IMPORTANT: Both hotspot files last prepared by the assistant contain `{"Objects":[]}`. Their existence is confirmed in Nitrado; actual file bytes are not read yet. They do NOT constitute installed or playable custom hotspots.**

## What remains unverified / not installed

- No custom buildings, ZONA 47 HQ, military bunker, fridge, shipping-container lock mechanic, dedicated PvP arena, or fully validated event economy is established by the evidence.
- A loaded configuration and PS5 login do not prove the rare cases work, that increased loot is balanced, or that custom objects are present.
- Experimental object placement requires supported class names and **actual terrain height Y**, collisions, player exits and a rollback plan. Never use synthetic altitudes.
- Latest server RPT log showed successful world/CE startup but also recoverable storage backup read warnings; no confirmed total world backup.
- Never reset the mission, wipe the server, remove persistent `.bin` files or reinstall as a routine step.

## Recovery artifacts

A conversation-local ZIP named `BEILEYS47_V3_SNAPSHOT_VERIFICATO_20261031.zip` contains the reconstructed **configuration**, original files available from the conversation, SHA-256 inventory and validation scripts. It is **not a world persistence backup** and has not been uploaded into this public repository (to avoid assuming private live files are safe for publishing).

## Conservative release status

**Public playable server: YES (observed).**
**Franco V3 configuration: uploaded as reported; some settings independently observed.**
**Two custom PvP structures/hotspots: NOT INSTALLED.**
**Special fridge / shipping-container locks: NOT INSTALLED.**
**No-wipe guarantee: server policy only, no guarantee against provider/game incidents.**

Next safe work: use authenticated Nitrado to verify actual live file contents; preserve external config copies; investigate world persistence backup availability with provider; test one small clearly reversible Object Spawner change before scaling. Do not fabricate real Y elevations or claim PS5 certification from XML/JSON syntax validation.
