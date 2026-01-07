import os
import sys
import json
import pytest

# Ensure project root is on path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.run import app, chat_sessions, DEFAULT_SYSTEM_PROMPT  # noqa: E402
import llm.v2olama_chat as v2chat


# ---------------------------
# Pytest fixtures
# ---------------------------
@pytest.fixture(autouse=True)
def clear_sessions():
    chat_sessions.clear()
    yield
    chat_sessions.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_ai(client, prompt, session_id="wb", system="IGNORATO"):
    return client.post(
        "/ai",
        json={
            "prompt": prompt,
            "session_id": session_id,
            "system": system,  # nel tuo codice NON viene usato
        },
    )


def banner(title: str):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# =============================================================================
# WB01 - La sessione viene creata e il system prompt è SEMPRE quello rigido
# =============================================================================
def test_wb01_session_created_with_default_system_prompt(client, monkeypatch):
    banner("WB01 | Verifica: creazione sessione + system prompt forzato (ignora system utente)")

    def fake_generateMock(system, prompt, temperature=0.7):
        print(f"[WB01] fake_generateMock chiamato | system_in='{system[:40]}...' | prompt='{prompt}'")
        return '[{"nome":"A","cognome":"B","indirizzo":"C"}]'

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    print("[WB01] POST /ai con system utente finto: 'SYSTEM_UTENTE_NON_DEVE_PASSARE'")
    res = post_ai(client, "ciao", session_id="t01", system="SYSTEM_UTENTE_NON_DEVE_PASSARE")
    assert res.status_code == 200

    print("[WB01] Controllo white-box: sessione esiste in chat_sessions e system == DEFAULT_SYSTEM_PROMPT")
    assert "t01" in chat_sessions
    chat = chat_sessions["t01"]
    assert chat.system == DEFAULT_SYSTEM_PROMPT


# =============================================================================
# WB02 - La sessione viene riusata e la history cresce di 2 ad ogni chiamata
# =============================================================================
def test_wb02_session_reused_and_history_grows(client, monkeypatch):
    banner("WB02 | Verifica: riuso sessione + history cresce (user+assistant) ad ogni chiamata")

    def fake_generateMock(system, prompt, temperature=0.7):
        print(f"[WB02] fake_generateMock chiamato | prompt='{prompt}'")
        return '[{"nome":"X","cognome":"Y","indirizzo":"Z"}]'

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    print("[WB02] 1ª chiamata: session_id=t02, prompt='p1'")
    res1 = post_ai(client, "p1", session_id="t02")
    assert res1.status_code == 200

    chat_obj_1 = chat_sessions["t02"]
    print(f"[WB02] history_len dopo 1ª chiamata: {len(chat_obj_1.history)} (atteso 2)")
    assert len(chat_obj_1.history) == 2  # user + assistant

    print("[WB02] 2ª chiamata: stesso session_id=t02, prompt='p2'")
    res2 = post_ai(client, "p2", session_id="t02")
    assert res2.status_code == 200

    chat_obj_2 = chat_sessions["t02"]
    print("[WB02] Controllo: stessa istanza sessione (object identity)")
    assert chat_obj_1 is chat_obj_2

    print(f"[WB02] history_len dopo 2ª chiamata: {len(chat_obj_2.history)} (atteso 4)")
    assert len(chat_obj_2.history) == 4  # +2 (user + assistant)

    print("[WB02] Controllo contenuto history: posizioni user messages")
    assert chat_obj_2.history[0] == ("user", "p1")
    assert chat_obj_2.history[2] == ("user", "p2")


# =============================================================================
# WB03 - Prompt mancante => 400 e nessuna sessione creata
# =============================================================================
def test_wb03_missing_prompt_returns_400_and_no_session(client):
    banner("WB03 | Verifica: prompt mancante => HTTP 400 + nessuna sessione creata")

    print("[WB03] POST /ai con prompt vuoto/spazi")
    res = client.post("/ai", json={"prompt": "   ", "session_id": "t03"})
    print(f"[WB03] status_code ricevuto: {res.status_code} (atteso 400)")
    assert res.status_code == 400

    print("[WB03] Controllo white-box: sessione 't03' NON deve esistere")
    assert "t03" not in chat_sessions

    body = res.get_json()
    print(f"[WB03] body.error='{body.get('error')}' (atteso 'Prompt mancante')")
    assert body["error"] == "Prompt mancante"


