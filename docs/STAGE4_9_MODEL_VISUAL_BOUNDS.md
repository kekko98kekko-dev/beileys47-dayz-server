# Stage 4.9 — ZONA 47: dimensioni dei modelli e corridoi di passaggio

**Stato: verifica geometrica di ingombri VISIVI P3D, non collisioni, compatibilità PlayStation o terreno reale.**

## Nuova fonte disponibile

Il catalogo pubblico indipendente **DayZ P3D Explorer** espone metadati numerici P3D e indici DayZ 1.30. Abbiamo registrato 13 corrispondenze nominali per gli oggetti candidati di ZONA 47, ciascuna con ID del record, nome modello, path, versione ODOL, `bbox_min` e `bbox_max`.

Documentazione API: https://www.dzp3dexplorer.com/api-docs.php

Il dataset del sito dichiara DayZ 1.30 e ODOL v56, ma indica anche un numero di vecchi modelli con metadati 1.29 riutilizzati. **La presenza di un modello non prova che `Land_...` sia una classe utilizzabile dall'Object Spawner PS4/PS5**. Inoltre non sono state scaricate le mesh, solo le proprietà numeriche del catalogo. Non si deduce che i bounding box VISIVI corrispondano alle geometrie di collisione o ai LOD utilizzati dal motore.

## Ingombri che contano

Esempi delle dimensioni X × Z del box visivo riportato:

- `Land_Mil_Barracks6_Old`: circa **31,51 × 16,09 m**.
- `Land_Mil_Barracks3`: circa **18,78 × 15,12 m**.
- `Land_Container_1Bo`: circa **2,70 × 10,00 m**.
- `Land_Mil_GuardBox_Green`: circa **2,65 × 4,56 m**.
- `Land_Mil_Guardhouse1`: circa **12,07 × 9,17 m**.

Il test usa per ogni modello un **cerchio conservativo** centrato sull'origine geometrica P3D e contenente tutti gli angoli X/Z della bounding box, quindi non dipende dallo yaw. Per modelli con origine spostata rispetto al centro della scatola, il raggio NON è semplicemente metà della diagonale: viene misurato dagli estremi reali `min/max`. Il cerchio non è un volume di collisione certificato.

## Rischio individuato nel primo piano

I cinque marker progettuali Stage 4.6 erano semplici posizioni X/Z; con gli ingombri visivi associati adesso possiamo verificare quali entrerebbero troppo vicino alle **linee astratte dei 16 collegamenti tattici**. Applichiamo un margine interno di **4 m** dal bordo del cerchio alla linea, che serve solo per identificare proposte poco ragionevoli.

Il programma segnala i marker che non raggiungono il margine e propone modifiche X/Z limitate:

- ricerca in griglia da **2 m**;
- spostamento massimo di **20 m** rispetto al marker;
- ogni marker resta entro **25 m** dal centro del proprio settore;
- mantenimento di almeno **4 m** fra cerchi visivi degli altri quattro elementi;
- scelta della soluzione con spostamento minimo e, a parità, maggior margine dalla linea di percorso.

Le nuove coordinate sono **alternative progettuali**, non sostituzioni automatiche del layout master. Mancano ancora altezze reali Y, fondazioni, tipologia di terreno, strade, boschi, collisioni e controlli sul rendimento PS4/PS5. In particolare, un segmento disegnato potrebbe non corrispondere a nessun percorso calpestabile: il programma NON dichiara sicuri i corridoi.

## Implementazione e sicurezza

File:
- `config/stage4_9_p3d_bbox_evidence.json`: 13 record numerici attribuiti alla fonte e marcati **not collision proof**.
- `scripts/assess_stage4_9_visual_envelopes.py`: analisi dei 5 marker su 16 tratti astratti.
- `scripts/test_stage4_9_visual_envelopes.py`: controlli dimensioni, calcolo per scatole non centrate, distanze da segmenti e integrità dell'archivio.
- `dist/stage4_9_visual_envelopes/pilot_visual_clearance_report.json` e archivio `beileys47-visual-clearance-not-deployable.zip`.

I risultati e i sorgenti vengono aggiunti al Recovery Kit/Release dopo il superamento dei test. Il report mantiene per ogni proposta `suggested_world_y: null`, `ready_to_install: false`, `deployment_allowed: false`.

**Condizione per la futura prova:** confrontare le proposte con un rilievo in gioco, verificare le classi realmente caricabili in Nitrado PlayStation, scegliere l'orientamento corretto del modello e misurare quote, distanza di collisione e possibilità di attraversamento. Nessuna nuova struttura è stata creata nel mondo di DayZ.
