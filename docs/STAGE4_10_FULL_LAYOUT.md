# Stage 4.10 — Audit del layout completo: 26 elementi, 325 confronti

**Stato: analisi statica del PROGETTO. Nessun sito o edificio è stato realmente ispezionato in DayZ. Non installabile su PS4/PS5.**

## Scoperta: il modello non coincide con il segnaposto

La Stage 4.9 poteva confrontare cinque proposte con gli ingombri visivi P3D, ma alcuni abbinamenti provvisori erano troppo generici: ad esempio un `bent_barrier` o `front_entry_marker` non sono automaticamente una casetta militare. Usare l'ingombro di un edificio per ogni marker significa generare falsi conflitti e scegliere oggetti che non rispondono al ruolo di gioco.

Per questo la **Stage 4.10** crea un registro esplicito dei 26 elementi:

- **9 proposte di modello associabili al ruolo visuale**, basate sui 13 record numerici P3D acquisiti alla Stage 4.9. Sono solo opzioni, **nessuna è approvata su PlayStation**.
- **17 marcatori senza un modello specifico**: grandezza sconosciuta, **mai trattata come zero**.
- Tre marcatori `barracks_04`, `hq_04`, `hq_05` descrivono possibili elementi di ambientazione o copertura **interni**. Questo significa che ritrovarli dentro il raggio visivo di un edificio non equivale automaticamente a un bug. Bisogna verificare porte, pavimenti, passaggi e collisioni.

## Quali conflitti sono controllabili

Il codice `scripts/audit_stage4_10_all_placements.py` confronta **tutte le 325 coppie distinte** dei 26 segnaposto.

- Per due modelli con raggio visuale noto, confronta i loro **cerchi visivi conservativi**, segnala sovrapposizioni e distanze inferiori alla soglia **interna** di 4 metri.
- Per un modello con raggio visivo noto e uno ancora sconosciuto, misura la distanza fra il **bordo visuale noto e il punto centrale del marker sconosciuto**. Se il punto sconosciuto ricade dentro il raggio del modello, segnala una priorità alta; **non** dichiara sovrapposte le due geometrie reali.
- Per due elementi sconosciuti non produce un falso margine di sicurezza e registra esplicitamente **`BOTH_SIZES_UNKNOWN`**.
- Per tutti i marker confronta la distanza dai **16 collegamenti tattici disegnati**, distinguendo quelli che terminano nel centro del proprio settore da quelli che attraversano altre aree.

### Un errore di interpretazione che vogliamo evitare

Il nostro grafo **collega il centro di un settore con il centro del settore successivo**. Se mettiamo la caserma vicino al centro di Barracks, il disegno della linea potrebbe attraversare il suo ingombro visuale: questa è una **sovrapposizione fra due concetti**, non la prova che i giocatori siano fisicamente bloccati.

Per certificare un percorso serviranno gli **effettivi ingressi agli edifici, sentieri, scale, porte e collegamenti calpestabili**. Non sposteremo automaticamente un edificio soltanto perché un segmento schematico ne attraversa il centro.

## Le priorità della ricognizione

Il confronto iniziale, utilizzando l'opzione visiva per `barracks_01` e `hq_01`, evidenzia la necessità di rivedere:
- `barracks_02`, `barracks_03`, `barracks_04` intorno alla caserma principale; `barracks_04` può essere una decorazione interna, `barracks_03` richiede conferma di collocazione.
- `hq_04` e `hq_05` vicino o dentro il perimetro visuale del comando, potenzialmente **interni**.
- Il collegamento **service → secret**, prioritario per l'anti-camping, che resta puramente progettuale.

L'audit non modifica il blueprint master né produce file Object Spawner: queste sono **priorità da ispezionare**, non correzioni al terreno reale.

## File creati e sicurezza

- `config/stage4_10_placement_roles.json` — un record per tutti i 26 elementi, con opzione di modello o assenza esplicita di modello, ruolo e intenzione interna/esterna.
- `scripts/audit_stage4_10_all_placements.py` — analisi di tutte le coppie, controllo del grafo e report con provenienza dei limiti.
- `scripts/test_stage4_10_all_placements.py` — test positivi e negativi che rifiutano oggetti inventati e marker mancanti.
- `dist/stage4_10_full_layout/full_26_layout_risk_report.json` — analisi completa e raccomandazioni.
- `dist/stage4_10_full_layout/all_26_placement_review.csv` e `all_325_pair_review.csv` — due fogli di lavoro facilmente ispezionabili.
- `dist/stage4_10_full_layout/beileys47-full-layout-paper-audit-only.zip` — archivio checksum SHA-256 **DO NOT DEPLOY**.

L'audit conserva `deployment_allowed=false`, `any_world_y_measured=false`, `any_console_model_verified=false`, `any_real_collision_confirmed=false` e `object_spawner_generated=false`.

**Prossimo passaggio:** ottenere modelli appropriati e riconoscibili per i 17 marker ancora indefiniti, veri punti Y/percorsi verificati e collisioni testate in gioco. Tutto il lavoro qui è gratuito, reversibile e limitato a file offline / GitHub. Nessun intervento su Nitrado.
