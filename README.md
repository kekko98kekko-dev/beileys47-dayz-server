# BEILEYS47 | DAYZ SURVIVAL WAR

Progetto di configurazione per **DayZ PlayStation (PS4/PS5)**, mappa **Livonia**, server community da **10 slot**.

**Stato:** progettazione e controlli preliminari. **Non abbiamo acquistato Nitrado, né configurato un deploy automatico.**

## Obiettivo

Un survival con **PvP frequente**, loot aumentato in modo selettivo, veicoli accessibili e progressione significativa. Le casse e le basi devono mantenere i dati ai riavvii ordinari, entro le regole di persistenza impostate. Nessuno può garantire zero bug o zero lag.

## Struttura

- `config/profile.json`: specifiche e obiettivi di bilanciamento; **non è un file caricabile su DayZ**.
- `mission/`: destinazione dei veri file di missione DayZ (non presenti finché non li recuperiamo da una versione compatibile).
- `scripts/validate.py`: verifica sintassi XML/JSON e valori del profilo.
- `.github/workflows/validate.yml`: controlli gratuiti su GitHub Actions; **nessun caricamento su Nitrado**.
- `NEXT_STEPS.md`: piano operativo e verifica prerequisiti.

## Funzioni previste

1. Missione Livonia; compatibilità PS4/PS5 (console, non mod PC).
2. PvP sempre attivo, spawn e hotspot progettati con cautela.
3. Aumento **selettivo** di cibo/medicinali e loot, non moltiplicatori ciechi per ogni oggetto.
4. Bilanciamento auto, parti di ricambio e munizioni.
5. Impostazioni di stamina/notte e danni alle strutture solo se realmente supportate.
6. Backup e test di persistenza prima dell'apertura al pubblico.

## Come testare i file

```sh
python3 scripts/validate.py
```

Al momento il test controlla `config/profile.json`. Quando aggiungeremo XML/JSON reali in `mission/`, controllerà anche **la loro sintassi e alcune incoerenze elementari**. Un test superato non dimostra che DayZ li carichi o che il gameplay sia bilanciato.

## Sicurezza e costi

- Il repository è **pubblico**: NON inserirvi password, token, FTP/API key, dati privati o file di backup con segreti.
- GitHub Actions sui runner standard per repository pubblici non consuma la quota dei 2.000 minuti dei repository privati, nel rispetto delle condizioni GitHub.
- Nessuna modifica sarà inviata automaticamente al server finché non avremo collaudato un metodo autorizzato e sicuro.
- **Non spendere per Nitrado** finché le attività preliminari non sono complete e il prezzo non è confermato.


## Stage 2 — Anteprima survival/PvP già generabile

✅ GitHub Actions costruisce anche una Stage 2 che include tutte le modifiche Stage 1, più:
- equipaggiamento PvP di fascia intermedia e materiali di riparazione;
- maggior probabilità di componenti base su due modelli di auto, senza aumentare il numero dei veicoli;
- durata obiettivo di 21 giorni per `UndergroundStash`, senza cambiare la durata di 45 giorni delle casse `WoodenCrate`;
- stamina leggermente aumentata e minore penalità del peso;
- test automatici di regressione e controllo di sicurezza del pacchetto ZIP.

I pacchetti si trovano sotto **Actions → ultima esecuzione riuscita → Artifacts**. Scaricare `beileys47-livonia-stage2-preview`.

[Configurazione Stage 2](docs/STAGE2.md) · [Checklist Nitrado e recupero](docs/OPERATIONS.md)

**Anteprima verificata sintatticamente, NON testata su PS5 e NON distribuita su Nitrado.**

## Stage 1 — Anteprima già generabile

✅ Il builder GitHub Actions crea automaticamente due veri XML per **Livonia**, usando un commit ufficiale Bohemia del 16 ottobre 2026:
- `db/types.xml` — maggior disponibilità di 8 tipi di cibo/medicinali;
- `cfgplayerspawnpoints.xml` — spawn iniziali concentrati in Brena, Sobotka e Kolembrody.

Il pacchetto rimane nella sezione **Actions → ultimo workflow riuscito → Artifacts → beileys47-livonia-stage1-preview**.

[Leggi la configurazione Stage 1](docs/STAGE1.md)

**Non installare ancora questi file su un server reale senza backup e verifica della versione.** Il workflow non distribuisce nulla a Nitrado.

## Riferimenti tecnici

- [Bohemia Interactive: DayZ Central Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy)
- [Bohemia Interactive: Gameplay Settings](https://community.bistudio.com/wiki/DayZ:Gameplay_Settings)
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)


## Recupero offline e nuova verifica Stage 2

✅ La pipeline controlla ora l'**intero contenuto** dei quattro file Stage 2 confrontandoli con la baseline Bohemia e applicando indipendentemente solo le variazioni consentite dalle regole JSON. Le verifiche automatiche non sostituiscono prove su PlayStation.

✅ Dopo ogni build riuscita GitHub Actions genera anche l'artifact **beileys47-recovery-kit**, al cui interno si trova **beileys47-recovery-kit.zip**. Contiene scripts, regole, documentazione, preview Stage 1/2, rapporti e manifest SHA-256. I tre artifact sono conservati per 90 giorni (salvo limiti delle impostazioni repository); **non** sono backup permanenti.

**Non contiene** personaggi, basi, auto, casse né dati persistenti del server Nitrado. Prima della scadenza Nitrado, scaricare lo ZIP sul proprio PC (ideale 48 ore prima) e salvare i file live separatamente se accessibili.

[Guida al recupero sul PC Windows](docs/RECOVERY_KIT.md) · [GitHub Actions](../../actions)

**Nessun deployment GitHub → Nitrado attivo.** È ancora obbligatorio verificare la versione del server, fare copie dei file originali e collaudare Stage 1 e Stage 2 su PS5/PS4.
