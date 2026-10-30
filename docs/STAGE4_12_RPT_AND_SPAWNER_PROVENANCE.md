# Stage 4.12 — Diagnosi Object Spawner e riconoscimento errori RPT

**Stato: codice offline e inventario delle evidenze preparati; NON abbiamo ricevuto alcun log reale, installato oggetti o verificato classi su PS5.**

## Verifica documentale, non prova di gioco

La documentazione ufficiale Bohemia dell'[Object Spawner](https://community.bistudio.com/wiki/DayZ:Object_Spawner) specifica che:
- il JSON del server elenca oggetti e orientamenti, con `name` per la classe o un percorso P3D consentito;
- **solo** i percorsi P3D delle cartelle `DZ/plants*` e `DZ/rocks*` sono accettati direttamente;
- un oggetto specificato **inesistente** produce in RPT la frase `Object spawner failed to spawn`.

Questo non significa che tutte le 13 classi `Land_...` già individuate in `mapgrouppos.xml` siano valide nel nostro Object Spawner PS5. Né i 14 nuovi P3D dei 17 segnaposto ancora privi di classe reale (Stage 4.11) possono essere caricati direttamente come path `structures/...`. I file CE non sono un registro completo e certificato delle classi installabili.

Nel report `class_evidence_no_runtime.json` abbiamo 13 **nomi di riferimento presenti nella mappa ufficiale**, 26 segnaposto, 9 opzioni di classe tratte da tali nomi e 17 modelli esclusivamente visivi. **Zero classi provate sul runtime PlayStation.**

## Analizzatore privacy-safe per log futuri

Quando il proprietario avrà realmente un server console autorizzato e potrà esportare il suo file RPT, il comando da eseguire **in locale** sarà:

```bash
python scripts/triage_stage4_12_rpt.py --log "C:/DayZ_privato/server.RPT" --output "C:/DayZ_privato/triage_sanitizzato.json"
```

La directory di input e output deve stare **fuori dal repository pubblico** e fuori dalla sua cartella `dist`. Lo strumento legge il file in locale, senza chiamate ad API e senza credenziali; accetta file fino a 25 MB e fino a 200.000 righe, e rifiuta file binari e righe anormalmente lunghe. Per file troppo grandi si possono analizzare spezzoni **privatamente**, senza sostenere che rappresentino l'intero riavvio.

Il risultato registra **solo**:
- quantità e numero di riga dei messaggi che contengono l'esatta frase ufficiale di errore, con differenze di maiuscole/spazi accettate;
- menzioni delle 13 classi già note, **solo quando presenti sulla stessa riga del messaggio**;
- numero di errori senza una delle 13 classi riconosciute, senza copiare nomi arbitrari;
- conteggi orientativi di riferimenti a `cfgGameplay`, `objectSpawnersArr` e indicazioni generiche di file assenti (soltanto segnali, non prove di guasti);
- stato **UNTESTED** per ogni classe che non abbia evidenza documentata in gioco.

**Nessuna riga originale del log viene inserita nel report.** Queste righe potrebbero contenere nomi di giocatori, IP, identificativi, coordinate, conversazioni e altri dati da non pubblicare. Anche i report privati non vanno caricati automaticamente nella repository.

### Interpretazione corretta

Un errore RPT con `Object spawner failed to spawn` è una **evidenza di fallimento** del caricamento dell'oggetto richiamato. Se in quella stessa riga compare un nome della shortlist ufficiale, lo segnaliamo come menzione: non garantiamo che sia l'unico oggetto coinvolto.

**Zero righe di errore NON significa successo.** Potrebbe non esserci stato un riavvio completo, `enableCfgGameplayFile` potrebbe essere disattivato, `objectSpawnersArr` potrebbe essere vuoto o assente, il log potrebbe essere parziale o il modello potrebbe essere posizionato sotto terra. Servono sempre osservazioni in gioco e verifica Y/collisioni.

## Pipeline pubblica e recupero

L'esecuzione automatica su GitHub **non dispone di log reali**. Genera soltanto:
- `dist/stage4_12_rpt_diagnostics/rpt_triage_no_logs.json`, marcato `NO_REAL_LOG_AVAILABLE`;
- `dist/stage4_12_rpt_diagnostics/class_evidence_no_runtime.json`, elenco delle classi sorgente e dei 26 marker, **senza approvazioni**;
- archivio `beileys47-spawner-log-preflight-only.zip`, manifest SHA-256, avviso **DO NOT DEPLOY**.

I test sintetici controllano la frase ufficiale, le classi simili ma non identiche, il caso privo di errori, il blocco delle scritture private nel repository e che dati fittizi simil-personali **non escano nel report**. Nessuna traccia finta viene pubblicata come log DayZ autentico.

## Condizioni prima del primo prototipo reale

Occorrono (1) un'istanza di prova console e relativo consenso/proprietà; (2) backup completo delle configurazioni e della persistenza; (3) misurazioni altimetriche reali e accurata verifica in gioco; (4) 3–5 classi spawnabili con prova di RPT/oggetti osservati; (5) collaudi di collisione, FPS e rollback. **Questa Stage 4.12 non sblocca il rilascio e non modifica Nitrado.**