# =============================================================================
# WB04 - normalize_list: accetta name/surname/address e produce items standard
# =============================================================================
def test_wb04_parse_and_normalize_items_from_alt_keys(client, monkeypatch):
    banner("WB04 | Verifica: parse JSON + normalize_list (name/surname/address -> nome/cognome/indirizzo)")

    def fake_generateMock(system, prompt, temperature=0.7):
        print("[WB04] fake_generateMock ritorna lista con chiavi miste + un record incompleto (da scartare)")
        return json.dumps([
            {"name": "Mario", "surname": "Rossi", "address": "Via Roma 1"},
            {"nome": "Anna", "cognome": "Bianchi", "indirizzo": "Corso Italia 10"},
            {"nome": "SCARTO", "cognome": "NOADDR"}  # viene scartato
        ])

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    print("[WB04] POST /ai e verifica che items vengano normalizzati e filtrati")
    res = post_ai(client, "dammi utenti", session_id="t04")
    assert res.status_code == 200
    body = res.get_json()

    resp = body["data"]["response"]
    print(f"[WB04] response.format={resp['format']} (atteso 'json')")
    print(f"[WB04] response.valid={resp['valid']} (atteso True)")
    print(f"[WB04] items_normalizzati={len(resp['items'])} (atteso 2)")
    assert resp["format"] == "json"
    assert resp["valid"] is True
    assert isinstance(resp["items"], list)
    assert len(resp["items"]) == 2

    assert resp["items"][0] == {"nome": "Mario", "cognome": "Rossi", "indirizzo": "Via Roma 1"}
    assert resp["items"][1] == {"nome": "Anna", "cognome": "Bianchi", "indirizzo": "Corso Italia 10"}


# =============================================================================
# WB05 - Output non JSON => format=text, items=[], valid=False (ma 200)
# =============================================================================
def test_wb05_non_json_output_falls_back_to_text_mode(client, monkeypatch):
    banner("WB05 | Verifica: output NON JSON => fallback controllato (format=text, items=[], valid=False)")

    def fake_generateMock(system, prompt, temperature=0.7):
        print("[WB05] fake_generateMock ritorna testo non parsabile JSON: 'NON_JSON'")
        return "NON_JSON"

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    print("[WB05] POST /ai: mi aspetto status 200 ma response.format='text'")
    res = post_ai(client, "x", session_id="t05")
    assert res.status_code == 200
    body = res.get_json()
    resp = body["data"]["response"]

    print(f"[WB05] response.format={resp['format']} (atteso 'text')")
    print(f"[WB05] response.valid={resp['valid']} (atteso False)")
    print(f"[WB05] response.items={resp['items']} (atteso [])")
    print(f"[WB05] response.text='{resp['text']}' (atteso 'NON_JSON')")
    assert resp["format"] == "text"
    assert resp["valid"] is False
    assert resp["items"] == []
    assert resp["text"] == "NON_JSON"
    assert resp["raw"] == "NON_JSON"


# =============================================================================
# WB06 - Eccezione LLM => 500, success=False e response None
# =============================================================================
def test_wb06_llm_exception_returns_500(client, monkeypatch):
    banner("WB06 | Verifica: eccezione nel LLM => HTTP 500 + payload error (success=False)")

    def boom_generateMock(system, prompt, temperature=0.7):
        print("[WB06] fake_generateMock solleva RuntimeError('LLM exploded')")
        raise RuntimeError("LLM exploded")

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", boom_generateMock, raising=True)

    print("[WB06] POST /ai: mi aspetto status 500 e body.success=False")
    res = post_ai(client, "x", session_id="t06")
    print(f"[WB06] status_code ricevuto: {res.status_code} (atteso 500)")
    assert res.status_code == 500

    body = res.get_json()
    print(f"[WB06] body.success={body.get('success')} (atteso False)")
    print(f"[WB06] body.status={body.get('status')} (atteso 'error')")
    print(f"[WB06] body.data.session_id={body.get('data', {}).get('session_id')} (atteso 't06')")
    print(f"[WB06] body.data.response={body.get('data', {}).get('response')} (atteso None)")
    print(f"[WB06] body.data.error contiene 'LLM exploded'? -> {'LLM exploded' in body.get('data', {}).get('error', '')}")

    assert body["success"] is False
    assert body["status"] == "error"
    assert body["data"]["session_id"] == "t06"
    assert body["data"]["response"] is None
    assert "LLM exploded" in body["data"]["error"]
