# BEILEYS47 V18 — safe single-feature rollout

Live Nitrado baseline (run 41297961969, 2026-11-01) confirmed a running V16 server with zero players **at read time**, V16 object spawner with 32 props, 2 Dolnik tents, night multiplier 8 and case economy: Orange case nominal 2/min 1, but the matching Orange key nominal 0/min 0. Blue/Red case keys were already active and are not modified. The joining password field appeared blank; PS5 public entry remains untested.

This V18 patch changes only the Orange GunCase key `nominal: 0 → 2` and `min: 0 → 1` in LIVE `db/types.xml`. It creates **no new structures, scripts or containers**, and cannot prove that the key works when held by a player. The patch is an exact scoped byte substitution, not a full-file reserialization.

Guardrails: strict pinned hash of live V16 `db/types.xml`; one unique target classname, established orange case and blue/red key prerequisites, military usage; no unknown player count or online players; second server state check; safe Nitrado stop, re-read, 1-file upload and SHA256 readback; 7-day GitHub backup artifact and rollback on upload failure; restart and final re-read. Never edit persistence/storage, never wipe.

If an unexpected live source hash, status, player count, XML structure or category is encountered, **abort**, preserve existing configuration and report the reason. GitHub CI tests are necessary but not PS5 gameplay evidence. DO NOT retrigger old V15/V16 jobs.

Remaining: all 15 PS5 acceptance checks, large original ZONA 47, fabricated underground bunker, shipping container red/blue door unlocking, mobile script-controlled hordes, automatic in-game rewards, instant trucks, exact 15-day plank refill. These cannot be marked done by running this workflow.
