import os
import json
import pandas as pd
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file, session
import sys

# Aggiungi il percorso src al PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from llm.v2olama_chat import V2OlamaChat


DEFAULT_SYSTEM_PROMPT = (
    "Rispondi SEMPRE e SOLO con un array JSON. "
    "Nessun testo fuori dal JSON, nessun markdown, nessuna spiegazione. "
    "Ogni elemento deve essere un oggetto con chiavi: nome, cognome, indirizzo. "
    "Esempio valido: [{\"nome\":\"Emily\",\"cognome\":\"Rossi\",\"indirizzo\":\"Rua ...\"}] "
    "Se non puoi soddisfare, restituisci []. Non ripetere la domanda."
)


# -----------------------------------------------------------------
# CONFIGURAZIONE APP FLASK
# -----------------------------------------------------------------
# Calcola il percorso corretto per template e static (che sono in ../frontend)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, "frontend", "template")
static_dir = os.path.join(base_dir, "frontend", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, static_url_path="/static")
app.config["DEBUG"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# -----------------------------------------------------------------
# GESTIONE SESSIONI CHAT
# -----------------------------------------------------------------
chat_sessions = {}  # {session_id: V2OlamaChat}


# -----------------------------------------------------------------
# HOME PAGE
# -----------------------------------------------------------------
@app.route("/")
@app.route("/index")
def home():
    """Home page di accesso a ComputoGreen."""
    return render_template("index.html")


@app.route("/chat")
def chat_page():
    """Pagina di chat."""
    return render_template("chat.html")


#   route per chat
# -----------------------------------------------------------------
@app.route("/ai", methods=["POST"])
def ai_chat():
    """Interfaccia Flask -> V2OlamaChat."""
    print("\n" + "="*50)
    print("[DEBUG] Ricevuta richiesta /ai")
    
    data = request.get_json()
    print(f"[DEBUG] Data ricevuta: {data}")
    
    prompt = data.get("prompt", "").strip()
    session_id = data.get("session_id", "default")
    
    print(f"[DEBUG] Prompt: {prompt}")
    print(f"[DEBUG] Session ID: {session_id}")
    
    if not prompt:
        print("[ERROR] Prompt mancante!")
        return jsonify({"error": "Prompt mancante"}), 400

    # Ottieni o crea una sessione chat
    if session_id not in chat_sessions:
        # Forziamo sempre il system prompt rigido per JSON
        system_prompt = DEFAULT_SYSTEM_PROMPT
        print(f"[DEBUG] Creata nuova sessione con system prompt: {system_prompt}")
        chat_sessions[session_id] = V2OlamaChat(system=system_prompt)
    
    chat = chat_sessions[session_id]
    
    try:
        print(f"[DEBUG] Invio al modello LLM...")
        response_text = chat.send_message(prompt)
        print(f"[DEBUG] Risposta ricevuta: {response_text[:200]}...")

        # Helpers per coercizione in JSON strutturato (solo JSON puro, nessun euristico)
        def normalize_list(data):
            normalized = []
            if not isinstance(data, list):
                return normalized
            for item in data:
                if not isinstance(item, dict):
                    continue
                nome = item.get("nome") or item.get("name")
                cognome = item.get("cognome") or item.get("surname") or item.get("last_name")
                indirizzo = item.get("indirizzo") or item.get("address")
                if nome and cognome and indirizzo:
                    normalized.append({"nome": nome, "cognome": cognome, "indirizzo": indirizzo})
            return normalized

        def parse_structured(text):
            try:
                data_json = json.loads(text)
                items = normalize_list(data_json)
                if items:
                    return True, items
            except Exception:
                pass
            return False, []

        valid_json, items = parse_structured(response_text)

        # Risposta JSON rigidamente strutturata
        result = {
            "success": True,
            "status": "ok",
            "data": {
                "session_id": session_id,
                "prompt": prompt,
                "response": {
                    "format": "json" if valid_json else "text",
                    "valid": bool(items),
                    "items": items,
                    "text": response_text,
                    "raw": response_text,
                    "model": getattr(chat, "model", None)
                },
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        }
        print(f"[DEBUG] Invio risposta al client")
        print("="*50 + "\n")
        return jsonify(result), 200
    except Exception as e:
        print(f"[ERROR] Eccezione: {str(e)}")
        import traceback
        traceback.print_exc()
        error_result = {
            "success": False,
            "status": "error",
            "data": {
                "error": str(e),
                "session_id": session_id,
                "response": None
            }
        }
        print("="*50 + "\n")
        return jsonify(error_result), 500


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """Endpoint alternativo per la chat."""
    return ai_chat()


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


# -----------------------------------------------------------------
# AVVIO APP
# -----------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)