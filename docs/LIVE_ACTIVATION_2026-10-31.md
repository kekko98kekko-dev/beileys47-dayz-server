# BEILEYS47 — Attivazione Nitrado e test console (31 ottobre 2026)

**Stato reale verificato con utente e pannello:** noleggio DayZ **PlayStation**, **10 slot**, **Livonia / `dayzOffline.enoch`**, server raggiungibile con successo dalla **PS5** e nome personalizzato `BEILEYS47 | DAYZ SURVIVAL WAR | LIVONIA | NO WIPE`. L'utente riferisce di aver esportato le impostazioni generali e di aver effettuato un riavvio ordinario. Queste prove dimostrano solo l'accesso iniziale alla missione originale, **non** che la configurazione Stage 1/2/3 sia stata installata. IP, credenziali, FTP, personaggi e altri dati sensibili NON devono essere aggiunti qui.

## Stato delle verifiche (non promuovere senza evidenza)

| Prova | Esito |
|---|---|
| Servizio attivo PlayStation / Livonia / 10 slot | CONFERMATO dal pannello |
| Nome e descrizione custom | CONFERMATI dal pannello |
| Accesso Community da PS5 e ingresso in mondo | CONFERMATO dall'utente |
| Impostazione `wipe_on_next_restart` | OFF, letta nelle impostazioni |
| Impostazione `resetmission` | OFF, letta nelle impostazioni |
| Export impostazioni generali | ESEGUITO secondo l'utente; copia e integrità non ispezionate |
| Versione binaria server DayZ | NON VERIFICATA; campo versione mostrato vuoto |
| Mission root effettivo e file originali | NON ANCORA ISPEZIONATI / SCARICATI |
| Backup ripristinabile Nitrado pre-deploy | NON VERIFICATO |
| Persistenza inventario, base, oggetti dopo restart | NON TESTATA |
| Stage 1/2/3 installati | NO |
| Stage 4 ZONA 47, struttura HQ o bunker costruiti | NO; materiali di progettazione non deployabili |

## Prossima azione: baseline **senza alcuna modifica live**

1. Lasciare il server attivo per un test PS5 **vanilla**. Verificare movimento, interazione con un oggetto, inventario e uscita/riconnessione. Annotare solo gli esiti, senza diffondere password o identificativi PSN privati.
2. Da **Strumenti → Filebrowser** nel pannello Nitrado, verificare il percorso reale `dayzps_missions/dayzOffline.enoch/` (non supporlo finché non è visibile), i file `db/types.xml`, `cfgplayerspawnpoints.xml`, `cfgspawnabletypes.xml`, `cfggameplay.json`, `db/events.xml`, `db/messages.xml`. I file di missione effettivi potrebbero differire dalla release ufficiale.
3. **Scaricare gli originali** dei file destinati al prossimo test e conservarli **privatamente** sul PC in una cartella `BEILEYS47/vanilla-2026-10-31/`. Annotare dimensioni e hash SHA-256; non caricare originali contenenti dati riservati nel repository pubblico.
4. Da **Strumenti → Ripristina backup**, **solo leggere l'elenco dei backup esistenti**. NON premere ripristina. Una copia Nitrado è distinta dall'export impostazioni e dal kit GitHub, e potrebbe mancare al primo giorno.
5. Confrontare versione e contenuto reali dei file con quelli del pacchetto Stage 1 derivato dalla baseline Bohemia ufficiale. Se versione o missione divergono, **STOP** prima di qualsiasi upload.
6. Per proteggere la persistenza senza wipe, verificare se un contenitore o item test rimane dopo un riavvio normale; **non** attivare `wipe_on_next_restart` o `resetmission`. Una singola prova non dimostra persistenza illimitata.

## Installazioni: un esperimento per volta

- **Stage 1**, solo dopo baseline/rollback: sostituzione sorvegliata di **`db/types.xml`** e **`cfgplayerspawnpoints.xml`**. Validare ciascun originale e la provenienza della sua controparte. Prima interrompere l'accesso dei giocatori, arrestare normalmente il server, attendere circa 3–5 minuti, sostituire soltanto i file approvati nel percorso reale, avviare, entrare da PS5, testare loot nel tempo e spawn di **nuovi** personaggi (non eliminare personaggi esistenti solo per il test). In caso di errori, ripristinare **esattamente** gli XML originali.
- **Stage 2**, solo dopo Stage 1 superato: `cfgspawnabletypes.xml` e `cfggameplay.json` più i file Stage 1 identici verificati. Abilitare `enableCfgGameplayFile` nel pannello **soltanto dopo aver ispezionato il JSON**: questa opzione può sovrascrivere impostazioni di danni alle basi, illuminazione e altro. Misurare stamina, veicoli e persistenza.
- **Stage 3**, solo dopo Stage 2 superato: `db/events.xml` e `db/messages.xml`. Confermare elicotteri/convogli e messaggi nel gioco, non solo sintassi; evitare moltiplicatori eccessivi.
- **Stage 4 / ZONA 47**, protocollo indipendente **1 → 3 → 5 piccoli oggetti**, solo dopo sopralluogo con coordinate X/Z/Y reali, classname effettivamente spawnabile su PS5, collisioni, uscite e FPS. **Non** caricare i file di progetto, le 26 posizioni schematiche, il bunker o `Land_` ipotetici come se fossero pronti.
- **Stage 5–9** hanno report di progettazione, non funzioni installate. Il server non può essere dichiarato definitivo soltanto con test statici CI.

## No-wipe e ciclo di vita degli oggetti

- Nessun wipe programmato è una **politica del server**: non promette assenza di reset eccezionali per bug, aggiornamenti o interventi provider.
- `serverTimePersistent` in Generale preserva l'**orario del mondo**: **non** è l'interruttore che rende persistenti casse, basi o personaggi.
- Non impostare il `lifetime` di ogni oggetto a valori enormi. Tenere cleanup normale per vestiti e spazzatura; allungare selettivamente gli oggetti sensati solo dopo aver studiato `types.xml` attuale, i flag pertinenti e l'impatto sull'economia centrale.
- Non aumentare brutalmente zombies, veicoli e oggetti fisici: 10 slot non prova da solo la capacità del mondo di gestire migliaia di entità.

## Recupero e scadenza

- Il **Recovery Snapshot GitHub** salva il progetto e i file missione di prova: **non** salva automaticamente il mondo Nitrado.
- Export impostazioni Nitrado e copia degli XML originali / live vanno conservati **separatamente** e in privato.
- La dashboard mostrava scadenza **30 novembre 2026 10:56 ora italiana**. Il promemoria è **28 novembre 2026 10:56**. Verificare che il prepagato non sia stato convertito a rinnovo.
- Per eventuali dati di persistenza (personaggi, auto, basi), chiedere esplicitamente al supporto Nitrado se sia possibile conservare o migrare il mondo **console** prima della scadenza; **non garantire** download FTP di un backup completo né restore su un contratto futuro.

## Riferimenti

- Nitrado: https://server.nitrado.net/en-US/guides/editing-xml-files-manually-with-dayz-console-en/
- DayZ CE: https://github.com/BohemiaInteractive/DayZ-Central-Economy/releases/tag/DZ_130
- Installazione e rollback storico: [OPERATIONS.md](OPERATIONS.md)
- Pre-purchase mission review: [PREPURCHASE_MASTER.md](PREPURCHASE_MASTER.md)
- Stage 4.13: [STAGE4_13_CONSOLE_PILOT.md](STAGE4_13_CONSOLE_PILOT.md)
