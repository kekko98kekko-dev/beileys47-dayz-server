# ZONA 47 — PS4 / PS5 Acceptance and Rollback Protocol

**Status:** future live-test specification, not evidence of any completed test.

## Principle

We do **not** equate successful JSON/XML validation with rendering correctness. The site becomes deployable only if we can verify actual terrain, supported classes, collisions, pacing, player movement, combat sightlines, asset loading and the rollback path on a purchased PlayStation-compatible server.

## Baseline before any installation

1. Owner explicitly approves the test and its date. Verify DayZ build, Livonia map, actual server path and Nitrado plan.
2. Record the unmodified server file checksums and inspect available rollback/backups. Save private copies where possible.
3. Make a fresh run in the *same location* on PS5, plus PS4 if available, with **no ZONA 47 objects**. Record a repeatable traversal and combat-like sprint/aim test.
4. Capture weather, time of day, player count, network conditions, the approximate test route, abnormal stutters and any render errors.
5. Verify Stage 1/2/3 mission compatibility before trying Stage 4. If prior stages are not stable, stop and recover.

## Progressive installation gates

| Gate | Deployment state | Minimum acceptance |
| --- | --- | --- |
| A: 0 props | existing Stage 3 | Baseline measured, files backed up |
| B: 3–5 props | explicit small test | All visible, grounded, no clipping/traps, recovery proven |
| C: 10–15 props | only after B passes | Routes remain traversable, PS4 and PS5 behavior compared |
| D: up to 26 props | only after C passes | Three entries and HQ accessible, vehicles can approach, no persistent performance regression |
| E: expanded 40–60 | **not planned for first Nitrado trial** | Requires separate evidence, approval and another rollback plan |

The object counts are internal engineering targets, **not official DayZ guarantees**.

## Gameplay walk-through

For **every** entry (north, west, east):
- Walk, crouch, sprint and carry equipment along the route.
- Try at least two routes to the HQ, and turn back without being forced into one campable corridor.
- Test ladders, doors and narrow gaps only on objects actually included in the game build.
- Test head/shoulder peeking near cover, roof and rocks; eliminate invisible barriers, holes or strong one-way positions.
- Test the ridge from both the attacker and defender perspectives.
- Re-enter after a normal restart: ensure no duplicated props, missing props or mission errors.

For loot and bases:
- Do **not** add top-tier loot until CE impacts are measured.
- Verify bases can still be built and stored where the server intends; make sure ZONA 47 does not create abusive base placements.
- Confirm that no site props obstruct existing CE dynamic events or vehicle spawn points.

## Performance acceptance

Test the same route with the same settings, time/weather where practical, and comparable player activity.
- Look for new sustained frame-time spikes, texture streaming problems, unusually severe stutter, delayed inputs or crashes.
- Capture at least two repeats on each available console generation, both in open traversal and simulated gunfight.
- If PS4 behaves materially worse than the baseline, **reduce or remove** heavy structures first.
- Write down what was measured versus what was only perceived. Do not invent an FPS number.

## Failure response

If an object floats, clips a player, blocks an essential path, makes a sniper position invulnerable, breaks the mission or causes visible performance degradation:
1. Halt public rollout.
2. Stop the server using the official panel during a player-free test window.
3. Revert the Object Spawner reference and the changed gameplay file using the private original copies.
4. Check whether separate Nitrado backup restoration is required and available.
5. Verify clean startup, player inventory and relevant persistence *before* any reattempt.

**Rollback files are NOT the same as backups of live characters, bases, vehicles or world storage.**

## Evidence ledger

For each test record:
- Date and DayZ version, PS4/PS5, observed player count.
- Server world location and private site survey revision.
- Class name and placement IDs tested.
- Screenshot/video/console-visible behavior and server logs where available.
- Outcome: PASS / FAIL / NOT TESTED (never infer PASS from missing data).
- Exact files rolled back if necessary.

## Stage 4 release policy

- **Concept accepted** = paper structure and static checks pass.
- **Prototype available** = survey-backed offline Object Spawner files exist.
- **In-game validated** = real console tests pass, evidence recorded.
- **Live release approved** = owner authorizes specific deploy after rollback review.

Only the first state can be achieved for free today without an active Nitrado server.
