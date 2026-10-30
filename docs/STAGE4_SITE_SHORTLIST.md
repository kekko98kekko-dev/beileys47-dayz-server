# ZONA 47 — First provisional Livonia coordinates (do not deploy)

**Evidence:** independent distance calculations against the pinned Bohemia Livonia mission XML, **30 October 2026**. These are X/Z coordinates from source-file geometry, **not tested sites**. World Y, terrain slope, trees, roads, player paths, collision volumes, rendering and Object Spawner support are unknown.

The automated script in this branch regenerates a larger shortlist and the supporting evidence. This page presents **one provisional first-survey position per region**. It does NOT fill Stage 4's required actual site anchor.

| Region | First X / Z to inspect | Nearest active-stage fresh spawn | Nearest included active event point | Nearest terrain group anchor | Nearest military group anchor |
| --- | --- | ---: | ---: | ---: | ---: |
| Central military approaches | **9000 / 7800** | 3,527 m | 508 m | 343 m | 891 m |
| South-west wilderness | **4500 / 4000** | 6,429 m | 810 m | 305 m | 825 m |
| South-east approaches | **9200 / 2900** | 7,800 m | 713 m | 452 m | 877 m |

These distances are *straight-line differences between XML anchor coordinates*, not travel times or guaranteed safe separation. The source-based shortlist also lists two alternative center points per region.

## Preferred first survey: X=9000, Z=7800

With only ten initial slots, the priority is making an area reachable while preserving the sense of having progressed beyond the concentrated fresh spawns. This central candidate is less remote by coordinate distance than the southern alternatives. It also has no *terrain group anchor* within the internal 240 m screening radius, but **that does not establish an empty 240 × 220 m build footprint**.

This is **provisional prioritization**, not approval of the specific parcel: look at an actual terrain map and walk the place before selecting an anchor.

## Acceptance gate

A candidate is rejected if actual scouting reveals steep slopes, obstructed roads, unsuitable vegetation, hidden colliders, existing static mission structures, contaminated triggers, blocked exits or a strong uncounterable sightline. Ground elevations and real rotations must be measured for each intended element before experimental JSON export.

## Source and update policy

- The input baseline is Bohemia Interactive DayZ-Central-Economy, commit `f220b2918b1d79a5055b1ee9be70c0ec1516e876`.
- Source files: `mapgrouppos.xml`, `cfgplayerspawnpoints.xml`, `cfgeventspawns.xml`, `db/events.xml`; the last file filters out inactive events.
- Fresh-spawn groups: Brena, Sobotka, Kolembrody, following Stage 1.
- Screening rules: `config/stage4_site_screening_rules.json`.
- Regenerate with `python scripts/scan_stage4_sites.py`.
- **If the DayZ server version or user-approved spawn rules change, rescan before any real work.**

The figures are not proof of object fit, no scene is installed and no performance claim is made.
