import os
import json
import requests
import random
from typing import List, Optional, Any


OLLAMA = os.getenv("OLLAMA", "http://127.0.0.1:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3")


class OlamaClient:
    """
    Client minimale per interagire con un server Olama/OLLAMA locale.

    Fornisce un metodo `generate_mock` che richiede al modello di restituire
    esattamente `n` record JSON con i campi richiesti (nome, cognome, ecc.).
    """

    def __init__(self, model: Optional[str] = None, host: str = "127.0.0.1", port: int = 11434):
        self.model = model or LLM_MODEL
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"

    def set_model(self, model: str):
        self.model = model

    def _build_prompt(self, fields: List[str], n: int, extra_instructions: Optional[str] = None) -> str:
        """
        Costruisce un prompt che ordina al modello di restituire esattamente un array JSON.
        Il prompt richiede: nessun testo aggiuntivo, solo JSON valido.
        """
        fields_list = ", ".join(fields)
        instr = (
            f"Genera esattamente {n} oggetti JSON come un array. "
            f"Ogni oggetto deve avere questi campi: {fields_list}. "
            "Restituisci SOLO il JSON, senza testo descrittivo aggiuntivo. "
            "Per i valori, fornisci contenuti realistici (nomi, cognomi, generi, film, descrizioni, ecc.)."
        )
        if extra_instructions:
            instr += " " + extra_instructions
        instr += "\nEsempio di output valido (per 2 elementi):\n[{\"nome\": \"Mario\", \"cognome\": \"Rossi\"}, {\"nome\": \"Anna\", \"cognome\": \"Bianchi\"}]"
        return instr

    def generate_mock(self, n: int, fields: List[str], extra_instructions: Optional[str] = None, temperature: float = 0.0, retries: int = 0) -> List[Any]:
        """
        Richiede al modello di generare `n` record di mock contenenti i `fields` richiesti.

        Ritorna una lista di dizionari (se il modello restituisce JSON valido),
        altrimenti una lista vuota e una stringa d'errore nell'eccezione.
        """
        if not self.model:
            raise ValueError("Model not set. Use set_model() or provide LLM_MODEL env var.")
        prompt = self._build_prompt(fields, n, extra_instructions)
        # Try multiple common endpoints for Ollama/OLLAMA HTTP API, because installs/versions differ
        endpoints = [
            "/api/generate",
            "/api/chat",
            "/v1/generate",
            "/v1/chat/completions",
            "/api/completions",
        ]
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": 1000,
        }
        attempt = 0
        last_err = None

        # First try using the ollama Python client if available (some setups prefer this)
        try:
            import ollama
            try:
                client = ollama.Client()
                # Try chat/generate using client if provided
                # The API of ollama.Client may differ; we try to be conservative
                try:
                    # Some versions support client.chat
                    res_iter = client.chat(self.model, messages=[{"role": "user", "content": prompt}], stream=False)
                    # res_iter could be an iterator or a single response
                    if hasattr(res_iter, '__iter__') and not isinstance(res_iter, (str, bytes)):
                        # take last chunk with content
                        text = None
                        for chunk in res_iter:
                            if hasattr(chunk, 'message') and getattr(chunk.message, 'content', None):
                                text = chunk.message.content
                        if text is None:
                            text = str(res_iter)
                    else:
                        text = str(res_iter)
                    parsed = json.loads(text)
                    if isinstance(parsed, list) and len(parsed) == n:
                        return parsed
                except Exception:
                    # Try client.generate if available
                    try:
                        gen = client.generate(self.model, prompt)
                        text = getattr(gen, 'content', None) or str(gen)
                        parsed = json.loads(text)
                        if isinstance(parsed, list) and len(parsed) == n:
                            return parsed
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            # ollama client not available or failed - continue with HTTP attempts
            pass

        # If client didn't work, try HTTP endpoints
        while attempt <= retries:
            attempt += 1
            for ep in endpoints:
                url = f"{self.base_url}{ep}"
                try:
                    resp = requests.post(url, json=payload, timeout=30)
                    resp.raise_for_status()

                    # Olama/OLLAMA può rispondere in diversi formati. Cerchiamo la chiave "response" prima,
                    # poi tentiamo di parsare il testo in JSON.
                    try:
                        j = resp.json()
                    except ValueError:
                        # Not JSON: try to parse text
                        text = resp.text.strip()
                        parsed = json.loads(text)
                        if not isinstance(parsed, list):
                            raise ValueError("Output JSON non è una lista")
                        if len(parsed) != n:
                            raise ValueError(f"Output contiene {len(parsed)} elementi, attesi {n}")
                        return parsed

                    # If API wraps the content in a field
                    if isinstance(j, dict) and "response" in j:
                        content = j["response"]
                        # content could itself be JSON string
                        if isinstance(content, (list, dict)):
                            parsed = content if isinstance(content, list) else [content]
                        else:
                            parsed = json.loads(content)
                    elif isinstance(j, list):
                        parsed = j
                    else:
                        # Try to parse raw text as fallback
                        parsed = json.loads(resp.text)

                    if not isinstance(parsed, list):
                        raise ValueError("Output JSON non è una lista")
                    if len(parsed) != n:
                        raise ValueError(f"Output contiene {len(parsed)} elementi, attesi {n}")
                    return parsed

                except Exception as e:
                    last_err = e
                    # try next endpoint
                    continue
            # after trying all endpoints for this attempt, if none returned, either retry or break
            if attempt > retries:
                break
            # otherwise retry loop continues
        # unreachable but for typing
        raise RuntimeError(f"Errore nella richiesta a Olama: {last_err}")


if __name__ == "__main__":
    # Esempio d'uso rapido: genera 5 record con campi tipici richiesti dagli sviluppatori
    client = OlamaClient()
    fields = ["nome", "cognome", "sesso", "film_preferito", "descrizione"]
    try:
        records = client.generate_mock(5, fields, extra_instructions="Usa generi e film contemporanei.")
        print(json.dumps(records, indent=2, ensure_ascii=False))
    except Exception as exc:
        print("Errore durante la generazione dei mock:", exc)