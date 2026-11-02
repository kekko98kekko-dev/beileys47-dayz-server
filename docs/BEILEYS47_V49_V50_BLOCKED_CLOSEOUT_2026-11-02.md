# BEILEYS47 — V49/V50 console completion closeout (2 November 2026)

## Owner goal
Complete a stable PS4/PS5 Livonia survival+PvP server in one controlled development session. Avoid claiming unavailable console mods or untested game physics as complete. Previous owner authorization permits maintenance restart even with online players; interrupted player progress can be lost.

## What was actually completed in this session

1. V49 protected installer developed, unit-tested, committed in [PR #71](https://github.com/kekko98kekko-dev/beileys47-dayz-server/pull/71). It targets two additional ZONA 47 vanilla military infected zones at (8960,7810) and (9040,7730), 5–9 dynamic infected per zone, checks V20 stamina / V35 installed scene / V48 building flags / Nitrado backup metadata, creates original XML ZIP, and allows a single owner-authorized player-interrupting restart.
2. V49 workflow [run 41417122373](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41417122373) passed its offline safety test, but BOTH live attempts **failed pre-deployment** with `NitradoError: Nitrado download connection failed` after a 90-second signed-file download timeout. Logs: first near 2026-11-02 09:01:42 UTC; retry near 09:04:46 UTC. The mission folder was found; **no upload or restart was attempted**, and the V37 additions remain NOT verified/NOT installed.
3. V50 independent full read-only release audit developed and committed in [PR #72](https://github.com/kekko98kekko-dev/beileys47-dayz-server/pull/72). Checks 17 live configuration invariants, starter preset references, rare-key economy, 26-asset V35 scene, 3+2 infected territories, M3S event, zero remaining ordinary loot TTL patches, night/motorcycle/heli/convoy settings and provider backup metadata.
4. V50 workflow [run 41417543763](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41417543763) compiled successfully but **failed before generating a full audit** due the same signed Nitrado download connection error at 2026-11-02 09:06:29 UTC. This suggests a problem with access to the Nitrado file-server download path from GitHub Actions, NOT proof of a corrupt DayZ config or a worldwide provider outage.

## Last verified working live baseline

- V48 balanced Build Anywhere installed with forced player-interrupting restart and semantic remote readback: [run 41415666703](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41415666703) on 2 Nov 2026.
- V47 independent read-only verified V44 single new M3S CE event, V45 4h ordinary-loot lifetime rules after V46 raw SHA disagreement: [run 41337667223](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41337667223) on 1 Nov.
- V35 26 total registered ZONA47 object entries verified in live remote config on 1 Nov.
- V23 motorcycle nominal/max 11 verified; V20 unlimited sprint installed and read back; V16 original military/medical zones and hotspot scenes installed.
- Nitrado backups metadata audit [run 41400376165](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41400376165) on 2 Nov reported six available provider backup records and restore_possible=true. **Full persistence restore has not been tested.**

## Hard truth: remaining unsolved

- Actual PS5/PS4 in-game verification: new player gear, respawn at Dolnik, flag build, stackable boxes/barrels, additional fence height, physical spawned truck count/carried cargo/fuel, 26 ZONA47 object pivots and safe collision, NavMesh and infected AI, survival/PvP tuning and lag.
- Two old trucks persisted in live world cannot be selectively deleted merely by disabling their CE event sources.
- Modded script-driven hordes, automatic prize payouts to named winners, actively cooling refrigerators, exact 2-restart cleanup, exact 15-day refill and instant spawn of stolen live truck cannot be guaranteed by standard PlayStation Nitrado XML/JSON.
- Complete original multiroom underground bunker and tested locked naval containers not implemented.
- V46 `db/types.xml` raw-hash post-restart discrepancy unresolved; do NOT bulk overwrite `types.xml` or wipe `storage_1/data`.
- V37 2 extra infected zones: code ready but live not installed because remote file read failed.

## Safe next action when file downloads are reachable

1. Verify Nitrado file_server signed download works from a temporary GitHub runner before attempting any changes. Distinguish provider service issue from GitHub runner route by independently testing a read-only fetch in the Nitrado web panel if available. Never publish signed URLs or tokens.
2. Re-run V50 GET-only audit after connectivity is restored to establish a fresh live baseline. Verify V49 zones are absent, compare affected XML file SHA against current source and check provider restore record availability.
3. Trigger V49 one-shot installation with exact original XML backup, the explicit player-interruption guard and post-restart readback, then run V50 AGAIN to confirm all targeted configuration invariants.
4. Execute V17 fifteen-check **real PS5 field acceptance** with explicit passed/failed screenshots, actual vehicle inventory, object contact, performance and persistence. Treat any failure as scoped fix with backout, not a global wipe.
5. Finally publish an accurate launch checklist and documented backups; only call the supported console configuration '100% deployed' after every applicable check passes. Never call absent/engine-impossible features implemented.

Do not create unattended recurring Nitrado writes. Any future code changes must preserve the latest real server state and explicit safe rollback.
