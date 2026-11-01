# V44 — Un solo NUOVO evento camion M3S a Dolnik, punto originale

Il proprietario ha chiesto di eliminare due camion precedenti e far comparire uno solo al punto originale X11574.92, Z374.01, orientamento177.83°, massimizzando l'allestimento. Il codice **disattiva i due vecchi eventi CE** `VehicleBEILEYS47DolnikTest` e `VehicleBEILEYS47DolnikRescueV40` (nominal/min/max/active=0) e inserisce un unico nuovo evento `VehicleBEILEYS47DolnikUltimateV43` (1/1/1/active=1) precisamente al punto originale. Tutti gli altri eventi/veicoli e il salvataggio del mondo restano inalterati.

**LIMITAZIONE DETERMINANTE:** disattivare un evento NON cancella automaticamente i camion già persistenti. I vecchi due M3S possono ancora esistere nel mondo, anche se non nasceranno altri camion dai due vecchi eventi. Per eliminare **soltanto** quei due veicoli persistenti occorre intervenire sulle singole entità nel mondo o disporre di un editor della persistenza capace di identificarle in sicurezza. Non si deve cancellare `storage_1/data`, perché contiene anche altri veicoli, basi e casse. Non viene effettuato wipe.

## Allestimento NUOVI camion

- Meccanica: ruote, batteria camion, fari, porte, cofano garantiti nella config e veicolo pristine.
- Rastrelliere: 50 tronchi, 100 assi e fino a 40 lamiere (quantmin/quantmax 100%); **quattro barili** e **quattro casse** nei loro slot dedicati.
- Materiali bandiera: `TerritoryFlag`, 32 pietre, 6 scatole chiodi, 2 corde, 2 fili metallici, martello, mazza, pala e piccone. `TerritoryFlagKit` incluso solamente se il server lo definisce in types.xml; altrimenti va craftato con materiali vanilla. 
- Riparazioni: 3 epoxy, 2 kit gomme, 3 nastri, sega, chiavi, martello, mola, saldatore, kit cucito ecc.
- Ricambi veicoli: batteria auto `CarBattery`, batteria camion, 2 `SparkPlug`, `GlowPlug`, 2 fari e 4 batterie 9V. La speciale `MotorbikeBattery` non esiste nel types.xml live e non viene inventata.
- Equipaggiamento: Field Backpack 64 slot, Plate Carrier e accessori, visore notturno, maschera, M4A1, AKM, Glock, caricatori, munizioni, medicine, acqua, viveri.
- Fuori dal nuovo carico: custodie per armi, valigette scientifiche, chiavi delle custodie e piccoli case.

**Limiti di effettivo contenuto:** il M3S ha 600 slot cargo base più barili/casse aggiuntivi. `cfgspawnabletypes.xml` dichiara probabilità 100% delle voci, ma non garantisce che il motore inserisca fisicamente tutti gli oggetti quando ingombri e capacità reali non bastano. I barili e le casse sono montati e non automaticamente pieni: caricarli singolarmente richiede meccaniche aggiuntive e potrebbe alterare i drop globali. Il serbatoio del camion non viene reso automaticamente pieno via XML; vengono fornite taniche di benzina.

## Installazione e sicurezza

Il workflow crea un backup ZIP dei 3 XML prima di fermare il server, controlla 2 volte che nessuno stia giocando, verifica la corrispondenza dei file Nitrado, installa e riavvia senza wipe. In errore tenta il ripristino. In caso di giocatori collegati, lascia il server intatto e ritenta nelle finestre orarie programmate; dopo una riuscita è idempotente. L'installazione confermata dell'evento non è una prova visiva dello spawn del camion né della rimozione delle entità già salvate.

### Pulizia oggetti a terra
La richiesta di eliminare **tutti** gli oggetti liberi dopo due restart non è tecnicamente una regola CE nativa. Oggetti comuni possono essere puliti accorciando `lifetime`, ma oggetti conservati nei container, basi, veicoli e depositi persistenti devono essere protetti. Modifiche selettive verranno applicate separatamente per evitare un wipe involontario.

Confronti: [CE console](https://scullyxlife.github.io/dayz-console-wiki/02_cfgspawnabletypes_xml.html), [M3S 600+ storage](https://dayz.wiki.gg/wiki/M3S), [Flag Pole](https://dayz.wiki.gg/wiki/Flag_Pole).
