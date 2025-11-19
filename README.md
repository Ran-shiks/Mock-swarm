# Progetto: Generatore Intelligente di Dati Mock basato su Schema

## 1\. Visione e Descrizione Discorsiva

Nel ciclo di vita dello sviluppo software moderno, la dipendenza dai dati è critica. Sviluppatori Frontend, ingegneri QA e progettisti di API si trovano spesso in una situazione di stallo: l'interfaccia è pronta, ma il Backend non è ancora completo, oppure si necessita di popolare un database con migliaia di record per test di carico.

L'approccio tradizionale prevede la scrittura manuale di file JSON statici (lento e non scalabile) o l'utilizzo di script che generano stringhe casuali (spesso prive di significato semantico o che violano i vincoli di validazione).

**Il progetto "Schema-Driven Smart Mock Generator"** nasce per colmare questo vuoto. Si tratta di un motore ibrido di generazione dati che accetta come "unica fonte di verità" un **JSON Schema**. Il sistema non si limita a produrre stringhe a caso, ma comprende la struttura e i vincoli del dato (es. "questo campo deve essere una email", "questo numero deve essere compreso tra 10 e 100").

Il vero valore aggiunto, tuttavia, risiede nella sua **integrazione con i Large Language Models (LLM)**. Mentre un generatore algoritmico standard può creare un nome fittizio, l'LLM può generare dati *contestualmente coerenti*. Se lo schema descrive un "Prodotto" e l'utente fornisce il prompt *"Articoli sportivi invernali"*, il sistema non restituirà nomi generici, ma *"Sci Alpino Pro"* o *"Giacca Termica Goretex"*, pur rispettando rigorosamente la struttura tecnica definita dallo schema.

-----

## 2\. Architettura Logica e Flusso d'Uso

Il progetto è concepito per operare in due modalità principali, accessibili sia via **CLI (Command Line Interface)** che come **Libreria importabile** in progetti Node.js/Python/Go (a seconda del linguaggio scelto).

### Il Flusso di Lavoro (Workflow)

1.  **Input (Schema Ingestion):** L'utente fornisce un file `schema.json`. Il sistema analizza l'albero delle proprietà, identificando tipi (`string`, `integer`, `array`), formati (`email`, `uuid`, `date-time`) e vincoli (`pattern`, `enum`, `minItems`).
2.  **Configurazione del Contesto (Opzionale):** L'utente può fornire un "Prompt di contesto" (es: *"Genera dati per un CRM bancario"*).
3.  **Decision Engine:**
      * *Modalità Algoritmica:* Per campi standard o quando la velocità è prioritaria, il sistema usa librerie deterministiche (tipo Faker) per riempire i campi rispettando i vincoli.
      * *Modalità AI:* Se attivata, il sistema costruisce un prompt complesso per l'LLM includendo lo schema e richiedendo un output JSON rigoroso che popoli i dati con realismo semantico.
4.  **Validazione Post-Generazione:** Prima di restituire l'output, il sistema valida internamente che i dati generati (specialmente quelli dall'LLM) rispettino effettivamente lo schema di input.
5.  **Output:** Viene restituito un JSON (o una lista di JSON) pronto all'uso.

-----

## 3\. Requisiti Funzionali (Cosa deve fare)

Queste sono le funzionalità "hard" che il sistema deve implementare.

### A. Core Engine & Parsing

  * **Supporto JSON Schema:** Deve supportare le specifiche standard (Draft 7 o superiore). Deve interpretare correttamente keywords come `type`, `properties`, `items`, `required`, `enum`, `const`.
  * **Gestione Vincoli (Constraints):**
      * Stringhe: `minLength`, `maxLength`, `pattern` (Regex), `format` (email, uri, ipv4, date).
      * Numeri: `minimum`, `maximum`, `exclusiveMinimum`, `multipleOf`.
      * Array: `minItems`, `maxItems`, `uniqueItems`.
  * **Dati Annidati:** Deve essere in grado di generare oggetti complessi con livelli di profondità multipli e array di oggetti.

### B. Integrazione LLM (The "Smart" Feature)

  * **Prompt Injection:** L'utente deve poter passare una stringa di contesto (es. `--prompt "Utenti arrabbiati per un servizio scadente"`). Il sistema userà questo tono per generare campi testuali come "recensioni" o "commenti".
  * **Interfaccia Provider:** Il sistema deve essere agnostico rispetto all'LLM. Deve supportare driver per:
      * OpenAI (GPT-4o/Turbo)
      * Anthropic (Claude)
      * Modelli Locali (via Ollama o LocalAI per privacy e costi zero).
  * **Schema-guided Generation:** Il prompt inviato all'LLM deve includere lo schema minimizzato per istruire il modello sulla struttura esatta del JSON da restituire ("Strict Structured Output").

### C. Interfaccia Utente (CLI & Lib)

  * **Modalità CLI:**
      * Comando: `mockgen generate --schema ./user.json --count 50 --out ./data.json`
      * Flag AI: `mockgen generate --schema ./review.json --ai --prompt "Positive tech reviews"`
  * **Output Formats:** JSON standard, NDJSON (Newline Delimited JSON per streaming), o CSV (appiattendo gli oggetti).

-----

## 4\. Requisiti Non Funzionali (Qualità del sistema)

Questi requisiti definiscono "come" il sistema deve comportarsi.

  * **Determinismo (Seeding):** Deve essere possibile fornire un "seed" (seme). A parità di schema, seed e prompt, il sistema deve generare **sempre lo stesso output**. Fondamentale per i test di regressione.
  * **Resilienza:** Se l'LLM genera un JSON malformato o che non rispetta lo schema, il sistema deve avere un meccanismo di *retry* (riprova) automatico o di *fallback* (ripiego) sulla generazione algoritmica standard, avvisando l'utente.
  * **Performance:**
      * La generazione algoritmica deve essere istantanea (ms).
      * La generazione AI deve mostrare un feedback di caricamento (spinner) e gestire timeout.
  * **Privacy:** Se si usano LLM remoti, il tool non deve inviare dati sensibili dell'utente, ma solo la struttura (schema) e il prompt generico.

-----

## 5\. Esempio di Utilizzo Avanzato

Immagina di dover testare un'app di recensioni di ristoranti.

**Schema Input (`review_schema.json`):**

```json
{
  "type": "object",
  "properties": {
    "restaurant_name": { "type": "string" },
    "rating": { "type": "integer", "minimum": 1, "maximum": 5 },
    "comment": { "type": "string", "maxLength": 200 },
    "visit_date": { "type": "string", "format": "date" }
  },
  "required": ["restaurant_name", "rating", "comment"]
}
```

**Comando:**
`mockgen --schema review_schema.json --ai --prompt "Ristoranti italiani di lusso con servizio pessimo"`

**Risultato Atteso (Generato da LLM):**

```json
[
  {
    "restaurant_name": "La Trattoria Dorata",
    "rating": 2,
    "comment": "Cibo squisito ma abbiamo aspettato un'ora per l'antipasto. Il cameriere è stato scortese.",
    "visit_date": "2023-10-15"
  },
  {
    "restaurant_name": "Velluto & Vino",
    "rating": 1,
    "comment": "Prezzi esorbitanti per porzioni minuscole. Mai più.",
    "visit_date": "2023-11-02"
  }
]
```


## Struttura Esempio di Progetto
.
├── src/
│   ├── mockgen/
│   ├── generators/
│   └── ...
├── tests/
│   └── test_generators.py
├── features/                 ← cartella per i test behave
│   ├── schema_generation.feature
│   └── steps/
│       └── test_schema_steps.py
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml
