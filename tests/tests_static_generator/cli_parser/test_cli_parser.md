
* **Black Box:** La maggior parte dei test, poiché verificano solo l'input (argomenti riga di comando) e l'output (Namespace o Errore), senza sapere come `argparse` funzioni dentro.
* **White Box:** Solo il caso `TC-P11`, poiché manipola l'ambiente interno (`sys.argv`) tramite Mock.

---

# 🔧 **Modulo `cli_parser**`

Il modulo gestisce l'interfaccia a riga di comando (CLI). La strategia di test è prevalentemente **Black Box**, mirata a verificare che tutte le combinazioni di input (valide, invalide, limite) vengano interpretate correttamente secondo le specifiche.

### **Tabella Test – Validazione Input (Happy Path)**

Utilizziamo la tecnica **WECT (Weak Equivalence Class Testing)** per verificare le classi di input valido.

| Test ID | Classificazione | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-P01** | **Black Box** (WECT) | `--schema data.json` | Defaults corretti (`count=1`, `format=json`) | Verifica il funzionamento con l'input minimo indispensabile. |
| **TC-P02** | **Black Box** (WECT) | Tutti i parametri (`--count`, `--seed`, ecc.) | Tutti i valori sovrascritti nel Namespace | Verifica che l'utente possa configurare ogni singola opzione manualmente. |
| **TC-P03** | **Black Box** (WECT) | `--format` in `[json, csv, ndjson, sql]` | Formato corrispondente | Verifica (parametrizzata) che tutti i formati definiti nell'Enum siano accettati. |
| **TC-P14** | **Black Box** (Syntax) | `--key=value` (invece di spazi) | Parsing corretto | Verifica il supporto per la sintassi alternativa con il segno di uguale. |
| **TC-P12** | **Black Box** (Smoke) | `--help` | Exit Code 0, Messaggio di aiuto | Verifica che il flag standard di aiuto funzioni correttamente. |

---

### **Tabella Test – Gestione Errori (Robustness)**

Questi test verificano che il parser agisca da "guardiano", rifiutando input non conformi (Fail Safe).

| Test ID | Classificazione | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-P04** | **Black Box** (Negative) | Nessun argomento | Exit Code 2 (Missing Required) | Verifica che l'assenza del parametro obbligatorio `--schema` blocchi l'esecuzione. |
| **TC-P05** | **Black Box** (Type Check) | `--count dieci` (Stringa) | Exit Code 2 (Invalid Int) | Verifica che il parser rifiuti tipi di dato errati per parametri numerici. |
| **TC-P06** | **Black Box** (Constraint) | `--format xml` (Non in whitelist) | Exit Code 2 (Invalid Choice) | Verifica che vengano rifiutati valori non presenti nella lista `choices`. |
| **TC-P07** | **Black Box** (Negative) | `--velocissimo` (Flag inesistente) | Exit Code 2 (Unrecognized arg) | Verifica la protezione contro typo o flag sconosciuti. |
| **TC-P15** | **Black Box** (Negative) | `-s` (Flag breve) | Exit Code 2 (Unrecognized arg) | Documenta che gli alias brevi non sono supportati. |

---

### **Tabella Test – Casi Limite e Integrazione (BVA & System)**

Qui analizziamo i valori ai confini (**BVA**) e l'integrazione con l'ambiente di sistema.

| Test ID | Classificazione | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-P08** | **Black Box** (BVA) | `--count 0` e `--count -5` | Valori accettati (`0`, `-5`) | Verifica i limiti dei numeri interi. Il parser accetta la sintassi int (la logica semantica è demandata all'Engine). |
| **TC-P09** | **Black Box** (BVA) | `--out ""` (Stringa vuota) | Valore accettato (`""`) | Verifica il comportamento con stringa vuota come boundary value per i path. |
| **TC-P13** | **Black Box** (Robustness) | `--count 5 --count 10` | `count=10` | Verifica la regola "Last One Wins" in caso di argomenti ripetuti. |
| **TC-P10** | **Black Box** (Logic) | `--format json --table-name users` | Entrambi parsati | Verifica che il parser sia agnostico al contesto (accetta parametri SQL anche se il formato è JSON). |
| **TC-P11** | **White Box** (Integration) | `parse_arguments(None)` | Legge da `sys.argv` mockato | **Unico test White Box:** Usa `patch` su `sys.argv` per verificare che la funzione legga l'input di sistema se non vengono passati argomenti espliciti. |