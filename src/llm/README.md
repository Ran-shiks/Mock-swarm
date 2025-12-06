# Modulo LLM - Large Language Models Integration

Questo modulo fornisce un'interfaccia flessibile e estensibile per l'integrazione di Large Language Models (LLM) nel progetto Mock-swarm.

## Caratteristiche

- ✅ **Architettura modulare** con interfaccia base astratta
- ✅ **Supporto per Llama** tramite Ollama (locale e privacy-friendly)
- ✅ **Scelta flessibile del modello** - l'utente decide quale modello utilizzare
- ✅ **Factory pattern** per creazione semplificata delle istanze
- ✅ **Generazione di testo** semplice
- ✅ **Generazione di JSON strutturato** guidata da schema
- ✅ **Configurazione tramite codice o variabili d'ambiente**
- ✅ **Estensibile** - facile aggiungere nuovi provider (OpenAI, Anthropic, ecc.)

## Installazione

Il modulo richiede la libreria `requests`:

```bash
pip install requests
```

Per utilizzare Llama localmente, è necessario avere Ollama installato e in esecuzione:

```bash
# Installa Ollama (vedi https://ollama.ai)
curl https://ollama.ai/install.sh | sh

# Scarica un modello Llama
ollama pull llama2
ollama pull llama3
ollama pull codellama
```

## Utilizzo Base

### Inizializzazione diretta

```python
from src.llm import LlamaLLM

# Inizializzazione con modello predefinito (llama2)
llm = LlamaLLM()

# Inizializzazione con modello scelto dall'utente
llm = LlamaLLM(model_name="llama3")
llm = LlamaLLM(model_name="codellama:7b")
llm = LlamaLLM(model_name="llama2:13b")
```

### Uso della Factory

```python
from src.llm import LLMFactory

# Creazione con provider e modello
llm = LLMFactory.create(
    provider='llama',
    model_name='llama3'
)

# Creazione da configurazione
config = {
    'provider': 'llama',
    'model_name': 'llama2:13b',
    'base_url': 'http://localhost:11434',
    'timeout': 60
}
llm = LLMFactory.create_from_config(config)
```

## Modelli Llama Supportati

Il modulo supporta tutti i modelli disponibili in Ollama, inclusi:

- **llama2** (7B parameters, default)
- **llama2:13b** (13B parameters)
- **llama2:70b** (70B parameters)
- **llama3** (latest Llama 3 version)
- **codellama** (specialized for code)
- **codellama:7b**, **codellama:13b**, **codellama:34b**

L'utente può scegliere qualsiasi modello disponibile in Ollama.

## Esempi di Utilizzo

### Generazione di Testo

```python
from src.llm import LlamaLLM

llm = LlamaLLM(model_name="llama2")

testo = llm.generate(
    prompt="Descrivi un prodotto sportivo innovativo",
    temperature=0.7,
    max_tokens=200
)

print(testo)
```

### Generazione di JSON Strutturato

```python
from src.llm import LlamaLLM

llm = LlamaLLM(model_name="llama2")

schema = {
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "price": {"type": "number"},
        "category": {"type": "string"},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5}
    }
}

data = llm.generate_json(
    prompt="Genera dati per un prodotto tecnologico",
    schema=schema
)

print(data)
# Output: {"product_name": "Laptop Pro", "price": 1299.99, ...}
```

### Verifica Disponibilità

```python
from src.llm import LlamaLLM

llm = LlamaLLM(model_name="llama3")

if llm.is_available():
    print("Llama è disponibile!")
    
    # Ottieni lista modelli disponibili
    models = llm.get_available_models()
    print("Modelli disponibili:", models)
else:
    print("Llama non disponibile. Avvia Ollama e scarica il modello.")
```

### Configurazione tramite Variabili d'Ambiente

```python
import os
from src.llm import LLMFactory

# Configura tramite variabili d'ambiente
os.environ['LLM_PROVIDER'] = 'llama'
os.environ['LLAMA_MODEL'] = 'codellama'

# La factory usa automaticamente le variabili d'ambiente
llm = LLMFactory.create()
print(llm.get_model_name())  # Output: codellama
```

## Architettura

### Classe Base: `BaseLLM`

