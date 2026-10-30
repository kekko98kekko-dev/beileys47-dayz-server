# Stage 4.11 — 17 proposte di piccoli modelli P3D per ZONA 47

**Risultato: un catalogo coerente di opzioni visive, NON una lista di classi confermate e installabili su PS4/PS5.**

Dopo la Stage 4.10 avevamo 9 segnaposto associati a un ingombro P3D di riferimento e 17 senza nemmeno una dimensione di base. Abbiamo consultato le schede API di **DayZ P3D Explorer**, indicizzate per DayZ 1.30 (ODOL v56) e registrato **14 nuovi modelli univoci** con ID, modello, percorso, `bbox_min` e `bbox_max`. Questi possono rappresentare **17 ruoli** del campo, riutilizzando alcuni tipi piccoli. Fonte: https://www.dzp3dexplorer.com/api-docs.php . Il catalogo dichiara alcuni fallback di vecchi metadati 1.29: non certifica, da solo, la disponibilità di un oggetto sulla console.

## Selezioni proposte (solo visive)

| Segnaposto | P3D suggerito | Scopo |
|---|---|---|
| checkpoint_01 | Roadblock_Bags_EndL | Semibarriera lato sinistro |
| checkpoint_02 | Roadblock_Bags_EndR | Semibarriera lato destro |
| woods_01 | Misc_BarbedWire | Recinzione rovinata, da verificare rispetto ai passaggi |
| woods_02 | Misc_SupplyBox1 | Cassa abbandonata |
| service_01 | Misc_RoadBarrier | Ostacolo stradale lungo, potenzialmente troppo ingombrante |
| service_03 | Sign_Roadblock_Arrow | Piccolo segnale di direzione |
| barracks_02 | Misc_BagFence_3m | Protezione esterna vicino alle camerate |
| barracks_03 | Misc_BagFence_Corner | Copertura angolare, da verificare rispetto alla caserma |
| barracks_04 | Misc_Table | Elemento narrativo **forse** interno |
| logistics_04 | Misc_Tire | Indizio di riparazioni |
| hq_02 | Misc_BagFence_Corner | Copertura per l'entrata, non una porta |
| hq_03 | Misc_BagFence_3m | Protezione dell'uscita posteriore |
| hq_04 | Desk_Office | Scrivania interna, pavimento da verificare |
| hq_05 | Desk_Globe | Piccolo indizio su tavolo, **non appoggiabile direttamente al terreno** |
| ridge_02 | Misc_SupplyBox1 | Cassa vicino alla via di fuga |
| secret_01 | Misc_WoodenCrate | Piccola cache di legno |
| secret_02 | Misc_SupplyBox2 | Indizio nascosto |

## Limitazione ufficiale fondamentale

La documentazione Bohemia del [DayZ Object Spawner](https://community.bistudio.com/wiki/DayZ:Object_Spawner) accetta nomi di **classi spawnabili** oppure percorsi P3D solo nelle categorie `DZ/plants*` e `DZ/rocks*`. **Non si possono usare direttamente le path `structures/...`, `structures_bliss/...` o `structures/furniture/...` dei modelli sopra come se fossero spawner validi.**

Il catalogo NON costruisce nomi `Land_...` a partire dal P3D, NON modifica il campo `class_name` nel blueprint e NON crea `zone47_objects.json`. Anche i nove precedenti `Land_...` erano indizi da verificare in runtime, non certificazioni console.

Un ingombro P3D visuale NON è la geometria delle collisioni DayZ. Inoltre un punto vicino a un edificio può essere voluto come decorazione interna: i confronti 2D non sostituiscono controlli porte, pavimenti, scale, coperture e accessi.

## Cosa calcoliamo

Lo script `scripts/assess_stage4_11_role_model_options.py` fonde *solo per analisi* le 9 opzioni P3D precedenti e le 17 nuove:

- 26 punti con un modello visivo di riferimento, **0 con classe PS5 provata**;
- 325 coppie con distanza fra cerchi visuali 2D approssimati, distinguendo interferenza e semplice margine inferiore a 4 metri;
- mappa dei punti da ispezionare, con segnali per oggetti magari interni a Barracks/HQ;
- coordinate world X/Z **matematiche**, quote `world_y: null` e nessun piazzamento autorizzato.

Quando il report parla di *sovrapposizioni*, intende unicamente **intersezioni dei cerchi conservativi ricavati dalle bounding box visive**; non dimostra che i modelli o i giocatori si scontrerebbero fisicamente. Non vengono modificati i 26 punti originali.

Il codice e i test rifiutano classi console inventate, path strutturali dichiarate erroneamente spawnabili, quote reali fittizie e proposte mancanti. Le unit test restano sintetiche; nessun server è stato raggiunto.

## File

- `config/stage4_11_p3d_role_candidates.json`: 14 P3D con coordinate bbox e 17 abbinamenti, sempre `verified_console_object_classname: null`.
- `scripts/assess_stage4_11_role_model_options.py` e `scripts/test_stage4_11_role_model_options.py`.
- `dist/stage4_11_role_catalog/candidate_26_visual_fit_report.json` e tabelle CSV degli ingombri/avvisi.
- `dist/stage4_11_role_catalog/beileys47-stage411-visual-role-options-not-deployable.zip`, con manifest SHA-256 e avvertenza **DO NOT DEPLOY**.

**Prossimo blocco reale:** ottenere conferme di `name` validi con il registro effettivo e il log RPT del server PS5, misurare altimetria o pavimenti, controllare collisioni e prestazioni in gioco. Non usare questi file come configurazione Nitrado.
