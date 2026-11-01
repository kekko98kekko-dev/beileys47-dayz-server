# V41 — Explicit owner approval for one ordered DayZ restart with one online player

At 18:22 Europe/Rome on 1 Nov 2026, the server owner authorized: "ok puoi anche riavviare e farlo comparire". The previous V40 installation was correctly skipped because one player was online.

V41 is one **push-only** workflow, serialized with V37 and V40, for the actual 3-file V40 deployment. Unlike subsequent hourly schedules it may stop/restart DayZ **only if the server reports 0 or 1 connected players**, never 2+, unknown count, or changing player numbers. An online character will be disconnected by the normal server restart. The standalone V40 scheduler still refuses *any* online players.

Before stop: site and class audits; private SHA-verified ZIP of all three current mission XML files; read-only backups, no wipe. Before each upload: confirm original hashes after stopping. After upload: SHA verification, restart and final readback of the configured CE event. Existing Dolnik truck is never forcibly deleted or relocated; a *new* CE event is created nearby, avoiding overlap where possible. The 64-slot `AliceBag_Green` spawns with newly generated `Truck_01_Covered` cargo if enough room and CE instantiates it.

**Critical limitation:** Restart and a registered CE event are not proof the vehicle is actually instantiated at its location. Only an in-game PS5/PS4 check confirms the truck appeared and can be driven. Filling the fuel tank and the precise shape of collision cannot be guaranteed from XML.

A single successful attempt means the V40 idempotent hourly workflow will automatically stop making changes. New V41 workflow does not run on schedules. If the server is still unfit for safe restart, the operation remains blocked rather than damaging player/world data.
