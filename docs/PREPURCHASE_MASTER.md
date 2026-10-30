# BEILEYS47 — Master kit pre-acquisto DayZ Livonia PS5

**È una consegna revisionabile, NON una configurazione provata su console.**

## Cosa abbiamo completato senza acquistare Nitrado

- File di missione Stage 1, Stage 2 e Stage 3 generati con modifiche ristrette a una base ufficiale Bohemia DayZ CE 1.30 **ancorata a un commit specifico**.
- Controlli automatici per sei file Stage 3; digest SHA-256 di ogni file; pacchetto leggibile con istruzioni, senza percorsi assoluti Nitrado né credenziali.
- Documentazione e sistemi di verifica ZONA 47 fino alla Stage 4.13, con moduli vuoti e controlli che bloccano affermazioni di collaudo non effettuato.
- Procedure di backup, ripristino e prova per fasi in console.

**Niente è stato ancora eseguito su DayZ PS5/PS4. Nessun backup Nitrado esiste in nostro possesso.**

## Il pacchetto pratico di missione

La pipeline genera:

`dist/prepurchase/beileys47-livonia-mission-review-candidate.zip`

Contiene un manifesto e i seguenti **sei file in `MISSION_FILES_REVIEW_ONLY/dayzOffline.enoch/`**:

| Percorso missione | Scopo |
|---|---|
| `db/types.xml` | Loot e persistenza oggetti |
| `cfgplayerspawnpoints.xml` | Spawn iniziali |
| `cfgspawnabletypes.xml` | Componenti veicoli |
| `cfggameplay.json` | Parametri gameplay, abilitarli solo dopo controllo impostazioni Nitrado |
| `db/events.xml` | Eventi dinamici selezionati |
| `db/messages.xml` | Messaggi della community senza countdown di spegnimento |

Lo ZIP serve per **ispezionare ed estrarre** i singoli file. Non è un modpack né si carica sul server come archivio. Per la prova reale si procede **Stage 1 → Stage 2 → Stage 3** e si modificano soltanto i percorsi della fase corrente. In particolare, non si prendono tutti e sei i file del pacchetto Stage 3 e si copiano a server nuovo come prima operazione.

I file non includono **alcun Object Spawner ZONA 47**. Il builder verifica che `WorldsData.objectSpawnersArr` sia una lista vuota. Non vengono distribuite coordinate Y inventate, classi `Land_...` mai verificate o modelli P3D come se fossero classi di oggetti PlayStation.

## Gate acquisto: autorizzato un noleggio di prova, NON il lancio pubblico

**Stato: TEST_RENTAL_PERMITTED / LIVE_DEPLOYMENT_BLOCKED.** Una pipeline GitHub verde dimostra solo che i file sono coerenti. Per imparare la configurazione Nitrado è ragionevole noleggiare il minimo per pochi giorni, ma nessun server è stato finora collaudato su PS5.

Configurazione da controllare prima del pagamento:

- Gioco: **DayZ**; piattaforma di hosting: **PlayStation 4** (DayZ viene eseguito su PS5 per retrocompatibilità), mai PC o Xbox.
- Numero giocatori: **10 slot** per la prova; aumentabili successivamente se il progetto funziona.
- Durata: **3 giorni prepagati**, se offerti al checkout effettivo; non sottoscrivere rinnovi automatici per questo primo test.
- Data center: **Francoforte (Europa)** come prima preferenza dalla Campania, verificando la latenza nell'offerta.
- Mappa **Livonia** da confermare nel pannello dopo l'attivazione; non presupporre che il server parta automaticamente sulla mappa richiesta.
- Accesso con password privata; server non pubblicizzato fino a superamento Stage 1–3 e dei test PS5.
- Conservare ricevuta, schermata della configurazione e indirizzo del pannello senza pubblicare credenziali.

**Condizioni economiche:** l'importo esatto dipende da piattaforma, durata, checkout, imposte e offerte attive. Nitrado indica che i noleggi di tre giorni **non sono rimborsabili** e che il prepagato termina senza rinnovo; controllare il riepilogo prima del pagamento. Un test di tre giorni non garantisce abbastanza tempo per certificare tutta ZONA 47: serve prima come verifica vanilla/Stage 1–3. Fonte condizioni: https://server.nitrado.net/pages/agb e https://server.nitrado.net/it-IT/support.

