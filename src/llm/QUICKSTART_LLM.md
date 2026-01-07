# Quick Start Guide - Modulo LLM

## Installazione e Setup

### 1. Installa Ollama (per usare Llama localmente)

```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Oppure visita: https://ollama.ai
```

### 2. Scarica un modello Llama

```bash
# Modello base (consigliato per iniziare)
ollama pull llama2

# Altri modelli disponibili:
ollama pull llama3
ollama pull llama2:13b
ollama pull llama2:70b
ollama pull codellama
```

### 3. Avvia Ollama

```bash
ollama serve
# Server disponibile su http://localhost:11434
```

## Utilizzo Veloce

### Esempio 1: Inizializzazione Base

```python
from src.llm import LlamaLLM

# Crea un'istanza con il modello che preferisci
llm = LlamaLLM(model_name="llama2")  # o "llama3", "codellama", ecc.

# Verifica che sia disponibile
if llm.is_available():
    print("✓ Llama pronto!")
else:
    print("✗ Ollama non disponibile. Avvia il servizio.")
```

### Esempio 2: Scelta del Modello

```python
from src.llm import LlamaLLM

# TU scegli il modello!
modello = "llama3"  # Cambia questo con il modello che preferisci

llm = LlamaLLM(model_name=modello)
print(f"Usando modello: {llm.get_model_name()}")
```

### Esempio 3: Generazione di Testo

```python
from src.llm import LlamaLLM

llm = LlamaLLM(model_name="llama2")

prompt = "Descrivi un prodotto innovativo per lo sport"
testo = llm.generate(prompt, temperature=0.7)

print(testo)
```

### Esempio 4: Generazione JSON per Mock Data

```python
from src.llm import LlamaLLM

llm = LlamaLLM(model_name="llama2")

# Schema per i dati mock
schema = {
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "price": {"type": "number"},
        "category": {"type": "string"},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5}
    }
}

# Genera dati mock realistici
data = llm.generate_json(
    prompt="Genera dati per un prodotto elettronico di consumo",
    schema=schema
)

print(data)
# Output: {"product_name": "Smartphone XYZ", "price": 799.99, ...}
```

### Esempio 5: Uso della Factory

```python
from src.llm import LLMFactory

# Metodo 1: Creazione diretta
llm = LLMFactory.create('llama', model_name='llama3')

# Metodo 2: Da configurazione
config = {
    'provider': 'llama',
    'model_name': 'codellama',
    'base_url': 'http://localhost:11434',
    'timeout': 60
}
llm = LLMFactory.create_from_config(config)
```

## Modelli Disponibili

Puoi usare qualsiasi modello disponibile in Ollama:

| Modello | Dimensione | Uso Consigliato |
|---------|-----------|------------------|
| llama2 | 7B | General purpose, veloce |
| llama2:13b | 13B | Migliore qualità |
| llama2:70b | 70B | Massima qualità (richiede GPU) |
| llama3 | Varia | Ultima versione |
| codellama | 7B-34B | Generazione di codice |

```python
# Vedi modelli installati
ollama list

# Usa quello che preferisci
llm = LlamaLLM(model_name="il-tuo-modello-preferito")
```

## Configurazione Avanzata

### Custom URL e Timeout

```python
llm = LlamaLLM(
    model_name="llama2",
    base_url="http://192.168.1.100:11434",  # Server remoto
    timeout=120  # Timeout in secondi
)
```

### Variabili d'Ambiente

```python
import os
from src.llm import LLMFactory

# Configura via env vars
os.environ['LLM_PROVIDER'] = 'llama'
os.environ['LLAMA_MODEL'] = 'llama3'

# Usa automaticamente le variabili
llm = LLMFactory.create()
```

## Gestione Errori

```python
from src.llm import LlamaLLM, LLMError, ValidationError

llm = LlamaLLM()

try:
    data = llm.generate_json(prompt, schema)
except ValidationError:
    print("JSON generato non valido, riprovo...")
    # Fallback a generazione algoritmica
except LLMError as e:
    print(f"Errore LLM: {e}")
    # Usa metodo alternativo
```

## Troubleshooting

### "Il modello non è disponibile"

```bash
# Scarica il modello
ollama pull llama2

# Verifica che sia installato
ollama list
```

### "Connection refused"

```bash
# Assicurati che Ollama sia in esecuzione
ollama serve
```

### "requests module not found"

```bash
pip install requests
```

## Prossimi Passi

1. ✅ Modulo LLM installato e funzionante
2. 🔄 Integra l'LLM nel generatore di dati mock
3. 🔄 Implementa altri provider (OpenAI, Anthropic) se necessario

## Risorse

- **Documentazione completa**: `src/llm/README.md`
- **Esempi dettagliati**: `src/llm_examples.py`
- **Test**: `tests/test_llm.py`
- **Ollama**: https://ollama.ai
