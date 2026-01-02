## Test LLM: JSON-only (black-box) + white-box

Questa repo contiene due famiglie di test per l’endpoint `POST /ai`.

### 1) Black-box (contract + qualità)
- Verifica che il modello risponda **solo con JSON valido** (niente testo, niente markdown).
- Esegue controlli di schema (es. 10 record IoT, 3 items in orders, ecc.).
- Usa **DeepEval** come segnale “soft” di qualità (relevancy/hallucination), con un judge locale via Ollama.

> Nota: DeepEval è un framework di evaluation per LLM. “Eval” = valutazione automatica della qualità dell’output (coerenza con input, allucinazioni, ecc.) tramite metriche.

### 2) White-box (internals + branching)
I test white-box non dipendono dal modello reale: patchano la funzione LLM (`generateMock`) e controllano i rami interni della route:
- creazione/riuso sessione (`chat_sessions`)
- system prompt **forzato** (`DEFAULT_SYSTEM_PROMPT`)
- crescita history (user/assistant)
- parsing e normalizzazione JSON (`items`)
- fallback quando l’output non è JSON
- gestione eccezioni (500 + payload error)

### Esecuzione
- Black-box: `deepeval test run tests/testLlm/test_deepeval_json_only.py`
- White-box: pytest -q -s tests/testLlm/test_ai_whitebox.py

