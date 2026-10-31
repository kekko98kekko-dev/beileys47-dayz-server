# Stage 8 — Fattibilità bunker su DayZ PS5: prove prima del montaggio

**Stato: analisi di provenienza e fattibilità offline, NON collaudata in console.** Non abbiamo un server Nitrado né una PS5 raggiungibile attraverso questa pipeline. Nessun oggetto, struttura, terreno, loot o riavvio viene installato.

## Una scoperta che cambia il progetto

Il repository pubblico `scalespeeder/DayZ-LIVONIA-Yugovostok-Underground-Bunker-Custom-Json-File-For-PC-and-Console` include un vecchio esempio di bunker Livonia. Lo stesso autore scrive chiaramente che **non si riesce a uscire normalmente**, che si deve fare **logout/login** e che gli oggetti lasciati cadere potrebbero ricomparire in superficie. Dichiara test limitati su **PC locale DayZ 1.16**. Il progetto non è una prova che lo stesso bunker sia sicuro o funzionante sulla versione corrente PS5.

Fonte: https://github.com/scalespeeder/DayZ-LIVONIA-Yugovostok-Underground-Bunker-Custom-Json-File-For-PC-and-Console

**Decisione di progettazione:** non copiamo quel file e non promettiamo un tunnel sotterraneo di cui non conosciamo la fisica. Un oggetto che intrappola i giocatori, impedisce di recuperare equipaggiamento o richiede logout per uscire è un fallimento del collaudo.

## Tre strade alternative

| Approccio | Vantaggio | Problema da risolvere | Primo noleggio |
| --- | --- | --- | --- |
| Riutilizzare un sito vanilla già percorribile | Niente costruzione di geometrie sotterranee non native | Verificare accessi e presenza reale del sito, possibili vincoli della mappa | Ricognizione, nessuna modifica |
| **Quartier generale in superficie**, atmosfera bunker | Approccio conservativo con piccoli test di strutture vanilla | Le classi candidato non sono ancora approvate sullo spawner console | **Prima scelta progettuale**, dopo vanilla e Stage 1–3 |
| Struttura sotterranea assemblata | Esperienza visiva particolare, solo se fattibile | Terreno, collisioni, uscite, pavimenti, classi, performance, persistenza | **Non autorizzata** nel primo test |

La seconda opzione preserva le **10 funzioni ambientali e i 3 accessi** della Stage 7 come *obiettivi narrativi*, senza dichiarare disponibili dieci stanze fisiche o un bunker scavato nel terreno. Se il gioco non supporta un accesso sotterraneo sicuro, preferiamo una base scenografica in superficie.

## Evidenze già recuperate

- **13 identificatori di strutture** riconosciuti in `mapgrouppos.xml` della fonte Bohemia Livonia fissata nel progetto. Sono **nomi di gruppi di mappa**, non la prova che possano essere generati dal nostro Object Spawner su console.
- Fra questi, due candidati associati all'HQ da esaminare: `Land_Mil_GuardHouse3` e `Land_Mil_Guardhouse1`. **Nessuna delle due classi è certificata spawnabile su PS5** in questo progetto.
- **14 modelli P3D di riferimento visivo** (catalogo terzo, Stage 4.11); per interni i riferimenti includono `Desk_Office` e `Desk_Globe`. Le path relative a `structures/...` e `structures_bliss/...` **non sono percorsi P3D direttamente autorizzati** dall'Object Spawner, e non equivalgono a nomi di classe spawnabili.
- **10 ambienti e 18 archi** nella Stage 7, con percorsi alternativi confermati solo nel grafo; nessuna quota Y reale.

Fonte primaria Bohemia: https://community.bistudio.com/wiki/DayZ:Object_Spawner . La documentazione consente classi di oggetti supportate e, come percorsi P3D diretti, solo le famiglie delle **piante e rocce** elencate nel wiki, non i percorsi arbitrari di strutture o arredo. Ricorda anche che tanti oggetti possono peggiorare le prestazioni.

## Regole per accettare un eventuale bunker

Per qualunque bunker selezionato sul server privato:

1. L'oggetto deve essere riconosciuto dalla versione PlayStation in uso e apparire davvero nel mondo dopo il restart.
2. **Almeno due uscite praticabili da verificare a piedi**: non basta un diagramma teorico. Nessuna uscita deve richiedere logout/login o sfruttare glitch.
3. Pavimenti, scale e porte devono essere attraversabili, senza punti che intrappolino i giocatori o linee di tiro invisibili.
4. Gli oggetti lasciati cadere devono restare accessibili e i contenitori/loot devono comportarsi come previsto anche dopo un restart normale.
5. Entrate, vie di fuga, collisioni e stabilità devono essere provate su PS5; il supporto PS4 va confermato a parte.
6. Se il test fallisce, **rollback** dei file missione modificati e dei riferimenti Object Spawner senza fare affidamento sul ritorno di salvataggi persi.

I file di progetto restano bloccati a `deployment_allowed=false`, con quote Y e classi di console sconosciute. Il programma **non** crea `Objects` da caricare in DayZ.

## Artefatti e verifica

`python scripts/build_stage8_feasibility.py` produce esclusivamente `dist/stage8_bunker_feasibility/feasibility_review.json`, un rapporto che incrocia:

- configurazione Stage 8, 13 nomi di gruppo ufficiali, 14 schede P3D non ufficiali;
- dossier bunker Stage 7 e fasi pilota ufficialmente concordate 1 → 3 → 5;
- obbligo di uscite normali, tutela degli oggetti e backup;
- impossibilità di trattare un esempio PC 1.16 come prova PS5.

`python scripts/test_stage8_feasibility.py` usa varianti di dati **sintetiche** per verificare che il sistema rifiuti falsi test PS5, geometrie inventate, classi/percorsi non confermati, scorciatoie sui test e layout dichiarati installabili.

Lo snapshot Recovery Kit contiene le sorgenti e questo rapporto. **Non comprende personaggi, basi, veicoli o salvataggi Nitrado.**

## Prossimo punto di decisione

Quando Franco attiverà Nitrado: test server vanilla e versione → copie originali → Stage 1–3 separati → sopralluogo dell'HQ → singola classe a basso rischio → 1→3→5 props con osservazione reale. Un bunker sotterraneo rimane fuori dalla prima installazione fino a prova di fattibilità e sicurezza.
