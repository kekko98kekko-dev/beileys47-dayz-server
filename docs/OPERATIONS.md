# Piano di messa online — DayZ PS5 (Nitrado)

**Non acquistato. Non esiste un server attivo. Questo documento non autorizza modifiche live.**

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
- Nitrado non acquistato e nessun collegamento API/FTP collaudato.
- Nessuna distribuzione automatica attiva da GitHub.
- Nessuna prova reale DayZ PS5 e nessuna garanzia di assenza bug/lag.
- Nessuna pianificazione effettiva dei raid a orari prestabiliti.

## Guide ufficiali
- Backup DayZ: https://server.nitrado.net/it-IT/guides/ripristino-backup-su-dayz-it
- Server messages DayZ: https://server.nitrado.net/en-US/guides/server-messages-for-dayz
- Ricerca del server console: https://server.nitrado.net/guides/connecting-to-a-nitrado-dayz-server-console-en
- Gameplay settings: https://community.bistudio.com/wiki/DayZ:Gameplay_Settings
