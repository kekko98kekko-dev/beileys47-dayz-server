# BEILEYS47 V40 — One full M3S truck near previous Dolnik spawn, Field Backpack 64

## Actual known live facts (independently read from Nitrado, 1 November 2026)
- Original special truck event `VehicleBEILEYS47DolnikTest` exists and is fixed at **X 11574.92, Z 374.01, heading 177.83°**, nominal/min/max 1 each.
- Existing M3S `Truck_01_Covered` has 4 normal + 4 dual wheels, battery, headlights, hood and doors, but wheel chances 40–60%, battery 25%, lights 10%. All 17 attachments groups found.
- `AliceBag_Green` is defined in the actual server's types.xml and is a vanilla Field Backpack with **64 inventory slots**.
- At first audit, one player was connected: no restart or upload is allowed then.

## Requested outcome and delivery mechanics
1. Add one isolated, **new** vanilla CE event `VehicleBEILEYS47DolnikRescueV40` for a single complete `Truck_01_Covered` next to the original Dolnik spawn. This is necessary because a persisted original truck may have been taken elsewhere; changing its `nominal` alone cannot force another new truck.
2. Place the *additional* truck **35–55 metres from the old coordinates**, rather than stacking two trucks at exactly the same original coordinates. Select the closest safe flat surveyed position using the public Livonia terrain elevation raster, existing buildings/object spawners and vehicle spawn points; this is still not a full physics proof.
3. Make new `Truck_01_Covered` spawn with 100% chance of every existing wheel, battery, headlights, hood, doors and materials attachments, pristine condition, and a `<cargo chance="1.00"><item name="AliceBag_Green" chance="1.00"/></cargo>` prioritized ahead of legacy cargo. **Limitation:** `cfgspawnabletypes.xml` applies by vehicle classname, therefore this affects all future spawns of standard `Truck_01_Covered`, not just the rescue event. Existing persistent trucks are untouched and cannot be retrofitted by XML.
4. The original truck event stays in place, so any owner's existing truck is not deleted or forcibly moved. The event may result in two Dolnik-related trucks in the world if the old one still exists elsewhere. That is intentional to fulfill the replacement request without destroying persistence.
5. **No wipe.** Before changes create a private exact-byte ZIP backup of `db/events.xml`, `cfgeventspawns.xml` and `cfgspawnabletypes.xml`. Upload only those 3 files, SHA-readback, normal restart, SHA-readback. Roll back on errors if no new players joined. First check at zero players, second zero-player check after delay.
6. GitHub Actions will retry hourly while the server is busy, within the current rental period ending 30 November 2026. Once event is installed, repeats safely no-op. **A successful upload does not prove that the DayZ engine already instantiated the truck or that the fuel tank is full.** Cargo includes an existing fuel canister; CE cannot reliably fill a persistent truck's tank through XML alone.

## Safety and expectations
- We cannot query exact locations of existing CE-persistent trucks using these mission files. The additional event uses an offset site to reduce spawn overlap, but a player still needs to check ground clearance and collision.
- The Field Backpack has 64 slots, not a 64-item loadout. It is delivered via the **newly generated** truck's cargo if the engine accepts/loads the item and space permits.
- Everything is compatible with console-side mission XML; no PC mods, server script injection, or player-storage edits.
- If a failed terrain/proximity/remote-state guard blocks, the live config remains unchanged.
- For in-game proof a PS5 player needs to travel to the **chosen offset coords in workflow report**, verify truck exists, all parts attached and bag is in its inventory, then check fuel and driving collision.

References: [Official DayZ Central Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy) and [Field Backpack classname and capacity](https://dayz.wiki.gg/wiki/Field_Backpack).
