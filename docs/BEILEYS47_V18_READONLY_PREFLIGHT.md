# BEILEYS47 V18 — Live read-only preflight

This stage runs once on the merge to main and is strictly read-only. No server stop, restart, upload, persistence edit, wipe or password edit.

The actual remote Nitrado configuration is compared with V16 to inspect gun case/key class names, nominal counts, compatible cargo, the special infected zones, CE positions and loot limits. Password data is never logged; only a possible boolean hint about blank game-join password is recorded.

CI and Nitrado XML/JSON evidence cannot verify in-game structure heights, collision, door/key interaction, persistence or performance. An additional safe change requires separate approval gates: fresh remote reads, minimal diff, zero connected players, integrity-checked rollback, and live readback after restart.

Do not rerun legacy V15/V16 deploy marker jobs. This stage installs nothing. The no-wipe policy is not a substitute for a verified persistent-world backup.

Source: https://community.bistudio.com/wiki/DayZ:Object_Spawner


## Verified live result — 2026-11-01

- [Baseline read-only Nitrado run 41297961969](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41297961969): V16 STARTED, 32 V16 world props, 2 Dolnik tents, 3 targeted infected territory entries, helicopter/convoy nominal 5 each, night acceleration 8; API game-password field blank; player count 0 at baseline inspection. Public gameplay is **not** verified on PS5.
- [Single-file guarded V18 rollout 41298341010](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41298341010): SUCCESS, with zero-player guard, backup before upload, SHA256 readback, normal restart and post-restart readback. Only `db/types.xml` changed, to raise `GunCaseKeys_Orange` from `nominal=0/min=0` to `nominal=2/min=1`. Other active red/blue keys were retained. Rollback ZIP and factual result stored in [short-lived artifact 13080198584](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41298341010/artifacts/13080198584) (7-day retention).
- [Independent post-deploy Nitrado audit 41298602716](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41298602716): SUCCESS. Confirmed active Orange keys nominal2/min1 alongside V16 32-prop spawner, 2 Dolnik tents, med lootmax10/mil lootmax8, blue/red keys2, night multiplier8 and vanilla increased crash/convoy events. No wipe operation performed by V18 scripts; game-world persistence **not verified** by API or PS5 gameplay.

## Remaining requests — never label as complete without real evidence

| Request | Factual result after V18 | Remaining blocker |
| --- | --- | --- |
| 240×220 m original ZONA 47 | V16 extension of Radunin site is present | Larger original design has no measured terrain Y or visual PS5 collision/progress test |
| New custom underground bunker | Only existing vanilla bunker perimeter reinforced | No verified placeable multiroom underground interior, portals or safe exits on console |
| Red/blue key shipping-container puzzle | Colored rifle cases and some keys enabled in CE | No working shipping-container door/key interaction demonstrated on Livonia |
| Mobile scripted zombie hordes | 3 V16 infected territories configured | No custom scripts or intelligent moving horde system available through vanilla console XML alone |
| Weekly winner prizes | Scheduled GitHub community issues, in-game periodic notices | No automatic winner identification or inventory payout in vanilla PS5 |
| Immediate replacement of driven-away trucks | V15 truck economy and test event configured | CE counts persistent live vehicles; replacement not guaranteed while moved truck still exists |
| Exact 15-day plank refills | Newly generated piles configured at full quantity | Cannot replenish persistent existing piles exactly on calendar day with static `types.xml` |
| Fridge & exotic working objects | No proven interactive refrigerator on console | Vanilla decorative props only after classname+terrain+PS5 check |
| Fully public and visually tested server | Game password field blank, Nitrado STARTED | PS5 community connection, placements, loot, infected, vehicle and stash persistence still unverified |

**Do not** trigger old V15/V16 one-time GO_LIVE markers. Next safe action is the [V17 15-point PS5 field acceptance protocol](BEILEYS47_V17_PS5_ACCEPTANCE.md). This is the first required evidence before expanding static world geometry; any failure should be corrected through targeted and reversible Nitrado edits.

