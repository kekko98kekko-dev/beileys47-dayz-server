# Stage 3 — BEILEYS47 | Encounter Identity (Livonia, PS4/PS5)

**Stato: PREVIEW solo GitHub; NON provato su PlayStation; NON installato su Nitrado.**

## Visione di gioco

**Sopravvivi → Rischia → Conquista**. Prima di aumentare ancora loot e armi, creiamo punti di interesse spontanei e un'identità riconoscibile. Un server da 10 posti non può garantire incontri PvP frequenti ogni minuto: il numero reale di giocatori connessi conta più dei nominal di configurazione.

## Modifiche automatiche Stage 3

La Stage 3 **eredita tutti e quattro i file Stage 2 senza modificarli**. Aggiunge soltanto due file XML ufficialmente previsti per DayZ.

### db/events.xml — incontri dinamici (anteprima)

Modifiche al file ufficiale Livonia Bohemia del 16 ottobre 2026:
- **StaticHeliCrash**: nominal 3 → **4** e max del solo figlio Wreck_Mi8_Crashed 3 → **4**; min del figlio invariato.
- **StaticMilitaryConvoy**: nominal 3 → **4**; il resto dell'evento invariato.

I pool di coordinate in cfgeventspawns.xml, i raggi, i tempi, il loot assegnato agli eventi, gli zombie, gli altri figli e i conteggi veicoli restano **identici** alla baseline. La presenza di limiti/event group può influire sui risultati effettivi; **non garantiamo** quattro eventi simultanei in partita. Prestazioni e comportamento CE devono essere verificati dal vivo.

### db/messages.xml — identità e onboarding

Tre messaggi italiani, massima lunghezza 160 caratteri:
1. Benvenuto a chi entra.
2. Suggerimento sugli incontri militari ogni 35 minuti.
3. Regola PvP/lealtà ogni 60 minuti.

Nessun messaggio indica la posizione precisa degli eventi, genera eventi, assegna ricompense, esegue comandi o disconnette giocatori. shutdown=0 e deadline=0 per tutti. Verificare nel pannello PlayStation il caricamento e la formattazione degli annunci.

## Ciò che resta da progettare per l'effetto WOW

- **POI originali** con scenografia leggera: possibile Object Spawner ufficiale, ma servono coordinate X/Y/Z, asset verificati e prove di collisione/FPS su PS5. Non generare oggetti casuali sulla mappa senza queste verifiche.
- **Obiettivi contesi**: possibili eventi gestiti manualmente, non simulare missioni automatiche senza un motore che le supporti.
- **PvP e basi**: scegliere una policy chiara su raid, exploit e regole. Non dichiarare raid a tempo senza procedura sicura e collaudata.
- **Ingresso del nuovo giocatore**: ottimizzare primo spawn, progressione e leggibilità, senza equipaggiamento pay-to-win.
- **Community e identità**: nome coerente, calendario eventi, guida italiana, clip e momenti condivisibili.
- **Confronto 10 utenti vs 20/30 utenti**: dati di connessioni simultanee, incontri/ora, morti e uptime. Non acquistare slot aggiuntivi prima di aver misurato.

## Come funziona il controllo

- Builder: python scripts/build_stage3.py (richiede accesso al commit Bohemia e Stage 2 disponibile o lo ricostruisce).
- Test: python scripts/test_stage3.py (test statico indipendente su XML degli eventi, messaggi e contenuto ZIP).
- Output: dist/stage3/beileys47-livonia-stage3-preview.zip.
- **Non** usare scripts/plan_nitrado.py Stage 2 come autorizzazione di installazione Stage 3: non contiene tutti i suoi file.
- Prima di un qualunque futuro caricamento: backup file reali, confronto versione ufficiale, Stage 1 prima di Stage 2, poi Stage 3 e verifiche reali in partita.

## Fonti di riferimento

- https://community.bistudio.com/wiki/DayZ:Server_Messages
- https://community.bistudio.com/wiki/DayZ:Central_Economy_mission_files_modding
- https://server.nitrado.net/en-GB/guides/editing-xml-files-manually-with-dayz-console-en
- https://community.bistudio.com/wiki/DayZ:Object_Spawner

**La correttezza XML non prova il funzionamento del server PS5, FPS, spawns né persistenza.**
