# BEILEYS47 — Recupero offline, GitHub Actions e Nitrado

**Stato: Stage 1/2 preview; nessun server DayZ PS5/PS4 collaudato.**

## Che cosa conserviamo

GitHub conserva *nella normale cronologia Git*, finché il repository esiste, regole JSON, script builder, documenti e workflow. I veri XML/JSON generati vengono pubblicati come **artifacts temporanei**, non come commit; i loro download non durano per sempre.

Il workflow costruisce un file separato chiamato **beileys47-recovery-kit**, contenente **beileys47-recovery-kit.zip**, con:
- sorgenti e documentazione del repository alla specifica revisione;
- preview ZIP Stage 1 e Stage 2 e relativi rapporti delle modifiche;
- **MANIFEST_SHA256.json** con gli hash dei file (verificati nel workflow).

I pacchetti Actions sono configurati per **90 giorni** (massimo standard per repository pubblici, salvo restrizioni del repository). **Scaricare e conservare sul proprio PC lo ZIP**: i 90 giorni NON sono un backup permanente. Il codice versionato rimane ricostruibile, a condizione che il commit ufficiale Bohemia bloccato resti disponibile.

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

- **Recupero:** rifare i file e conservare una copia. È quello che il workflow fa automaticamente.
- **Distribuzione:** scrivere sul server Nitrado, potenzialmente interrompendo il gioco. **Non è attiva né autorizzata.**
- **Ripristino live:** richiede file reali recuperati dal server e/o backup provider effettivamente disponibile. Lo ZIP di configurazione non basta.
- Prima di installare Stage 2: installazione Stage 1, controlli in gioco, backup e verifica della versione console. Se la versione DayZ è diversa da quella del 16 ottobre 2026, aggiornare prima gli script e la baseline.

## Controllo aggiuntivo automatico

**scripts/audit_stage2.py** scarica i **quattro file originali** dallo specifico commit Bohemia, ricostruisce indipendentemente le sole modifiche previste dalle regole Stage 1/2 e confronta *interamente* il contenuto XML/JSON della preview. Blocca differenze non autorizzate (per esempio nomi di oggetti, posizioni, eventi o parametri non previsti).

È un audit statico più rigoroso, **non** una prova della compatibilità con PS5, delle prestazioni, della disponibilità loot o della persistenza del server.
