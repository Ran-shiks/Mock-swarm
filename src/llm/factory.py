"""
Factory per la creazione di istanze LLM.

Fornisce un'interfaccia semplice per istanziare il provider LLM corretto
in base alla configurazione o alle variabili d'ambiente.
"""

import os
import logging
from typing import Optional, Dict, Any
from .base import BaseLLM, LLMError
from .llama import LlamaLLM

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory per creare istanze di provider LLM.
    
    Supporta la creazione di provider basata su:
    - Specificazione esplicita del tipo
    - Variabili d'ambiente (LLM_PROVIDER)
    - Configurazione predefinita
    """
    
    # Mapping dei provider disponibili
    _providers = {
        'llama': LlamaLLM,
        'ollama': LlamaLLM,  # Alias per Llama
    }
    
    @classmethod
    def create(
        cls,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """
        Crea un'istanza del provider LLM specificato.
        
        Args:
            provider: Tipo di provider ('llama', 'openai', 'anthropic').
                     Se None, usa la variabile d'ambiente LLM_PROVIDER o default 'llama'
            model_name: Nome del modello da utilizzare.
                       Se None, usa il default del provider
            **kwargs: Parametri aggiuntivi specifici del provider
            
        Returns:
            Istanza del provider LLM configurato
            
        Raises:
            LLMError: Se il provider non è supportato
            
        Examples:
            >>> # Usa Llama con modello default
            >>> llm = LLMFactory.create('llama')
            
            >>> # Usa Llama con modello specifico
            >>> llm = LLMFactory.create('llama', model_name='llama2:13b')
            
            >>> # Usa variabile d'ambiente
            >>> os.environ['LLM_PROVIDER'] = 'llama'
            >>> llm = LLMFactory.create()
        """
        # Determina il provider da usare
        if provider is None:
            provider = os.getenv('LLM_PROVIDER', 'llama').lower()
        else:
            provider = provider.lower()
        
        logger.info(f"Creazione provider LLM: {provider}")
        
        # Verifica se il provider è supportato
        if provider not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise LLMError(
                f"Provider '{provider}' non supportato. "
                f"Provider disponibili: {available}"
            )
        
        # Ottiene la classe del provider
        provider_class = cls._providers[provider]
        
        # Determina il modello da usare
        if model_name is None:
            model_name = cls._get_default_model(provider)
        
        logger.info(f"Inizializzazione {provider} con modello: {model_name}")
        
        # Crea e restituisce l'istanza
        try:
            return provider_class(model_name=model_name, **kwargs)
        except Exception as e:
            raise LLMError(f"Errore nella creazione del provider {provider}: {str(e)}")
    
    @classmethod
    def _get_default_model(cls, provider: str) -> str:
        """
        Ottiene il nome del modello predefinito per un provider.
        
        Args:
            provider: Nome del provider
            
        Returns:
            Nome del modello predefinito
        """
        defaults = {
            'llama': os.getenv('LLAMA_MODEL', 'llama2'),
            'ollama': os.getenv('LLAMA_MODEL', 'llama2'),
        }
        return defaults.get(provider, 'llama2')
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Registra un nuovo provider LLM personalizzato.
        
        Args:
            name: Nome identificativo del provider
            provider_class: Classe che implementa BaseLLM
            
        Raises:
            ValueError: Se la classe non estende BaseLLM
            
        Examples:
            >>> class CustomLLM(BaseLLM):
            ...     # implementazione
            >>> LLMFactory.register_provider('custom', CustomLLM)
        """
        if not issubclass(provider_class, BaseLLM):
            raise ValueError(
                f"La classe {provider_class.__name__} deve estendere BaseLLM"
            )
        
        cls._providers[name.lower()] = provider_class
        logger.info(f"Provider '{name}' registrato con successo")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Ottiene la lista dei provider disponibili.
        
        Returns:
            Lista di nomi dei provider registrati
        """
        return list(cls._providers.keys())
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> BaseLLM:
        """
        Crea un provider LLM da un dizionario di configurazione.
        
        Args:
            config: Dizionario con chiavi 'provider', 'model_name' e parametri aggiuntivi
            
        Returns:
            Istanza del provider LLM configurato
            
        Examples:
            >>> config = {
            ...     'provider': 'llama',
            ...     'model_name': 'llama2:13b',
            ...     'base_url': 'http://localhost:11434',
            ...     'timeout': 60
            ... }
            >>> llm = LLMFactory.create_from_config(config)
        """
        provider = config.get('provider')
        model_name = config.get('model_name')
        
        # Estrae i parametri aggiuntivi
        kwargs = {k: v for k, v in config.items() 
                  if k not in ('provider', 'model_name')}
        
        return cls.create(provider=provider, model_name=model_name, **kwargs)
