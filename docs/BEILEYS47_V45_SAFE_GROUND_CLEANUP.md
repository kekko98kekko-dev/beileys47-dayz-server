# V45 — Pulizia oggetti comuni a terra, senza azzerare basi e veicoli

**Non esiste un contatore vanilla dei restart per ogni oggetto a terra su DayZ PS4/PS5.** Per ridurre il disordine in modo compatibile con console, V45 imposta a **14400 secondi (4 ore)** la durata dei soli oggetti normali idonei del Central Economy. È un tempo reale, NON garantisce che l'oggetto scompaia al secondo restart. Non imposta o modifica il calendario dei restart Nitrado.

Selezione prudente: solo `db/types.xml` con `nominal>0`, categoria `food`, `tools`, `weapons`, `clothes`, `medical`, `ammunition`, `drinks`, `lifetime` originale fra 4 ore e meno di 7 giorni, nome non correlato a veicoli, batterie, casse, barili, tende, rifugi, bandiere, materiali per costruire, kit, chiavi, carburante o persistent storage. Il resto resta identico.

Protezione:
- No wipe e no editing dello storage_1
- Nessun oggetto con durata >=7 giorni viene accorciato
- Non cambia tempi di vita di casse, barili, tende, watchtower, basi, veicoli e materiali da costruzione
- Non modifica player inventories
- Originale XML copiato con ZIP/SHA prima di ogni update
- Due controlli zero-giocatori e serializzazione con gli interventi Nitrado V37/V40/V44
- Al termine confronto byte-level del solo file modificato, riavvio normale e rollback se necessario

Limitazioni: `types.xml` non permette di differenziare perfettamente lo stesso classname fra oggetti in terra e dentro tutti i contenitori; la persistenza vanilla gestisce in altro modo gli oggetti contenuti. Questa è pulizia dopo un periodo di tempo, non dopo due eventi di riavvio. Se la modifica seleziona zero oggetti, il workflow segnala no-op, non inventa un risultato.

Fonti: [DayZ Central Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy) e [Nitrado lifetime](https://server.nitrado.net/en-US/guides/xml-changing-loot-quantity-in-dayz).
