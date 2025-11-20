import os
import json
from typing import List, Optional, Any

import requests

#guys, per funzionare abbiamo olama in locale che runna a questo indirizzo
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "127.0.0.1")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3") # questo è il modello che usiamo, abbastanza pesantuccio, circa 5g

class OlamaClient:
    """
    Client ottimizzato per interagire con un server Ollama locale.
    Prioritizza l'uso della libreria ollama-python con output JSON forzato.
    """

    def __init__(self, model: Optional[str] = None, host: str = OLLAMA_HOST, port: str = OLLAMA_PORT):
        self.model = model or LLM_MODEL
        self.base_url = f"http://{host}:{port}"
        # Se la libreria ollama è disponibile, la inizializziamo
        try:
            import ollama
            self.ollama_client = ollama.Client(host=self.base_url)
        except ImportError:
            self.ollama_client = None
            print("Attenzione: La libreria 'ollama' non è installata. Il client non funzionerà.")


    def _build_prompt(self, fields: List[str], n: int, extra_instructions: Optional[str] = None) -> str:
        """
        qua bisogna dare il prompt preciso al modello per fargli restituire esattamente un array JSON
        con n oggetti, ciascuno con i campi specificati in fields.se vogliamo possia anche dire di generare piu
        """
        fields_list = ", ".join(fields)
        # Istruzioni molto specifiche per l'output JSON
        instr = (
            "Sei un generatore di dati mock. Ignora qualsiasi testo o introduzione. "
            f"Il tuo unico compito è generare ESATTAMENTE un array JSON contenente {n} oggetti. "
            "Ogni oggetto deve avere TUTTI i seguenti campi: "
            f"{fields_list}. "
            "Fornisci valori realistici e coerenti per tutti i campi. "
            "L'output DEVE essere solo l'array JSON."
        )
        if extra_instructions:
            instr += " " + extra_instructions
        
        # Aggiungiamo un esempio nel prompt di sistema per rafforzare la struttura
        instr += f"\nEsempio di output valido (per 2 elementi):\n[{{\"{fields[0]}\": \"Valore1\", \"{fields[1]}\": \"Valore2\"}}, ...]"
        return instr


    def generate_mock(self, n: int, fields: List[str], extra_instructions: Optional[str] = None, temperature: float = 0.6) -> List[Any]:
        """
        Richiede al modello di generare `n` record di mock in formato JSON.
        """
       
        system_prompt = self._build_prompt(fields, n, extra_instructions)
        
        try:
            # Chiamata all'API di Ollama utilizzando 'generate'
            response = self.ollama_client.generate(
                model=self.model,
                # Forziamo il modello a produrre JSON
                format='json', 
                # Il prompt di sistema è cruciale per la struttura
                system=system_prompt,
                # Il prompt dell'utente è spesso solo un attivatore
                prompt="Inizia la generazione del JSON.", 
                options={'temperature': temperature, 'num_predict': 4096} # Aumenta num_predict
            )
            
            # Ollama wrap il risultato nella chiave 'response'
            text = response.get('response', '')
            
            # Se la risposta è vuota o il modello ha avuto problemi
            if not text.strip():
                 raise ValueError("Il modello ha restituito una stringa JSON vuota.")

            # Parsa il testo in JSON
            parsed = json.loads(text)
            
            # Validazione finale
            if isinstance(parsed, list) and len(parsed) == n:
                return parsed
            elif isinstance(parsed, dict) and len(parsed) == n:
                 # Alcuni modelli potrebbero restituire un dict anziché una lista root
                 return list(parsed.values()) 
            else:
                raise ValueError(f"Output JSON malformato o con numero errato di elementi. Trovato: {type(parsed)} con {len(parsed)} elementi (attesi {n}).")

        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"Errore nella richiesta a Ollama. Assicurati che il modello '{self.model}' sia scaricato (ollama pull {self.model}) e il server sia attivo: {http_err}")
        except json.JSONDecodeError as json_err:
            # Questo è l'errore più comune se l'LLM non aderisce al JSON
            print(f"--- OUTPUT GREZZO FALLITO ---:\n{text}\n--- FINE ---")
            raise RuntimeError(f"Errore nel parsing JSON dall'output del modello. L'LLM non ha fornito JSON valido: {json_err}")
        except Exception as e:
            raise RuntimeError(f"Errore di generazione non gestito: {e}")


if __name__ == "__main__":
    # --- Esempio d'uso ---
    client = OlamaClient()
    
    # Definisci lo schema richiesto
    fields = ["nome_utente", "email", "ruolo_azienda", "data_iscrizione", "stato_attivo"]
    
    # Istruzioni aggiuntive per rendere i dati più realistici
    istruzioni_extra = (
        "Genera nomi utente realistici e coerenti con le email. "
        "Le email devono essere uniche e seguire il formato standard. "
        "I ruoli aziendali devono essere scelti tra: 'Amministratore', 'Utente', 'Ospite'. "
        "Le date di iscrizione devono essere comprese tra il 2015 e il 2024. "
        "Lo stato attivo deve essere 'vero' o 'falso' con una distribuzione del 70% vero e 30% falso."
    )
    N_RECORDS = 5
    
    print(f"Tentativo di generare {N_RECORDS} record mock con il modello '{client.model}'...")
    
    try:
        records = client.generate_mock(N_RECORDS, fields, extra_instructions=istruzioni_extra)
        print("\n✅ GENERAZIONE RIUSCITA!")
        print(json.dumps(records, indent=2, ensure_ascii=False))
    except RuntimeError as exc:
        print("\n❌ ERRORE CRITICO:")
        print(exc)