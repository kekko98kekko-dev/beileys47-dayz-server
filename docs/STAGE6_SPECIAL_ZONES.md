# Stage 6 — Luoghi speciali, infetti e riavvii sicuri

**Stato: design-only; NESSUN bunker, zombie speciale, loot aggiuntivo o riavvio è installato.** Non esiste ancora il server Nitrado e i collaudi PS5 non sono stati effettuati.

## Le quattro esperienze preparate

| Esperienza | Settore ZONA 47 | Proposta | Prima del test live |
| --- | --- | --- | --- |
| Bunker dimenticato | HQ | Ingresso militare, percorso da esplorare, ambientazione con strutture statiche del gioco | Classi console reali, altezze Y, porte/scale/collisioni, via alternativa |
| Cordone infestato | Checkpoint | Pressione di infetti vanilla all'ingresso, senza nuove AI | Esaminare `env/zombie_territories.xml` del server e corrispondenti eventi `Infected...`; modifiche incrementali e controllo PS5 |
| Deposito conteso | Logistics | Difficoltà PvP e ricompense limitate | Controllare loot già generabile, `mapgrouppos.xml`, `mapgroupproto.xml`, `types.xml`, tag e categorie |
| Cache nascosta | Secret | Ricompensa di esplorazione, non forziere automatico di armi | Verificare punti CE effettivi e accesso senza exploit |

### Cosa è davvero fattibile su PlayStation

L'**Object Spawner ufficiale** carica oggetti del gioco da JSON referenziati in `cfggameplay.json`. Non possiamo caricare mod Workshop da PC o creare liberamente nuove entità 3D. Il solo modello visibile non garantisce porte funzionanti, collisioni, navmesh degli infetti o generazione del loot; vanno provati dentro DayZ. È possibile che un bunker bello da vedere debba essere semplificato se la struttura scelta non è accessibile oppure causa problemi di prestazioni.

Per gli **infetti vanilla** l'area è importante: la disposizione di territori e zone è nei file `env/zombie_territories.xml`, mentre `db/events.xml` descrive gli eventi (es. `InfectedArmy`). Non confondere il normale sistema dei territori degli infetti con il pool di posizioni degli eventi *fixed* in `cfgeventspawns.xml`. Il progetto NON ha ancora modificato nessuno di questi file e NON promette orde da 30–40 zombie. Per la prima prova scegliamo una sola zona e osserviamo la reazione della PS5 prima di espandere.

Per il **loot nei nuovi edifici** inserire solo un edificio nell'Object Spawner non basta a provare che vi nascano automaticamente oggetti. Servono definizioni, punti e gruppi CE adatti e verificati con i file attuali del server. Il primo test può prevedere ambientazione senza loot aggiuntivo; la sua economia va verificata separatamente.

### Riavvii: piano, non comando automatico

Le guide ufficiali Bohemia/Nitrado spiegano come utilizzare un `messages.xml` con `deadline`, `shutdown=1` e `#tmin` per lo **spegnimento ordinato con avvisi**. Poi deve esistere un compito di **riaccensione** supportato dal provider. Nitrado mette in guardia dall'opzione diretta di riavvio automatico, che potrebbe causare problemi a inventario e avvio.

Per il primo collaudo proponiamo **360 minuti dall'avvio** come intervallo indicativo da valutare, NON un orario locale, NON una promessa di 4 riavvii ogni giorno: bisogna prima verificare se il pannello offre la task di accensione, la timezone e il comportamento concreto. Le tre comunicazioni Stage 3 del progetto hanno tuttora `shutdown=0` e `deadline=0` e non saranno cambiate per errore.

### Percorso di prova reale

1. Verificare server vanilla Livonia, pannello, backup, compatibilità della versione.
2. Stage 1 → Stage 2 → Stage 3 senza saltare il test di persistenza dopo restart manuale.
3. Sopralluogo di ZONA 47 e altezze Y, classi di oggetto realmente caricabili su console.
4. Oggetti in **fasi 1 → 3 → 5**, con passaggi a piedi, collisioni, FPS e rollback.
5. Controllo separato di una zona infetta (territori ed eventi), poi dei punti CE per loot: non abilitare simultaneamente bunker+orde+loot.
6. Solo dopo, valutare lo spegnimento ordinato e un task Nitrado di riaccensione, osservando i salvataggi.

`python scripts/build_stage6_special_zones.py` genera solo `dist/stage6_special_zones/concept_review.json`; `python scripts/test_stage6_special_zones.py` verifica che non esistano affermazioni di collaudo o parametri di deploy nascosti. **Il JSON è un rapporto, NON un file DayZ installabile.**

## Riferimenti

- Object Spawner: https://community.bistudio.com/wiki/DayZ:Object_Spawner
- Central Economy: https://community.bistudio.com/wiki/DayZ:Central_Economy_setup_for_custom_terrains
- Server Messages: https://community.bistudio.com/wiki/DayZ:Server_Messages
- Riavvii Nitrado: https://server.nitrado.net/en-GB/guides/server-messages-for-dayz/

**Nessun acquisto, nessuna modifica alle missioni esistenti, nessun test reale simulato.**
