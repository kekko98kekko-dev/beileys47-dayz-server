# BEILEYS47 — collegamento ufficiale Nitrado API a GitHub

## Stato corrente
Installata nel repository una prima automazione **SOLO LETTURA**:
- `scripts/nitrado_snapshot.py`
- `.github/workflows/nitrado-readonly.yml`

**Nessuna modifica è stata eseguita sul server Nitrado 20113048.** Nessun wipe, stop, riavvio o upload. Le vecchie configurazioni V11–V14 non vengono attivate da questa procedura.

## Preparazione unica (account proprietario)
1. Apri Nitrado e accedi: https://server.nitrado.net/en/user/oauth/tokens
   Se il link è cambiato, apri il profilo Nitrado > Developer Portal > Long Life Tokens.
2. Genera un token chiamato **BEILEYS47 GitHub** con il SOLO scope `service`.
   NON selezionare `service_order` o permessi di pagamento.
3. Nel repository GitHub apri:
   https://github.com/kekko98kekko-dev/beileys47-dayz-server/settings/secrets/actions
   Seleziona **New repository secret**.
4. Nome segreto: `NITRADO_API_TOKEN` (esattamente).
   Valore: incolla il token Nitrado che hai appena generato e salva.
   **Non inserire il token nei commit, nelle Issues, in ChatGPT o negli screenshot.**

## Primo test (non tocca il server)
- Apri https://github.com/kekko98kekko-dev/beileys47-dayz-server/actions/workflows/nitrado-readonly.yml
- Seleziona **Run workflow**, modalità **probe**, poi **Run workflow**.
- Controlla che il job di connessione sia verde.
- Se il probe è verde, ripeti con modalità **snapshot**.
- Scarica dagli *Artifacts* del run il file **BEILEYS47_NITRADO_CONFIG**. Rimane disponibile per 3 giorni.

## Cosa fa
Il probe testa autenticazione Nitrado, accesso al file browser e individuazione di `dayzOffline.enoch`.
Lo snapshot scarica soltanto dieci file di configurazione:
`cfggameplay.json`, `cfgeconomycore.xml`, `cfgspawnabletypes.xml`,
`cfgweather.xml`, `cfgeventspawns.xml`, `mapgrouppos.xml`,
`mapgroupproto.xml`, `db/events.xml`, `db/types.xml`,
`custom/beileys47_dolnik_military_base_v9.json`.

Questa copia NON è un backup dei personaggi, delle basi e degli oggetti persistenti. Il programma non cancella e non modifica i file di Nitrado. Non invia il token a nessuno tranne all'API Nitrado. Lo ZIP di configurazione è un artefatto dell'esecuzione GitHub, non un nuovo commit.

## Fase successiva
Solo dopo aver verificato il probe e aver esaminato lo snapshot reale, aggiungeremo una **separata** automazione di deploy: diff, backup verificato, controllo giocatori, stop esplicito, caricamento selettivo, verifica successiva e possibilità di rollback. Non abilitiamo modifiche o riavvii automatici finché questa fase non sarà collaudata.

## Sicurezza
Il token `service` ha ampia autorità sul server (inclusa la gestione remota). Proteggi il repository e chi può eseguire Actions. Se compromesso, revocalo subito nel pannello Nitrado e crea un nuovo token. Non caricare nei workflow file non fidati. Le GitHub Actions possono essere soggette alle quote gratuite del tuo account, anche se NitrAPI è gratuita.
