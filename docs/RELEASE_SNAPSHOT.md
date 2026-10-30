# BEILEYS47 — Recovery Snapshot / Copia di sicurezza

Questa release contiene **il kit di recupero completo dei file di progetto**, generato e testato in automatico tramite GitHub Actions. A differenza degli artifact temporanei (retention 90 giorni), **gli asset delle GitHub Releases non hanno una scadenza predefinita di 90 giorni**. Restano disponibili finché la release e il repository continuano a esistere, nel rispetto delle condizioni del servizio. **Non è una garanzia assoluta di conservazione per sempre.**

## Contenuto

- `beileys47-recovery-kit.zip`: sorgenti versionati, script, documenti, configurazioni, report, preview e report di sicurezza.
- `beileys47-recovery-kit.zip.sha256`: checksum SHA-256 per controllare che lo ZIP non sia stato alterato durante il download.
- I file sono generati dal commit del repository associato al tag della release. Non viene distribuito alcun software esterno né alcuna credenziale Nitrado.

### Attenzione: cosa NON contiene

**Questo archivio non salva il mondo reale di DayZ:** personaggi, inventari, basi, veicoli, persistenza, configurazione specifica dell'account Nitrado o credenziali. Questi elementi dovranno essere salvati separatamente dal server effettivo. Inoltre, ZONA 47 **non è ancora installata o collaudata** su PlayStation: le preview e le coordinate candidate sono materiale progettuale e di verifica statica.

## Scaricarlo sul PC Windows

1. Apri **Releases** del repository `kekko98kekko-dev/beileys47-dayz-server`.
2. Entra nell'ultima release chiamata `BEILEYS47 Recovery Snapshot`.
3. Sotto **Assets**, scarica **beileys47-recovery-kit.zip** e, se vuoi, anche il file **.sha256**.
4. Salva una copia in una cartella locale, ad esempio `Documenti\BEILEYS47-Backup\`, e se puoi su una seconda unità o disco esterno.
5. Non caricare il kit completo su Nitrado: contiene sorgenti, report e file concettuali. Quando avremo un server, installeremo solo i file missione realmente convalidati.

Per verificare l'integrità su Windows PowerShell:

```powershell
Get-FileHash ".\beileys47-recovery-kit.zip" -Algorithm SHA256
```

Confronta il valore con la prima stringa del file `beileys47-recovery-kit.zip.sha256`.

## Rigenerazione e versioni successive

Il workflow **Publish long-lived recovery snapshot** può essere avviato manualmente dal tab **Actions → Publish long-lived recovery snapshot → Run workflow** sul ramo `main` ogni volta che vuoi una nuova release dal commit corrente. Gli snapshot sono associati al commit e non sovrascrivono le vecchie release. Se si rilancia lo stesso commit, il workflow verifica l'asset esistente invece di creare una copia duplicata.

Il primo snapshot viene creato automaticamente dopo il merge del documento e del workflow, **soltanto se i test e la generazione del kit vanno a buon fine**. Il workflow non compra servizi, non installa server e non tocca dati Nitrado.

**Licenze e uso:** il kit include file derivati dalla Central Economy ufficiale DayZ; controlla e rispetta le licenze originali prima di redistribuire a fini commerciali.
