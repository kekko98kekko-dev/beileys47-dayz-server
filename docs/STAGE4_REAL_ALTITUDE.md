# Stage 4.5 — ZONA 47: acquisizione e verifica delle vere quote del terreno

**Risultato: pipeline di acquisizione e analisi predisposta. Quote Y reali di Livonia NON ancora disponibili o misurate.** Non abbiamo eseguito codice DayZ, non abbiamo visitato il luogo in gioco, non abbiamo un server Nitrado attivo e non autorizziamo installazioni.

## Perché non possiamo ricavare Y da un'immagine

La mappa ufficiale e i file Central Economy contengono molte coordinate di edifici, eventi e spawn, ma non la superficie topografica continua alle nostre 182 posizioni. Le immagini delle mappe sono fotografie/texture o carte topografiche, non matrici certificate di altitudine Y utilizzabili per un Object Spawner.

I servizi di stima dell'altitudine da edifici vicini dichiarano che la quota è approssimata e può essere assente lontano dagli edifici. Non useremo quelle stime per mettere una caserma sul terreno. E soprattutto non sostituiremo automaticamente la quota Y di un edificio esistente lontano 192 metri con quella del nostro punto.

## Come si ottengono le misure **reali**

L'API di un ambiente DayZ compatibile espone `GetGame().SurfaceY(x,z)`, che legge la quota della mesh del terreno a quelle coordinate. È diversa dalla quota della strada o di un ponte; per questi casi serve `SurfaceRoadY` o una verifica della superficie effettivamente calpestabile.

Fonti:
- https://github.com/StarDZ-Team/DayZ-Modding-Wiki/blob/main/en/06-engine-api/19-terrain-queries.md
- https://community.bistudio.com/wiki/DayZ:Object_Spawner
- https://dayzbot.com/tools/map-coordinates (altezze *stimate*, non idonee come quote d'installazione)
- https://tools.dzhosts.com/maps/ (immagini derivate dalle *texture* del terreno, non una griglia di quote)

**Importante:** non possiamo eseguire script arbitrari sulla versione DayZ PS5 o sul server Nitrado console. Un'eventuale acquisizione tramite API va eseguita su un ambiente PC DayZ autorizzato e compatibile, oppure usando dati di elevazione realmente verificati e calibrati con il mondo di gioco; questa disponibilità non è stata stabilita e non comporta un acquisto automatico.

## File creati

`scripts/prepare_stage4_height_capture.py` genera tre JSON `*_surfaceY_empty.json`, uno per ciascun candidato Stage 4.4, con:
- 156 punti `GRID` a passo 20 m;
- 26 punti `PROP` presso i futuri elementi dell'avamposto;
- coordinate X/Z corrette e identità stabili;
- **182 valori `ground_y: null`** per candidato;
- campi di provenienza `measurement`: metodo, build del gioco, data e riferimento delle prove, tutti inizialmente null.

La raccolta segue il *centro* del rettangolo e non la sua origine locale, correggendo il rischio individuato in Stage 4.4.

### Verifica di un dataset autentico

Quando saranno disponibili misure reali, inserire le letture nel file JSON fuori dal repository pubblico, completando il blocco `measurement`; metodo ammesso `DayZ_CGame_SurfaceY` oppure `DayZ_terrain_data_verified`.

Eseguire:

```bash
python scripts/audit_stage4_height_samples.py --input percorso/central_surfaceY_misurato.json --output percorso/risultati_audit.json
```

Lo script:
- blocca coordinate scambiate, regioni errate, ID duplicati, valori NaN, quote non plausibili e provenienza mancante;
- esige tutte le **182 quote** (156 griglia + 26 dettagli di collocazione);
- calcola la pendenza tra celle adiacenti usando le vere distanze X/Z, massimo e 95º percentile degli angoli locali, e dislivello totale;
- segnala come rischio interno una pendenza locale maggiore di **10°** o un'escursione Y complessiva maggiore di **18 m**. *Questi sono criteri di progettazione iniziali, NON limiti ufficiali di DayZ*;
- non produce alcun file di Object Spawner e conserva `terrain_approval=false`, `object_spawner_ready=false`, `deployment_allowed=false` anche quando tutti i valori sono presenti: l'accuratezza e la provenienza fisica vanno ancora verificate indipendentemente.

