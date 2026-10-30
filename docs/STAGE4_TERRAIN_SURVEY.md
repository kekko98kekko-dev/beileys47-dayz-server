# Stage 4.4 — ZONA 47: rilievo topografico preparatorio (X/Z)

**Stato: griglia di coordinate pronta, altimetria NON misurata. Nessun oggetto è stato installato.**

La Stage 4.3 ha già verificato la provenienza dei file ufficiali DayZ 1.30. I controlli Stage 4.1–4.2 individuano e confrontano nove centri candidati; la prima zona da ispezionare resta **X 9000 / Z 7800**, con orientamento preliminare di **120°** secondo il filtro geometrico sui soli punti degli XML.

## Che cosa abbiamo corretto

Nel progetto locale, il rettangolo dell'avamposto misura **240 × 220 metri** e viene disegnato con origine in basso a sinistra. **Il centro locale è X=120/Z=110**, non X=0/Z=0.

Le coordinate candidate **9000 / 7800 indicano il CENTRO del rettangolo nel mondo**, non l'origine locale del generatore. Il nuovo script esegue la conversione tramite la rotazione e controlla matematicamente che il centro trasformato rimanga esattamente quello desiderato.

Se avessimo copiato 9000 / 7800 direttamente nei campi `world_origin_x` e `world_origin_z` del vecchio generatore, avremmo spostato l'intera struttura. Il report ora fornisce separatamente l'origine calcolata, ma **non la applica automaticamente ad alcun survey autorizzato o server**.

## Che cosa produce la Stage 4.4

Lo script `scripts/build_stage4_terrain_survey_grid.py` legge i risultati di Stage 4.2 e produce, per ciascuna delle tre aree principali (centrale, sud-ovest, sud-est):

- **156 punti di campionamento** ogni 20 metri sulla griglia locale 240 × 220 m, con la posizione X/Z corretta dopo rotazione. Le colonne **quota del terreno Y, tipo di superficie, note pendenza e fonte** sono volutamente **vuote**.
- **26 posizioni X/Z dei componenti concettuali**, corrispondenti al blueprint; nessun elemento dispone di Y, modello verificato o conferma di collisione.
- Elenco dei gruppi di edifici/oggetti ufficiali più vicini, **con le loro quote Y originali**. Sono quote dei rispettivi *punti sorgente*, NON una quota interpolata o utilizzabile per la nostra costruzione.

Per il candidato centrale viene creato anche uno schema SVG delle coordinate di campionamento, senza immagini topografiche di terzi e senza simulare terreno o vegetazione.

**Totale:** 468 caselle di rilevazione Y da compilare per tre siti, oppure 156 se si parte dalla sola area centrale. Il disegno prevede 26 collocazioni concettuali per area.

## La fonte corretta delle vere altezze

I dati pubblici di Central Economy forniscono le quote di molti oggetti preesistenti, ma NON una matrice fitta di tutte le altezze del terreno. Un edificio vicino con Y=300 non dimostra che al nostro X/Z la quota sia 300. Neppure la sola vista satellitare o la carta a curve di livello garantiscono quote esatte per un elemento da piazzare con Object Spawner.

Per misurazioni reali, su un ambiente PC DayZ compatibile si può ricorrere a `GetGame().SurfaceY(x,z)`, che interroga la superficie del terreno, e `SurfaceRoadY(x,z)` per superfici stradali; tale accesso tramite script **non è disponibile come modifica vanilla diretta su un server Nitrado PlayStation**. Alternative pratiche: rilievo con strumenti DayZ PC autorizzati, letture attendibili in gioco o dati altimetrici della mappa con origine e risoluzione verificate.

Riferimenti:
- https://community.bistudio.com/wiki/DayZ:Object_Spawner
- https://github.com/StarDZ-Team/DayZ-Modding-Wiki/blob/main/en/06-engine-api/19-terrain-queries.md
- https://www.izurvive.com/livoniaHiking/
- https://tools.dzhosts.com/maps/

## Criteri per il prossimo sblocco

La griglia potrà essere valutata come *rilievo reale* soltanto dopo aver acquisito e documentato:
1. Fonte, data e versione DayZ del dato altimetrico.
2. Altezze effettive e attendibili presso la zona centrale e gli elementi da collocare.
3. Pendenze reali del terreno; eventuali piattaforme inadatte saranno scartate.
4. Verifica visiva di strade, boschi, acquitrini, ostacoli fisici e almeno tre ingressi praticabili.
5. Verifica che i modelli scelti esistano su PlayStation e test in gioco per collisioni e prestazioni.

Finché tali verifiche mancano, **l'esportatore Object Spawner resta bloccato**, non sarà inviata alcuna modifica a Nitrado e non è possibile dire che ZONA 47 sia una base pronta.

## Comandi, archivio e recupero

Da `main`:

```bash
python scripts/build_stage4_terrain_survey_grid.py
python scripts/test_stage4_terrain_grid.py
```

Output `dist/stage4_terrain_survey/`:
- `terrain_survey_grid.json`
- `central_empty_Y_grid.csv`, `southern_west_empty_Y_grid.csv`, `southern_east_empty_Y_grid.csv`
- `central_xz_survey.svg`
- `beileys47-zone47-terrain-survey-worksheet-only.zip`, con avviso **DO NOT DEPLOY** e manifest SHA-256.

Gli output non installabili vengono conservati da GitHub Actions e inclusi nel Recovery Kit. Le GitHub Releases potranno conservarne gli snapshot anche oltre la scadenza degli artifact temporanei.
