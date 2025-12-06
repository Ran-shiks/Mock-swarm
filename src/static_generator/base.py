from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseGenerator(ABC):
    """
    Classe base astratta per tutte le strategie di generazione.
    """

    @abstractmethod
    def generate(self, schema: Dict[str, Any], context: Optional[str] = None) -> Any:
        """
        Genera dati basati su uno schema.
        
        Args:
            schema: Il dizionario del JSON Schema.
            context: (Opzionale) Prompt o contesto extra, usato principalmente dai generatori AI.
            
        Returns:
            Dati generati (dict, list, string, etc.)
        """
        pass

class FieldGenerator:
    def __init__(self, field_name, field_props):
        self.name = field_name
        self.props = field_props

    def generate(self):
        raise NotImplementedError("Implementare il metodo generate.")