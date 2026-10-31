# BEILEYS47 V11 — Test loot by category (candidate only)

**NOT DEPLOYED, NOT IN-GAME VALIDATED.** This file spawns 57 source-confirmed DayZ item classes with Object Spawner. Some may clip into tent floors or fail to persist; Y coordinates use the original Scalespeeder tent object's origin plus +0.35m, **not independently measured ground height**. Test one group on PS5 before enabling all. Do not install it on the public server while active players are present.

It is a **representative set of testable equipment, NOT every usable DayZ object**. All classes have been checked against Bohemia official Livonia 1.30 `db/types.xml`. Items will be arranged in 3-column rows in six existing tents; no new tents, walls or tables are added.

## MEDICAL_A
- Existing tent: Land_Medical_Tent_Big; center X11508.32, Y212.44, Z441.74
- Contents (9): BandageDressing, SalineBag, TetracyclineAntibiotics, CharcoalTablets, Morphine, Epinephrine, BloodTestKit, DisinfectantSpray, VitaminBottle

## MEDICAL_B
- Existing tent: Land_Medical_Tent_Big; center X11516.97, Y212.44, Z435.24
- Contents (8): BloodBagEmpty, BloodBagIV, PainkillerTablets, Thermometer, SurgicalGloves_Blue, FirstAidKit, Heatpack, IodineTincture

## FOOD_WATER
- Existing tent: Land_Mil_Tent_Big1_1; center X11572.61, Y213.33, Z482.56
- Contents (8): Canteen, WaterBottle, SodaCan_Cola, BakedBeansCan, TacticalBaconCan, CanOpener, PortableGasStove, Rice

## WEAPONS
- Existing tent: Land_Mil_Tent_Big2_4; center X11476.40, Y214.76, Z456.85
- Contents (10): M4A1, AK74, AKM, SKS, Mosin9130, MP5K, Glock19, Deagle, HuntingKnife, CombatKnife

## AMMUNITION
- Existing tent: Land_Mil_Tent_Big2_4; center X11481.71, Y214.61, Z452.55
- Contents (10): Mag_STANAG_30Rnd, Mag_AKM_30Rnd, Mag_AK74_30Rnd, Mag_MP5_30Rnd, Mag_Glock_15Rnd, AmmoBox_556x45_20Rnd, AmmoBox_762x39_20Rnd, AmmoBox_762x54_20Rnd, AmmoBox_9x19_25rnd, AmmoBox_45ACP_25rnd

## TOOLS_BUILDING
- Existing tent: Land_Mil_Tent_Big1_1; center X11580.70, Y213.55, Z475.13
- Contents (12): TireRepairKit, CanisterGasoline, Wrench, LugWrench, Pliers, HandSaw, Hammer, WoodenLog, WoodenPlank, MetalPlate, NailBox, DuctTape


To test after backup and stop, upload `custom/beileys47_test_items_v11.json` and temporarily append it to **active** `cfggameplay.json > WorldsData.objectSpawnersArr`; never overwrite existing spawner references. Ensure old `beileys47_test_showcase_v7.json` is **not** enabled. For clean public server, remove the V11 test items reference after acceptance. No wipe necessary. These pickups are world objects generated on mission start, not auto-refilling supply containers while the server runs.

If a group fails visually, disable the ENTIRE test file reference and restore from backup; don't invent new Y values based only on neighboring object origins.
