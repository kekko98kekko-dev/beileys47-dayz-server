# Stage 5 — BEILEYS47: ritmo di gioco e bilanciamento offline

**Stato: progetto e controlli statici, non testato in DayZ PlayStation.** Questa fase NON aggiunge nuovi file di missione, modifica loot, spawner, runtime o server Nitrado. Misura esattamente le modifiche che Stage 1–3 già generano, per permettere il primo collaudo senza effetti collaterali.

## Principio creativo

Il nostro obiettivo non è «armi infinite» e nemmeno «fame costante». Vogliamo che un nuovo arrivato possa sopravvivere, imparare la mappa e scegliere se correre rischi; che gli scontri fra giocatori siano una conseguenza della progressione e degli obiettivi, non dello spawn killing; e che chi gioca da solo abbia una possibilità reale di divertirsi.

Con **10 slot** non promettiamo frequenti incontri PvP: se ci sono solo due giocatori online l'intervallo fra incontri può essere lungo. Non inventiamo indici di divertimento o tassi di loot ottenuti da un parser XML.

## Nuovo giocatore: esperienza da collaudare, non promessa

| Intervallo dalla prima connessione | Esperienza desiderata | Controllo reale da registrare |
| --- | --- | --- |
| 0–15 minuti | Capire dove si è, trovare acqua o cibo senza spawn camping sistematico | Località di spawn, sopravvivenza iniziale, numero morti entro 15 min |
| 15–35 minuti | Ricerca di medicina, riparo e prime armi leggere | Oggetti osservati, distanza percorsa, frustrazioni |
| 35–60 minuti | Decidere se rischiare un luogo militare o cercare un veicolo | Qualità delle alternative, quantità di contatti indesiderati |
| 60–120 minuti | Avere un obiettivo raggiungibile: sopravvivere, fare squadra, migliorare equipaggiamento, PvP o base | Giocatori che restano, ritorni dopo la morte, feedback |

Queste fasce temporali sono **obiettivi di design**, non tempi garantiti dal motore. Se il giocatore non trova nulla durante la prova, si modificano i valori in base ai dati osservati e si ripetono i test; non si gonfiano tutti i nominal indiscriminatamente.

## Incontri contesi e punti caldi

- **Brena, Sobotka, Kolembrody:** aree degli spawn freschi scelti da Stage 1. Garantire possibilità di fuga e non creare un'unica via obbligata verso i combattimenti.
- **Gliniska e gli altri luoghi di interesse esistenti:** monitorare effettiva attrattiva e rischio. Le località non diventano «eventi automatici» perché nominate nella documentazione.
- **StaticHeliCrash e StaticMilitaryConvoy:** Stage 3 aumenta due valori nominali da 3 a 4, ma non prova né frequenza osservata né presenza simultanea. Il numero di incontri va verificato sul server.
- **ZONA 47:** futuro avamposto scenografico e possibile luogo conteso. Nessuna struttura viene installata finché quote Y, classi spawnabili e collisioni non saranno confermate in PS5.

## Politica base, commercio e monetizzazione

PvP abilitato, equipaggiamento ottenuto giocando, **nessuna ricompensa pay-to-win**. Regole su raid e costruzione di basi da pubblicare con chiarezza dopo test del comportamento effettivo; non promettere fasce raid automatizzate senza supporto effettivo in DayZ console. Prima della pubblicazione verificare che lo spawn killing e il blocco sistematico di ingressi critici non rendano la mappa frustrante.

## Il nostro nuovo misuratore Stage 5

Il programma `python scripts/build_stage5_balance.py` genera `dist/stage5_gameplay/ce_balance_scorecard.json` e:

1. Confronta gli XML CE reali di Stage 1, 2 e 3 costruiti dalla baseline Bohemia fissata.
2. Verifica l'inventario di classi e i valori `nominal`, `min`, `lifetime` per i soli elementi selezionati; ogni altra differenza nei nodi XML è rifiutata.
3. Riconcilia le differenze con i ledger di generazione e le regole dei file JSON, senza fidarsi di numeri inseriti a mano.
4. Conferma che Stage 3 erediti `types.xml` dalla Stage 2 **byte per byte** e descrive le variazioni nominali dei due eventi.
5. Produce l'elenco preciso degli oggetti migliorati, la loro variazione nominale e la somma configurata su tutte le classi, come indicatore statico (NON un conteggio oggetti in mondo).

**Non è un simulatore DayZ**: `nominal` non significa oggetti al minuto, tempo di respawn o quantità garantita visibile. L'economia effettiva dipende da molti fattori del motore, giocatori, restock, lifetime, container e distribuzione spaziale.

Per i test avversari: `python scripts/test_stage5_balance.py`. Falliscono prima di emettere un nuovo report se viene alterata senza autorizzazione una classe, se Stage 3 non eredita esattamente i byte della Stage 2, o se il ledger non rispecchia i file XML.

## Primi collaudi con Franco e PS5

Testare almeno una sessione con un personaggio appena creato e una con un personaggio persistente, registrando **valori osservati** su loot, morti, tempi, posizioni e accesso ai veicoli. Riavviare normalmente e verificare persistenza. Solo se il contenuto vanilla, Stage 1, Stage 2 e Stage 3 funziona correttamente cominciamo a progettare Stage 5.1 con correzioni *misurate* e reversibili.

**Gate di rilascio:** `deployment_allowed=false`; il report non è un file da caricare su Nitrado. La verifica di build/backup/file missione e l'autorizzazione al caricamento rimangono obbligatorie.
