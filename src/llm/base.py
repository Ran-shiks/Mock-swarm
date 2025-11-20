"""
Base class astratta per l'interfaccia LLM.

Definisce il contratto che tutti i provider LLM devono implementare.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseLLM(ABC):
    """
    Classe base astratta per tutti i provider LLM.
    
    Ogni provider LLM (OpenAI, Anthropic, Llama, ecc.) deve estendere
    questa classe e implementare i metodi astratti.
    """
    
    def __init__(self, model_name: str, **kwargs):
        """
        Inizializza il provider LLM.
        
        Args:
            model_name: Nome del modello da utilizzare
            **kwargs: Parametri aggiuntivi specifici del provider
        """
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Genera testo basato sul prompt fornito.
        
        Args:
            prompt: Il prompt da inviare al modello
            schema: Schema JSON opzionale per guidare la generazione strutturata
            temperature: Controllo della creatività (0.0 = deterministico, 1.0 = creativo)
            max_tokens: Numero massimo di token da generare
            **kwargs: Parametri aggiuntivi specifici del provider
            
        Returns:
            Il testo generato dal modello
            
        Raises:
            LLMError: Se si verifica un errore durante la generazione
        """
        pass
    
    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Genera un oggetto JSON basato sullo schema fornito.
        
        Args:
            prompt: Il contesto/prompt per la generazione
            schema: Schema JSON che definisce la struttura attesa
            temperature: Controllo della creatività
            **kwargs: Parametri aggiuntivi
            
        Returns:
            Oggetto Python (dict) generato conformemente allo schema
            
        Raises:
            LLMError: Se si verifica un errore durante la generazione
            ValidationError: Se l'output non rispetta lo schema
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se il provider LLM è disponibile e configurato correttamente.
        
        Returns:
            True se il provider è disponibile, False altrimenti
        """
        pass
    
    def get_model_name(self) -> str:
        """
        Restituisce il nome del modello configurato.
        
        Returns:
            Nome del modello
        """
        return self.model_name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Restituisce la configurazione del provider.
        
        Returns:
            Dictionary con la configurazione
        """
        return self.config.copy()


class LLMError(Exception):
    """Eccezione base per errori relativi agli LLM."""
    pass


class ValidationError(LLMError):
    """Eccezione per errori di validazione dello schema."""
    pass
