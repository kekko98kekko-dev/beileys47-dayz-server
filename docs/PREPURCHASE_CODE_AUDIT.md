# Revisione del codice pre-acquisto — BEILEYS47

**Ambito: Stage 1 → Stage 3, Master Kit Livonia, pubblicazione snapshot e controlli fail-closed.**

## Difetti riscontrati e corretti

### A. Stage 3 poteva incorporare una Stage 2 obsoleta

**Severità: alta per la riproducibilità.** Il builder `scripts/build_stage3.py` ricostruiva Stage 2 *solo se i suoi quattro file mancavano*. Se esisteva già una vecchia Stage 2, cambiamenti successivi alle regole del loot, della stamina, dei veicoli o alla baseline potevano essere ignorati, mantenendo file stantii dentro la Stage 3.

**Correzione:** Stage 3 rigenera sempre Stage 2 dalla sorgente ufficiale ancorata e dalle regole correnti, prima di copiarne i quattro file. `scripts/test_stage3_dependency_refresh.py` prepara una Stage 2 sintetica volutamente vecchia e verifica che **due** esecuzioni consecutive forzino la rigenerazione. Nota: la scelta comporta download CE ripetuti nei workflow, ma elimina l'ambiguità di stato.

### B. ZIP non riproducibili fra due esecuzioni dello stesso commit

**Severità: alta per backup, checksum e GitHub Releases.** I primi tre builder usavano `zipfile.write()` che incorpora i timestamp dei file del runner. Due esecuzioni identiche dello stesso commit potevano quindi dare ZIP diversi e rompere la verifica in byte della Release GitHub già pubblicata (o far cambiare hash senza cambiare i file di gioco).

**Correzione:** `scripts/zip_deterministic.py` inserisce i file con `ZipInfo` a data fissa, compressione e permessi controllati. Stage 1, 2 e 3 lo usano per ogni membro. `scripts/test_zip_reproducibility.py` controlla tutte le date interne e confronta SHA-256 di due ZIP creati con il **medesimo contenuto** ma timestamp sorgente diversi. Il Recovery Kit conserva il nuovo modulo e questi test.

**Limite distinto:** un report di sorveglianza della versione ufficiale può cambiare se cambia il repository upstream tra due esecuzioni; la disponibilità della baseline e il suo stato vanno sempre verificati. La modifica non finge di congelare eventi esterni.

### C. Input CE malformati potevano venire accettati silenziosamente

**Severità: media.** I nomi dei gruppi di spawn della Stage 1, dei tipi di loot e dei due veicoli modificati nella Stage 2 venivano trasformati in dizionari senza rilevare ambiguità. Il file vanilla `cfgspawnabletypes.xml` può però contenere duplicati legittimi **per altre classi**: la verifica è stata corretta per rifiutare soltanto duplicati dei veicoli sui quali interveniamo. Inoltre probabilità di parti veicolo `NaN`, infinite o fuori da 0–1 potevano contaminare i file.

**Correzione:** rifiuto di gruppi di spawn/tipi loot duplicati o privi di nome e dei duplicati riguardanti i due veicoli modificati (senza riorganizzare le altre voci vanilla); validazione dei target delle probabilità (reali finiti in [0,1], senza booleani) e dei valori originali prima della modifica. `scripts/test_ce_input_guards.py` verifica gli scenari anomali con XML **sintetico**.

## Ambito dei test e garanzie reali

La suite comprende anche i controlli già presenti: file Stage 3 ereditati dalla Stage 2 senza mutazioni impreviste, confronto degli eventi/modifiche con la baseline ufficiale, contenuto dei messaggi, integrità e whitelist del pacchetto a sei file, checksum, assenza dell'Object Spawner di ZONA 47 e pacchetto Recovery Kit interamente ricostruibile.

I nuovi test vengono eseguiti **sia** nel workflow di validazione **sia** prima di ogni GitHub Release. Nessuna operazione modifica Nitrado.

Le verifiche **non** dimostrano comportamento del motore DayZ su PS4/PS5, performance con giocatori reali, compatibilità di un aggiornamento futuro, correttezza fisica di ZONA 47, riavvio del servizio, disponibilità di un backup Nitrado o assenza universale di bug.

## Ulteriori rischi da verificare solo dopo l'acquisto

