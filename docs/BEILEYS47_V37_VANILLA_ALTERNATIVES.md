# V37 — Vanilla infected pressure at the fully installed central ZONA 47

**This is an in-game-compatible alternative to scripted roaming hordes.** It creates two nearby 55-metre-radius military infected territory zones at Livonia X8960 Z7810 and X9040 Z7730 with dynamic 5–9 infected each. Vanilla zombie navigation, aggression and pursuit remain handled by the original game engine; no PC mod and no promises of scripted roaming across the entire map.

Implementation: a guarded, reversible patch of the existing `env/zombie_territories.xml`, checking the real `InfectedArmy` event exists, the old three V16 zones still exist, no new zone overlaps existing zones within 75m and the two new circles do not overlap. Expected additional nearby dynamic count is at most 18, bounded for PS4 stability. The engine's global zombie count cap still applies. XML backup is archived privately and every write is SHA-read back. Normal stop/restart only after two zero-player checks, without wipe/player-data access.

Bunker: the original navigable Livonia bunker remains the supported location. **No underground construction with unverified egress is installed**; this intentionally avoids a player-trap bug and item-loss trap. Existing V16 bunker military infected zone is preserved.

Colored keys: preserve the already installed vanilla `GunCase_Black` / `GunCaseKeys_Blue`, `GunCase_White` / `GunCaseKeys_Red` and orange case/key. These are not shipping containers with working blue/red locks. Their in-game opening interaction still needs real PS5 proof.

Fridges: no functional refrigerator storage with cooling can be created using PlayStation XML/JSON. Do not invent a working freezer; vanilla food can be stored in existing inventories without cooling but this is not equivalent.

Prize automation: the scheduled weekly GitHub community challenge announces prizes that can be found through the normal DayZ loot economy. No code-based identification of winners or automatic item transfer is possible on the console via XML.

Plank maintenance: the 15-day GitHub issue reminder already runs. Persistent piles cannot be rewritten by `types.xml` without a world-state editor, and changing global CE counts would not reset 252/252 piles.

Quality: successful deployment means registered XML on Nitrado, **not** actual navmesh/PS4/PS5 runtime. Physical player tests remain required. Provider backup inventory found 3 reported records with restore_possible=true, but no restore was executed to avoid undoing player progress. The provider's 24-hour backup mechanism is not a guarantee of a successful world restore.

References:
- https://github.com/BohemiaInteractive/DayZ-Central-Economy/blob/master/dayzOffline.enoch/env/zombie_territories.xml
- https://community.bistudio.com/wiki/DayZ:Object_Spawner
- https://server.nitrado.net/it-IT/guides/ripristino-backup-su-dayz-it
