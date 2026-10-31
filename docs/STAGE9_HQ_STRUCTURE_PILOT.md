# Stage 9 — HQ di ZONA 47: primo prototipo strutturale

**Risultato: due possibili edifici da verificare in campo, non due prefabbricati PS5 installabili.** La base ufficiale Livonia fornisce nomi di gruppi di mappa; il catalogo P3D di terzi dà dimensioni dell'aspetto visivo. Nessuno dei due è prova di spawn via Object Spawner PlayStation.

## Due alternative da confrontare

| Candidato DayZ da verificare | Modello visivo catalogato | BBox indicativa X/Z | Uso possibile |
| --- | --- | --- | --- |
| `Land_Mil_Guardhouse1` | Mil_GuardHouse1 | ca. 12,07 × 9,17 m | Piccola struttura di comando, test preliminare preferito **solo per compattezza visiva** |
| `Land_Mil_GuardHouse3` | Mil_GuardHouse3 | ca. 13,84 × 10,84 m | Variante leggermente più ingombrante, da provare solo dopo |

Le misure sono *bounding box P3D indicative*, non collisioni, spazi calpestabili, posizione delle porte, dimensioni interne né geometria sotterranea. La preferenza preliminare dipende **solo** dall'ingombro grafico, non da risultati di gioco.

Il punto `hq_01` dello schema è **X locale 119, Z locale 175**. Non è una coordinata DayZ da installare: mancano ancora la quota reale Y, la posizione fisica verificata, gli ostacoli e i nomi supportati dallo spawner PS5. Intorno consideriamo i marker `hq_02` / `hq_03` (possibili ingressi) e `hq_04` / `hq_05` (possibili arredi interni). Il calcolo offline sottrae il **raggio di ingombro visivo** dalla distanza fra centri; le dimensioni dei marker vicini sono ignote: non possiamo dichiarare alcun corridoio percorribile.

## Sequenza esatta quando Franco attiva il server

La checklist generata in `dist/stage9_hq_structure/hq_structure_checklist.csv` contiene **16 verifiche**, tutte marcate `NOT_TESTED` e `BLOCKED`.

- Prima: provider corretto PlayStation, Livonia e versione compatibile, accesso PS5 vanilla e copia privata degli originali / possibilità di rollback.
- Poi: collaudi separati delle Stage 1 → 2 → 3.
- Poi ancora: sopralluogo delle quote e degli ostacoli e protocollo Stage 4.13 **1 → 3 → 5 oggetti leggeri**. La Stage 9 **non sostituisce, non salta e non accelera** tale test.
- **Soltanto dopo**, se il proprietario approva, testare **un solo candidato HQ alla volta**, verificando con file e log reali che DayZ console lo riconosca. Non utilizzare direttamente path `structures/` P3D come Object Spawner.
- Verificare presenza visibile, orientamento, almeno due vie di uscita **normalmente percorribili**, geometria delle collisioni, scale e stanze, oggetti posati, FPS/stutter e persistenza dopo riavvio.
- Fermarsi e ripristinare le copie dei file modificati in caso di errori, di oggetti volanti, di intrappolamento o degrado delle prestazioni; provare anche il rollback.

**Non aggiungere loot automatico alla prima prova dell'edificio.** È un problema separato: un nuovo edificio non garantisce che la Central Economy generi oggetti nei suoi interni. Le funzioni narrative del bunker di Stage 7 potranno diventare un HQ di superficie se la struttura sotterranea risulterà impraticabile.

## Il nuovo software

`python scripts/build_stage9_hq_structure.py`:

1. Legge il piano Stage 8, i nomi di gruppo mappe Bohemia e gli ingombri del catalogo visivo Stage 4.9.
2. Verifica che nessun file affermi l'esistenza di quote Y, collisioni o classi console già approvate.
3. Calcola dimensioni e distanze **soltanto nel disegno**, tenendo conto dei quattro marker vicini.
4. Genera `hq_structure_review.json` con zero installazioni approvate e `hq_structure_checklist.csv` con 16 attività da collaudare.
5. È controllato da `python scripts/test_stage9_hq_structure.py`: simulazioni avversarie rifiutano dati inventati, valori numerici non finiti, salti del protocollo 1→3→5 e inserimento surrettizio di `objects.json`.

Questi output sono **report e checklist**: non sono configurazioni del gioco, non vanno caricati in Nitrado. Il Recovery Kit li conserva insieme ai sorgenti e ai test.

## Limiti verificabili

L'Object Spawner ufficiale Bohemia permette di indicare oggetti per `name` e posizione, ma i percorsi P3D diretti ammessi riguardano solo piante/rocce previste dall'interfaccia, non i modelli strutturali arbitrari: https://community.bistudio.com/wiki/DayZ:Object_Spawner .

Concluderemo sulla reale fattibilità **solo dopo** misure terreno, prove sul server e accessi/uscite realmente controllati. Anche con tutti i controlli Python verdi, `deployment_allowed=false` fino a verifica e autorizzazione.
