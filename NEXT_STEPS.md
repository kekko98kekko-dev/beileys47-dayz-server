# Stato del progetto — BEILEYS47 DayZ PS5

## Fatto: fase gratuita
- [x] Repository GitHub pubblico autorizzato a ChatGPT.
- [x] Profilo di gioco Livonia 10 slot / PvP survival.
- [x] File ufficiali DayZ CE Livonia ancorati al commit del 16/10/2026.
- [x] Stage 1: cibo, medicine e spawn concentrati.
- [x] Stage 2: loot PvP selettivo, ricambi auto, persistenza stash, stamina.
- [x] Builder automatico di XML/JSON.
- [x] Test di regressione e controllo contenuto ZIP.
- [x] Anteprima Stage 1 e Stage 2 prodotta da GitHub Actions.
- [x] Guida operativa backup, collaudo, rollback e limitazioni PS5.
- [x] Audit indipendente completo sulle differenze XML/JSON rispetto ai file Bohemia.
- [x] Recovery ZIP verificato con SHA-256 e conservazione artifact fino a 90 giorni.
- [x] Piano statico di preflight Nitrado senza alcuna capacità di upload/deploy.
- [x] Nessuna spesa, nessun accesso a Nitrado necessario.

## Prima della scadenza di un futuro server Nitrado
- [ ] Scaricare su PC l'ultimo beileys47-recovery-kit.zip (preferibilmente almeno 48 ore prima).
- [ ] Salvare separatamente i file di missione realmente presenti sul server, se il pannello lo permette.
- [ ] Verificare disponibilità e limiti dei backup dati persistenti nel pannello.

## Prima dell'acquisto Nitrado
- [ ] Confermare prezzo e piano PREPAGATO di PlayStation, non PC.
- [ ] Confermare Livonia nel pannello, versione DayZ compatibile e limite slot.
- [ ] Verificare disponibilità delle opzioni di editing file/API per account console.
- [ ] Verificare metodo di backup e rollback disponibile.
- [ ] Controllare che il progetto funzioni con l'ultima versione DayZ prima di usare i file.

## Dopo l'acquisto: collaudo reale
- [ ] Avvio server vanilla con password temporanea.
- [ ] Controllo backup automatico.
- [ ] Installazione controllata Stage 1.
- [ ] Test su PS5 (spawn, loot, cassa e riavvio).
- [ ] Solo se Stage 1 funziona, installazione Stage 2.
- [ ] Test su PS5 di auto, armi, stamina, persistenza stash.
- [ ] Verifica stabilità prestazioni con amici.
- [ ] Solo dopo valutare accesso pubblico e pianificazione eventi.

## Automazione Nitrado
- [ ] Accertare con un server reale che le API/file siano accessibili e affidabili.
- [ ] Non pubblicare token, né inserire credenziali nelle azioni/workflow di PR non attendibili.
- [ ] Progettare installazione con conferma, backup e rollback.
- [ ] NESSUN deploy automatico Nitrado attivo al momento.

## Collegamenti
- [Stage 1](docs/STAGE1.md)
- [Stage 2](docs/STAGE2.md)
- [Recupero ZIP](docs/RECOVERY_KIT.md)
- [Checklist e recupero](docs/OPERATIONS.md)
- [GitHub Actions](../../actions)

**Importante:** i test su GitHub dimostrano solo correttezza sintattica e alcune invarianti. Non certificano il comportamento del gioco né garantiscono conservazione del loot.
