# STAGE 7 — Bunker di ZONA 47: topologia tattica (solo progetto)

**Stato:** pianta e simulazione geometrico-logica offline. **Non è un bunker fisico DayZ e non è un Object Spawner.** Le 10 stanze e le 18 connessioni della pianta sono simboliche. Non esistono quote reali Y, classi confermate su console, prove di collisione, porte o tunnel sotterranei, loot in-game, AI di infetti o FPS rilevati.

## Identità narrativa e obiettivi

L'HQ di ZONA 47 ospita idealmente un vecchio bunker di comando. La progressione concepita è: avvicinamento al complesso → esplorazione degli archivi e dell'infermeria → scelta fra corridoi → accesso al deposito sigillato, dove **potremmo** collocare un oggetto di valore se le regole e gli spawn CE lo consentiranno. Nessun premio garantito, nessun sistema di serrature funzionanti inventato.

## Pianta progettuale

La topologia si trova in `config/stage7_bunker_layout.json`. Il generatore crea una vista SVG leggibile in `dist/stage7_bunker/bunker_topology.svg` e un rapporto in `dist/stage7_bunker/bunker_topology_report.json`. I numeri sono **coordinate X/Z locali del disegno di 240 × 220**, non posizioni DayZ installabili.

| Elemento | Funzione desiderata |
| --- | --- |
| Accessi ovest, sud, est | Tre alternative di entrata, *non* tre porte già disponibili in DayZ |
| Decontaminazione | Area narrativa di transizione, copertura da verificare |
| Generatore | Punto di passaggio e possibile distrazione tattica, nessuna interazione scriptata |
| Archivi | Percorso laterale e ricompensa esplorativa da progettare |
| Infermeria | Seconda via di progressione e risorse non garantite |
| Nodo centrale | Raccordo fra percorsi; non deve essere l'unico ingresso all'obiettivo |
| Deposito sigillato | Obiettivo conteso, senza loot automatico |
| Cunicolo di servizio | Collegamento alternativo, non un tunnel reale assicurato |

**Rischio principale:** i tunnel e le stanze sotterranee non sono fabbricabili liberamente con gli strumenti disponibili su PS5. Le strutture riutilizzabili devono esistere nel gioco e avere accessi/collisioni corretti. Se non fosse realizzabile un bunker sotterraneo, il nostro piano alternativo è un **complesso di comando in superficie** che conservi gli stessi percorsi e la stessa identità narrativa.

## Controlli anti-campeggio, soltanto teorici

Lo script `scripts/build_stage7_bunker.py` legge il progetto originale HQ, il piano Stage 6 e il protocollo di collaudo 1 → 3 → 5. Verifica:

1. Tre accessi e un obiettivo centrale nella stessa area locale, senza coord. Y o classi fittizie.
2. Connessioni uniche, niente stanze con un solo accesso sulla carta.
3. **Almeno due percorsi internamente disgiunti** da ingressi distinti al deposito (calcolati con flusso massimo e splitting dei nodi).
4. Dopo il blocco teorico di qualunque stanza interna, almeno due ingressi possono ancora raggiungere l'obiettivo.
5. Niente dichiarazioni di compatibilità, spawn automatici, porte, serrature o installazione.

I test provano anche un grafico negativo con un unico punto obbligato e verificano che venga individuato. **Non significa che il bunker sia immune al campeggio**: visuale, linee di tiro, collisioni e uscite effettive vanno provate in gioco.

## Condizioni per trasformarlo in un prototipo su Nitrado

- Confermare server DayZ PlayStation, mappa e versione della missione, conservando i file originali.
- Visitare su PS5 il terreno reale: ricognizione, pendenze, acqua, rocce, vegetazione, edifici e terreno percorribile.
- Identificare soltanto classi di strutture disponibili nel gioco console. Testare eventuali stanze, porte, scale e accessi.
- Se le classi consentono davvero l'effetto bunker, collocare **un elemento** per volta secondo il protocollo Stage 4.13 (1 → 3 → 5), senza caricare il diagramma SVG come file DayZ.
- Verificare con almeno due console/giocatori vie di fuga, scontri, vantaggi eccessivi, blocchi dei passaggi, FPS e stabilità ai riavvii.
- Se impossibile sotterrare il complesso, conservare il concept narrativo ma spostarlo in superficie, senza inventare geometria giocabile.
- Affrontare loot e territori degli infetti solo come attività successive, con configurazioni CE separate e verificabili.

## Sicurezza e riproducibilità

`python scripts/build_stage7_bunker.py` genera esclusivamente **report JSON e SVG**. `python scripts/test_stage7_bunker.py` controlla il rifiuto di dati erronei, connessioni duplicate, classi di oggetti inventate, finte quote reali, loot/spawner “pronti”, e percorsi anti-campeggio falsamente dichiarati.

Nessun riavvio Nitrado viene programmato, nessuna missione XML/JSON viene modificata e nessun server è stato noleggiato per questa fase. Il Recovery Kit contiene pianta, sorgenti, controlli e grafico. Il successo della pipeline certifica la **coerenza del progetto**, non l'esperienza DayZ su PS5.

Fonte ufficiale: https://community.bistudio.com/wiki/DayZ:Object_Spawner
