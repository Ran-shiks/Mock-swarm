Questa repository contiene tre livelli di test per l’endpoint POST /ai e per i componenti LLM associati.

L’approccio è stratificato per separare chiaramente:

contratto esterno dell’API

logica interna dell’applicazione

comportamento dei singoli componenti

1) Black-box (contract + qualità)

I test black-box trattano il sistema come una scatola nera, senza alcuna conoscenza dell’implementazione interna.

Verifica che il modello risponda esclusivamente con JSON valido
(nessun testo extra, nessun markdown, nessun backtick).

Controlli di schema e vincoli strutturali, ad esempio:

utenti e-commerce (campi obbligatori)

payload ordini (3 items + total)

errori HTTP strutturati

JSON profondamente annidati

dataset IoT con 10 record

Verifica della tenuta del contratto JSON-only anche in sessioni multi-turn.

Utilizzo di DeepEval come segnale soft di qualità
(relevancy, assenza di allucinazioni), con judge locale via Ollama.

Nota
DeepEval è un framework di evaluation per LLM.
“Eval” indica la valutazione automatica della qualità dell’output (coerenza con l’input, rilevanza semantica, allucinazioni) tramite metriche basate su modelli di giudizio.

2) White-box (internals + branching)

I test white-box verificano il comportamento interno dell’endpoint /ai, indipendentemente dal modello reale.

Il modello LLM viene mockato (patch di generateMock) per rendere i test deterministici e riproducibili.

Vengono verificati esplicitamente i principali rami logici:

creazione e riuso delle sessioni (chat_sessions)

system prompt forzato (DEFAULT_SYSTEM_PROMPT)

crescita corretta della history (user / assistant)

parsing e normalizzazione del JSON (items)

fallback corretto quando l’output non è JSON

gestione delle eccezioni del modello
(HTTP 500 + payload di errore coerente)

Questi test garantiscono che la logica applicativa sia corretta e robusta anche in presenza di output anomali del modello.

3) Unit test (componenti LLM)

I test unitari isolano i singoli componenti senza passare dall’API HTTP.

In particolare, vengono testate le funzionalità della classe V2OlamaChat:

crescita corretta della history ad ogni messaggio

impostazione e modifica del system prompt (set_system)

reset completo dello stato (reset)

corretto passaggio di system, prompt e temperature alla funzione LLM (generateMock)

Il modello LLM è sempre mockato, quindi:

nessuna chiamata di rete

nessuna dipendenza da Ollama

test rapidi, deterministici e ripetibili

Questi test garantiscono la correttezza del comportamento locale dei componenti LLM.

Esecuzione

Black-box (DeepEval)

deepeval test run tests/testLlm/test_deepeval_json_only.py


White-box (pytest)

pytest -q -s tests/testLlm/test_ai_whitebox.py


Unit test (pytest)

pytest -q tests/testLlm/test_v2olama_chat_unit.py