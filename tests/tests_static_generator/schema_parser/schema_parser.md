**Contesto del Codice**

- **Nome della Classe/Metodo:** `SchemaParser.parse_file`
- **Linguaggio di Programmazione:** Python
- **Obiettivo Funzionale:** Caricare un file JSON e validarne la struttura secondo uno schema JSON.
- **Input Principali:**  
  - `file_path: str` (percorso del file JSON da validare)
- **Output Previsto:**  
  - Restituisce un `dict` con i dati del file se valido, altrimenti solleva eccezioni (`FileNotFoundError`, `SchemaError`)
- **Vincoli/Dipendenze:**  
  - Il file deve esistere, essere un JSON valido e rispettare lo schema.

---

| ID Test Case | Criterio (WECT/BVA/Errore) | Descrizione del Caso | Input Fornito | Risultato Atteso |
| :--- | :--- | :--- | :--- | :--- |
| TC-001 | WECT Valido | File JSON valido e conforme allo schema | `file_path` con JSON valido e schema corretto | Restituisce dict con i dati |
| TC-002 | WECT Non valido | File JSON valido ma non conforme allo schema (campo mancante) | `file_path` con JSON che manca un campo richiesto | Solleva `SchemaError` |
| TC-003 | Errore | File non esistente | `file_path` inesistente | Solleva `FileNotFoundError` |
| TC-004 | Errore | File non JSON (formato errato) | `file_path` con contenuto non JSON | Solleva `SchemaError` |
| TC-005 | BVA Minimo | File JSON con il minimo numero di campi richiesti dallo schema | `file_path` con JSON con solo i campi minimi | Restituisce dict con i dati |
| TC-006 | BVA Minimo - 1 | File JSON con meno campi del minimo richiesto | `file_path` con JSON con un campo mancante | Solleva `SchemaError` |
| TC-007 | BVA Massimo | File JSON con tutti i campi previsti e opzionali | `file_path` con JSON con tutti i campi | Restituisce dict con i dati |
| TC-008 | BVA Massimo + 1 | File JSON con campi extra non previsti dallo schema | `file_path` con JSON con campi extra | Restituisce dict (se lo schema consente campi extra) o solleva `SchemaError` (se lo schema li vieta) |
| TC-009 | Errore | File JSON con tipo di dato errato per un campo | `file_path` con campo di tipo errato (es. stringa invece di intero) | Solleva `SchemaError` |
| TC-010 | Happy Path | File JSON tipico e completo | `file_path` con dati tipici e corretti | Restituisce dict con i dati |
