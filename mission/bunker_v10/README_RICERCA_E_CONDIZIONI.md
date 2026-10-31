# BEILEYS47 — Bunker V10: audit tecnico e piano per Livonia PS5 (31/10/2026)

**STATO: PROGETTAZIONE; NON INSTALLATO.** La presenza di un file JSON non dimostra che la costruzione sia percorribile o al giusto livello del terreno.

## Situazione corrente (da conversazione con il proprietario)
- Server Nitrado Livonia / PS5, 10 slot, DayZ 1.30; base Dolnik V9 installata secondo conferma utente, ma **collaudo in gioco non dimostrato**.
- Kit V8, mappa e spawn X=11405 Z=586 configurati; bunker custom ancora mancante.
- ZONA47 in pausa. Shop con valuta fase successiva. Nessun wipe autorizzato per quest'operazione.

## Fonti candidate gratuite esaminate

1. **Scalespeeder Yugovostok Livonia, X10655 Z3620**: https://github.com/scalespeeder/DayZ-LIVONIA-Yugovostok-Underground-Bunker-Custom-Json-File-For-PC-and-Console
   - **SCARTATO**. README: non si può uscire senza logout/login; gli oggetti droppati possono scomparire. Test limitato DayZ 1.16, 2021. Non copiare su live.
2. **Livonia bunker template Steam**: https://steamcommunity.com/sharedfiles/filedetails/?id=3297469177
   - L'autore dichiara una variante JSON console compatibile ma NON consente terrain override e occlusion blocks su PS5. Non abbiamo ancora ricevuto/esaminato il file JSON effettivo della variante per console; non presumere funzionamento.
3. **Tisy Research Facility Updated** (origine Chernarus): https://github.com/DayZedAndConfused762/DayZedAndConfusedServer/blob/main/Snippets/builds-json/Tisy_Research_Facility_Updated.json
   - 122 oggetti, footprint X 293.1m x Z 188.3m, dislivello Y 29.0m, include classi Land_Underground_Stairs_Start / Land_Underground_Stairs_Exit. Fonte descrive base a due livelli sopra terra (non un bunker collaudato su Livonia). **Troppo grande per posizionamento cieco**.
4. **Bunker Entrance prefab**: https://github.com/DayZedAndConfused762/DayZedAndConfusedServer/blob/main/Snippets/builds-json/Bunker_Entrance.json
   - 15 elementi, ingombro planimetrico 11.3 x 16.3m, classi Land_Underground_Stairs_Exit / Land_Underground_Stairs_Start. È un modulo di ingresso, NON un bunker completo: non chiamarlo finito. Possibile scheletro per un bunker compatto se dopo assemblaggio e prova le scale sono percorribili.

## Aree Livonia: collisioni statiche preliminari

Controllo su mapgrouppos.xml ufficiale Bohemia, **non** su heightmap, strade, vegetazione o collisioni del mondo:
- X10655 Z3620: oggetto vanilla più vicino a 62,3 m, altitudine di riferimento di un tavolo circa Y311,09 a 62 m. Non corrisponde all'altezza del terreno esatta.
- X10530 Z3600: oggetto vanilla più vicino a 126,7 m; migliore candidato **soltanto per un complesso piccolo** come modulo d'ingresso 12x16 m. Altimetria e pendenza non verificate; nessuna quota Y può essere decisa da questo dato.
- NON installare un'area di 293x188 m solo perché il centro è lontano da strutture: serve controllo dell'intero ingombro e del dislivello.

## Soluzione gratuita di precisione identificata
- Editor: https://dzpage.com/en/map-editor
- Supporta import di JSON esistenti, vista 3D Livonia, asset vanilla, quote del terreno da dati del mondo e export ObjectSpawner JSON e mapgrouppos. Dichiara precisione di quota di 2,7 mm su campioni, ma ciò **non garantisce** assenza di collisioni/ingressi bloccati.
- Importare il **template console**, visualizzare tutta la superficie e le uscite, adeguare le quote e le rotazioni su terreno realmente libero, esportare JSON e voci CE, quindi solo con backup installare.

## Criteri obbligatori prima di attivare su Nitrado
1. Modello JSON per console (NO bldr_enoch, scripts, Steam mod o classi PC-only). Provenienza/licenza chiarite.
2. VISTA 3D della reale Livonia: spazio libero, quote terreno, pendenza, volume completo della costruzione, distanze da edifici e altri spawner e zone gas.
3. Due vie percorribili (ingresso e uscita) e nessuna necessità di logout/teletrasporto; non creare stanze sotto il terreno senza supporto collisioni/triggers.
4. Collisioni controllate e nessuno spawn player interno al complesso. Se vicino a Dolnik, spostare bubble V8 **solo dopo** verifica terreno.
5. Backup recuperabili di cfggameplay.json, cfgplayerspawnpoints.xml e mapgrouppos.xml; modifica chirurgica; zero wipe; riavvio a zero giocatori.
6. Unico collaudo finale su PS5: ingresso, uscita, inventario, drop/pickup, loot, performance, nessun crash RPT, rollback disponibile.

**Nota di trasparenza:** nessun editor 3D o controllo PS5 e nessuna installazione bunker sono stati eseguiti in questa sessione. Non fornire all'utente un falso file pronto o una quota inventata.
