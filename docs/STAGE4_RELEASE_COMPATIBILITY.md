# Stage 4.3 — Official DayZ PlayStation / CE release provenance

**Read-only monitor, not a PlayStation runtime test.**

## Official facts checked on 30 October 2026

- Bohemia's **DayZ-Central-Economy** repository officially labels the `DZ_130` tag as **Stable Update 1.30**. The tag resolves to commit `f220b2918b1d79a5055b1ee9be70c0ec1516e876`, which is exactly the mission baseline already pinned in our Stage 1–4 project.
- The official repository `master` branch pointed to that same commit at the time of review, so there is **no newer published master CE baseline to import** at that point.
- The PlayStation stable 1.30 **Update 2**, build **1.30.164200**, was released **21 October 2026** according to the official PlayStation update forum.
- **Do not confuse Steam Experimental Update 3, 1.30.164289, with the PlayStation stable build.** The latter has not been observed running on our future Nitrado service because no service is active.

References:
- https://github.com/BohemiaInteractive/DayZ-Central-Economy/releases/tag/DZ_130
- https://forums.dayz.com/forum/180-console-updates/

## What the CI check actually does

`python scripts/check_stage4_release_gate.py` reads the **official GitHub** REST API in read-only mode:
1. Confirm `DZ_130` still points to our pinned commit.
2. Confirm its official release description still reads `Stable Update 1.30`.
3. Compare official `master` with the pinned commit to detect later upstream modifications. If different, the report warns **review required**, rather than blindly importing or assuming compatibility.
4. Produce the JSON under `dist/compatibility/stage4_release_gate_report.json`, with `deploy_allowed=false` and `release_ready=false` without exceptions.

`scripts/test_stage4_release_gate.py` verifies the output, the pinned SHA, official tag and the deployment block.

**What this cannot establish:** the current version running on Nitrado, whether the exact modified files are accepted by a server on the target game version, whether a chosen console object class actually spawns, persistence correctness, or PS4/PS5 performance.

## Operational consequences

- We have resolved the question “Are we starting from an arbitrary official release?” **No** — the baseline is the official stable 1.30 CE tag.
- We have **not resolved** “Will our modified mission work without bugs in the current PlayStation Nitrado build?” — no valid server has been deployed or live-tested.
- Before any purchase or upload, compare real service files and current version again. Recheck tags after every official DayZ release.
- Preserve public-source attribution and review licensing before any proposed commercial use; Bohemia's DayZ-Central-Economy repository advertises a noncommercial share-alike license.

The monitor does not download any user account data or interact with Nitrado.