Interfaccia astratta che definisce il contratto per tutti i provider LLM:

- `generate(prompt, schema, temperature, max_tokens)` - Genera testo
- `generate_json(prompt, schema, temperature)` - Genera JSON strutturato
- `is_available()` - Verifica disponibilità del provider

### Implementazione: `LlamaLLM`

Implementazione concreta per modelli Llama tramite Ollama:

- Supporto per tutti i modelli Ollama
- Lazy loading delle dipendenze
- Gestione errori e fallback
- Parsing automatico di JSON da risposte markdown

### Factory: `LLMFactory`

Pattern Factory per creare istanze LLM:

- `create(provider, model_name, **kwargs)` - Crea provider specifico
- `create_from_config(config)` - Crea da dizionario
- `register_provider(name, class)` - Registra provider personalizzato
- `get_available_providers()` - Lista provider disponibili

## Estensione con Nuovi Provider

È facile aggiungere supporto per nuovi provider LLM:

```python
from src.llm import BaseLLM, LLMFactory

class OpenAILLM(BaseLLM):
    def generate(self, prompt, **kwargs):
        # Implementazione per OpenAI
        pass
    
    def generate_json(self, prompt, schema, **kwargs):
        # Implementazione per OpenAI
        pass
    
    def is_available(self):
        # Verifica API key, ecc.
        pass

# Registra il nuovo provider
LLMFactory.register_provider('openai', OpenAILLM)

# Usa il nuovo provider
llm = LLMFactory.create('openai', model_name='gpt-4')
```

## Gestione Errori

Il modulo fornisce eccezioni specifiche:

- `LLMError` - Errore generico LLM (connessione, API, ecc.)
- `ValidationError` - Errore di validazione JSON/schema

```python
from src.llm import LlamaLLM, LLMError, ValidationError

llm = LlamaLLM()

try:
    result = llm.generate_json(prompt, schema)
except ValidationError as e:
    print(f"JSON non valido: {e}")
except LLMError as e:
    print(f"Errore LLM: {e}")
```

## Testing

Il modulo include una suite completa di unit test:

```bash
# Esegui i test
pytest tests/test_llm.py -v

# Test con coverage
pytest tests/test_llm.py --cov=src/llm
```

## Esempi Completi

Vedi il file `src/llm_examples.py` per esempi completi di tutti i casi d'uso.

```bash
# Esegui gli esempi
python src/llm_examples.py
```

## Configurazione Ollama

### Avvio di Ollama

```bash
# Avvia il servizio Ollama (default: http://localhost:11434)
ollama serve
```

### Gestione Modelli

```bash
# Scarica un modello
ollama pull llama2
ollama pull llama3
ollama pull codellama

# Lista modelli installati
ollama list

# Rimuovi un modello
ollama rm llama2
```

### Configurazione Custom

```python
# Usa Ollama su porta/host diverso
llm = LlamaLLM(
    model_name="llama2",
    base_url="http://192.168.1.100:11434",
    timeout=120
)
```

## Best Practices

1. **Scegli il modello appropriato**:
   - `llama2` (7B): Veloce, uso generale
   - `llama2:13b`: Bilanciamento qualità/velocità
   - `llama2:70b`: Massima qualità (richiede hardware potente)
   - `codellama`: Specializzato per codice

2. **Gestisci la disponibilità**:
   ```python
   if not llm.is_available():
       # Fallback a generazione algoritmica
       pass
   ```

3. **Ottimizza i prompt per JSON**:
   - Fornisci sempre uno schema chiaro
   - Usa temperature più basse (0.3-0.5) per output deterministico
   - Gestisci eccezioni `ValidationError`

4. **Timeout appropriati**:
   - Modelli più grandi richiedono più tempo
   - Usa timeout di almeno 60-120 secondi

## Roadmap

Future implementazioni previste:

- [ ] Supporto OpenAI (GPT-4, GPT-3.5)
- [ ] Supporto Anthropic (Claude)
- [ ] Retry automatico con exponential backoff
- [ ] Caching delle risposte
- [ ] Streaming delle risposte
- [ ] Batching di richieste multiple
- [ ] Metriche e logging avanzato

## Licenza

Vedi LICENSE nel repository principale.
