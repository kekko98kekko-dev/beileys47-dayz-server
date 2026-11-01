# BEILEYS47 V20 — Unlimited sprint, fast sprint acceleration (PS5 and PS4)

## Requested player experience

Sprint **without draining stamina** when upright or crouched, and no inventory-weight reduction in total stamina. `timeToSprint=0.01` and `timeToStrafeSprint=0.01` make sprint transitions practically immediate (the documented minimum). **They DO NOT increase the character's top movement speed.**

Exactly five changes in LIVE `cfggameplay.json`:

| PlayerData key | Target | Expected function |
|---|---:|---|
| StaminaData.sprintStaminaModifierErc | 0 | No stamina usage when sprinting upright |
| StaminaData.sprintStaminaModifierCro | 0 | No stamina usage when crouch sprinting |
| StaminaData.staminaKgToStaminaPercentPenalty | 0 | Load/encumbrance doesn't shorten stamina bar |
| MovementData.timeToSprint | 0.01 | Fastest documented jog-to-sprint transition |
| MovementData.timeToStrafeSprint | 0.01 | Fastest documented sprint-strafe transition |

Stamina cap remains unchanged (avoid unexpected numeric overflow). Swimming, melee, climbing, jump/vault, shock, health, weather, world objects and all spawner paths also remain unchanged. Sprint no longer drains stamina but **other actions can still consume it**.

## Deployment guardrails

- V18 live original `cfggameplay.json` SHA: `c10b1a0d42f3ab2c057bb6fe87ceeaaf1c0cfb4d0e37adbaa03eb94dc4b42950`. The install refuses a different hash.
- Preserve existing V16/Dolnik object spawner references, player kit, MapData and GeneralData; exact deep semantic equality for all non-target keys.
- Only proceed if Nitrado reports known zero-player count (or server already stopped) and safe server state, with second check.
- If `enableCfgGameplayFile` is explicitly false, refuse to change anything until the setting is reviewed. If not exposed in API, runtime effect remains unconfirmed until PS5 test.
- Save exact original file with SHA256 before upload; stop normally only if players zero; read back after upload; restart; verify again.
- No wipe, no world storage mutation, no change of max running speed or PSN identities.
- Re-running V20 after a successful install will fail on SHA drift rather than overwriting unrelated edits.
- **Still requires a PS5 test**: confirm sprint in actual gameplay doesn't reduce the stamina bar and terrain/objects behave normally.

## Unresolved previous BEILEYS47 requests

The 240×220 original ZONA47, a separate custom underground bunker, functional ship-container locks, script-controlled moving hordes, automated named-player prizes, immediately replenished trucks, exactly timed persistent plank refills, working refrigerators and PS5 collision/performance acceptance **are not magically implemented by these stamina settings**. See [V19 factual feature gate](BEILEYS47_V19_ALL_NINE_FEATURES.md). No unsupported workarounds or arbitrary terrain heights should be pushed onto the live server.

Official source: https://community.bistudio.com/wiki/DayZ:Gameplay_Settings

## Post-deploy evidence — November 1, 2026

- Live install: https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41300300611 — SUCCESS.
- Independent read-only audit: https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41300572865 — SUCCESS; server started and enableCfgGameplayFile enabled.
- Verified running configuration: sprintStaminaModifierErc=0, sprintStaminaModifierCro=0, staminaKgToStaminaPercentPenalty=0, timeToSprint=0.01, timeToStrafeSprint=0.01.
- Original configuration rollback archive: https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41300300611/artifacts/13081490079 (5-day retention).
- Real PS5 sprint behavior remains untested; sprint top speed stays vanilla.
