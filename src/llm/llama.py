"""
Implementazione del provider LLM per Llama tramite Ollama.

Questo modulo fornisce l'integrazione con modelli Llama eseguiti localmente
tramite Ollama o altri runtime compatibili.
"""

import json
import logging
from typing import Dict, Any, Optional
from .base import BaseLLM, LLMError, ValidationError

logger = logging.getLogger(__name__)


class LlamaLLM(BaseLLM):
    """
    Provider LLM per modelli Llama.
    
    Supporta l'esecuzione di modelli Llama tramite Ollama o API compatibili.
    Il modello specifico viene scelto dall'utente durante l'inizializzazione.
    
    Esempi di modelli supportati:
    - llama2
    - llama2:13b
    - llama2:70b
    - llama3
    - codellama
    """
    
    def __init__(
        self,
        model_name: str = "llama2",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        **kwargs
    ):
        """
        Inizializza il provider Llama.
        
        Args:
            model_name: Nome del modello Llama da utilizzare (es: "llama2", "llama3", "codellama")
            base_url: URL base dell'API Ollama (default: localhost)
            timeout: Timeout in secondi per le richieste API
            **kwargs: Parametri aggiuntivi
        """
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = None
        
        logger.info(f"Inizializzazione LlamaLLM con modello: {model_name}")
    
    def _get_client(self):
        """
        Lazy initialization del client Ollama.
        
        Returns:
            Client Ollama configurato
            
        Raises:
            LLMError: Se Ollama non è disponibile
        """
        if self._client is None:
            try:
                # Importazione lazy per evitare dipendenze obbligatorie
                import requests
                self._client = requests
            except ImportError:
                raise LLMError(
                    "Il pacchetto 'requests' è richiesto per usare LlamaLLM. "
                    "Installalo con: pip install requests"
                )
        return self._client
    
    def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Genera testo usando il modello Llama.
        
        Args:
            prompt: Il prompt da inviare al modello
            schema: Schema JSON opzionale per guidare la generazione
            temperature: Temperatura per il sampling (default: 0.7)
            max_tokens: Numero massimo di token (opzionale)
            **kwargs: Parametri aggiuntivi per Ollama
            
        Returns:
            Il testo generato
            
        Raises:
            LLMError: Se si verifica un errore durante la generazione
        """
        client = self._get_client()
        
        # Prepara il prompt con lo schema se fornito
        full_prompt = prompt
        if schema:
            schema_str = json.dumps(schema, indent=2)
            full_prompt = (
                f"{prompt}\n\n"
                f"Genera una risposta che rispetti il seguente schema JSON:\n"
                f"{schema_str}"
            )
        
        # Prepara i parametri per Ollama
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        # Aggiungi parametri aggiuntivi
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            logger.debug(f"Invio richiesta a Ollama: {self.base_url}/api/generate")
            response = client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Errore nella generazione con Llama: {e}")
            raise LLMError(f"Errore nella generazione: {str(e)}")
    
    def generate_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Genera un oggetto JSON usando il modello Llama.
        
        Args:
            prompt: Il contesto per la generazione
            schema: Schema JSON che definisce la struttura
            temperature: Temperatura per il sampling
            **kwargs: Parametri aggiuntivi
            
        Returns:
            Oggetto Python generato
            
        Raises:
            LLMError: Se si verifica un errore
            ValidationError: Se l'output non è un JSON valido
        """
        # Costruisce un prompt ottimizzato per la generazione JSON
        json_prompt = (
            f"{prompt}\n\n"
            f"Genera SOLO un oggetto JSON valido che rispetti questo schema:\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"Rispondi SOLO con il JSON, senza testo aggiuntivo."
        )
        
        # Genera il testo
        response_text = self.generate(
            json_prompt,
            schema=None,  # Schema già incluso nel prompt
            temperature=temperature,
            **kwargs
        )
        
        # Prova a estrarre e parsare il JSON
        try:
            # Cerca di estrarre JSON dalla risposta
            response_text = response_text.strip()
            
            # Rimuovi eventuali markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Rimuovi prima e ultima riga (``` markers)
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = "\n".join(lines)
            
            # Parse JSON
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Risposta non è un JSON valido: {response_text[:200]}")
            raise ValidationError(
                f"Il modello non ha generato un JSON valido: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """
        Verifica se Ollama è disponibile e il modello è accessibile.
        
        Returns:
            True se disponibile, False altrimenti
        """
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            # Verifica se il modello richiesto è disponibile
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Controlla sia il nome esatto che con tag implicito
            available = (
                self.model_name in model_names or
                f"{self.model_name}:latest" in model_names or
                any(m.startswith(f"{self.model_name}:") for m in model_names)
            )
            
            if not available:
                logger.warning(
                    f"Modello '{self.model_name}' non trovato. "
                    f"Modelli disponibili: {model_names}"
                )
            
            return available
            
        except Exception as e:
            logger.debug(f"Ollama non disponibile: {e}")
            return False
    
    def get_available_models(self) -> list:
        """
        Ottiene la lista dei modelli disponibili in Ollama.
        
        Returns:
            Lista di nomi di modelli disponibili
            
        Raises:
            LLMError: Se non è possibile connettersi a Ollama
        """
        try:
            client = self._get_client()
            response = client.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [m.get("name", "") for m in models]
            
        except Exception as e:
            raise LLMError(f"Impossibile ottenere i modelli: {str(e)}")
