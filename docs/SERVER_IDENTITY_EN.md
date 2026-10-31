# BEILEYS47 — English international server identity

**As of 31 October 2026:** purchased DayZ PlayStation server running Livonia and successfully joined from PS5; these new English general settings and Stage 3 English announcements are **NOT YET CONFIRMED LIVE**.

## Nitrado Settings → General (manual only)

- **hostname**: `BEILEYS47 | SURVIVAL WAR | LIVONIA | NO SCHEDULED WIPES`
- **description**: `International community | PvP & PvE | All players welcome | Custom content coming soon`
- Keep `mission=dayzOffline.enoch`; `wipe_on_next_restart=false`; `resetmission=false`.
- Keep a temporary private password until the intended public launch, then remove it only after moderation, backup and performance checks.
- Never paste password, private account data, cookies, FTP details or player identities into GitHub.
- Shut down normally with players offline before changing settings; save and start/normal restart as instructed by Nitrado. Verify the name in the PS5 Community server search.
- `No Scheduled Wipes` describes the **policy**; exceptional technical recoveries or future resets remain possible.

## Stage 3 announcements (not yet installed)

The canonical English texts live in `config/stage3_rules.json` and will be generated into **`dayzOffline.enoch/db/messages.xml`** once Stage 3 is built. Do **not** manually upload Stage 3 before Stage 1 and Stage 2 have been tested, original live files backed up, and server version/mission path verified.

**On connect:**

> Welcome to BEILEYS47 | SURVIVAL WAR! Livonia is unforgiving. Explore, survive and compete. Players from every country are welcome.

**Repeat every 35 minutes:**

> SURVIVAL WAR | Military convoys and helicopter crashes are worth the risk. Stay alert: other survivors may be close.

**Repeat every 60 minutes:**

> SURVIVAL WAR | PvP is enabled. No cheats, exploits or harassment. Respect other players and enjoy the hunt.

The messages do not claim unfinished content is already installed, grant game items, start events, or control restarts. `shutdown=0` and `deadline=0`; each message is at most 160 characters. The 35/60 minute repeat intervals start only after live Stage 3 loading is verified.

## Reference & activation

- `config/server_identity_en.json` is the exact source of server name and description; `config/stage3_rules.json` is canonical for game announcements.
- [PS5 activation evidence and safe rollout](LIVE_ACTIVATION_2026-10-31.md).
- [DayZ Server Messages — Bohemia](https://community.bistudio.com/wiki/DayZ:Server_Messages).
- [Nitrado DayZ console settings](https://server.nitrado.net/en-GB/guides/settings-dayz-console/).

**No automatic GitHub → Nitrado deployment.**
