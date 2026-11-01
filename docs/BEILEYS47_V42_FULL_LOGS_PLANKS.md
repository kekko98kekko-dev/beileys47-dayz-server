# V42 — M3S timber racks filled to capacity for newly spawned trucks

After the successful owner-authorized V41 real deployment (run 41333625484), the exact private result confirms the truck CE configuration at X11605.23 Z356.51, with one AliceBag_Green 64-slot backpack and the server started.

However the original V11 M3S `Truck_01_Covered` profile set both `WoodenLog` and `WoodenPlank` attachments to `quantmin="50" quantmax="50"`. The V40/V41 code upgraded attachment **chance** to 100% but did not upgrade lumber quantities, so the rack loads were only half full.

**V42 corrects that discrepancy:** set only those two attachment quantities to `quantmin="100" quantmax="100"` with chance already 100%. The intended maximum M3S timber storage is **50 logs + 100 planks** when rack capacity and spawn mechanics allow. The metal plates remain at their prior value; Field Backpack 64 and full truck components are unchanged.

Importantly, `cfgspawnabletypes.xml` controls **future spawns**, not pre-existing persistence entities. V42 does not magically fill a truck that spawned during V41: the player must check the existing truck or wait for a *new* M3S to spawn. To replace a persistent truck instantly would require removing or altering a world-state object, which V42 intentionally does not do.

Workflow: fail closed on changed or partial 50/100 baseline, ZIP backup the exact original XML, double-check 0 online players, stop/update/readback/restart/readback, rollback if safe. Hourly retry only while rental active to 30 Nov 2026, with common lock shared with V37 and V40, no wipe. A successful XML readback is not a console-world vehicle spawn/quantity test.

Real V41 result: https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41333625484
Reference maximum M3S log/plank capacity: https://dayz.wiki.gg/wiki/M3S
