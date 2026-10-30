# BEILEYS47 — Recupero offline, GitHub Actions e Nitrado

**Stato: Stage 1–4.13 e kit di preparazione all'acquisto, testati solo staticamente e con dati sintetici; nessun server DayZ PS5/PS4 collaudato.**

## Che cosa conserviamo

GitHub conserva *nella normale cronologia Git*, finché il repository esiste, regole JSON, script builder, documenti e workflow. I veri XML/JSON generati vengono pubblicati come **artifacts temporanei**, non come commit; i loro download non durano per sempre.

Il workflow costruisce un file separato chiamato **beileys47-recovery-kit**, contenente **beileys47-recovery-kit.zip**, con:
- sorgenti e documentazione del repository alla specifica revisione;
- preview ZIP Stage 1, Stage 2 e Stage 3, relativi rapporti e piano Nitrado Stage 2 **di sola simulazione**;
- progetto ZONA 47 Stage 4 con schema SVG, file concettuali (non installabili), audit e modello di rilievo sul terreno **vuoto**;
- report Stage 4.1 con posizioni candidate X/Z, criteri di esclusione, visualizzazione delle coordinate e avviso **non distribuire**;
- report Stage 4.2 con analisi del rettangolo 240 × 220 m e sei orientamenti, con limiti espliciti: **non è una verifica delle collisioni reali**;
- report Stage 4.3 che verifica la provenienza della release ufficiale DayZ 1.30, segnala eventuali aggiornamenti Bohemia e non autorizza mai il deploy;
- griglie Stage 4.4 X/Z corrette rispetto al centro della zona e modelli per misurare l'altezza Y (tutte le quote volutamente vuote), senza alcun posizionamento sul server;
- Stage 4.5 con 182 punti per sito per acquisizione di misure DayZ Y, audit di pendenza, esempio non testato di script PC per SurfaceY e convertitore di log con test sintetici: nessuna quota reale è stata acquisita;
- Stage 4.6 con contratto di coordinate riferite al centro, verifica del formato ufficiale Object Spawner e piano di cinque elementi X/Z non installabile;
- Stage 4.7 con report di resilienza dei percorsi PvP su grafo schematico, bypass est progettato e analisi di 45 scenari di blocco contemporaneo di due settori;
- Stage 4.8 con dossier ricognizione PS4/PS5: 11 waypoint X/Z, 16 collegamenti e 6 percorsi ancora da verificare sul terreno; direzioni compass precalcolate e altezze Y vuote;
- Stage 4.9 con 13 bounding box VISIVI P3D 1.30 attribuiti a una fonte terza e analisi di margini del primo progetto a cinque elementi; NON certifica collisioni, Y o classi su PS5;
- Stage 4.10 con tutti i 26 marker, 325 confronti geometrici schematici, 9 ingombri VISIVI ipotetici e 17 dimensioni sconosciute; nessuna collisione reale verificata;
- Stage 4.11 con 14 nuovi P3D fonte catalogo per 17 ruoli, 26 ingombri visivi proposti, 325 confronti 2D e blocco automatico delle path P3D non ammesse dal DayZ Object Spawner; nessuna classe confermata su PS5;
- Stage 4.12 con analizzatore locale privacy-safe di RPT, marker di errore ufficiale Bohemia, registro di 13 classi nominali/26 marker e archivio vuoto di prove: NESSUN log reale o risultato di spawn su PS5;
- Stage 4.13 con protocollo incrementale 1→3→5 oggetti, moduli vuoti e audit di backup/riavvio/collisioni: nessun test reale;
- Master pre-acquisto con 6 file di missione Stage 3 e hash SHA-256, esclusione di ZONA 47 e piano di verifica prima della configurazione Nitrado.
- script di preflight che non può eseguire upload o riavviare il server;
- **MANIFEST_SHA256.json** con gli hash dei file (verificati nel workflow).

I pacchetti Actions sono configurati per **90 giorni** (massimo standard per repository pubblici, salvo restrizioni del repository). **Scaricare e conservare sul proprio PC lo ZIP**: i 90 giorni NON sono un backup permanente. Il codice versionato rimane ricostruibile, a condizione che il commit ufficiale Bohemia bloccato resti disponibile.

