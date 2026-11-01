# BEILEYS47 V18 — Live read-only preflight

This stage runs once on the merge to main and is strictly read-only. No server stop, restart, upload, persistence edit, wipe or password edit.

The actual remote Nitrado configuration is compared with V16 to inspect gun case/key class names, nominal counts, compatible cargo, the special infected zones, CE positions and loot limits. Password data is never logged; only a possible boolean hint about blank game-join password is recorded.

CI and Nitrado XML/JSON evidence cannot verify in-game structure heights, collision, door/key interaction, persistence or performance. An additional safe change requires separate approval gates: fresh remote reads, minimal diff, zero connected players, integrity-checked rollback, and live readback after restart.

Do not rerun legacy V15/V16 deploy marker jobs. This stage installs nothing. The no-wipe policy is not a substitute for a verified persistent-world backup.

Source: https://community.bistudio.com/wiki/DayZ:Object_Spawner
