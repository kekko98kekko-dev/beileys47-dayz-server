# Franco V1 — Approved, safe-to-prepare changes (31 Oct 2026)

**NO LIVE DEPLOYMENT.** A seven-feature change set was approved by the users for BEILEYS47 DayZ PlayStation Livonia. The currently live English `db/messages.xml` remains version 1. New identity/messages must only be published after corresponding gameplay passes PS5 tests.

## Scope and caveats

1. **MetalPlate**: quantity range 100–100; no change in number of item spawns. Other building resources such as NailBox have `quantmin=-1` in reference CE, so do not blindly force all resources to 100.
2. **Weapons**: retain randomized weapon condition; inspect original `db/globals.xml` damage interval plus per-weapon `cfgspawnabletypes.xml`. No global damage override or rare-weapon loot inflation.
3. **Vehicles**: for two existing vanilla models, improve four first wheel probabilities to 0.90 and radiator, battery, spark plug to at least 0.75 each, WITHOUT increasing vehicle event counts.
4. **Events**: `StaticHeliCrash` and `StaticMilitaryConvoy` nominal 3→4; Mi8 heli child cap 3→4. The world does not guarantee four simultaneously visible incidents.
5. **Hotspots**: two existing areas, community-planned only; no custom loot or zombie coordinates authored until the real sites, location Y, and class support are checked on PS5. ZONA 47 remains a separate blocked concept.
6. **Nights/weather**: proposed Nitrado General 4x global/4x additional night, and isolated `cfgweather.xml` weather limits. Tests are required to verify actual time and whether settings take effect after a restart.
7. **Community events**: manually managed weekly Survival Hunt / Military Extraction / Squad vs Squad / Treasure Hunt. No automated quest plugin exists in this repo.

## Invariants / do not touch

No scheduled wipes, no extra cars at every position, no changes to stash lifetime, no global zombie multiplication, no `cfggameplay.json` override, no unsupported PC modifications.

## Recovery gate

Read-only Nitrado check at time of approval still showed **no provider backups available**. Do not presume a recoverable world snapshot, and do not confuse XML rollback with restoring bases/players/vehicles. Save the live originals `db/types.xml`, `cfgspawnabletypes.xml`, `db/events.xml`, `cfgweather.xml` and read-only `db/globals.xml` separately, record each hash, compare against live version and reference CE, and validate one file at a time. No FTP/API credentials should enter this repo.

## International launch wording

Keep current host name: `BEILEYS47 | SURVIVAL WAR | LIVONIA | NO SCHEDULED WIPES`.

Current live description: `International community | PvP & PvE | All players welcome | Custom content coming soon`.

Only after confirmed installation and console tests, change to: `International PvP/PvE | Building loot+ | Repairable rides | Military events+ | No scheduled wipes`, and load `config/franco_v1_messages_after_deploy.xml` in the actual mission `db/messages.xml` through an approved controlled procedure.

The candidate patcher has been built and unit-tested off-repository for this session; this PR records the feature approval and launch settings but does **not** claim to contain or deploy server mission replacements. CI validation of existing Stage 1–9 must stay green.
