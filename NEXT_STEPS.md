# Stato del progetto — BEILEYS47 DayZ PS5

## Fatto: fase gratuita
- [x] Repository GitHub pubblico autorizzato a ChatGPT.
- [x] Profilo di gioco Livonia 10 slot / PvP survival.
- [x] File ufficiali DayZ CE Livonia ancorati al commit del 16/10/2026.
- [x] Stage 1: cibo, medicine e spawn concentrati.
- [x] Stage 2: loot PvP selettivo, ricambi auto, persistenza stash, stamina.
- [x] Stage 3 PREVIEW: elicotteri/convogli dinamici e messaggi di benvenuto/identità, solo test statici.
- [x] Stage 4 DESIGN: ZONA 47 narrative blueprint, 8 sectors, 3 entries, 26 local symbolic placements; no fake world coordinates.
- [x] Stage 4 topological checks, offline SVG schematic and non-installable concept ZIP in Actions.
- [x] 13 candidate asset names checked against pinned official Livonia terrain groups (NOT in-game verified).
- [x] Fail-closed Stage 4 survey template and offline Object Spawner exporter (requires real terrain input).
- [x] Synthetic-only negative tests: reject missing height, unknown model and absent verification.
- [x] Document PS4/PS5 acceptance gates, performance checks, and rollback protocol.
- [x] Stage 4.8 11 provisional X/Z waypoints and 16 paper-route segments for PS4/PS5 reconnaissance; correct misleading legacy directional entry labels.
- [ ] Stage 4.8 verify physical paths and DayZ terrain Y in game; no PlayStation or Nitrado visit yet (NOT DONE).
- [x] Stage 4.7 PvP schematic graph stress: identified east access failure under checkpoint+logistics lockdown; planned service-to-secret bypass; 0/45 conceptual two-sector lockouts after route amendment.
- [ ] Verify east bypass and all 16 proposed paths in actual Livonia terrain on PlayStation (NOT DONE).
- [x] Stage 4.6 official Bohemia Object Spawner schema checked; center-only world coordinates enforced; five-prop non-deployable prototype plan; synthetic and negative tests.
- [ ] Stage 4.6 obtain real ground heights, verify in-game asset geometry and collision, then pilot on authorized Nitrado PS4/PS5 (NOT DONE).
- [x] Stage 4.5 prepare 182 per-region true DayZ SurfaceY acquisition slots, slope auditor and strict incomplete/provenance fails; NO real heights yet.
- [ ] Stage 4.5 collect and independently verify DayZ terrain Y, real roads/trees/footprints; NOT DONE.
- [x] Stage 4.4 full-scale X/Z survey-grid conversion with corrected world-center versus southwest-origin coordinates, 156 blank Y samples per region and 26 placed conceptual markers; NO height claims.
- [x] Stage 4.3 pinned source release verified against Bohemia official stable DZ_130 tag; version drift monitor added, deployment blocked until live console tests.
- [x] Stage 4.2 rectangle proxy pre-screen for full 240x220m footprint, six orientations, static anchor margins (NOT terrain surveyed).
- [x] Stage 4.1 static candidate screen: terrain anchors, player spawns, and dynamic event anchors compared against pinned Livonia mission; non-deployable report.
- [ ] Stage 4 real terrain parcel, verified slope/roads/vegetation, verified assets and console-tested Object Spawner (NOT DONE).
- [x] Builder automatico di XML/JSON.
- [x] Test di regressione e controllo contenuto ZIP.
- [x] Anteprima Stage 1 e Stage 2 prodotta da GitHub Actions.
- [x] Guida operativa backup, collaudo, rollback e limitazioni PS5.
- [x] Audit indipendente completo sulle differenze XML/JSON rispetto ai file Bohemia.
- [x] Recovery ZIP verificato con SHA-256 e conservazione artifact fino a 90 giorni.
- [x] Piano statico di preflight Nitrado senza alcuna capacità di upload/deploy.
- [x] Nessuna spesa, nessun accesso a Nitrado necessario.

## Prima della scadenza di un futuro server Nitrado
- [ ] Scaricare su PC l'ultimo beileys47-recovery-kit.zip (preferibilmente almeno 48 ore prima).
- [ ] Salvare separatamente i file di missione realmente presenti sul server, se il pannello lo permette.
- [ ] Verificare disponibilità e limiti dei backup dati persistenti nel pannello.

## Prima dell'acquisto Nitrado
- [ ] Confermare prezzo e piano PREPAGATO di PlayStation, non PC.
- [ ] Confermare Livonia nel pannello, versione DayZ compatibile e limite slot.
- [ ] Verificare disponibilità delle opzioni di editing file/API per account console.
- [ ] Verificare metodo di backup e rollback disponibile.
- [ ] Controllare che il progetto funzioni con l'ultima versione DayZ prima di usare i file.

## Dopo l'acquisto: collaudo reale
- [ ] Avvio server vanilla con password temporanea.
- [ ] Controllo backup automatico.
- [ ] Installazione controllata Stage 1.
- [ ] Test su PS5 (spawn, loot, cassa e riavvio).
- [ ] Solo se Stage 1 funziona, installazione Stage 2.
- [ ] Test su PS5 di auto, armi, stamina, persistenza stash.
- [ ] Solo dopo Stage 2 collaudata, testare Stage 3 (crash, convogli, messaggi, performance).
- [ ] Verifica stabilità prestazioni con amici.
- [ ] Solo dopo valutare accesso pubblico e pianificazione eventi.

## Automazione Nitrado
- [ ] Accertare con un server reale che le API/file siano accessibili e affidabili.
- [ ] Non pubblicare token, né inserire credenziali nelle azioni/workflow di PR non attendibili.
- [ ] Progettare installazione con conferma, backup e rollback.
- [ ] NESSUN deploy automatico Nitrado attivo al momento.

## Collegamenti
- [Stage 1](docs/STAGE1.md)
- [Stage 2](docs/STAGE2.md)
- [Stage 3](docs/STAGE3.md)
- [Stage 4 ZONA 47](docs/STAGE4_ZONE47.md)
- [Stage 4.1 Terrain screening](docs/STAGE4_SITE_SCREEN.md)
- [Recupero ZIP](docs/RECOVERY_KIT.md)
- [Checklist e recupero](docs/OPERATIONS.md)
- [GitHub Actions](../../actions)

**Importante:** i test su GitHub dimostrano solo correttezza sintattica e alcune invarianti. Non certificano il comportamento del gioco né garantiscono conservazione del loot.
