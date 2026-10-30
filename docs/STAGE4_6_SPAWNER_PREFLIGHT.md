# Stage 4.6 — ZONA 47: Object Spawner preflight e primo micro-prototipo

**Stato:** controllo statico e piano di prova offline, **NON installabile**. Non è stato misurato alcun Y reale né sono stati eseguiti test su DayZ PS4/PS5.

## Cosa abbiamo corretto

Il vecchio esportatore sperimentale considerava `world_origin_x/z` come l'angolo locale sud-occidentale del progetto. Il controllo Stage 4.4 usa invece X 9000 / Z 7800 come **centro reale** dell'area 240 × 220 m. Copiare queste coordinate nell'origine precedente sposterebbe l'avamposto di circa 160 m.

Da Stage 4.6 l'esportatore accetta **soltanto schede di rilievo v2**, con la convenzione univoca `WORLD_CENTER_OF_BLUEPRINT`:
- `site.world_center_x/z`: centro Livonia in metri (X verso est, Z verso nord);
- `site.source_site_candidate`: una delle tre aree esaminate nella fase precedente;
- `site.rotation_degrees`: l'orientamento geometrico preliminare associato alla stessa area.

La trasformazione è:

```text
dx = local_x - (240/2)
dz = local_z - (220/2)
world_x = center_x + cos(yaw) * dx - sin(yaw) * dz
world_z = center_z + sin(yaw) * dx + cos(yaw) * dz
```

L'angolo locale (0,0) **non** viene confuso con il centro locale (120,110). L'export rifiuta la vecchia scheda v1, gli attributi `world_origin_x/z`, centri fuori dalle tre opzioni studiate e rotazioni che non corrispondono alla scheda di preselezione. Queste restano **posizioni preliminari**, non prova dell'idoneità effettiva del terreno.

## Verifica del formato di Bohemia

La [documentazione ufficiale Object Spawner](https://community.bohemia.net/wiki/DayZ:Object_Spawner) indica:
- File JSON nella cartella missione con `{"Objects":[...]}`.
- Ogni elemento specifica `name`, `pos` nell'ordine **X, Y, Z**, `ypr` nell'ordine **yaw, pitch, roll**, `scale`; `enableCEPersistency` è ammesso.
- `WorldsData.objectSpawnersArr` di `cfggameplay.json` può riferirsi a più file JSON.
- Molti oggetti caricati possono influire negativamente sulle prestazioni.

Il nostro **test su dati sintetici**, ora migliorato, controlla la struttura JSON, la preservazione delle altre impostazioni di `cfggameplay.json`, il blocco dell'export quando mancano dati e il corretto centro world X/Z. Il fatto che un nome sia presente in `mapgrouppos.xml` non garantisce che l'oggetto sia spawnabile, accessibile o senza collisioni sulla build PlayStation.

## Piano di collaudo minimo: cinque elementi simbolici

`scripts/build_stage4_6_pilot_preflight.py` produce un archivio **non installabile**, con cinque marker distribuiti sul centro candidato (X 9000 / Z 7800, orientamento solo preliminare di 120°):

- `checkpoint_01`: Broken Checkpoint — primo elemento d'ingresso;
- `woods_01`: West Breach — accesso laterale;
- `service_01`: Service Approach — secondo percorso laterale;
- `logistics_02`: Logistics Depot — prova di copertura;
- `hq_02`: Command Core — percorso verso il centro di comando.

Il piano contiene soltanto **X/Z trasformati**, zone e ruoli. Per tutti e cinque, `ground_y = null`, `selected_model_classname = null` e `ready_to_install = false`.

Non è possibile utilizzarlo direttamente con il motore DayZ; non contiene file `zone47_objects.json` né `cfggameplay.json`.

## Controlli automatici

La pipeline:
1. Ricontrolla che i tre centri della `config/stage4_centered_export_contract.json` coincidano con Stage 4.2 e Stage 4.4.
2. Riesegue l'esportazione sperimentale **solo su coordinate e Y sintetici**, in cartella temporanea. Verifica che ogni elemento X/Z corrisponda esattamente alla conversione **dal centro**.
3. Rifiuta schede v1, coordinate centro spostate, angoli non riconosciuti e vecchie chiavi di origine.
4. Conferma che un survey v2 iniziale, vuoto e non verificato **non produce alcun file installabile**.
5. Rigenera il piccolo piano di collaudo e lo salva nel Recovery Kit con checksum.

## Prima di rendere installabile il micro-prototipo

Sono ancora indispensabili: quote reali DayZ `SurfaceY` e geometria dettagliata sotto ogni elemento; verifica dell'orientamento praticabile, strade, alberi e ostacoli; classi effettivamente supportate dalla build PS4/PS5; backup reale del server; approvazione del test e prova di avvio. Il passaggio 5 oggetti → 10/15 → 26 dipende da **collaudi sul server e sulle console**, non dal risultato dei test Python.

Nessuna spesa, nessun accesso a Nitrado, nessun caricamento automatico e nessuna certificazione di prestazioni.