Il campionamento a **20 metri** può saltare fossati, piccoli strapiombi, rocce e irregolarità nei metri intermedi. Una pendenza media accettabile non dimostra l'assenza di ostacoli né l'accessibilità dei tre ingressi. Ogni costruzione grande richiederà anche più misure sul proprio ingombro e prove dirette in gioco.

## Opzione per acquisire automaticamente le 182 quote su un DayZ PC autorizzato

Il nuovo script `scripts/build_stage4_surfacey_snippet.py` genera `central_surfaceY_pc_runtime_example.c`: un **esempio sorgente Enforce Script NON compilato né eseguito** da questa chat. In un ambiente DayZ PC con strumenti di scripting appropriati, una persona autorizzata dovrà integrare la funzione `Z47CaptureSurfaceY_Example()` e richiamarla una sola volta. La funzione invoca `GetGame().SurfaceY(x,z)` per ciascuno dei 182 punti centrali e stampa nel log una riga `Z47_ALT|...` per punto.

Il tool `scripts/import_stage4_surfacey_log.py` converte automaticamente tali righe nel JSON di misurazione, verificando punti mancanti, duplicati e coordinate non coerenti. **Quinta revisione:** il parser rifiuta inoltre righe troncate, letture con caratteri estranei, registrazioni multiple nella stessa riga e log eccessivi; non sovrascrive file già esistenti né salva misure reali nel repository pubblico (nemmeno in `dist/`). Selezionare un percorso di output privato **fuori** dalla cartella del repository. La data `--captured-utc` deve essere un vero istante UTC nel formato ISO-8601, ad esempio `2026-10-30T00:00:00Z`. Esempio, da usare **solo con un log effettivamente estratto dal runtime**:

```bash
python scripts/import_stage4_surfacey_log.py --log rilievo_gioco.log --output rilievo_reale.json --game-build "VERSIONE_EFFETTIVA" --captured-utc "AAAA-MM-GGT00:00:00Z" --evidence "RIFERIMENTO_REALE_AL_RILIEVO"
python scripts/audit_stage4_height_samples.py --input rilievo_reale.json --output audit_reale.json
```

Non installare il frammento `.c` su Nitrado PlayStation: la modalità console non supporta lo stesso scripting personalizzato del PC. La generazione del codice **non equivale** alla sua esecuzione in gioco e un log fornito da terzi non prova automaticamente che le letture siano autentiche. Servono verifiche indipendenti e prove su PS4/PS5 prima dell'Object Spawner.

## Sicurezza e CI

GitHub Actions genera i template vuoti e un audit che dichiara espressamente **`BLOCKED_MISSING_MEASUREMENTS_OR_PROVENANCE`**. I test positivi e negativi usano un piano Y *matematicamente sintetico*, eliminato senza pubblicarlo: non equivale a una misura di Livonia.

La pipeline conserva risultati, procedure e codice nel Recovery Kit e nello snapshot GitHub Releases. Non include token di accesso, non contatta Nitrado e non modifica gli XML/JSON del server.

**Condizione per Stage 4.6:** acquisizione delle misure attendibili e indipendentemente confermate, valutazione delle pendenze per ogni edificio, verifica strade, vegetazione, collisioni e prestazioni PlayStation. Fino a quel punto ZONA 47 rimane un progetto con posizione preliminare, non una costruzione testata.


Un file di log non autentica automaticamente i dati altimetrici, anche quando supera tutti i controlli di sintassi: l'approvazione PS5 e l'installazione restano bloccate.
