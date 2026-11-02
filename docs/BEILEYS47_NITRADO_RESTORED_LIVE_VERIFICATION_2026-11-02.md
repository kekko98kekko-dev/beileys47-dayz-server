# BEILEYS47 — Nitrado restored; V49 installed; V50 17/17 (2 Nov 2026)

**Platform:** DayZ PlayStation (PS4/PS5), Livonia. **Status:** CONFIGURATION BASELINE VERIFIED, NOT PHYSICAL GAMEPLAY CERTIFIED.

## The actual sequence and evidence

- Earlier signed-download outage was confirmed by Nitrado support as a wider provider issue. No evidence that the existing world data were erased.
- **V50 GET-only audit, GitHub run 41417543763, rerun around 10:43 UTC**: provider download REST path WORKING; 16 of 17 automated configuration checks passed; ONLY `v49_two_more_infected_territories` absent. Server reported started.
- **V49 installation, GitHub run 41417122373, rerun around 10:44–10:46 UTC**: unit safety job passed; original `env/zombie_territories.xml` verified and backed up; installation concluded **INSTALLED_AND_VERIFIED_POST_RESTART**; no player/world data wipe, no `db/types.xml` modification. Two new military-infected zones targeting (8960,7810) and (9040,7730), 5–9 dynamic infected per zone (configuration only), were added. V49 evidence artifact ID 13133289690 has short retention (7 days).
- **V50 independent GET-only audit after V49, same run 41417543763, latest rerun around 10:47 UTC**: status **started**, **17/17 checks passed**, critical_regressions=[]; PS5/PS4 field test explicitly **false**. No further edits in audit. Evidence: [V49 action](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41417122373) and [V50 action](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41417543763).

## What 17/17 means — and what it does NOT mean

The 17 automatic checks cover: registered V16 scenes and 32 props; Dolnik two tents and tent loot group limits; 25-prop V35 scene + P1 existing scene; three original infected territories plus V49 new ones; V20 stamina; V48 build permissions; V44 M3S event source and disabled old event sources; V45 loot-time rules; server night acceleration; weather fog; helicopter/convoy event targets; motorcycle event; server messages.

**These are configuration checks.** They do not verify that objects render at correct altitude, doors open, loot appears in containers, old persisted trucks disappear, a player gets correct kit, PS4 remains smooth, NavMesh behaves, or a bunker/fridge/locked-container has functional interaction.

## Explicitly remaining work, by priority

1. **PS5 acceptance and persistence baseline**. Check physical V35 + P1 placements at ZONA47 (center roughly X9000/Z7800), three routes, doors/steps, collision, clipping, zombie pathfinding, PS4/PS5 stutter, after-restart persistence. Also verify spawn Dolnik, map display, kit, two sterile bandages, stamina, Build Anywhere, actual crate/barrel stacking and tall fences. Save screenshots and structured PASS/FAIL/NOT_TESTED.
2. **M3S physical inventory and duplicate cleanup**. Event is configured; verify actual truck location, petrol, 25 logs, planks, nails, tools, construction kits and 64-slot bag. Older persisted trucks CANNOT be assumed removed by disabling their event source. Avoid global world wipe.
3. **Loot / PvP / events**. Real-world test 2–3 hotspots, tent contents, key classes (blue/red)/gun cases, helicopter/convoy rates, weather and night settings; address failed checks only through scoped changes.
4. **Free Map Builder expansion requested by Franco**. No purchase of DayZ PC. Use Bohemia vanilla `Object Spawner` JSON and optionally free browser map builders. Preserve all existing `WorldsData.objectSpawnersArr` entries in `cfggameplay.json`. Before installing huge walls, gate on exact Livonia classnames, measured Y/model origins, escape routes, overlap with the existing 26 placements, backup + reversible registration, RPT log and actual PS5 test. Stage 3–5 props, then 10–15, then expanded perimeter only if performance allows. The original 25 objects are registered but NOT evidence of a walkable complete fortress.
5. **Bunker**. Design a supported enterable structure with genuine safe egress and collisions, rather than labelling the schematic bunker as installed. Stage7 and bunker_v10 remain research-only. Real underground volume and locked doors require explicit console validation.
6. **Refrigerators and special containers**. Test vanilla classnames for visible object, inventory interaction and persistence separately. A fridge with working refrigeration is NOT established. Special keys/cases in `types.xml` do not themselves guarantee functional locks or automatic rewards.
7. **Community systems**. Setup realistic events and rewards with vanilla compatible mechanisms; scripted mobile hordes, winner-specific loot payouts, automatic 15-day plank refill, instant stolen-truck replacement and exact two-restart cleanup are not demonstrated possible via basic PlayStation XML/JSON.
8. **Release and recoverability**. Obtain fresh **private offline** mission XML/JSON backups + provider backup inventory; validate a documented restore route without overwriting player/world persistence; publish final status only when applicable live/game tests pass.

## Deployment constraints

- No additional blind overwrites or blanket uploads of `db/types.xml` (previous raw hash discrepancies).
- No deletion of `storage_1/data`, world wipe, password exposure, game character deletion or automatic destructive world reset.
- Avoid unattended retries of live writes and overlapping game restarts.
- Verify player count, server status, pre/post SHA, current configuration and recovery evidence before EVERY new live write.
- PS5 user visual acceptance is still mandatory for anything described as a working in-world feature.
- User requests **single consolidated work session** and minimal further expense, but a fully physical PS5 acceptance still depends on observable console gameplay; do not invent those results.

## Technical starting point

V49 installer: `scripts/v49_live_final_infected.py`.
V50 release auditor: `scripts/v50_full_live_audit.py`.
World construction evidence and strict safety: `config/v33/BEILEYS47_ZONE47_25_NOT_LIVE.json` and `docs/ZONE47_QA_PROTOCOL.md`.
Object Spawner specification: https://community.bistudio.com/wiki/DayZ:Object_Spawner .

**Latest claim supportable:** all 17 static/remote-live configuration invariants pass after V49. Entire game experience **not yet 100% complete or PS5 verified**.
