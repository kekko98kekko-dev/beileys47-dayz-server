# BEILEYS47 | V19 — Stato definitivo delle nove richieste (1 novembre 2026)

## Risultato verificabile

**Server Nitrado live:** V18 per l'economia delle chiavi arancioni; V16 per le strutture di mondo e gli hotspot. Ultimo audit remoto riuscito: [GitHub Actions 41298602716](https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/runs/41298602716). L'audit verifica file e impostazioni, non il gameplay.

Questa V19 aggiunge **controlli eseguibili e organizzazione degli eventi/manutenzioni**, non una mod PC o un pacchetto segretamente installato su PlayStation. **NESSUNA modifica a Nitrado, restart o wipe** è prodotta dagli script V19. Il Recovery Kit conserva i sorgenti, non i salvataggi del mondo.

| Richiesta | Stato reale | Soluzione effettivamente disponibile |
|---|---|---|
| Grande ZONA 47 240×220 m | NON COMPLETATA: V16 Radunin ha 20 nuovi props, non la struttura originale progettata | Blueprint, exporter offline con controlli di quota Y, percorso 1→3→5 e verifiche PS5 prima di aggiungere grandi strutture. Senza quote reali si blocca l'installazione per evitare clipping e trappole |
| Nuovo bunker sotterraneo | NON COMPLETATO: bunker vanilla esistente fortificato | Utilizzare il bunker Livonia già disponibile e, dopo test, migliorare accessi e arredi senza inventare una seconda struttura sotterranea |
| Container con chiavi colorate | NON DIMOSTRATO: gun cases e chiavi colorate attive, container navali non collaudati | Caccia al tesoro tramite GunCase vanilla e chiavi corrispondenti; **non equivale a un shipping-container con serratura verificata** |
| Orde mobili | NON DISPONIBILI come AI con script personalizzato | 3 aree d'infetti già configurate dalla V16, comportamento effettivo da osservare su PS5 |
| Premi automatici ai vincitori | NON DISPONIBILI con soli XML PS5 | Eventi annunciati automaticamente su GitHub; prova del vincitore e assegnazione extra in gioco da admin, con stato documentato. Nessun falso payout automatico |
| Respawn immediato dei camion allontanati | NON DISPONIBILE in CE standard | Evento camion V15 e quantità CE maggiori; veicoli spostati continuano ad essere conteggiati |
| Tavole a 252/252 ogni 15 giorni | NON DISPONIBILE per le pile persistenti con types.xml | Pile create nuove a quantità piena; aggiunto promemoria GitHub quindicinale il 15 e 30 novembre 2026 per controlli **manuali**, non per refill in-game |
| Frigoriferi funzionanti | NON REALIZZATI | Eventuali prop vanilla decorative richiedono prova classname/altezza/PS5. Nessun sistema di refrigerazione creato |
| Collaudo completo PS5 | NON REALIZZATO in questa sessione | Check-list V17 da 15 prove: accessibilità, collisioni, loot, infetti, persistenza, notti, prestazioni e accesso pubblico |

## Cosa è cambiato realmente in V19

1. `scripts/v19_release_gate.py`: legge gli oggetti della V16 e produce `deploy/v19/FEATURE_GATE.json` con i nove risultati non inventati. Valuta l'ingombro dei **soli 20 props Radunin V16** e lo confronta con le dimensioni richieste del progetto originale.
2. `scripts/test_v19_release_gate.py`: impedisce che l'assenza di prove PS5 sia etichettata come completamento al 100%.
3. `scripts/v19_plank_maintenance.py`: controlla il calendario di manutenzione 15 giorni dal 31 ottobre, fino alla scadenza attualmente documentata del servizio il 30 novembre; può aprire un Issue su GitHub il 15 e 30 novembre, **senza accesso Nitrado**. La schedulazione di GitHub Actions non garantisce esecuzione al minuto.
4. `scripts/test_v19_plank_maintenance.py`: verifica calendario, idempotenza, interruzione dopo scadenza e assenza di dichiarazioni errate di refill.
5. `.github/workflows/weekly-community-events.yml`: i prossimi eventi GitHub riportano modalità per registrare/validare i vincitori e la consegna extra manuale (non automatica sul server).
6. `scripts/v16_audit_live.py`: elimina due etichette errate: "hordes_confirmed" (in realtà zone infetti) e "no_wipe: true" (una API read-only non prova l'integrità degli stash).

## Perché non installiamo la ZONA 47 originale e i bunker sperimentali senza prova

L'Object Spawner ufficiale supporta oggetti vanilla tramite un JSON e `cfggameplay.json`, ma le altezze Y sono coordinate effettive da determinare sul terreno, e troppi props possono danneggiare prestazioni di server/client. Il progetto comprende già `scripts/export_zone47_spawner.py` che **blocca** l'export senza tutte le 26 quote e classi verificate. Non è un bug: è una protezione indispensabile.

Un noto progetto di bunker personalizzato per Livonia ammette persino che i giocatori debbano uscire tramite logout/login. Non installeremo una costruzione che intrappoli o distrugga oggetti dei giocatori.

## Per completare davvero il collaudo

- Aprire [V17 PS5 acceptance](BEILEYS47_V17_PS5_ACCEPTANCE.md).
- In gioco controllare in ordine ZONA 47 (X7100 Z6965), bunker (X9022 Z7458), Dolnik (X11490 Z461). Controllare loot, collisioni, uscite, infetti e stutter.
- Verificare separatamente la persistenza di casse di superficie, stash interrati e veicoli durante un riavvio sicuro, con giocatori avvisati e backup effettivo del provider.
- Compilare il registro di prova locale fuori da GitHub. Non salvare dati PSN privati in repository pubblici.

## Fonti

- https://community.bistudio.com/wiki/DayZ:Object_Spawner
- https://server.nitrado.net/en-GB/guides/settings-dayz-console/
- https://dayz.wiki.gg/wiki/Central_Loot_Economy
- https://github.com/scalespeeder/DayZ-LIVONIA-Yugovostok-Underground-Bunker-Custom-Json-File-For-PC-and-Console

**Niente slogan "100%": il gioco limita le funzionalità, e il collaudo PS5 non è sostituibile da una pipeline GitHub.**
