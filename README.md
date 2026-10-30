# BEILEYS47 | DAYZ SURVIVAL WAR

Progetto di configurazione per **DayZ PlayStation (PS4/PS5)**, mappa **Livonia**, server community da **10 slot**.

**Stato:** progettazione e controlli preliminari. **Non abbiamo acquistato Nitrado, né configurato un deploy automatico.**

## Obiettivo

Un survival con **PvP frequente**, loot aumentato in modo selettivo, veicoli accessibili e progressione significativa. Le casse e le basi devono mantenere i dati ai riavvii ordinari, entro le regole di persistenza impostate. Nessuno può garantire zero bug o zero lag.

## Struttura

- `config/profile.json`: specifiche e obiettivi di bilanciamento; **non è un file caricabile su DayZ**.
- `mission/`: destinazione dei veri file di missione DayZ (non presenti finché non li recuperiamo da una versione compatibile).
- `scripts/validate.py`: verifica sintassi XML/JSON e valori del profilo.
- `.github/workflows/validate.yml`: controlli gratuiti su GitHub Actions; **nessun caricamento su Nitrado**.
- `NEXT_STEPS.md`: piano operativo e verifica prerequisiti.

## Funzioni previste

1. Missione Livonia; compatibilità PS4/PS5 (console, non mod PC).
2. PvP sempre attivo, spawn e hotspot progettati con cautela.
3. Aumento **selettivo** di cibo/medicinali e loot, non moltiplicatori ciechi per ogni oggetto.
4. Bilanciamento auto, parti di ricambio e munizioni.
5. Impostazioni di stamina/notte e danni alle strutture solo se realmente supportate.
6. Backup e test di persistenza prima dell'apertura al pubblico.

## Come testare i file

```sh
python3 scripts/validate.py
```

Al momento il test controlla `config/profile.json`. Quando aggiungeremo XML/JSON reali in `mission/`, controllerà anche **la loro sintassi e alcune incoerenze elementari**. Un test superato non dimostra che DayZ li carichi o che il gameplay sia bilanciato.

## Sicurezza e costi

- Il repository è **pubblico**: NON inserirvi password, token, FTP/API key, dati privati o file di backup con segreti.
- GitHub Actions sui runner standard per repository pubblici non consuma la quota dei 2.000 minuti dei repository privati, nel rispetto delle condizioni GitHub.
- Nessuna modifica sarà inviata automaticamente al server finché non avremo collaudato un metodo autorizzato e sicuro.
- **Non spendere per Nitrado** finché le attività preliminari non sono complete e il prezzo non è confermato.


## Stage 2 — Anteprima survival/PvP già generabile

✅ GitHub Actions costruisce anche una Stage 2 che include tutte le modifiche Stage 1, più:
- equipaggiamento PvP di fascia intermedia e materiali di riparazione;
- maggior probabilità di componenti base su due modelli di auto, senza aumentare il numero dei veicoli;
- durata obiettivo di 21 giorni per `UndergroundStash`, senza cambiare la durata di 45 giorni delle casse `WoodenCrate`;
- stamina leggermente aumentata e minore penalità del peso;
- test automatici di regressione e controllo di sicurezza del pacchetto ZIP.

I pacchetti si trovano sotto **Actions → ultima esecuzione riuscita → Artifacts**. Scaricare `beileys47-livonia-stage2-preview`.

[Configurazione Stage 2](docs/STAGE2.md) · [Checklist Nitrado e recupero](docs/OPERATIONS.md)

**Anteprima verificata sintatticamente, NON testata su PS5 e NON distribuita su Nitrado.**

## Stage 1 — Anteprima già generabile

✅ Il builder GitHub Actions crea automaticamente due veri XML per **Livonia**, usando un commit ufficiale Bohemia del 16 ottobre 2026:
- `db/types.xml` — maggior disponibilità di 8 tipi di cibo/medicinali;
- `cfgplayerspawnpoints.xml` — spawn iniziali concentrati in Brena, Sobotka e Kolembrody.

Il pacchetto rimane nella sezione **Actions → ultimo workflow riuscito → Artifacts → beileys47-livonia-stage1-preview**.