## Copia di lunga durata in GitHub Releases

Abbiamo un nuovo workflow separato **Publish long-lived recovery snapshot** che verifica le Stage 1–4, rigenera il kit e crea una **GitHub Release** associata al commit `main`. La release contiene `beileys47-recovery-kit.zip` e il file SHA-256 per l'integrità. Gli asset GitHub Releases non sono soggetti alla scadenza standard degli artifact Actions dopo 90 giorni; possono comunque diventare indisponibili se la release o il repository vengono cancellati, se cambiano le condizioni del servizio o se GitHub non è disponibile.

Apri il repository → **Releases** → l'ultima release intitolata `BEILEYS47 Recovery Snapshot` → **Assets**, scarica lo ZIP e salvalo sul PC. Per verificare l'hash e sapere come rigenerare una nuova release, leggi [RELEASE_SNAPSHOT.md](RELEASE_SNAPSHOT.md).

**Importante:** la release è destinata a recuperare i **file del progetto**, non i dati del mondo di gioco su Nitrado. La seconda copia locale sul PC non può essere creata da GitHub o da questa chat senza un download da parte dell'utente.

## Come scaricare l'archivio sul PC Windows

1. Aprire il repository → tab **Actions**.
2. Aprire l'ultimo workflow **riuscito** sul ramo main (non usare una preview di pull request non approvata).
3. Scorrere fino a **Artifacts** → scaricare **beileys47-recovery-kit**.
4. Estrarre l'archivio GitHub: all'interno c'è **beileys47-recovery-kit.zip**.
5. Conservare **quel secondo ZIP** in una cartella locale e, meglio, in una seconda unità.
6. In un futuro ripristino, leggere **README_RECOVERY.txt**, la documentazione e il **MANIFEST_SHA256.json** prima di caricare qualsiasi cosa.

Il recupero delle configurazioni è possibile anche usando la cronologia Git, ricostruendo le anteprime con GitHub Actions. **Non è una garanzia** sulla disponibilità di versioni future dei file ufficiali o di Nitrado.

## Quando Nitrado sarà attivo

**A 48 ore dalla scadenza comunicata:** produrre/scaricare nuovamente l'archivio aggiornato e, *se l'interfaccia Nitrado console lo consente*, salvare separatamente in una cartella privata sul PC le impostazioni effettive e i file di missione attualmente caricati. Registrare versione DayZ, mappa, data e differenze rispetto al repository.

Il recovery kit *non contiene* salvataggi mondo, personaggi, casse, auto, basi o loot live. Non garantisce la possibilità di ripristinare i dati persistenti, specialmente dopo la scadenza del servizio. Se Nitrado prevede backup automatici di altro tipo, verificarne esistenza, accessibilità e politica di scadenza prima dell'ultimo giorno. Non mettere backup con credenziali nel repository pubblico.

## Differenza tra ripristino e distribuzione

- **Recupero:** rifare i file e conservare una copia. È quello che il workflow fa automaticamente. Il piano Nitrado di sola simulazione copre Stage 2, non autorizza Stage 3.
- **Distribuzione:** scrivere sul server Nitrado, potenzialmente interrompendo il gioco. **Non è attiva né autorizzata.**
- **Ripristino live:** richiede file reali recuperati dal server e/o backup provider effettivamente disponibile. Lo ZIP di configurazione non basta.
- Prima di installare Stage 2: installazione Stage 1, controlli in gioco, backup e verifica della versione console. Se la versione DayZ è diversa da quella del 16 ottobre 2026, aggiornare prima gli script e la baseline.

## Controllo aggiuntivo automatico

**scripts/audit_stage2.py** scarica i **quattro file originali** dallo specifico commit Bohemia, ricostruisce indipendentemente le sole modifiche previste dalle regole Stage 1/2 e confronta *interamente* il contenuto XML/JSON della preview. Blocca differenze non autorizzate (per esempio nomi di oggetti, posizioni, eventi o parametri non previsti).

È un audit statico più rigoroso, **non** una prova della compatibilità con PS5, delle prestazioni, della disponibilità loot o della persistenza del server.
