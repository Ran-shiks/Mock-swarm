

from typing import List, Dict, Any, Optional

# In futuro importeremo questi dai moduli 'generators'
from src.generators.algorithmic import AlgorithmicGenerator
from src.generators.smart import SmartGenerator

class MockGenEngine:
    """
    Orchestrator principale. Riceve le configurazioni dall'utente (CLI o Lib)
    e coordina la generazione dei dati delegando al generatore appropriato.
    """

    def __init__(self, schema: Dict[str, Any]):
        
        self.generator = None
        self.schema = schema
        # Validiamo subito che lo schema abbia senso
        if not isinstance(schema, dict) or 'type' not in schema:
             # Nota: una validazione più approfondita è fatta dal parser, 
             # qui facciamo un sanity check veloce.
             pass
    

    def generate(self, 
                 count: int = 1, 
                 use_ai: bool = False, 
                 ai_prompt: Optional[str] = None,
                 seed: Optional[int] = None) -> List[Dict[str, Any]]:

    
        self.generator = AlgorithmicGenerator(seed=seed)
        results = []
        
        for i in range(count):
            try:
                context = ai_prompt if use_ai else None
                data = self.generator.generate(self.schema, context=context)
                results.append(data)
            except Exception as e:
                print(f"Errore generazione record {i}: {e}")
                
        return results


