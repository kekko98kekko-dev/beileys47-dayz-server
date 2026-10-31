# Piano di messa online — DayZ PS5 (Nitrado)

**Aggiornamento 31/10/2026:** Nitrado PlayStation acquistato, Livonia raggiungibile da PS5. Il resto della guida è una procedura preparata *prima dell'acquisto*; i pacchetti Stage 1–9 non sono ancora installati. Vedi [LIVE_ACTIVATION_2026-10-31.md](LIVE_ACTIVATION_2026-10-31.md). Nessun caricamento automatico o modifica live autorizzata.

## Prima dell'acquisto
- Confermare sul sito Nitrado **PlayStation** (NON PC), mappa Livonia, 10 posti, prezzo in euro, opzione prepagata e rinnovo automatico disattivato.
- Il repository pubblico GitHub non deve contenere token Nitrado, cookie, password o log con dati privati.
- I pacchetti generati in GitHub Actions sono **anteprime**; il supporto delle funzioni nella versione console va collaudato.

## Preflight gratuito prima di Nitrado

La pipeline ora crea **dist/stage2/nitrado_dry_run_plan.json** e lo inserisce nell'archivio di recupero. Questo documento elenca esattamente i quattro file XML/JSON della Stage 2, con percorso relativo, dimensioni e SHA-256, oltre alle verifiche necessarie prima di una futura installazione.

Il piano mantiene **ready_to_deploy = false** e **server_mission_root = null**: nessuno conosce ancora il percorso reale del server, la versione installata o le autorizzazioni del servizio. **Non esegue richieste API, FTP, caricamenti, riavvii o eliminazioni**.

### Prima di un futuro collegamento GitHub → Nitrado

- Verificare con l'account PlayStation attivo se API, file manager o altro metodo siano disponibili e consentano modifiche ai file.
- Recuperare il percorso reale della missione, senza dedurlo dal template.
- Fare copie dei quattro file reali già presenti prima di sostituirli, e registrare hash/versione.
- Utilizzare segreti privati e una conferma esplicita per qualunque futura operazione live.
- Implementare rollback controllato e test con Stage 1 prima di automatizzare Stage 2.

## Protocollo Franco → avvio: sequenza prioritaria per il primo giorno

**Stato:** preparato in anticipo, NESSUNA operazione ancora eseguita su Nitrado o PS5. Il primo obiettivo è verificare che il noleggio e i file di missione siano utilizzabili, non costruire subito ZONA 47.

| Priorità | Verifica | Prova richiesta | Esito per avanzare |
| --- | --- | --- | --- |
| P0 | Ordine corretto: DayZ PlayStation (PS4/PS5), 10 slot o piano concordato, prepagato, regione Europa | Riepilogo del pannello senza dati di pagamento | Confermare piano e scadenza |
| P1 | Server acceso, mappa Livonia, IP/porta e nome server | Schermata pannello con credenziali oscurate | Server raggiungibile |
| P2 | Connessione PS5 vanilla da lista Community | Conferma accesso e spawn in gioco | Accesso completato senza errori |
| P3 | Versione del gioco, missione reale e file manager | Screenshot del percorso `dayzOffline.enoch`, versione visibile e file elencati | Nessuna differenza incompatibile |
| P4 | Possibilità di ripristino e copia privata dei file originali | Elenco backup effettivamente presenti + copie file disponibili | Esiste un piano di rollback credibile |
| P5 | Test Stage 1, poi Stage 2, poi Stage 3 | Risultati separati per fase e uno o più riavvii | Ogni fase passa prima della successiva |
| P6 | ZONA 47: sito reale, quote Y, modelli supportati, 1→3→5 oggetti | Evidenza di gioco e dati di rilevamento privati | **Bloccato** finché manca la prova sul campo |

**Nessun caricamento automatico** di ZIP, Recovery Kit, Stage 3 completo o materiali Stage 4. Si estrae il singolo file appropriato e lo si confronta con l'originale prima di ogni intervento autorizzato.

### Cosa inviare ad Alfred al primo accesso

Una schermata della **pagina principale del server** e, quando disponibile, una del **file manager** che mostri la missione. Oscurare login, password, token, email personali, dettagli di pagamento e qualsiasi credenziale; non pubblicare backup con dati dei giocatori. Le schermate di IP/porta possono essere condivise privatamente, ma non in un repository pubblico.

Da lì posso verificare i percorsi e preparare la modifica esatta, oppure operare con strumenti compatibili quando disponibili e autorizzati. **Non presumere che io possa controllare direttamente Nitrado** finché il pannello e gli accessi non sono stati verificati.

### Criteri di arresto immediato

- Il server acquistato è PC/Xbox invece di PlayStation, o Livonia non è selezionabile.
- Il server vanilla non è raggiungibile dalla PS5.
- Il file manager/missione differisce da quanto previsto oppure non permette copia dei file necessari.
- La versione DayZ in esecuzione è diversa da quella verificata con la baseline ufficiale senza revisione dei cambiamenti.
- Mancano copie degli originali o una possibilità documentata di rollback per una modifica rischiosa.
- La prova produce errori, instabilità, perdita di inventario o problemi di persistenza.

In tutti questi casi **non caricare altre configurazioni**; conservare lo stato e diagnosticare prima di proseguire.

### Come usare bene un noleggio breve

**Sessione 1:** confermare piattaforma, server vanilla, mappa e accesso PS5. Poi verificare versioni, file manager e backup. Se uno dei primi controlli fallisce, usare il tempo restante per diagnosticare anziché installare file.

