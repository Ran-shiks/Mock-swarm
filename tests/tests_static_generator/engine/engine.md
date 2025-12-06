### Contesto del Codice

* **Nome della Funzione/Metodo/Modulo:** `MockEngine.generate`, `MockEngine.generate_record`
* **Linguaggio di Programmazione:** Python
* **Obiettivo Funzionale:** Genera uno o più record mock basati su uno schema fornito.
* **Input Principali:** 
  * `schema_path: str` (per il costruttore)
  * `n: int` (per il metodo `generate`)
* **Output Previsto:** 
  * Una lista di dizionari (record generati secondo lo schema)
* **Vincoli/Dipendenze:** 
  * Lo schema deve essere valido e leggibile.
  * Dipende da `SchemaParser` e da generatori definiti in `algorithmic.py`.

---

| ID Test Case | Criterio (WECT/BVA/Errore) | Descrizione del Caso | Input Fornito | Risultato Atteso |
| :--- | :--- | :--- | :--- | :--- |
| TC-001 | WECT Valido | Generazione di un singolo record con schema valido | `schema_path="valid_schema.json"`, `n=1` | Lista con 1 record conforme allo schema |
| TC-002 | WECT Non Valido | Schema non esistente | `schema_path="missing_schema.json"`, `n=1` | Eccezione (FileNotFoundError o simile) |
| TC-003 | WECT Non Valido | Schema non valido (malformato) | `schema_path="malformed_schema.json"`, `n=1` | Eccezione (json.JSONDecodeError o simile) |
| TC-004 | BVA Minimo | Generazione con n=0 | `schema_path="valid_schema.json"`, `n=0` | Lista vuota `[]` |
| TC-005 | BVA Minimo-1 | Generazione con n=-1 | `schema_path="valid_schema.json"`, `n=-1` | Lista vuota `[]` o gestione errore |
| TC-006 | BVA Tipico | Generazione con n=10 | `schema_path="valid_schema.json"`, `n=10` | Lista con 10 record conformi allo schema |
| TC-007 | BVA Massimo | Generazione con n=1000 (supponendo limite pratico) | `schema_path="valid_schema.json"`, `n=1000` | Lista con 1000 record conformi allo schema |
| TC-008 | BVA Massimo+1 | Generazione con n=1001 | `schema_path="valid_schema.json"`, `n=1001` | Lista con 1001 record o gestione errore/performance |
| TC-009 | Errore | Input n non numerico | `schema_path="valid_schema.json"`, `n="dieci"` | Eccezione (TypeError) |
| TC-010 | Errore | Input n None | `schema_path="valid_schema.json"`, `n=None` | Eccezione (TypeError) |
| TC-011 | Happy Path | Generazione con schema valido e n tipico | `schema_path="valid_schema.json"`, `n=5` | Lista con 5 record conformi allo schema |
| TC-012 | Errore | Campo dello schema con tipo non supportato | `schema_path="unsupported_type_schema.json"`, `n=1` | Eccezione o record con valore di default/null |