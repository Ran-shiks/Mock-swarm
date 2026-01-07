
# 📄 **DOCUMENTAZIONE TEST – EXPORTER**

---

# 🔧 **Classe `DataExporter**`

### **Tabella Test – DataExporter (Formati & Logica Core)**

Questa tabella copre la logica di dispatching e la correttezza sintattica dei vari formati di output.

| Test ID | Tipo Test | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-E01** | Black Box – Happy Path | Dati validi, format=`json` | JSON parsabile | Verifica che l'output sia un JSON valido standard. |
| **TC-E02** | Black Box – Happy Path | Dati validi, format=`csv` | CSV con Header e righe | Verifica la presenza dell'intestazione e la separazione corretta. |
| **TC-E03** | Black Box – Happy Path | Dati validi, format=`ndjson` | JSON Newline Delimited | Verifica che ogni riga sia un oggetto JSON autonomo. |
| **TC-E04** | Black Box – Happy Path | Dati validi, format=`sql` | Sintassi `INSERT INTO` | Verifica la struttura base della query SQL generata. |
| **TC-E11** | WECT – Default Value | format=`sql`, no `table_name` | Tabella `my_table` | Verifica il fallback sul nome tabella di default. |
| **TC-E12** | WECT – Unicode Support | Stringhe con Emoji e Cinese | Caratteri corretti (no `\uXXXX`) | Verifica che `ensure_ascii=False` preservi i caratteri speciali. |
| **TC-E06** | BVA – Empty Input | Lista dati vuota `[]` | Nessun output, nessun crash | Verifica il comportamento su input minimo (Early Return). |
| **TC-E07** | WECT – Invalid Input | format=`xml` (non supportato) | `ValueError` | Verifica che il Dispatcher rifiuti formati sconosciuti. |
| **TC-E09** | White Box – Complex Types | Strutture annidate (dict/list) in SQL | JSON serializzato come stringa | Verifica che oggetti complessi vengano convertiti in stringhe JSON per SQL. |
| **TC-E17** | Security – SQL Injection risk | Chiavi del dizionario con sintassi SQL | SQL Injection nell'output | Documenta che le chiavi non vengono sanificate (Input Trust). |
| **TC-E19** | WECT – Invalid Syntax | Chiavi con spazi (es. "user name") in SQL | SQL sintatticamente errato (es. `user name`) | Documenta limitazione: i nomi campi JSON devono essere compatibili SQL. |

---

### **Tabella Test – DataExporter (Robustness & Edge Cases)**

Questa sezione si concentra sulla gestione degli errori, sui tipi di dato limite e sulla stabilità del processo di scrittura.

| Test ID | Tipo Test | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-E05** | White Box – SQL Escaping | Valori: `None`, `'`, `True`, `float` | SQL: `NULL`, `''`, `TRUE`, numeri | Verifica la funzione interna `_format_sql_value` e l'escaping degli apici. |
| **TC-E14** | BVA – SQL Nasty String | Stringa mista: `O'Reilly "Hello" \n` | Escaping selettivo solo su `'` | Verifica che l'escaping SQL sia conforme allo standard ANSI (doppio apice singolo). |
| **TC-E13** | BVA – CSV Escaping | Valori contenenti `,` e `\n` | Valore quotato (es. `"a,b"`) | Verifica che il modulo CSV gestisca i delimitatori interni ai dati. |
| **TC-E16** | WECT – CSV Sparse Data | Riga 1: keys `[a,b]`, Riga 2: key `[a]` | Riga 2 completa con valore vuoto | Verifica gestione dati mancanti (allineamento colonne). |
| **TC-E10** | Robustness – CSV Schema Error | Riga 2 con chiavi extra rispetto a Riga 1 | `RuntimeError` | Verifica che il cambio di schema a metà file venga intercettato come errore. |
| **TC-E08** | Robustness – I/O Failure | Stream mockato che lancia `IOError` | `RuntimeError` | Verifica il wrapping delle eccezioni di sistema in eccezioni applicative. |
| **TC-E15** | Robustness – Serialization Fail | Oggetto con riferimenti circolari (JSON) | `RuntimeError` | Verifica gestione errori del modulo `json` (es. `RecursionError`). |
| **TC-E18** | WECT – Invalid Type | Tipi Python non serializzabili (es. `set`) | `RuntimeError` | Verifica gestione tipi non supportati dallo standard JSON. |
| **TC-E20** | WECT – Partial Write | Lista `[Valid, Invalid]`, format=`ndjson` | Riga 1 scritta, poi Crash | Verifica comportamento stream: i dati validi vengono scritti prima dell'errore. |

---

### 🔍 Analisi Tecnica del Codice

Il codice dell'Exporter è molto pulito e ben organizzato. Ecco alcune osservazioni tecniche basate sui test:

1. **Pattern Dispatcher:** L'uso del dizionario `strategies` rende il codice estremamente estendibile. Aggiungere XML o YAML in futuro richiederà zero modifiche alla logica principale `export`.
2. **SQL Escaping Manuale (`_format_sql_value`):**
* Hai implementato l'escaping standard SQL (`' -> ''`). È corretto per la generazione di file `.sql` statici.
* *Nota:* Come evidenziato da **TC-E17** e **TC-E19**, questo sistema si fida ciecamente delle chiavi del dizionario (i nomi delle colonne). È una scelta accettabile per un tool di generazione dati (dove lo schema è controllato dallo sviluppatore), ma va tenuto a mente se lo schema viene dall'esterno.


3. **Gestione CSV:**
* L'uso di `lineterminator='\n'` è fondamentale per evitare righe vuote extra su Windows. Ottima inclusione.
* La gestione dello schema in CSV è rigida (basata sulla prima riga). **TC-E10** dimostra correttamente che se la struttura cambia, l'export fallisce.


4. **Gestione Stream:**
* Il metodo accetta un generico `output_stream` (default `stdout`). Questo rende il codice testabile al 100% in memoria (usando `io.StringIO`) senza creare file spazzatura su disco. Molto ben fatto.

