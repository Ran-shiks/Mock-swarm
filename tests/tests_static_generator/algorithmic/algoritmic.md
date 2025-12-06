
### Contesto del Codice

* **Nome della Funzione/Metodo/Modulo:** `get_generator` (e classi generatori: `UUIDGenerator`, `ChoiceGenerator`, `FloatGenerator`, `StringGenerator`, `ObjectGenerator`, `ArrayGenerator`)
* **Linguaggio di Programmazione:** Python
* **Obiettivo Funzionale:** Genera valori fittizi (mock) per campi di vari tipi (uuid, scelta, float, stringa, oggetto, array) in base alle proprietà specificate.
* **Input Principali:** 
    * `field_name: str` — nome del campo
    * `field_props: dict` — proprietà del campo, tra cui almeno `"type"` e altre proprietà specifiche (es: `options`, `min_value`, `max_value`, ecc.)
* **Output Previsto:** Istanza di generatore che produce un valore coerente con il tipo e le proprietà specificate.
* **Vincoli/Dipendenze:** 
    * Il tipo deve essere tra quelli supportati (`uuid`, `choice`, `float`, `string`, `object`, `array`)
    * Alcuni generatori richiedono proprietà specifiche (es: `options` per `ChoiceGenerator`)
    * Dipende dal modulo `faker` per la generazione di dati fittizi.

---

### Tabella dei Test Case

| ID Test Case | Criterio (WECT/BVA/Errore) | Descrizione del Caso | Input Fornito | Risultato Atteso |
| :--- | :--- | :--- | :--- | :--- |
| TC-001 | WECT Valido | Generazione UUID | `{"type": "uuid"}` | Stringa UUID valida (formato 8-4-4-4-12) |
| TC-002 | WECT Valido | Scelta tra opzioni | `{"type": "choice", "options": ["A", "B", "C"]}` | Uno tra "A", "B", "C" |
| TC-003 | WECT Non Valido | Scelta senza opzioni | `{"type": "choice"}` | Eccezione o valore di default (lista vuota) |
| TC-004 | BVA Minimo | Float al valore minimo | `{"type": "float", "min_value": 0.0, "max_value": 1.0}` | Valore float ≥ 0.0 |
| TC-005 | BVA Massimo | Float al valore massimo | `{"type": "float", "min_value": 0.0, "max_value": 1.0}` | Valore float ≤ 1.0 |
| TC-006 | BVA Minimo - 1 | Float con min_value negativo | `{"type": "float", "min_value": -1.0, "max_value": 1.0}` | Valore float ≥ -1.0 |
| TC-007 | BVA Massimo + 1 | Float con max_value > 1.0 | `{"type": "float", "min_value": 0.0, "max_value": 2.0}` | Valore float ≤ 2.0 |
| TC-008 | WECT Valido | Stringa indirizzo | `{"type": "string", "generator": "address.street_address"}` | Stringa con indirizzo valido |
| TC-009 | WECT Valido | Stringa città | `{"type": "string", "generator": "address.city"}` | Stringa con nome città valido |
| TC-010 | WECT Non Valido | Stringa con generator non supportato | `{"type": "string", "generator": "unknown"}` | Stringa casuale (fallback) |
| TC-011 | WECT Valido | Oggetto con campi | `{"type": "object", "fields": {"id": {"type": "uuid"}, "score": {"type": "float"}}}` | Dizionario con chiavi "id" (UUID) e "score" (float) |
| TC-012 | WECT Non Valido | Oggetto senza campi | `{"type": "object"}` | Dizionario vuoto |
| TC-013 | WECT Valido | Array di stringhe con opzioni | `{"type": "array", "item_type": "string", "item_options": ["X", "Y", "Z"], "min_items": 2, "max_items": 2}` | Lista di 2 elementi tra "X", "Y", "Z" |
| TC-014 | BVA Minimo | Array con min_items = 0 | `{"type": "array", "item_type": "string", "min_items": 0, "max_items": 0}` | Lista vuota |
| TC-015 | BVA Massimo | Array con max_items grande | `{"type": "array", "item_type": "string", "min_items": 1, "max_items": 10}` | Lista con 1-10 elementi |
| TC-016 | Errore | Tipo non supportato | `{"type": "unknown"}` | Eccezione `ValueError` con messaggio "Tipo non supportato: unknown" |
| TC-017 | Errore | Proprietà mancante "type" | `{}` | Eccezione `KeyError` o errore di validazione |
| TC-018 | Errore | Input non dizionario | `"type": "uuid"` (stringa) | Eccezione di tipo (TypeError) |
| TC-019 | Happy Path | Generazione tipica di float | `{"type": "float", "min_value": 10.0, "max_value": 20.0, "decimal_places": 1}` | Valore float tra 10.0 e 20.0 con 1 decimale |
| TC-020 | Happy Path | Generazione tipica di array | `{"type": "array", "item_type": "string", "item_options": ["A", "B"], "min_items": 1, "max_items": 2}` | Lista di 1 o 2 elementi tra "A", "B" |