

from typing import List, Dict, Any, Optional

# In futuro importeremo questi dai moduli 'generators'
# from mockgen.generators.algorithmic import AlgorithmicGenerator
# from mockgen.generators.smart import SmartGenerator

class MockGenEngine:
    """
    Orchestrator principale. Riceve le configurazioni dall'utente (CLI o Lib)
    e coordina la generazione dei dati delegando al generatore appropriato.
    """

    def __init__(self, schema: Dict[str, Any]):
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
        """
        Esegue il loop di generazione.
        
        Args:
            count: Numero di record da generare.
            use_ai: Se True, usa il generatore LLM. Altrimenti usa quello algoritmico.
            ai_prompt: Contesto opzionale per l'AI.
            seed: Seme per la riproducibilità (usato principalmente nell'algoritmico).
        
        Returns:
            Una lista di dizionari (i dati generati).
        """
        
        # 1. Selezione della Strategia (Strategy Pattern)
        generator = self._get_generator_strategy(use_ai, seed)

        results = []

        # 2. Loop di generazione
        # Nota: Se usiamo l'AI, potremmo voler ottimizzare inviando una richiesta batch
        # invece che un loop, ma per ora manteniamo la logica semplice.
        for i in range(count):
            try:
                # Passiamo il prompt solo se siamo in modalità AI
                context = ai_prompt if use_ai else None
                
                # Chiamata polimorfica: entrambi i generatori avranno un metodo .generate()
                # data = generator.generate(self.schema, context=context)
                
                # --- MOCK TEMPORANEO PER FAR FUNZIONARE I TEST DI BASE ---
                data = self._mock_generation(self.schema, i) 
                # ---------------------------------------------------------
                
                results.append(data)
            except Exception as e:
                # Qui gestiremo eventuali errori di generazione (es. timeout AI)
                print(f"Errore nella generazione del record {i+1}: {e}")
                # Opzionale: implementare logica di retry o fallback qui
        
        return results

    def _get_generator_strategy(self, use_ai: bool, seed: Optional[int]):
        """
        Factory method che istanzia il generatore corretto.
        """
        if use_ai:
            # return SmartGenerator(api_key=..., provider=...)
            return "SmartGeneratorInstance" # Placeholder
        else:
            # return AlgorithmicGenerator(seed=seed)
            return "AlgorithmicGeneratorInstance" # Placeholder

    def _mock_generation(self, schema, index):
        """
        Metodo temporaneo per non far crashare il codice finché non
        implementiamo la cartella /generators.
        """
        return {"id": index, "mock": "data", "info": "Generators not implemented yet"}


'''

    # Aggiorna il metodo _get_generator_strategy
    def _get_generator_strategy(self, use_ai: bool, seed: Optional[int]):
        if use_ai:
            return SmartGenerator() # In futuro passeremo config
        else:
            return AlgorithmicGenerator(seed=seed)

    # Aggiorna il metodo generate rimuovendo il _mock_generation
    def generate(self, count: int = 1, use_ai: bool = False, ai_prompt: Optional[str] = None, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        generator = self._get_generator_strategy(use_ai, seed)
        results = []
        
        for i in range(count):
            try:
                context = ai_prompt if use_ai else None
                # ORA FUNZIONA VERAMENTE:
                data = generator.generate(self.schema, context=context)
                results.append(data)
            except Exception as e:
                print(f"Errore generazione record {i}: {e}")
                
        return results
'''
