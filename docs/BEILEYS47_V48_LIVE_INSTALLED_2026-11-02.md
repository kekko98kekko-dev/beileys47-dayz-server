# BEILEYS47 V48 — LIVE INSTALLED, 2026-11-02

**Status:** Config installed and verified after one forced Nitrado restart. GitHub Actions run [41415666703](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41415666703) completed successfully.

- Safety/offline tests: PASS.
- The owner expressly permitted the maintenance restart even while players were connected; Nitrado reported **1 player online** on both pre-stop checks.
- The installer took a checksum-verified backup of the original live `cfggameplay.json`, stopped and restarted the DayZ PlayStation server (no storage/wipe operation).
- Readback after restart confirmed the new gameplay JSON semantically, with **five** building-setting changes (V48 balanced profile):
  - `BaseBuildingData.HologramData.disableIsCollidingBBoxCheck = true`
  - `BaseBuildingData.HologramData.disableIsBaseViableCheck = true`
  - `BaseBuildingData.HologramData.disableIsCollidingAngleCheck = true`
  - `BaseBuildingData.HologramData.disableHeightPlacementCheck = true`
  - `BaseBuildingData.ConstructionData.disableIsCollidingCheck = true`
- Changes to settings for sprint, map, starter gear, object spawners, vehicle economy and other mission files were NOT part of this operation.
- This deployment does not affect physical stacking mechanics for **WoodenCrate**, barrels or the engine's complete FenceKit-on-FenceKit support. These behaviours require an in-game PS5/PS4 test; JSON readback is not a physical gameplay validation.

**Restore artifact (expires 2026-11-09 at 08:50 UTC):**
[BEILEYS47_V48_LIVE_REPORT_AND_EXACT_GAMEPLAY_ROLLBACK](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41415666703/artifacts/13128125174).
Download it to PC before expiry; it contains configuration backup, **not** the entire persistent world (vehicles, bases and players).

**Important:** The user-authorized player interruption was used for this one-time V48 operation. No hourly auto-restart or scheduled Nitrado mutation was created. A forced restart can interrupt players' unsaved progress.

**Known unrelated pending limitations:** V46 `db/types.xml` raw-hash mismatch investigation remains relevant for *future writes to that XML*; the V48 gameplay deployment did not touch `db/types.xml`. Do not infer deletion of two persistent old M3S truck instances from CE source changes. No physical PS5 field test has been performed here.
