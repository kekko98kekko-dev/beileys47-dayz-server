# V32 — Geometric correction of the 26-slot ZONA 47

This is a computer-generated **offline** layout improvement to the V31 26-slot concept. It holds nine large/landmark model candidates (including already-live P1) fixed, and shifts only smaller substitute props until all conservative visual P3D bounding circles have at least 2.5 metres' separation.

The new layout re-reads the public Livonia 2048² terrain elevation raster for each moved X/Z and recomputes ground Y. All position changes and slope values are recorded in the artifact; no model is assumed to use ground height as its correct origin.

**No claim of 100% completion**. We cannot verify PS4/PS5 object rendering, collision/doors/paths, world obstacles, true full-world backups or large-object origins without inspecting the actual console gameplay. The existing V29 P1 is unchanged and still awaits a physical PS5 test. No Nitrado action is performed by V32.

There are console platform limits: DayZ console cannot run ordinary PC server mods, scripted winners, moving script-controlled hordes or programmable freezer systems. See https://server.nitrado.net/en-GB/guides/settings-dayz-console/ and https://community.bistudio.com/wiki/DayZ:Object_Spawner.

Files:
- `scripts/v32_zone47_clearance_solver.py` deterministic placement optimizer
- `dist/v32/ZONE47_25_EXPERIMENTAL_RELOCATED.json` new spawner candidates, **not live**
- `dist/v32/ZERO_VISUAL_COLLISIONS_NOT_PS5_PROOF.json` movement/clearance report
- `config/stage4_14_public_terrain_survey.json` measured Livonia terrain data
