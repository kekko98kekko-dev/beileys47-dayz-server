# BEILEYS47 — V17 PS5 field acceptance (after V16)

**2026-11-01 baseline:** GitHub V16 deployment and Nitrado file/settings readback were successful. This is NOT a PlayStation gameplay verification. V17 is offline and never deploys to, wipes or restarts Nitrado.

## Working world locations
| Site | Approximate center | V16 change | Required console proof |
| --- | --- | --- | --- |
| ZONA 47 / Radunin | X7100 Z6965 | 20 new props around earlier site | Structures appear; no floating, clipped or blocked passage |
| Existing bunker | X9022 Z7458 | 9 external fortification props | Safe bunker entry and exit; no collision trap |
| Dolnik | X11490 Z461 | 3 small props outside the V15 two-tent setup | Exactly two tents; med/military loot; accessible containers |

Three infected-zone XML entries mean only *configured spawn territories*, not script-controlled moving hordes. CE loot and rare colored cases are chance-based, not guaranteed on first visit. Static placement heights are estimates pending PS5 visual inspection.

## Field sequence (no wipe)
1. From PS5/PS4, connect to the server's Livonia Community entry; privately record date, version and a short video.
2. Walk around ZONA 47 from multiple approaches. Record terrain clipping, inaccessible loot, entrances, exits and observed infetti.
3. Visit the existing bunker, test entry and exit, and note whether fortifications cause traps.
4. Visit Dolnik: verify the two intended tents and corresponding loot. Observe infetti at all three sites; if they do not appear immediately, note the circumstances rather than assuming a configuration failure.
5. Inspect CE loot points across all three areas over normal play. Check any special cases you genuinely find. Do NOT claim a working red/blue shipping-container lock without observing the key/open interaction.
6. Only during an agreed no-player maintenance window, place a marked surface stash, buried stash and parked test vehicle. Record inventories, truck position and fuel, restart normally, then inspect them all. This assesses *restart persistence*, not proof of no historical wipe.
7. Observe day/night and play with others to assess stutter, crashes and response. Nitrado's night multiplier of 8 is a configuration fact, not an experiential test result.

## Strict recorded-evidence gate
Copy the template from deploy/v17/PS5_ACCEPTANCE.template.json to a **private local** path (never commit real player information or private videos). For every check, use result = passed, failed or not_tested. For each tested check, add at least 10 characters in observation and a private evidence_ref identifying a screenshot/recording/field note.

Run:

    python scripts/v17_ps5_acceptance.py /private/path/PS5_ACCEPTANCE.json
    python scripts/test_v17_ps5_acceptance.py

The gate fails closed for missing checks and missing evidence. Until all 15 critical checks pass on user-supplied actual gameplay observations, PS5 acceptance is **not verified**. Any failed check stops release work for targeted troubleshooting. Even a 15/15 pass does **not** certify all originally requested features.

## Still outside V16/V17 verified scope
- New scripted underground bunker interior (V16 fortifies an existing bunker only)
- Red/blue key-locked shipping containers with verified access-control mechanism
- Moving hordes with scripts
- Automatic in-game rewards to named community-event winners
- Instant replacement of trucks immediately after driving them away
- Exactly scheduled 15-day replenishment of persistent plank stacks

The older V16 audit contains a field no_wipe: true, but it was assigned as a deployment intention; it is **not a direct measurement of player persistence**. No persistent player data should ever be published to this public repository.

Official reference: https://community.bistudio.com/wiki/DayZ:Object_Spawner — a valid JSON entry does not guarantee an object appeared or is usable in the engine; errors are in the server RPT logs and heavy object spawning may affect performance.
