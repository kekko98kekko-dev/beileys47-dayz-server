# Livonia — Prima configurazione survival/PvP (Stage 1)

**Stato: anteprima generata automaticamente, NON installata sul server.**
I file sono costruiti a partire da una versione immutabile dei file ufficiali Bohemia Interactive (commit `f220b2918b1d79a5055b1ee9be70c0ec1516e876`, 16 ottobre 2026). Prima di una futura installazione, verificare che la versione del server sia compatibile.

## Perché partire con modifiche piccole

Vogliamo incontri PvP più frequenti, ma senza trasformare il gioco in un deathmatch e senza introdurre glitch dovuti a quantità eccessive di loot o spawn.

### 1. Più risorse essenziali

Il builder modifica **solo** i valori CE `nominal` e `min` delle classi seguenti, se presenti e già abilitate:

| Classe | Moltiplicatore obiettivo |
| --- | ---: |
| BandageDressing | 1,35× |
| TetracyclineAntibiotics | 1,20× |
| VitaminBottle | 1,20× |
| SodaCan_Cola | 1,40× |
| PeachesCan | 1,40× |
| BakedBeansCan | 1,40× |
| Rice | 1,30× |
| PurificationTablets | 1,20× |

Se una classe opzionale non esiste, il builder la segnala nel `change_report.json`. Se manca una classe essenziale, la generazione fallisce. I moltiplicatori **non** equivalgono a una probabilità garantita di trovare un oggetto.

**Armi, bossoli, zombie, persistenza delle casse e veicoli restano ai valori originali per Stage 1**: li bilanceremo dopo i test per non accumulare modifiche potenzialmente instabili.

### 2. Incontri più frequenti

Per i nuovi personaggi, manteniamo solo **tre gruppi già esistenti** nel file ufficiale di Livonia: `Brena`, `Sobotka` e `Kolembrody`. Le coordinate esistenti, le distanze di sicurezza e la sezione `hop` non vengono alterate.

Questo concentra i punti di partenza e può favorire gli incontri, ma NON garantisce PvP continuo con 10 slot. È una modifica che va provata in partita prima di renderla definitiva.

## Come vengono creati i veri XML

1. GitHub Actions recupera dal repository ufficiale `BohemiaInteractive/DayZ-Central-Economy` due XML originali di Livonia.
2. Lo script `scripts/build_mission.py` applica **solo** le differenze descritte sopra.
3. Controlla che la sintassi XML rimanga valida e interrompe tutto se non trova gli elementi essenziali.
4. Produce uno ZIP e un rapporto JSON in `dist/`.
5. GitHub Actions allega la **preview** alla scheda del workflow. **Non invia nulla a Nitrado.**

Puoi avviare localmente:
```sh
python scripts/build_mission.py
```

### Percorsi dentro lo ZIP

- `dayzOffline.enoch/db/types.xml`
- `dayzOffline.enoch/cfgplayerspawnpoints.xml`
- `change_report.json` (rapporto: NON caricare nella missione)

**Non caricare lo ZIP direttamente nel pannello senza estrarlo e controllare i percorsi.**

## Rischi e precauzioni

- Prima di modificare Nitrado: **backup completo** del server e copia dei file originali.
- Non caricare mai file senza verificare che la mappa sia Livonia.
- Il controllo sintattico non verifica classi, performance o il comportamento reale della build PS5.
- Dopo l'upload è necessario verificare da PS5 i punti di spawn, il loot e la persistenza dopo un riavvio.
- Non eliminare per errore il resto della missione; sostituire soltanto i file autorizzati e verificati.
- Nessun deploy automatico è stato autorizzato o attivato.