**Sessione 2:** introdurre e verificare Stage 1, Stage 2 e Stage 3 in sequenza, senza saltare le verifiche e tornando alla versione precedente se emerge un problema.

**Sessione 3:** consolidare evidenze e risultati; se possibile fare una ricognizione **non invasiva** del sito di ZONA 47 per valutare accessibilità e ostacoli. Non pretendere che tutte le 26 strutture siano operative dopo una sola prova.

Prima della scadenza, salvare separatamente la configurazione effettiva e i file Nitrado che il provider consente di esportare. Il nostro Recovery Kit GitHub conserva sorgenti e anteprime, **non** i dati persistenti live (personaggi, veicoli, basi, contenitori). Alla scadenza non presumere di poter recuperare questi ultimi.

## Primo accesso
1. Entrare nel pannello Nitrado con 2FA.
2. Selezionare Livonia e un nome riconoscibile come `BEILEYS47 | DAYZ ITALIA | SURVIVAL WAR`.
3. Attivare inizialmente una password temporanea, **mai condivisa nel repository GitHub**.
4. Verificare che da PS5 il server sia visibile nella lista Community.
5. Lasciare il server alle impostazioni originali e verificare che parta regolarmente.

## Prevenzione perdita loot

**Prima di ogni modifica** fare una copia dei file di missione modificabili e verificare che nel pannello esistano backup automatici del server. La guida ufficiale Nitrado dice che i backup sono creati approssimativamente ogni 24 ore e, per DayZ console, **non è possibile richiedere backup manuali via FTP**: non trattare quindi un backup del mondo appena creato come garantito.

Per interventi importanti:
- non effettuare modifiche con giocatori online;
- annotare data/ora, file da modificare e valore originale;
- evitare di caricare file di una versione DayZ diversa;
- modificare un file per volta, evitando di sovrascrivere file extra;
- non modificare né cancellare per errore la cartella dello storage persistente;
- verificare la persistenza di casse, base e veicoli dopo i normali riavvii;
- NON promettere indennizzi automatici o zero bug.

## Percorsi previsti
Missione PlayStation: `dayzps_missions/dayzOffline.enoch/`. **Verificare il percorso reale nel pannello**: non dare per scontato che ogni account mostri lo stesso albero di cartelle.

Pacchetto Stage 2:
- `db/types.xml`
- `cfgplayerspawnpoints.xml`
- `cfgspawnabletypes.xml`
- `cfggameplay.json`

La relazione `change_report.json` NON va copiata nella missione.

**IMPORTANTE:** `cfggameplay.json` richiede `enableCfgGameplayFile = 1`, che si imposta nel pannello Nitrado (controllarne l'effettiva disponibilità su console).

## Eventuali test Stage 3

Stage 3 e' una preview separata, con due file aggiuntivi: db/events.xml e db/messages.xml. Il piano statico Nitrado attuale descrive soltanto Stage 2. Dopo aver collaudato Stage 1 e Stage 2, verificare copia dei file originali, numero reale degli eventi, log, FPS e apparizione dei messaggi. Nessun caricamento o aggiornamento live e' attualmente autorizzato.

## Smoke test su PS5
- [ ] Server accessibile da lista Community.
- [ ] Spawn su Brena, Sobotka o Kolembrody al nuovo personaggio (ripetere più volte).
- [ ] Kit medici e cibo ottenibili senza saturare la mappa (test non istantaneo).
- [ ] MP5K / SKS / munizioni: presenza coerente con la progressione.
- [ ] Un veicolo spawnato possiede le componenti previste, senza lag vistoso.
- [ ] Stamina effettivamente diversa solo dopo aver abilitato gameplay JSON.
- [ ] Una cassa in superficie conserva posizione e contenuto dopo un riavvio.
- [ ] Un nascondiglio sepolto conserva il contenuto dopo un riavvio.
- [ ] Dopo gli aggiornamenti DayZ, nessuna perdita di compatibilità XML/JSON.

## Riavvii
Non attivare automaticamente un calendario di restart senza aver collaudato il metodo.
La documentazione Nitrado per DayZ avverte che alcune opzioni di **riavvio automatico** possono creare problemi di inventario o avvio e consiglia, per quel flusso, l'uso di `messages.xml` per uno spegnimento ordinato seguito da un task di avvio. Verificare come si comporta sulla specifica offerta PlayStation prima di sceglierlo.

## Recupero
1. Non continuare a modificare file in presenza di anomalie.
2. Arrestare il server da pannello.
3. Ripristinare i file originali conservati oppure usare un backup Nitrado precedente al guasto (se effettivamente disponibile).
4. Attenzione: un ripristino globale del mondo può cancellare progressi successivi alla data del backup.
5. Riavviare, verificare da console e documentare l'esito.

## Quello che NON abbiamo
- Nitrado acquistato e accesso PS5 vanilla confermato; nessun collegamento API/FTP per il deploy collaudato.
- Nessuna distribuzione automatica attiva da GitHub.
- Accesso vanilla PS5 verificato; nessuna prova live delle Stage 1–9, nessuna garanzia di assenza bug/lag.
- Nessuna pianificazione effettiva dei raid a orari prestabiliti.

## Guide ufficiali
- Backup DayZ: https://server.nitrado.net/it-IT/guides/ripristino-backup-su-dayz-it
- Server messages DayZ: https://server.nitrado.net/en-US/guides/server-messages-for-dayz
- Ricerca del server console: https://server.nitrado.net/guides/connecting-to-a-nitrado-dayz-server-console-en
- Gameplay settings: https://community.bistudio.com/wiki/DayZ:Gameplay_Settings
