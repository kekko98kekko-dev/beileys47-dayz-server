# BEILEYS47 | QA tecnico V8 + V9 (31 ottobre 2026)

**AMBITO:** audit dei file di progetto nel repository; sola lettura del cruscotto Nitrado. Nessuna modifica al server, nessun wipe, nessun collaudo PS5 in questa sessione.

## Kit V8 — struttura validata
- `mission/franco_v8/beileys47_freshspawn_v8.json`: 81 combinazioni di cargo, tutte con esattamente 2 frutti (Apple/Pear/Plum), 2 scatolette (PeachesCan/SpaghettiCan/BakedBeansCan), CombatKnife, 2 BandageDressing, ChernarusMap.
- Gli slot contengono maglietta, pantaloni, scarpe e TaloonBag_Blue.
- `ChernarusMap` è anche il classname dell'oggetto mappa utilizzato su Livonia; l'interfaccia mostra il terreno in uso.
- `cfggameplay_V9_CANDIDATE.json` contiene `PlayerData.spawnGearPresetFiles=["custom/beileys47_freshspawn_v8.json"]`; parametri MapData richiesti tutti true.
- Limite di verifica: questo non dimostra che 2 bende e mappa vengano sempre consegnate nel gioco senza errori di preset o inventario; test PS5 necessario.

## Base Dolnik V9 — strutture e CE
- `beileys47_dolnik_military_base_v9.json`: 29 oggetti, precedentemente ricavati dal progetto Scalespeeder su Livonia.
- `dolnik_mapgrouppos_additions_ONLY.xml`: 29 elementi `<group />` corrispondenti.
- Nessuna delle 29 coppie nome+posizione corrisponde a una voce preesistente esatta nel mapgrouppos.xml vanilla Bohemia (verifica coordinate X/Z e classe, tolleranza 0,3 m).
- Il precedente hotspot `beileys47_hotspot_southwest.json` contiene 9 oggetti identici a 9 della nuova base; il precedente `beileys47_test_showcase_v7.json` contiene 21 elementi attorno allo spawn, compresa la tenda difettosa.
- `cfggameplay_V9_CANDIDATE.json` richiama SOLO `custom/beileys47_hotspot_zone47.json` e `custom/beileys47_dolnik_military_base_v9.json` come spawner: vecchio hotspot sudovest e test eliminati dalla lista, senza cancellare i relativi file.
- Limite: non è stato possibile leggere gli effettivi file LIVE dopo l'installer Windows. L'utente ne ha riferito l'esecuzione riuscita; questa non è una prova di caricamento oggetti/loot/assenza di clipping.

## CRITICITÀ ALTA: collisione tra spawn V8 e base V9
- Spawn V8: X11405, Z586; griglia 80×80 metri, dunque rettangolo di generazione centrato circa X11365–11445, Z546–626.
- **6 oggetti della base V9 ricadono direttamente nel rettangolo generatore**: 2 `Land_Mil_Fortified_Nest_Small`, 2 auto polizia abbandonate, 1 watchtower e 1 rottame camion.
- La distanza minima dal centro dello spawn V8 a un elemento della base è **26,87 m**.
- Questo non prova che un giocatore nasca dentro un edificio (il generatore applica altri filtri), ma è un rischio reale. **NON dichiarare spawn risolto**.
- Candidato già preparato in `cfgplayerspawnpoints_v9_SAFEZONE_CANDIDATE.xml`: X11400, Z770, circa **201,65 m** dal componente più vicino della base; edificio statico più vicino censito nel mapgrouppos vanilla **104,64 m**. Non sono stati verificati terreno/pendenza/alberi/acqua/strade; NON attivare a scatola chiusa.
- La documentazione ufficiale conferma che `generator_params.grid_width/grid_height` specificano le dimensioni del rettangolo di generazione: https://community.bohemia.net/wiki/DayZ:Player_Spawning_Configuration

## Stato osservato Nitrado
- Cruscotto server 20113048: DayZ 1.30, Livonia, server «è in esecuzione», contatore 0/10 nell'ultima lettura disponibile.
- Il pannello mostra un avviso generico di precedente avvio/arresto non terminato correttamente; non è possibile concludere che sia un errore attuale senza log/RPT.
- Questo cruscotto non permette di certificare il contenuto aggiornato dei singoli file LIVE; Browser con accesso lettura non può modificare o navigare schede.

## Chiusura richiesta, senza nuovi acquisti
1. Verificare in PS5 ingresso/spawn, inventario V8, mappa accessibile, strutture V9, ingresso/uscita tende, niente doppioni e loot.
2. Se il respawn genera dentro/sopra fortificazioni, scegliere uno spawn fisicamente verificato, non quote inventate. Il candidato X11400 Z770 va testato prima dell'uso.
3. Solo con struttura e loot validi: audit economia/veicoli/eventi usando dump effettivi dei file CE; non presentare stage docs o vecchie configurazioni come installate.
4. **Nessuna modifica automatica al live in questo audit.** Shop, bunker, ZONA 47 sono fuori dallo scope.

**Verdetto tecnico:** kit V8 e spawner V9 coerenti come file di progetto; QA sul runtime non chiuso; spawn V8 con rischio di collisione **documentato**.
