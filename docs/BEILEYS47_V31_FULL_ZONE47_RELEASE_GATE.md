# V31 — Complete ZONA47 26-placement concept: truthful geometry release gate

This version builds a complete **26-role** design layout anchored to Livonia central X 9000 Z 7800, using actual V28 ground elevations. P1 is already registered on live Nitrado, so the new **offline** JSON contains 25 additional candidate objects only. 

## Real deliverable
- Every one of the 26 role IDs is assigned an explicit vanilla class candidate and an X/Y/Z position.
- Previously unresolved 17 roles use visible, simple roadblock / fortified nest classnames already used in BEILEYS47's V16 configured mission. They are substitutions, **not** certified as the perfect intended model or PS5-rendered.
- All nine original model options remain unchanged, including the large barracks and command-house candidates. Third-party P3D **visual** bounding boxes are used for approximating clearances, NOT real collision.
- Pairwise visual envelopes are conservatively measured. Output flags pairs with less than 2.5 m estimated clearance. All unresolved conflicts and origin-height risks are tracked in the result file.
- A real object-spawner JSON is produced for **offline review**, NOT registered in `cfggameplay.json`, Nitrado or the current server.

## Release decision
**Do not call this 100% or install if models overlap, block terrain routes or lack actual PS5 contact tests**. If the visual test fails, a wipe cannot repair wrong classnames, Y model pivots or impassable buildings. The existing P1, V16 scenes, V20 sprint, V21 notices and vehicle/loot modifications remain unchanged.

**There are no public APIs for PS5 gameplay screenshot/collision or scripted PC-mod functionality**. No installer can substitute for observed ground contact, interactions and frame-rate checks.

## Source
- Bohemia: https://community.bistudio.com/wiki/DayZ:Object_Spawner
- Nitrado console restrictions: https://server.nitrado.net/en-GB/guides/settings-dayz-console/
- Ground heights: `config/stage4_14_public_terrain_survey.json`
- P3D visual bounding boxes: `config/stage4_9_p3d_bbox_evidence.json`
- Existing P1 acceptance gate: `docs/BEILEYS47_V29_P1_GUARDBOX.md`
- Script: `scripts/v31_full_zone47_dryrun.py`
