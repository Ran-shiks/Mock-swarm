"""
LLM Module - Supporto per l'integrazione di Large Language Models.

Questo modulo fornisce un'interfaccia comune per interagire con diversi
provider di LLM (OpenAI, Anthropic, Ollama, ecc.) per la generazione di dati mock.
"""

from .v2olama_chat import V2OlamaChat
from . import v2Olama

__all__ = ['V2OlamaChat', 'v2Olama']
