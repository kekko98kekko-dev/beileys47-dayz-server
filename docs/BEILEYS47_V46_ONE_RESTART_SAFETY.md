# V46 — Una sola manutenzione straordinaria autorizzata: M3S Dolnik + pulizia loot

Il proprietario aveva già autorizzato espressamente il riavvio del server. Il precedente V44 è correttamente rimasto in attesa perché il monitor Nitrado indicava **un giocatore connesso**. V46 consente un **solo** stop/restart straordinario anche con uno solo, non con due o più. Non è un'eccezione permanente: V44 e V45 programmati continuano a rifiutare interruzioni con giocatori.

Prima del riavvio scarica e archivia in uno ZIP/SHA verificato quattro file della missione:
`db/events.xml`, `cfgeventspawns.xml`, `cfgspawnabletypes.xml`, `db/types.xml`.
La V44 disattiva i due vecchi eventi di generazione M3S e crea **uno solo** nel punto originale Dolnik X11574.92 Z374.01 con 4 barili, 4 casse, tronchi/assi/lamiere pieni e carico premium di bandiera/riparazione/sopravvivenza.
La V45 cambia unicamente la persistenza temporale dell'ordinario loot libero, massimo quattro ore per le classi selezionate, senza wipe di basi o veicoli.

Si verifica l'assenza di nuovi giocatori, si arresta normalmente Nitrado, si modificano solo i file effettivamente diversi, si rilegge ogni hash, si riavvia una volta e si ripete la verifica. In caso di errore ripristino delle configurazioni originali se nessun altro è entrato.

**NON viene alterato `storage_1`, quindi questa procedura non cancella fisicamente i due vecchi camion già persistenti.** Disattivare due eventi non prova che i camion siano scomparsi. Un wipe della persistenza mondiale cancellerebbe anche altri veicoli, basi e casse e non viene eseguito. Il CE può non generare subito il nuovo camion se il vecchio è ancora sul punto.

**La quantità dei carichi dichiarata nei file è probabilistica condizionata anche da inventario/collisioni vanilla:** 100% nelle voci XML non prova tutti gli slot effettivamente occupati, barili/casse riempiti o serbatoio già pieno. La benzina è fornita in taniche. Nessuna pulizia basata su un contatore nativo dopo esattamente due restart.

Il workflow è push-only: non può effettuare restart straordinari ricorrenti.