**Dopo l'acquisto:** verificare prima accesso PS5 e salvataggi vanilla, disponibilità di backup Nitrado e download dei singoli file missione. Se il pannello nega i permessi necessari, la missione è differente oppure la versione corrente non coincide con la baseline esaminata, **interrompere l'installazione** e non forzare XML/JSON. Il Recovery Kit GitHub conserva le configurazioni, **non** i salvataggi del mondo Nitrado; dopo scadenza del noleggio non presumere che personaggi, basi, veicoli e persistenza possano essere recuperati.

## Cosa faremo quando sarà acquistato il server

1. Nel pannello Nitrado, verificare piattaforma PlayStation, missione **Livonia / dayzOffline.enoch**, numero slot e versione effettiva. Non usare il percorso missione presunto senza controllare il file manager.
2. Avviare il server **vanilla** con una password privata, controllare che compaia nella lista Community e che una PS5 riesca a entrare. Prima di qualsiasi sostituzione, scaricare una copia locale dei file originali.
3. Controllare in **Tools → Restore Backup** che sia effettivamente presente un backup precedente ai test. La guida Nitrado specifica backup automatici ogni 24 ore e nessuna possibilità di creare un backup completo manualmente via FTP su console. Un ripristino potrebbe cambiare indirizzo IP e far perdere progressi successivi.
4. **Fermare** il server per la manutenzione: Nitrado suggerisce di fermarlo 3–5 minuti prima di modificare le impostazioni. Testare Stage 1, osservando spawn e presenza dei file modificati senza giocatori di terzi online.
5. Se Stage 1 va bene, modificare esclusivamente i file Stage 2 pertinenti. Per `cfggameplay.json`, assicurarsi che `enableCfgGameplayFile` sia attivo in **Settings → General**; verificare effetti in gioco e persistenza dopo riavvio.
6. Solo dopo la verifica del gameplay, passare alla Stage 3: eventi e messaggi, uno alla volta e con possibilità di ripristinare i file precedenti.
7. Solo dopo, affrontare ZONA 47: misurare **Y reali**, confermare le classi spawnabili, verificare le collisioni sul sito; applicare il protocollo 1 → 3 → 5 della Stage 4.13. Non abilitare automaticamente nessuna delle 26 posizioni di progetto.

Al termine di ogni fase, verificare accesso da PS5, loot e spawn ragionevoli, eventi, assenza di nuovi problemi e conservazione di un contenitore/veicolo dopo riavvio. La verifica su PS4 va eseguita a parte.

## Materiali per il recupero

- `beileys47-livonia-mission-review-candidate.zip`: *soltanto* i sei file Stage 3, la documentazione e gli hash.
- `beileys47-recovery-kit.zip`: backup più completo dei sorgenti, file di riferimento e rapporti.
- Il repository GitHub conserva tutte le revisioni dei file, indipendentemente dalla durata degli artifact Actions.
- Nitrado conserva i propri backup del server, disponibili solo secondo la sua politica: **non** equivalgono al Recovery Kit GitHub e non includiamo alcuna copia reale di tali backup.

## Cosa impedisce di dire «server definitivo»

Non sono ancora disponibili: quote Y fisiche della posizione X 9000/Z 7800, un modello spawner effettivamente accettato da PS5, log e verifiche in gioco, collisioni/percorsi nell'avamposto, performance reali con giocatori, compatibilità con eventuali futuri aggiornamenti DayZ, prova di restaurabilità dei salvataggi. Una suite Python verde non sostituisce questi dati.

Inoltre è bene preservare la possibilità di **abbandonare la prima posizione** e sceglierne un'altra se il terreno non permette di costruire un avamposto divertente e senza blocchi.

## Fonti

- Bohemia: https://community.bistudio.com/wiki/DayZ:Gameplay_Settings
- Bohemia: https://community.bistudio.com/wiki/DayZ:Object_Spawner
- Nitrado: https://server.nitrado.net/en-US/guides/settings-dayz-console/
- Nitrado: https://server.nitrado.net/en-US/guides/backup%20restore%20on%20dayz

**Stato del pacchetto: `ready_to_deploy=false`. Spesa: 0 €.**
