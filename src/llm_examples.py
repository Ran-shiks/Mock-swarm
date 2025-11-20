"""
Esempi di utilizzo del modulo LLM.

Questo file mostra come utilizzare le classi LLM per inizializzare
e utilizzare Llama (o altri modelli) nel progetto.
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import LlamaLLM, LLMFactory

# ==============================================================================
# Esempio 1: Inizializzazione diretta di LlamaLLM con modello predefinito
# ==============================================================================

def esempio_1_inizializzazione_base():
    """Inizializzazione base con il modello Llama predefinito."""
    print("=== Esempio 1: Inizializzazione Base ===")
    
    # Il modello di default è "llama2"
    llm = LlamaLLM()
    
    print(f"Modello: {llm.get_model_name()}")
    print(f"URL: {llm.base_url}")
    print(f"Disponibile: {llm.is_available()}")
    print()


# ==============================================================================
# Esempio 2: Scelta del modello Llama personalizzato
# ==============================================================================

def esempio_2_modello_personalizzato():
    """Inizializzazione con modello Llama specifico scelto dall'utente."""
    print("=== Esempio 2: Modello Personalizzato ===")
    
    # L'utente può scegliere il modello che preferisce
    modelli_disponibili = [
        "llama2",
        "llama2:13b",
        "llama2:70b",
        "llama3",
        "codellama",
        "codellama:7b",
    ]
    
    # Esempio: scelta del modello llama3
    modello_scelto = "llama3"
    llm = LlamaLLM(model_name=modello_scelto)
    
    print(f"Modello scelto: {llm.get_model_name()}")
    print()


# ==============================================================================
# Esempio 3: Configurazione completa con parametri personalizzati
# ==============================================================================

def esempio_3_configurazione_completa():
    """Inizializzazione con configurazione personalizzata completa."""
    print("=== Esempio 3: Configurazione Completa ===")
    
    llm = LlamaLLM(
        model_name="llama2:13b",
        base_url="http://localhost:11434",
        timeout=60
    )
    
    print(f"Modello: {llm.get_model_name()}")
    print(f"URL: {llm.base_url}")
    print(f"Timeout: {llm.timeout}")
    print()


# ==============================================================================
# Esempio 4: Uso della Factory per creare l'LLM
# ==============================================================================

def esempio_4_uso_factory():
    """Uso della Factory per creare istanze LLM in modo flessibile."""
    print("=== Esempio 4: Uso della Factory ===")
    
    # Creazione con provider e modello specifici
    llm1 = LLMFactory.create(
        provider='llama',
        model_name='codellama'
    )
    print(f"LLM 1 - Modello: {llm1.get_model_name()}")
    
    # Creazione con configurazione da dizionario
    config = {
        'provider': 'llama',
        'model_name': 'llama2:13b',
        'base_url': 'http://localhost:11434',
        'timeout': 90
    }
    llm2 = LLMFactory.create_from_config(config)
    print(f"LLM 2 - Modello: {llm2.get_model_name()}")
    print()


# ==============================================================================
# Esempio 5: Verifica disponibilità modelli
# ==============================================================================

def esempio_5_verifica_disponibilita():
    """Verifica quali modelli sono disponibili in Ollama."""
    print("=== Esempio 5: Verifica Disponibilità ===")
    
    llm = LlamaLLM()
    
    # Verifica se il modello configurato è disponibile
    if llm.is_available():
        print(f"✓ Il modello '{llm.get_model_name()}' è disponibile")
        
        # Ottieni lista di tutti i modelli disponibili
        try:
            modelli = llm.get_available_models()
            print(f"\nModelli disponibili in Ollama:")
            for modello in modelli:
                print(f"  - {modello}")
        except Exception as e:
            print(f"⚠ Impossibile ottenere la lista dei modelli: {e}")
    else:
        print(f"✗ Il modello '{llm.get_model_name()}' non è disponibile")
        print("Assicurati che Ollama sia in esecuzione e che il modello sia scaricato.")
    print()


# ==============================================================================
# Esempio 6: Generazione di testo con Llama
# ==============================================================================

def esempio_6_generazione_testo():
    """Esempio di generazione di testo con Llama."""
    print("=== Esempio 6: Generazione di Testo ===")
    
    llm = LlamaLLM(model_name="llama2")
    
    if llm.is_available():
        prompt = "Descrivi un prodotto innovativo per lo sport invernale"
        
        try:
            testo_generato = llm.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )
            print(f"Prompt: {prompt}")
            print(f"\nRisposta:\n{testo_generato}")
        except Exception as e:
            print(f"Errore nella generazione: {e}")
    else:
        print("Llama non disponibile. Simulazione della risposta...")
    print()


# ==============================================================================
# Esempio 7: Generazione di JSON strutturato
# ==============================================================================

def esempio_7_generazione_json():
    """Esempio di generazione di dati JSON strutturati."""
    print("=== Esempio 7: Generazione JSON Strutturato ===")
    
    llm = LlamaLLM(model_name="llama2")
    
    # Schema JSON che definisce la struttura desiderata
    schema = {
        "type": "object",
        "properties": {
            "product_name": {"type": "string"},
            "category": {"type": "string"},
            "price": {"type": "number"},
            "rating": {"type": "integer", "minimum": 1, "maximum": 5}
        },
        "required": ["product_name", "category", "price"]
    }
    
    if llm.is_available():
        prompt = "Genera dati per un prodotto di elettronica di consumo"
        
        try:
            json_generato = llm.generate_json(
                prompt=prompt,
                schema=schema,
                temperature=0.7
            )
            print(f"Prompt: {prompt}")
            print(f"\nJSON generato:")
            import json
            print(json.dumps(json_generato, indent=2))
        except Exception as e:
            print(f"Errore nella generazione: {e}")
    else:
        print("Llama non disponibile. Esempio di output atteso:")
        print('''{
  "product_name": "Smartphone XYZ Pro",
  "category": "Elettronica",
  "price": 799.99,
  "rating": 4
}''')
    print()


# ==============================================================================
# Esempio 8: Configurazione tramite variabili d'ambiente
# ==============================================================================

def esempio_8_variabili_ambiente():
    """Uso di variabili d'ambiente per configurare l'LLM."""
    print("=== Esempio 8: Variabili d'Ambiente ===")
    
    import os
    
    # Imposta le variabili d'ambiente
    os.environ['LLM_PROVIDER'] = 'llama'
    os.environ['LLAMA_MODEL'] = 'codellama'
    
    # La factory usa automaticamente le variabili d'ambiente
    llm = LLMFactory.create()
    
    print(f"Provider: llama")
    print(f"Modello: {llm.get_model_name()}")
    print()


# ==============================================================================
# Main: Esegui tutti gli esempi
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ESEMPI DI UTILIZZO DEL MODULO LLM")
    print("=" * 80)
    print()
    
    esempio_1_inizializzazione_base()
    esempio_2_modello_personalizzato()
    esempio_3_configurazione_completa()
    esempio_4_uso_factory()
    esempio_5_verifica_disponibilita()
    esempio_6_generazione_testo()
    esempio_7_generazione_json()
    esempio_8_variabili_ambiente()
    
    print("=" * 80)
    print("Fine degli esempi")
    print("=" * 80)
