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

**Severità: media.** I nomi dei gruppi di spawn della Stage 1 e le liste dei tipi/veicoli della Stage 2 erano trasformati in dizionari senza controllare tutti i duplicati: a parità di nome, la seconda voce poteva sostituire la prima. Inoltre probabilità di parti veicolo `NaN`, infinite o fuori da 0–1 potevano contaminare i file.

**Correzione:** rifiuto esplicito di gruppi/tipi duplicati o privi di nome; validazione dei target delle probabilità (reali finiti in [0,1], senza booleani) e dei valori originali prima della modifica. `scripts/test_ce_input_guards.py` verifica gli scenari anomali con XML **sintetico**.

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
