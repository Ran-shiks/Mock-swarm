
## 📄 Documentazione Modulo: `SchemaParser`

### Contesto del Codice

* **Nome della Classe:** `SchemaParser`
* **Metodi Principali:** `__init__`, `validate_schema`, `parse_file`, `_sanitize_schema`
* **Linguaggio:** Python
* **Obiettivo Funzionale:**
1. Caricare uno schema JSON assicurandosi che sia valido (gestendo internamente tipi custom come `uuid`, `choice` tramite sanitizzazione).
2. Validare file di dati JSON rispetto allo schema caricato.


* **Input Principali:**
* `schema_path` o `schema_dict` (Inizializzazione)
* `file_path` (Validazione dati)


* **Output Previsto:**
* Restituisce il dizionario dei dati se validi.
* Solleva `SchemaError` per errori di validazione o struttura.
* Solleva `FileNotFoundError` per problemi di I/O.



---

### Tabella dei Test Cases

La suite di test è divisa in due categorie:

1. **Black Box (TC-001 a TC-010):** Verifica il comportamento esterno (Input/Output) ignorando l'implementazione interna.
2. **White Box (TC-011 a TC-017):** Verifica la logica interna, i rami condizionali, le eccezioni specifiche e la struttura del codice.

| ID Test | Tipo (Box) | Criterio | Descrizione | Scenario / Input | Risultato Atteso |
| --- | --- | --- | --- | --- | --- |
| **TC-001** | **Black Box** | WECT Valido | Validazione corretta | File JSON conforme allo schema | Restituisce `dict` dati |
| **TC-002** | **Black Box** | WECT Invalido | Dati incompleti | File JSON senza campo `required` | Eccezione `SchemaError` |
| **TC-003** | **Black Box** | Errore I/O | File inesistente | Path errato | Eccezione `FileNotFoundError` |
| **TC-004** | **Black Box** | Errore I/O | File non JSON | Contenuto testuale/corrotto | Eccezione `SchemaError` |
| **TC-005** | **Black Box** | BVA Minimo | Valori limite (Min) | Valori minimi (es. 0, array vuoto) | Restituisce `dict` dati |
| **TC-006** | **Black Box** | BVA Out | Sotto limite | Valore sotto il minimo consentito | Eccezione `SchemaError` |
| **TC-007** | **Black Box** | BVA Massimo | Valori limite (Max) | Valori massimi consentiti | Restituisce `dict` dati |
| **TC-008** | **Black Box** | BVA Extra | Campi aggiuntivi | JSON con campi non nello schema | Accettato (Default JSON Schema) |
| **TC-009** | **Black Box** | Type Check | Tipo errato | Stringa al posto di Int | Eccezione `SchemaError` |
| **TC-010** | **Black Box** | Happy Path | Flusso tipico | Schema e Dati standard | Restituisce `dict` dati |
| **TC-011** | **White Box** | API Logic | Init vuoto | `SchemaParser()` senza argomenti | Eccezione `ValueError` |
| **TC-012** | **White Box** | Internal Logic | Schema malformato | Manca `type: object` o `properties` | Eccezione `SchemaError` |
| **TC-013** | **White Box** | Type Check | Input Schema errato | Schema passato come `list` o `str` | Eccezione `SchemaError` |
| **TC-014** | **White Box** | Internal Logic | `required` errato | Campo `required` non è una lista | Eccezione `SchemaError` |
| **TC-015** | **White Box** | API Feature | Context Manager | Uso di `with SchemaParser(...)` | Istanza creata/chiusa |
| **TC-016** | **White Box** | API Feature | Factory Method | Uso di `SchemaParser.from_dict` | Istanza valida |
| **TC-017** | **White Box** | Robustness | Crash Interno | Mock eccezione durante `validate` | Catch -> `SchemaError` |