- Controllare build e percorso missione realmente caricato dal server, insieme a `enableCfgGameplayFile`.
- Fare backup verificabili e provare Stage 1, poi Stage 2, poi Stage 3 in un ambiente di prova autorizzato.
- Misurare quote Y reali di ZONA 47 e verificare classi spawner, collisioni, FPS/lag, accessi e persistenza.
- Confrontare i file attivi dopo ogni riavvio e prevedere rollback, senza eliminare dati persistenti.

**Conclusione:** il kit può raggiungere una qualità alta **prima dell'acquisto per le proprietà verificabili offline**, ma non può essere certificato «perfetto» in gioco senza il collaudo su un vero server.

## Secondo audit: archivi annidati e alterazioni non autorizzate

### D. Anche gli archivi Stage 4 e il pacchetto pre-acquisto erano non deterministici

**Severità: alta per l'affidabilità dei backup.** Il Recovery Kit esterno usava già una data interna fissa, ma diversi ZIP di ZONA 47 e lo ZIP con i sei file Livonia venivano creati con `ZipFile.writestr(nome, contenuto)` usando la data/ora del runner. Questo poteva cambiare l'hash del Recovery Kit per lo **stesso commit**, perché i suoi file annidati variavano.

**Correzione:** gli archivi generati Stage 4, la Stage 4.13 e il pacchetto pre-acquisto ora usano `zip_deterministic.add_bytes`. Un test dedicato ispeziona le date di tutti gli ZIP annidati nel Recovery Kit, ne verifica SHA-256 e confronta **due costruzioni consecutive** del pacchetto master e del Recovery Kit: devono essere identiche byte per byte.

### E. Il controllo del pacchetto Livonia non verificava integralmente il contenuto

**Severità: alta.** `build_prepurchase_bundle.py` accettava qualsiasi XML formalmente valido, purché avesse il nome giusto, e il controllo `if "base" not in notes and not event_changes` consentiva un report con modifiche mancanti se `notes` conteneva la parola «base». Un archivio Stage 3 alterato avrebbe potuto attraversare questa verifica senza che lo script se ne accorgesse.

**Correzione:** la creazione del pacchetto ora verifica i valori approvati per gli eventi elicottero/convoglio, i tre messaggi e le relative dichiarazioni nel report, e confronta **tutti e sei i file byte per byte** con la Stage 3 appena generata nel runner. Le prove negative in `test_prepurchase_bundle.py` alterano nominal di un evento, testo di un messaggio, loot XML e report: il pacchetto deve rifiutarli anche se la struttura resta valida.

### Limite che resta

Un archivio riproducibile non certifica il corretto comportamento dell'economia DayZ. Il confronto dei sei file prova la **coerenza del pacchetto con la build appena generata**, non che quella build sia compatibile con il server PlayStation realmente noleggiato. Lo stesso vale per collisioni e quote Y di ZONA 47, che restano da misurare.

## Terzo audit: parametri numerici e inventario completo del Recovery Kit

### F. Booleani JSON accettati erroneamente come interi DayZ

**Severità: media/alta per la correttezza semantica.** In Python `True` è un sottotipo di `int`. Una regola CE modificata in `true` poteva superare confronti numerici e generare valori `True` nei nodi numerici degli eventi XML o parametri stamina di tipo booleano nel gameplay JSON. Inoltre i fattori loot accettavano stringhe numeriche mediante coercizione.

**Correzione:** Stage 2 controlla tipi numerici esatti e finiti per fattori di loot e valori originali/obiettivo della stamina; Stage 3 impone interi veri per i nominal e i limiti dei figli degli eventi. Il test avversario aggiunge valori booleani, stringhe e non finiti.

### G. Nuovi sorgenti potevano mancare nel backup senza allarme

**Severità: alta per il recupero in futuro.** La lista `SOURCE_PATHS` del Recovery Kit comprende oggi tutti i 100 file versionati, ma era mantenuta manualmente. Un file importante aggiunto in futuro avrebbe potuto non entrare nel backup senza far fallire la pubblicazione.

**Correzione:** il builder confronta ora l'elenco dei file tracciati da Git con l'inventario del Recovery Kit, rifiuta omissioni, riferimenti stantii, duplicati e symlink. Un test di regressione simula un nuovo sorgente tracciato ma dimenticato e ne richiede il rifiuto. Il Recovery Kit resta un backup del **progetto**, non dei salvataggi reali Nitrado.

**Limite invariato:** i test offline non certificano il funzionamento su PS5, collisioni, altezza del terreno, latenza, prestazioni con giocatori o persistenza del mondo.
