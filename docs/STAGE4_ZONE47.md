# STAGE 4 — ZONA 47: MASTERPLAN V0.1

> **DESIGN ONLY.** No terrain site selected, no DayZ classnames confirmed, no real X/Y/Z, no Nitrado deployment, no PS4/PS5 test. Do not upload design ZIP as a game mission.

## The promise

A forgotten, storm-damaged military logistics outpost, slowly swallowed by forest. The scene tells a believable story: evacuation at the gate, ruined living quarters, looted depot, a command center abandoned in a hurry, a watchpost that can be outflanked, and a small human trace hidden behind the wreckage.

The objective is not maximum objects, maximum guns or artificial difficulty. **The objective is memorable choices:** explore cautiously, expose yourself for a reward, retreat intelligently, or return with friends for a different plan.

## Tactical layout — eight sectors

| Sector | Gameplay identity | Narrative evidence | Proposed reward role |
| --- | --- | --- | --- |
| Broken Checkpoint | Loud northern entry, exposed lines | Interrupted evacuation | Basic utility |
| West Breach | Concealed western approach | Fence opened from inside | Exploration; no rare drops |
| Service Approach | Eastern service entry | Emergency resupply trail | Repairs and utility |
| Barracks Yard | Crossfire and short-range rotations | Personal items abandoned | Moderate supplies |
| Logistics Depot | Mid-range, moving cover | Last military resupply | Ammo and repair |
| Command Core (HQ) | Primary contested interior | Final order never delivered | Scarce high-value opportunity |
| Overwatch Ridge | Strong sightline but exposed escape | Improvised observation point | Viewpoint, not loot jackpot |
| Hidden Cache | Optional discovery | Someone escaped and left a trace | Modest one-off discovery |

## Three different ways to infiltrate

**North: Checkpoint** — most obvious and direct, readable route, attracts attention. It branches toward the barracks and service route.

**West: Broken perimeter** — slower and concealed. Leads into barracks or toward overwatch; does not simply bypass all danger.

**East: Logistics trail** — safer access to maintenance equipment but crosses lanes near logistics. Two alternate paths lead to HQ.

A static graph audit checks that each entry sector has *two internally separate paths* to the HQ. This avoids building a route system where one defended doorway always wins.

### Overwatch counterplay

The watch position is *conceptually* allowed to dominate the checkpoint and part of the barracks, **never every sector**. It must be vulnerable to maneuvers from the woods and HQ. The map is not a verified line-of-sight measurement: actual obstruction, fog, terrain and player positioning require testing.

## Loot and progression

Do not spawn valuable equipment simply because an outpost exists. The initial Stage 4 concept changes **no loot files**. Once terrain and objects are verified, define one narrow, auditable loot layer:
- outer ring: medical and utility;
- service and logistics: tools, car parts, limited ammunition;
- barracks: modest infantry gear, without flood;
- HQ: an *opportunity*, not a guaranteed jackpot;
- ridge: observational advantage only;
- secret nook: discovery and story, never an M4 vending machine.

This is a proposal, not installed gameplay.

## Performance discipline

The **80-object** concept cap is an internal design guardrail, *not a Bohemia-certified hardware limit*. The first micro concept uses **26 symbolic placements** spread across eight sectors. Large structures, model names, Y elevation, size/scale, collision and orientation remain **unspecified**, deliberately.

To proceed:
1. Survey a Livonia land parcel with existing buildings, slope, roads and spawn proximity.
2. Assign real X/Y/Z and orientation using the real game/map tooling. Check terrain altitude for every planned element.
3. Verify each object's actual classname in a build compatible with the PlayStation server.
4. Export a separate Object Spawner JSON only when all details exist and validation passes.
5. Start with a tiny group of objects, not all 26. Check FPS while walking, sprinting, driving and fighting, with a PS4 client in addition to PS5.
6. If performance, collisions, sightlines or readability suffer, reduce assets before adding new ones.
7. Require an approved Nitrado maintenance window and backed-up mission files before any real installation.

Bohemia's official Object Spawner documentation explicitly warns about client and server performance. It requires a JSON list of world objects and a corresponding reference in `cfggameplay.json` `objectSpawnersArr`. This is **not an authorization to upload**.
https://community.bistudio.com/wiki/DayZ:Object_Spawner

## Livonia candidate areas — survey priorities, not selected sites

1. **Wilderness between Nadbór and Swarog**: design hypothesis for meaningful southern progression, but may overlap popular military loops, existing structures and terrain constraints. Survey thoroughly.
2. **Southward approaches near Gieraltów**: potential for remoteness and a different access loop; verify roads, terrain heights and existing event zones.
3. **Krsnik military corridor**: more accessible from northern spawn regions but risks compressing encounters too early and overlapping heavy military content.

These are **broad geographical directions only**. No land parcel or valid center X/Y/Z has been verified or selected. Do not read the local SVG coordinates as Livonia coordinates.

## Verified asset-name shortlist (NOT installation-ready)

An automated source check now reads the **pinned Livonia `mapgrouppos.xml`** and verifies that proposed asset identifiers actually occur in the official terrain group data.

Examples: military guard boxes, old barracks, storage containers, small nests, vehicle wrecks and watchtowers. The full 13-candidate shortlist is in `config/stage4_asset_candidates.json`.

**An object name existing in terrain data is NOT proof that it can be spawned through Object Spawner on PS4/PS5.** Heights, class availability at runtime, collisions, draw calls, lighting, orientation, loot and FPS are still unverified. Large buildings are candidates only, not commitments to spawn 13 big structures.

The audit report is `dist/stage4/asset_evidence.json`, saved together with the design preview and recovery kit.

## Quality gates

- **Concept**: three entrances, eight readable sectors, no disconnected gameplay, route redundancy.
- **Static checks**: blueprint/micro correspondence, graph paths, controlled prop budget, safe null coordinates, no mission package.
- **Survey**: verified parcel X/Y/Z, slope, overlap with CE and vehicles, class support.
- **Real game**: console rendering, ground alignment, moving-player collision, combat readability, loot, PS4/PS5 frame-rate and log errors.
- **Operate**: rollback file checklist, staged install, survival first, then PvP, then staged optimization.

The generated SVG is a **tactical schematic**, not a screenshot of Livonia. The generated Stage 4 ZIP intentionally lacks mission paths and exportable world objects. Its sole purpose is to preserve the design until evidence supports a real deployment.

## Commands / outputs

Run `python scripts/build_stage4_concept.py`.

Expected artifacts under `dist/stage4/`:
- `zone47_layout.svg`: top-down conceptual route map.
- `concept_audit.json`: static gate result.
- `beileys47-zone47-design-only.zip`: non-installable archived blueprint, SVG and report.

GitHub Actions publishes `beileys47-zone47-concept`, and the recovery kit retains the source specification. All outputs are **free and independent of Nitrado**.

## Project rules

**No paid service, no game-server deployment, no destructive operation and no claim of bug-free gameplay without owner approval and live evidence.**
