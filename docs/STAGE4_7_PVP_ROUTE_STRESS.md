# Stage 4.7 — ZONA 47: stress test delle rotte PvP e anti-camping

**Stato: miglioramento tattico del progetto, NON collaudo reale su Livonia o console.**

## Scoperta e correzione

Il nostro diagramma precedente aveva 15 collegamenti astratti fra 8 settori e 3 accessi. Uno stress test che simula il controllo ostile simultaneo di **due settori** ha individuato una debolezza precisa:

- **Ingresso est (service)**: se una squadra occupava contemporaneamente **checkpoint** e **logistics**, l'accesso est non poteva più raggiungere il quartier generale attraverso alcuno dei percorsi disegnati.
- Il problema rimaneva invisibile ai test precedenti, che verificavano solo due percorsi indipendenti nello schema iniziale e il blocco di **un solo settore**.

Abbiamo quindi previsto un collegamento secondario **service → secret → hq**: un passaggio esterno stealth verso il nascondiglio e poi il comando, che rende l'accesso est meno dipendente dal checkpoint e dalla logistica.

Non siamo autorizzati a dire che questo sentiero esista nel bosco vero: **è una proposta di percorso progettuale**. La sua apertura effettiva dovrà essere verificata con mappa, vegetazione, quote, costruzioni esistenti e passeggiate in gioco. Resta possibile che un elemento fisico attraversi il segmento diretto. La nuova via non deve inoltre trasformare la ricompensa segreta in una scorciatoia troppo forte.

## Stress test automatici

`scripts/stress_test_stage4_pvp_routes.py` genera un report e una matrice CSV. Usa solamente i collegamenti schematici `config/stage4_zone47_blueprint.json`:

- 3 ingressi: north, west, east.
- 8 settori del campo.
- 16 collegamenti, dopo l'aggiunta del bypass.
- 2 percorsi che non condividono **settori intermedi** da ogni ingresso iniziale verso HQ, secondo i nodi del diagramma.
- **21** casi ingresso / un settore chiuso (inclusa l'eventualità che l'ingresso stesso sia chiuso).
- **45** casi ingresso / due settori interni chiusi, esclusi il settore iniziale e HQ.

### Risultato sul grafo

Prima della correzione: **1 scenario critico su 45** (east, checkpoint+logistics). Dopo la correzione: **0 scenari critici su 45**.

Il risultato è circoscritto **all'astrazione dei collegamenti**, non ai sentieri realmente percorribili su Livonia. Non prova la possibilità di attraversare il terreno, utilizzare le porte o trovare una reale copertura visiva. Non equivale a FPS, bilanciamento reale del PvP o assenza di spawn camping.

Lo script calcola anche i tratti X/Z fra i centri dei settori; tali somme sono **distanze geometriche dei segmenti disegnati, non tempi di spostamento, distanze reali percorribili o misure di terreno**.

## Nuova protezione

L'audit blocca il progetto se anche un solo caso di doppio blocco fallisce o se si rimuove il bypass est. Una regressione di test rimuove appositamente il collegamento e verifica che il difetto venga segnalato. I controlli verificano inoltre che un falso `terrain_surveyed=true` sia rigettato.

Non viene prodotto alcun Object Spawner installabile. L'archivio `dist/stage4_7_route_balance/beileys47-route-stress-design-only.zip` contiene report, CSV, avvertenza e manifest SHA-256.

## Verifiche successive sul luogo di gioco

1. Confrontare con la vera mappa e con il rilievo terreno il collegamento **service → secret**, lungo circa 86 m sul disegno, ma non necessariamente in-game.
2. Verificare da entrambi i lati i tre ingressi; eliminare percorsi che intersecano acqua, rocce, barriere, edifici esistenti o pendenze eccessive.
3. Testare la visuale da ridge e HQ per evitare posizioni invulnerabili o camperabili senza contrattacco.
4. Ripetere l'analisi delle rotte soltanto dopo avere corretto il grafo con i sentieri **realmente percorribili**.
5. Verificare su PS4 e PS5 collocazione degli oggetti, passabilità e frame-time, con rilascio progressivo e piano di ripristino.

**La nuova via progettuale migliora il bilanciamento sulla carta, non trasforma il progetto in un server collaudato.**
