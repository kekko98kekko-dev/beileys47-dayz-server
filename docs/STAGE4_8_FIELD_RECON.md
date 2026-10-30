# Stage 4.8 — ZONA 47: dossier per ricognizione in partita su PlayStation

**Pronto: checklist + coordinate X/Z preliminari. NON verificato nel gioco.**

## Perché nasce questa fase

La Stage 4.7 ha eliminato un possibile blocco sul grafo tattico con un collegamento esterno `service → secret → hq`. Per renderlo un percorso vero serve controllare concretamente vegetazione, rocce, strade, acqua, pendenze e eventuali edifici vanilla. Non abbiamo ancora rilievi Y autentici né un ambiente DayZ PS5 su cui entrare in quest'area per eseguire test.

Stage 4.8 automatizza la preparazione della ricognizione **senza falsificare misure**:

- Centro candidato provvisorio: **X 9000, Z 7800**.
- Rettangolo locale: **240 × 220 m**.
- Rotazione dello schema: **120°**, scelta dallo screening sui punti XML, *non validata come reale orientamento di costruzione*.
- **11 waypoint**: 3 ingressi e 8 settori.
- **16 segmenti teorici**: collegamenti disegnati nel blueprint Stage 4.7.
- **6 percorsi da verificare**: due alternative su carta per ciascun ingresso verso HQ.
- Zero coordinate verticali Y misurate; nessuna verifica fisica di passabilità.

## La scoperta sulle direzioni

I nostri nomi `north`, `west`, `east` sono **identificatori tattici legacy**, non indicazioni geografiche attendibili dopo la rotazione del campo.

| ID legacy | X mondo approssimativo | Z mondo approssimativo | Direzione dal centro ricavata dalla trasformazione |
|---|---:|---:|---|
| `north` | 9087,603 | 7848,268 | **NE**, azimut 61,1° |
| `west` | 9055,866 | 7705,237 | **SE**, azimut 149,5° |
| `east` | 8941,304 | 7889,665 | **NW**, azimut 326,8° |

I valori sono il risultato matematico del modello X/Z del progetto; **non sono quote topografiche, orientamenti reali verificati o coordinate di oggetti già presenti nel mondo**. I nomi interni rimangono invariati per conservare la compatibilità con i rapporti e gli script preesistenti.

## I file utilizzabili per il sopralluogo

Lo script `scripts/build_stage4_8_field_recon.py` produce:

1. `central_waypoints.csv`: coordinate X/Z, nome e settore, direzione derivata, colonna Y volutamente vuota.
2. `central_route_links.csv`: tutti i 16 segmenti tra due coordinate, distanza rettilinea illustrativa e colonne vuote per passabilità, ostacoli e visuali.
3. `central_field_recon.json`: i sei percorsi alternativi e una checklist di campo che comprende passabilità, fossi/acqua, alberi, rocce, strada, pendenza, visuali PvP, prove video, build di gioco e test effettuati.
4. `beileys47-world-xz-field-guide-only.zip`: archivio **non installabile** con avvertenza, report CSV/JSON e hash SHA-256.

**Questi file non sono un Object Spawner, non contengono una missione DayZ e non vanno caricati su Nitrado.**

## Priorità di verifica in gioco

Il collegamento `service → secret` è il primo da controllare: risolve un collo di bottiglia solo *nel disegno*. Se un fiume, un edificio, una salita invalicabile o un bosco troppo fitto attraversa il tracciato, il percorso alternativo dovrà essere riprogettato. Vanno poi controllati i tre accessi e le visuali di ridge, checkpoint e HQ.

Una foto satellitare o una mappa illustrata può aiutare la ricognizione, ma non certifica pendenza, collisione, visibilità o comportamento del motore.

Mappa consultabile: https://www.izurvive.com/livonia/ — seguendo le coordinate X/Z e **non** gli ID storici degli ingressi.

## Quando possiamo passare alla prima installazione

Occorrono **misurazioni Y documentate e attendibili** nei punti dei primi oggetti, verifica in gioco dei 16 percorsi (o modifica progettuale verificata), classi DayZ testate e compatibili, autorizzazione, backup provider e test graduali 3–5 oggetti su PlayStation. Le conferme non si possono simulare con i test Python.

Non abbiamo speso denaro, usato Nitrado, eseguito DayZ o verificato un terreno reale. I test attestano soltanto che la ricognizione proposta è coerente con i dati e non sposta erroneamente le coordinate.
