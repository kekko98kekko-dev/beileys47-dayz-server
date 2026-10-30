# STAGE 2 — BEILEYS47 Livonia PvP Survival (PlayStation)

**Stato: PREVIEW. Non è stata installata su Nitrado e non è stata provata su PS5.**

## Contenuti del pacchetto

Versione ufficiale di origine: `BohemiaInteractive/DayZ-Central-Economy`, commit `f220b2918b1d79a5055b1ee9be70c0ec1516e876` del 16 ottobre 2026. La build applica anche tutte le modifiche Stage 1.

| File da sostituire SOLO dopo backup | Modifiche |
| --- | --- |
| `dayzOffline.enoch/db/types.xml` | Stage 1 cibo/medicinali + Stage 2 PvP, ricambi, durata stash |
| `dayzOffline.enoch/cfgplayerspawnpoints.xml` | Brena, Sobotka, Kolembrody per i respawn iniziali |
| `dayzOffline.enoch/cfgspawnabletypes.xml` | Probabilità componenti in 2 tipi di auto |
| `dayzOffline.enoch/cfggameplay.json` | Stamina e penalità per peso (solo se il server carica il JSON) |

### Progressione armamenti

Aumenti moderati **solo sulle classi che già spawnano**:
- MP5K +25%; SKS +25%; Mosin +15% (valori nominal arrotondati).
- Munizioni 9×19 e 7,62×39 +15%; scatole 7,62×39 +20%.
- Armi rare M4A1 e AKM non modificate: continuano a richiedere esplorazione e rischio.
- Restock, danni, località e livelli di loot non toccati.

I moltiplicatori sono applicati ai valori nominal/min del Central Economy, **non** alle probabilità di trovare immediatamente l'oggetto.

### Veicoli

Non modifichiamo `events.xml`: **nessuna auto nuova creata e nessun conteggio veicoli aumentato**.

Per Hatchback_02 e OffroadHatchback:
- probabilità ciascuna delle prime quattro ruote aumentata almeno al 90%;
- probabilità dei ricambi previsti dalla configurazione originale portata ad almeno 75%;
- ruota di scorta e tutte le classi degli oggetti invariati.

Questo non dà carburante gratis, non garantisce l'auto pronta né risolve i bug fisici del gioco.

### Basi e casse

- `WoodenCrate`: durata ufficiale lasciata invariata: 45 giorni.
- `UndergroundStash`: durata desiderata portata da 14 a **21 giorni**, soggetta a test reale su PlayStation. Non promettiamo che tutti i contenitori sepolti usino la stessa regola.
- Non possiamo impedire wipe, problemi del gioco o errori di salvataggio. Non promettiamo 'casse eterne'.
- Nessun automatismo per raid a tempo: le impostazioni globali di danno alle basi e ai contenitori rimangono abilitate (non bloccate). Eventuali raid limitati al weekend devono essere gestiti tramite procedure/admin esterni, oppure regolamento e moderazione.

### Stamina e accessibilità

Nel `cfggameplay.json` ufficiale:
- `staminaMax` 100 → 110.
- `staminaKgToStaminaPercentPenalty` 1.75 → 1.6.
- Danni a basi e contenitori restano configurati su `false` per `disableBaseDamage` e `disableContainerDamage`.

Nitrado deve avere l'opzione **enableCfgGameplayFile** abilitata per usare questo JSON. Se non la abilitiamo, il server ignorerà queste modifiche gameplay.

## Validazioni eseguite da GitHub Actions

- XML/JSON sintatticamente validi;
- nomi ufficiali richiesti presenti nella versione bloccata;
- nessuna classe creata da zero;
- armi rare e casse non alterate;
- spawn raggruppati e resto invariato;
- output ZIP generato e verificato;
- test di regressione su componenti e stamina.

Questi test **non** sostituiscono un collaudo su console, né provano gli FPS o la persistenza su Nitrado.

## Come preparare il vero deployment (NON farlo ancora)

1. Acquistare un server PlayStation compatibile e selezionare **Livonia**.
2. Fare **backup integrale** della missione e dei file prima di cambiare qualunque cosa.
3. Verificare la versione del server: se più recente della versione ufficiale fissata nel builder, aggiornare prima la baseline.
4. Arrestare il server e caricare i file uno alla volta nel percorso **dayzps_missions/dayzOffline.enoch/**, verificandolo prima nel pannello.
5. Attivare `enableCfgGameplayFile` nelle opzioni ufficiali del pannello solo dopo aver collocato il JSON giusto.
6. Riavviare, testare da PS5 e verificare dai log se qualcosa non viene letto.
7. Test persistenza: porre una cassa, annotare i contenuti, effettuare un riavvio ordinario, verificarne posizione e inventario.
8. Se si presentano errori: fermare il server e ripristinare il file originale dalla copia di backup.

**Non è configurata alcuna distribuzione diretta a Nitrado, token segreto, collegamento FTP/API o riavvio remoto.**
