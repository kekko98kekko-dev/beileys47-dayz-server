# BEILEYS47 | DAYZ SURVIVAL WAR

Progetto di configurazione per **DayZ PlayStation (PS4/PS5)**, mappa **Livonia**, server community da **10 slot**.

**Stato:** progettazione e controlli preliminari. **Non abbiamo acquistato Nitrado, né configurato un deploy automatico.**

## Obiettivo

Un survival con **PvP frequente**, loot aumentato in modo selettivo, veicoli accessibili e progressione significativa. Le casse e le basi devono mantenere i dati ai riavvii ordinari, entro le regole di persistenza impostate. Nessuno può garantire zero bug o zero lag.

## Struttura

- \`config/profile.json\`: specifiche e obiettivi di bilanciamento; **non è un file caricabile su DayZ**.
- \`mission/\`: destinazione dei veri file di missione DayZ (non presenti finché non li recuperiamo da una versione compatibile).
- \`scripts/validate.py\`: verifica sintassi XML/JSON e valori del profilo.
- \`.github/workflows/validate.yml\`: controlli gratuiti su GitHub Actions; **nessun caricamento su Nitrado**.
- \`NEXT_STEPS.md\`: piano operativo e verifica prerequisiti.

## Funzioni previste

1. Missione Livonia; compatibilità PS4/PS5 (console, non mod PC).
2. PvP sempre attivo, spawn e hotspot progettati con cautela.
3. Aumento **selettivo** di cibo/medicinali e loot, non moltiplicatori ciechi per ogni oggetto.
4. Bilanciamento auto, parti di ricambio e munizioni.
5. Impostazioni di stamina/notte e danni alle strutture solo se realmente supportate.
6. Backup e test di persistenza prima dell'apertura al pubblico.

## Come testare i file

\`\`\`sh
python3 scripts/validate.py
\`\`\`

Al momento il test controlla \`config/profile.json\`. Quando aggiungeremo XML/JSON reali in \`mission/\`, controllerà anche **la loro sintassi e alcune incoerenze elementari**. Un test superato non dimostra che DayZ li carichi o che il gameplay sia bilanciato.

## Sicurezza e costi

- Il repository è **pubblico**: NON inserirvi password, token, FTP/API key, dati privati o file di backup con segreti.
- GitHub Actions sui runner standard per repository pubblici non consuma la quota dei 2.000 minuti dei repository privati, nel rispetto delle condizioni GitHub.
- Nessuna modifica sarà inviata automaticamente al server finché non avremo collaudato un metodo autorizzato e sicuro.
- **Non spendere per Nitrado** finché le attività preliminari non sono complete e il prezzo non è confermato.

## Riferimenti tecnici

- [Bohemia Interactive: DayZ Central Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy)
- [Bohemia Interactive: Gameplay Settings](https://community.bistudio.com/wiki/DayZ:Gameplay_Settings)
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
