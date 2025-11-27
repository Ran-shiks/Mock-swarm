"""
LLM Module - Supporto per l'integrazione di Large Language Models.

Questo modulo fornisce un'interfaccia comune per interagire con diversi
provider di LLM (OpenAI, Anthropic, Ollama, ecc.) per la generazione di dati mock.
"""

from .base import BaseLLM
from .llama import LlamaLLM
from .factory import LLMFactory

__all__ = ['BaseLLM', 'LlamaLLM', 'LLMFactory']
