import os, requests

OLLAMA = "http://127.0.0.1:11434"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

def embed(text: str):
    r = requests.post(f"{OLLAMA}/api/embeddings",
                      json={"model": EMBED_MODEL, "prompt": text}, timeout=60)
    r.raise_for_status()
    return r.json()["embedding"]

def generateMock(system: str, prompt: str, temperature: float = 8.0) -> str:
    body = {
        "model": LLM_MODEL,
        "system": system,
        "prompt": prompt + "\n\nRispondi SOLO con JSON valido.",
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_ctx": 2048,
            "seed": 7
        },
        "stream": False
    }
    r = requests.post(f"{OLLAMA}/api/generate", json=body, timeout=300)
    r.raise_for_status()
    return r.json()["response"]


