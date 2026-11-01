# BEILEYS47 — Stato realmente installato V15 (1 novembre 2026)

## Evidenza verificata
- Nitrado servizio **20113048**, Livonia PS5/PS4, missione dayzOffline.enoch.
- Installazione GitHub Actions **41294393297**: preflight OK, upload OK.
- TUTTI i 7 file ricontrollati scaricandoli dopo l'upload e verificandone lo SHA256.
- Riavvio automatico GitHub Actions **41294623968**: stato Nitrado `stopped -> restarting -> updating -> started`; confermato **2026-11-01 09:48:30 UTC** (10:48:30 CET).
- **Nessun wipe effettuato**. Nessun test in partita PS5 al momento della scrittura.

## Modifiche installate a livello di configurazione (NON ancora collaudate in gioco)
1. `custom/beileys47_dolnik_military_base_v9.json`: da 29 a 18 oggetti, con 2 tende invece di 13.
2. `mapgrouppos.xml`: rimossi 11 riferimenti alle tende eliminate; gli altri gruppi rimangono.
3. `cfgspawnabletypes.xml`: 17 classi veicoli aggiornate (borraccia, tanica e riparazione pneumatici); 3 classi camion M3S con 10 scatole chiodi, attrezzi e oggetti insoliti, incluso GunCase e ScientificBriefcase. Il nome obsoleto JerryCan è stato tolto da due Offroad_02.
4. `cfgweather.xml`: nebbia fissata a 0, pioggia/nuvole/vento/temporali preservati.
5. `db/events.xml`: nominal camion maggiore, eventi `StaticHeliCrash` e `StaticMilitaryConvoy` aumentati; aggiunto evento camion test Dolnik.
6. `cfgeventspawns.xml`: un punto camion vanilla a X 11574.92 / Z 374.01 assegnato all'evento di prova (non duplica quello stesso punto).
7. `db/types.xml`: quantmin/quantmax del tipo `PileOfWoodenPlanks` impostati a 100, per le pile di nuova generazione secondo le regole CE (non modifica necessariamente pile esistenti, e il nominal di questo tipo era 0).

## Non finito né dimostrato
- Verifica PS5: due tende rimaste, assenza delle altre 11, qualità e posizione degli oggetti.
- Il camion test deve realmente generarsi al punto indicato, senza essere incastrato; la sola presenza dell'evento XML non è una prova in-game.
- Il carico di tutti gli attrezzi e oggetti rari potrebbe eccedere gli slot fisici e le relative chiavi potrebbero non funzionare come previsto.
- La tanica al 100% non prova da sola che il liquido contenuto sia benzina; verificare.
- Rifornimento automatico di pile **ogni 15 giorni** e camion istantaneamente dopo l'allontanamento: non garantiti dal CE XML.
- Bunker personalizzato, ZONA 47 completa, casse/chiavi speciali su mappa, loot test organizzato in edifici, eventi community settimanali automatici, ordate, eventuali ulteriori hotspot: da sviluppare/verificare.
- La V15 non implica un server "100% perfetto": serve conferma in gioco.

## Collegamenti di controllo
- [Run installazione verificata](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41294393297)
- [Run riavvio verificato](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41294623968)
- [Rapporto deploy](../deploy/v15/DEPLOY_RESULT.json)
- [Rapporto riavvio](../deploy/v15/START_WORKFLOW_RESULT.json)

### Nota di sicurezza
La cartella `deploy/v15/GO_LIVE.txt` e `deploy/v15/START_SERVER_NOW.txt` erano trigger puntuali. Non modificare questi marker per prova: genererebbero nuove esecuzioni. Le configurazioni vanno modificate con diff e controlli sui file reali, non mediante upload vanilla indiscriminato.
