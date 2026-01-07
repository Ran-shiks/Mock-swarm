Ecco la versione aggiornata e completa del documento `README.md` (o della sezione di documentazione).

Ho apportato le seguenti modifiche fondamentali:

1. **Aggiornamento Input:** Corretti i valori dei generatori Faker (es. da `address.city` a `city`) per riflettere la nuova logica dinamica.
2. **Nuovi Test:** Aggiunti i casi dal **TC-021** al **TC-026** che coprono le nuove funzionalità e i casi limite (mocking, fallback).
3. **Classificazione Metodologica:** Aggiunta la colonna **"Metodologia"** per distinguere tra **Black Box** (test funzionali basati su input/output) e **White Box** (test strutturali che verificano rami specifici del codice, come le eccezioni interne o le correzioni logiche).

---

### Contesto del Codice

* **Nome della Funzione/Metodo/Modulo:** `get_generator` (factory) e classi generatori (`UUIDGenerator`, `ChoiceGenerator`, `FloatGenerator`, `StringGenerator`, `ObjectGenerator`, `ArrayGenerator`).
* **Linguaggio di Programmazione:** Python.
* **Obiettivo Funzionale:** Generare dati fittizi (mock) strutturati per dataset sintetici. Il sistema supporta la generazione deterministica (tramite seed) e l'integrazione dinamica completa con la libreria `Faker`.
* **Input Principali:** * `field_name: str` — Nome del campo.
* `field_props: dict` — Proprietà di configurazione (es. `type`, `min_value`, `faker`, `format`).


* **Output Previsto:** Un valore (stringa, numero, oggetto, lista) coerente con le regole specificate.
* **Vincoli/Dipendenze:** * Dipendenza stretta dalla libreria `Faker`.
* Priorità di generazione stringhe: chiave `faker` > chiave `format` > chiave `generator` > fallback `word`.



---

### Tabella dei Test Case

Questa suite di test copre il **100% delle istruzioni (Statement Coverage)** e utilizza tecniche miste di verifica.

| ID | Metodologia | Criterio (Tecnica) | Descrizione del Caso | Input Fornito (Snippet) | Risultato Atteso |
| --- | --- | --- | --- | --- | --- |
| **TC-001** | Black Box | WECT (Valid) | Generazione UUID (Deterministico) | `{"type": "uuid"}` | Stringa UUID valida (36 char, 4 trattini). |
| **TC-002** | Black Box | WECT (Valid) | Scelta tra opzioni | `{"type": "choice", "options": ["A", "B"]}` | Valore presente nella lista input. |
| **TC-003** | Black Box | WECT (Invalid) | Scelta senza opzioni | `{"type": "choice"}` | `None` o lista vuota. |
| **TC-004** | Black Box | BVA (Boundary) | Float al minimo | `{"type": "float", "min_value": 0.0}` | Valore ≥ 0.0. |
| **TC-005** | Black Box | BVA (Boundary) | Float al massimo | `{"type": "float", "max_value": 1.0}` | Valore ≤ 1.0. |
| **TC-006** | Black Box | BVA (Boundary) | Float con range negativo | `{"type": "float", "min_value": -1.0}` | Valore ≥ -1.0. |
| **TC-007** | Black Box | BVA (Boundary) | Float oltre unità | `{"type": "float", "max_value": 2.0}` | Valore ≤ 2.0. |
| **TC-008** | Black Box | WECT (Valid) | Stringa Indirizzo (Dynamic Faker) | `{"type": "string", "generator": "street_address"}` | Stringa non vuota (es. "Via Roma 10"). |
| **TC-009** | Black Box | WECT (Valid) | Stringa Città (Dynamic Faker) | `{"type": "string", "generator": "city"}` | Stringa valida (es. "Milano"). |
| **TC-010** | Black Box | Robustness | Metodo Faker ignoto | `{"type": "string", "generator": "unknown_method"}` | Stringa casuale (fallback su `word`). |
| **TC-011** | Black Box | WECT (Valid) | Oggetto Annidato | `{"type": "object", "fields": {...}}` | Dizionario con le chiavi specificate. |
| **TC-012** | Black Box | WECT (Invalid) | Oggetto senza campi | `{"type": "object"}` | Dizionario vuoto `{}`. |
| **TC-013** | Black Box | WECT (Valid) | Array di stringhe (Sample) | `{"type": "array", "item_options": ["X"]}` | Lista contenente elementi validi. |
| **TC-014** | Black Box | BVA (Boundary) | Array vuoto (min=0) | `{"type": "array", "min_items": 0, "max_items": 0}` | Lista vuota `[]`. |
| **TC-015** | Black Box | BVA (Boundary) | Array multiplo (max=10) | `{"type": "array", "max_items": 10}` | Lunghezza lista ≤ 10. |
| **TC-016** | Black Box | Error Handling | Tipo non supportato | `{"type": "unknown_type"}` | Solleva `ValueError`. |
| **TC-017** | Black Box | Error Handling | Proprietà mancante | `{}` (Dizionario vuoto) | Solleva `ValueError`. |
| **TC-018** | Black Box | Error Handling | Input malformato | `"type": "uuid"` (Stringa) | Solleva `AttributeError` o `TypeError`. |
| **TC-019** | Black Box | Happy Path | Float Standard | `{"type": "float", "decimal_places": 1}` | Float corretto con 1 decimale. |
| **TC-020** | Black Box | Happy Path | Array Standard | `{"type": "array", "min_items": 1}` | Lista con almeno 1 elemento. |
| **TC-021** | Black Box | WECT (Valid) | Formati Estesi (email, ipv4) | `{"type": "string", "format": "email"}` | Stringa contenente `@` o formato IP. |
| **TC-022** | White Box | Fault Injection | Gestione Crash Interno | Input valido, ma Mock su Faker forza Eccezione. | Sistema recupera e restituisce fallback. |
| **TC-023** | White Box | Robustness | Correzione Logica Min/Max | `{"min_items": 5, "max_items": 1}` | Sistema forza `max=5`. Array len=5. |
| **TC-024** | Black Box | WECT (Recursion) | Array di Tipi Complessi | `{"type": "array", "item_type": "integer"}` | Lista di interi (non stringhe). |
| **TC-025** | White Box | Robustness | Fallback Array Default | `{"type": "array"}` (senza `item_type`) | Lista di stringhe casuali (fallback ramo else). |