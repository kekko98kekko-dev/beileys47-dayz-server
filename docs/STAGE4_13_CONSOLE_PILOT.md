# Stage 4.13 — Collaudo progressivo PS5: 1 → 3 → 5 oggetti

**Stato effettivo: protocollo e controlli automatici pronti, ZERO prove reali sul server.** Nessuna quota Y, classe console, collisione, prestazione, backup Nitrado o sessione PlayStation è stata verificata in questa fase.

## Perché non passiamo direttamente ai 26 oggetti

Gli Object Spawner DayZ caricano gli oggetti al lancio della missione e Bohemia avverte che l'uso di molti oggetti può peggiorare le prestazioni di server e client. Inoltre `cfggameplay.json` deve essere attivo; la chiave `objectSpawnersArr` indica i file JSON della missione da leggere. Fonti ufficiali: [Object Spawner](https://community.bistudio.com/wiki/DayZ:Object_Spawner) e [Gameplay Settings](https://community.bistudio.com/wiki/DayZ:Gameplay_Settings).

Su PlayStation non possiamo installare mod o eseguire il nostro esempio di script PC `SurfaceY` direttamente dentro Nitrado. I nomi P3D delle fasi precedenti non sono un'autorizzazione a usare le path `structures/*` nello spawner. Questo protocollo **non produce file da installare**.

## Prima di iniziare: sicurezza del server e dei salvataggi

Nitrado documenta che i backup DayZ completi vengono creati automaticamente **circa ogni 24 ore**, senza possibilità di forzarne manualmente uno attraverso FTP su console. Sono visibili nella sezione **Tools → Restore Backup**, dove si deve controllare l'esistenza di un backup **precedente al test**. Il suo ripristino è un'operazione che può riportare indietro i dati del mondo e, secondo Nitrado, **può modificare l'IP del server**. Non avviare mai un ripristino senza verificare l'impatto sulla persistenza e sui giocatori. Fonte: [Nitrado — Backup Restore on DayZ](https://server.nitrado.net/en-US/guides/backup%20restore%20on%20dayz).

La procedura blocca la sperimentazione senza conferma da parte del proprietario, mappa attiva `dayzOffline.enoch`, versione di gioco coerente, una copia **esterna al server** dei file di configurazione che verranno modificati, un backup Nitrado verificato visivamente, una strada di ripristino compresa e protezione degli eventuali giocatori. Copiare singoli file di configurazione non è equivalente a salvare la persistenza completa del mondo.

## Sequenza dei collaudi

| Passo | Elementi simbolici | Cosa verificare |
|---|---|---|
| **P1 — 1 elemento** | `checkpoint_01` | Comparsa effettiva e posizione con quota reale, collisione, accesso e stabilità dopo **due riavvii** osservati |
| **P3 — 3 elementi** | P1 + `woods_01`, `service_01` | Compatibilità fra gli oggetti, passaggi e visuali praticabili, assenza di crash e stuttering inaccettabile |
| **P5 — 5 elementi** | P3 + `logistics_02`, `hq_02` | Compatibilità, impatto percepito e continuità del gameplay, possibilità di uscire senza restare incastrati, funzionamento dopo riavvio |

Questi sono **marker del progetto** e non nomi di classi confermate. Non usare le classi immaginate dai test, le quote Y sintetiche o i percorsi P3D del catalogo. Ogni oggetto reale richiederà dati verificati separatamente.

Ogni fase registra:
- classe console dichiarata e conferma effettiva in gioco;
- misura di quota Y e prova sul terreno o sul pavimento, con riferimento documentale;
- ingresso/uscita percorribili, nessun passaggio bloccato e collocazione visivamente confermata su PS5;
- almeno **due** riavvii osservati con riferimento di prova, senza nuovi crash o scatti/rubberbanding inaccettabili;
- presenza o assenza di accesso al file RPT; l'accesso non è garantito su console. Se c'è, usare l'analizzatore Stage 4.12 in locale **senza pubblicare il log**;
- decisione manuale esplicita di proseguire o fermarsi e ripristinare.

**Due riavvii** e il margine qualitativo sulle prestazioni sono **criteri di progetto interni**, non requisiti ufficiali imposti da Bohemia. La PS4 va testata separatamente: superare P5 su PS5 **non dimostra** automaticamente compatibilità e prestazioni equivalenti su PS4. Le registrazioni dei test dovrebbero evitare ID privati di altri giocatori.

## Moduli e controlli preparati

- `config/stage4_13_pilot_protocol.json`: ordine delle fasi, prerequisiti e limiti dei backup Nitrado.
- `scripts/build_stage4_13_console_pilot.py`: genera `blank_1_3_5_console_trial.json`, con tutti i campi di prova vuoti.
- `scripts/audit_stage4_13_console_pilot.py`: controlla un modulo compilato **localmente**, rifiutando ID o coordinate alterati, altezze non valide, backup mancanti, fasi completate senza la precedente, classe con path P3D, oggetti non osservati, riavvii mancanti, collisioni o RPT falliti.
- `scripts/test_stage4_13_console_pilot.py`: prove positive e negative usando esclusivamente dati sintetici temporanei, non pubblicati.
- `dist/stage4_13_console_pilot/console_pilot_no_evidence_audit.json`: risultato pubblico corretto iniziale **BLOCKED**.
- `dist/stage4_13_console_pilot/beileys47-console-pilot-templates-only.zip`: soltanto modello vuoto e checksum, **non installabile**.

### Uso futuro in Windows, solo dopo test reali

Compilare una copia privata del template, **fuori dal repository GitHub**, con i risultati effettivi:

```powershell
python scripts/audit_stage4_13_console_pilot.py --input "C:\DayZ_privato\rilievo_compilato.json" --output "C:\DayZ_privato\esito_rilievo.json"
```

Il riepilogo salva **solo stato e conteggi**, non indirizzi, nomi di utenti, riferimenti a registrazioni o altre informazioni del server. Il sistema non può autenticare in modo indipendente un'autodichiarazione: perfino un modello compilato interamente riceve il risultato `REVIEW_PACKET_COMPLETE_BUT_UNAUTHENTICATED`, **non un'autorizzazione al deployment**. Un successo sintetico dei test Python dimostra la robustezza della procedura, non che DayZ sia stato avviato.

Il progetto e lo snapshot Recovery Kit potranno archiviare i **template vuoti**, mai il modulo compilato con informazioni private.

## Condizione per il prossimo avanzamento reale

La prima installazione richiede conferma del backup, informazioni di versione, sito e terreno Y verificati, classe spawner accertata e verifica fisica su PS5. La successiva espansione a tre e cinque elementi dovrà essere autorizzata soltanto dopo i risultati delle fasi precedenti. In caso di problemi: interrompere le prove, isolare i nuovi file di configurazione e pianificare il ripristino, valutando attentamente gli effetti sui salvataggi e sull'indirizzo server.

**Niente Nitrado automatico, niente costi, niente JSON installabili e nessuna promessa di zero bug.**
