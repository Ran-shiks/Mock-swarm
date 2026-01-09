import os
import json
import io
from flask import Flask, render_template, request, jsonify, send_file, session
import sys

# Aggiungi il percorso src al PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from llm.v2olama_chat import V2OlamaChat
from static_generator.engine import MockEngine
from static_generator.exporter import DataExporter


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
UPLOAD_DIR = os.path.join(base_dir, "uploaded_schemas")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@app.route("/drag-and-drop")
def drag_and_drop_page():
    """Pagina di drag and drop per JSON schema."""
    return render_template("dragAndDrop.html")


@app.route("/api/schema/upload", methods=["POST"])
def upload_schema():
    """Riceve un JSON schema e lo salva su disco."""
    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "")
    filename = payload.get("filename", "input.json")

    if not content:
        return jsonify({"success": False, "error": "Nessun contenuto fornito."}), 400

    # Verifica JSON valido
    try:
        json.loads(content)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"success": False, "error": f"JSON non valido: {exc}"}), 400

    safe_name = os.path.basename(filename) or "input.json"
    if not safe_name.endswith(".json"):
        safe_name += ".json"

    target_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    return jsonify({"success": True, "path": target_path}), 200


@app.route("/api/schema/generate", methods=["POST"])
def generate_from_schema():
    """Genera dati mock usando uno schema già caricato."""
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename", "input.json")
    content = payload.get("content", "")
    count = int(payload.get("count", 3) or 3)
    seed = payload.get("seed")
    format_type = payload.get("format", "json")
    table_name = payload.get("table_name", "my_table")

    # Usa contenuto inline (niente fetch dal server) se fornito
    if content:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            tmp.write(content)
            schema_path = tmp.name
    else:
        safe_name = os.path.basename(filename) or "input.json"
        if not safe_name.endswith(".json"):
            safe_name += ".json"
        schema_path = os.path.join(UPLOAD_DIR, safe_name)
        if not os.path.exists(schema_path):
            return jsonify({"success": False, "error": "Schema non trovato. Fornisci 'content' o carica il file."}), 404

    try:
        engine = MockEngine(schema_path=schema_path, seed=seed)
        data = engine.generate(n=count)

        # Esporta nel formato richiesto su buffer in memoria
        buf = io.StringIO()
        DataExporter.export(
            data=data,
            format_type=format_type,
            output_stream=buf,
            table_name=table_name,
        )
        text_out = buf.getvalue()
        ext_map = {"json": "json", "csv": "csv", "ndjson": "ndjson", "sql": "sql"}
        filename = f"mock.{ext_map.get(format_type, 'txt')}"

        return jsonify({
            "success": True,
            "data": data,
            "text": text_out,
            "format": format_type,
            "filename": filename,
        }), 200
    except Exception as exc:  # noqa: BLE001
        return jsonify({"success": False, "error": str(exc)}), 500

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