[Leggi la configurazione Stage 1](docs/STAGE1.md)

**Non installare ancora questi file su un server reale senza backup e verifica della versione.** Il workflow non distribuisce nulla a Nitrado.

## Riferimenti tecnici

- [Bohemia Interactive: DayZ Central Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy)
- [Bohemia Interactive: Gameplay Settings](https://community.bistudio.com/wiki/DayZ:Gameplay_Settings)
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)


## Stage 4 — ZONA 47: the signature outpost (DESIGN ONLY)

A versioned tactical design for a believable ruined military outpost: **8 distinct sectors, 3 access routes and 26 symbolic placements**, with automated route redundancy and object-budget checks. GitHub Actions generates a schematic SVG and a **non-installable design-only ZIP**.

**It does not contain valid DayZ world coordinates, class names, real object spawns, mission-file changes or console FPS benchmarks.** A safe, grounded PS4/PS5 map-site and asset survey must precede implementation.

[ZONA 47 design guide](docs/STAGE4_ZONE47.md) · [PS4/PS5 testing protocol](docs/ZONE47_QA_PROTOCOL.md) · [GitHub Actions](../../actions)

The Stage 4 concept also includes a **13-class candidate asset shortlist**, a blank 26-placement survey worksheet and a guarded **offline-only** Object Spawner exporter. The exporter refuses incomplete surveys; CI tests use and discard synthetic positions. No game-world coordinates or unverified objects are claimed as ready.

## Stage 3 — Survival War Encounter Identity (preview)

Stage 3 mantiene **identici** tutti i file Stage 2 e aggiunge:
- maggiore target di due eventi vanilla: elicotteri precipitati e convogli militari (3 → 4); adegua solo il limite del tipo elicottero specifico;
- tre messaggi in italiano: benvenuto, suggerimenti survival e regole PvP, **senza shutdown**;
- audit statico indipendente e archivio ZIP Stage 3 su GitHub Actions.

**Non crea missioni automatiche, mappe personalizzate o nuovi edifici.** Eventi e annunci vanno testati sulla console PlayStation.

[Stage 3: progettazione, limiti e test](docs/STAGE3.md)

## Recupero offline e nuova verifica Stage 2

✅ La pipeline controlla ora l'**intero contenuto** dei quattro file Stage 2 confrontandoli con la baseline Bohemia e applicando indipendentemente solo le variazioni consentite dalle regole JSON. Le verifiche automatiche non sostituiscono prove su PlayStation.

✅ Dopo ogni build riuscita GitHub Actions genera anche l'artifact **beileys47-recovery-kit**, al cui interno si trova **beileys47-recovery-kit.zip**. Contiene scripts, regole, documentazione, preview Stage 1/2/3, rapporti e manifest SHA-256. I tre artifact sono conservati per 90 giorni (salvo limiti delle impostazioni repository); **non** sono backup permanenti.

**Non contiene** personaggi, basi, auto, casse né dati persistenti del server Nitrado. Prima della scadenza Nitrado, scaricare lo ZIP sul proprio PC (ideale 48 ore prima) e salvare i file live separatamente se accessibili.

[Guida al recupero sul PC Windows](docs/RECOVERY_KIT.md) · [GitHub Actions](../../actions)

**Nessun deployment GitHub → Nitrado attivo.** È ancora obbligatorio verificare la versione del server, fare copie dei file originali e collaudare Stage 1 e Stage 2 su PS5/PS4.


## Preflight Nitrado in sola lettura

✅ Il nuovo script **scripts/plan_nitrado.py** genera un piano JSON di installazione dalla preview Stage 2 verificata: quattro file attesi, dimensioni, hash SHA-256, percorsi **relativi** e checklist delle condizioni mancanti. Il piano viene allegato allo ZIP di recupero.

**Non è un deploy**: non richiede credenziali, non parla con Nitrado, non legge dati live e non sa dove risiede la missione del futuro server. L'indicatore **ready_to_deploy** resta sempre false. Il percorso reale e le API PlayStation andranno verificati solo dopo un acquisto autorizzato.

[Procedura di preflight e installazione](docs/OPERATIONS.md)
