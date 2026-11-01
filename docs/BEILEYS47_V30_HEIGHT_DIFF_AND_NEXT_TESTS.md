# BEILEYS47 — V30: Live structure heights against Livonia terrain

**Run:** [V30 live read-only terrain comparison 41307362687](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41307362687) — SUCCESS, 1 November 2026.

**Server status:** started at the time of the audit. No Nitrado edit, wipe, restart, CE modification or user inventory access performed by the diagnostic.

## Current evidence

The diagnostic independently fetched the currently installed V16 and V29 Object Spawner JSON from Nitrado, downloaded the public DZPage **2048 × 2048 float32** Livonia heightmap and compared each object origin Y with interpolated ground Y. The orientation and mapping were previously calibrated against 1,100 official Bohemia static object positions in V27.

| Scene | Objects | Median absolute origin/ground difference | Above 1.5 m | Above 6 m |
|---|---:|---:|---:|---:|
| V16 Radunin, vanilla bunker perimeter and Dolnik | 32 | 2.267 m | 27 | 0 |
| V29 one guardbox at X 9057.3275 / Y 302.7723 / Z 7822.7058 | 1 | 0.000 m | 0 | 0 |

Samples of **raw pivot minus terrain**, not certified model-ground gaps:
- Radunin `Land_Mil_Fortified_Nest_Small` at X 7083 Z 6953: **+2.493 m**.
- Radunin `Land_Container_1Mo` at X 7088 Z 6982: **+2.577 m**.
- Radunin `Land_Roadblock_WoodenCrate` at X 7084 Z 6965: **+2.366 m**.
- Existing Livonia bunker perimeter `Land_Mil_Fortified_Nest_Small` at X 9040 Z 7455: **+3.139 m**.

## Interpretation and mandatory gate

**Do NOT lower the 27 origins automatically.** Buildings, vehicle wrecks and roadblocks use different local model pivots, and many pivot points are intentionally above ground to display correctly. The raster itself may differ by small amounts from runtime collision terrain or detailed foundations.

PS5 observations are still needed before adjusting or expanding each sector:
1. **V29 P1**: Is the `Land_Mil_GuardBox_Green` visible and touching the ground at X 9057 Z 7823? Are entrances usable and nearby roads clear?
2. **V16 Radunin**: check crates/containers/fortified nests at X 7083–7128 Z 6940–6992 for floating, clipping or blocked paths.
3. **Vanilla bunker perimeter**: check X 8999–9043 Z 7438–7474, especially object at X 9040 Z 7455.
4. **Dolnik**: verify tent area and loot props; the two original tents were not modified in V29.
5. If any placement needs adjustment, record classname, X/Z, actual visual displacement, corrective `Y` and PS5 video/screenshot; use a small one-file rollback-protected patch.

**No P3/P5 mass rollout while P1 is unverified.** Full 240 × 220 m ZONA47 remains incomplete, despite the 78 calibrated candidate ground heights stored in `config/stage4_14_public_terrain_survey.json`.

## Proven live state

- [V29 single-object Nitrado deployment 41306956859](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41306956859) — SUCCESS.
- [Independent V29 Nitrado readback 41307201374](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41307201374) — SUCCESS, all V16/V20/V21 invariants retained.
- [V30 comparison 41307362687](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41307362687) — SUCCESS.
- Existing original gameplay rollback copy: [V29 artifact 13084040649](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41306956859/artifacts/13084040649); short-lived configuration backup, NOT a world-persistence snapshot.
