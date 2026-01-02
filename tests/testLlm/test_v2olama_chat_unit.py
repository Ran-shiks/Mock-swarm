import os
import sys
import json
import pytest

# Ensure project root is on path (serve per importare "src.*")
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import src.llm.v2olama_chat as v2chat


def test_unit_chat_history_grows(monkeypatch):
    def fake_generateMock(system, prompt, temperature=0.7):
        return '[{"nome":"A","cognome":"B","indirizzo":"C"}]'

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    chat = v2chat.V2OlamaChat(system="SYS")
    out1 = chat.send_message("p1")
    out2 = chat.send_message("p2")

    assert out1.startswith("[")
    assert out2.startswith("[")
    assert len(chat.history) == 4
    assert chat.history[0] == ("user", "p1")
    assert chat.history[1][0] == "assistant"
    assert chat.history[2] == ("user", "p2")
    assert chat.history[3][0] == "assistant"


def test_unit_set_system_changes_system():
    chat = v2chat.V2OlamaChat(system="OLD")
    chat.set_system("NEW")
    assert chat.system == "NEW"


def test_unit_reset_clears_history(monkeypatch):
    def fake_generateMock(system, prompt, temperature=0.7):
        return "[]"

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    chat = v2chat.V2OlamaChat(system="SYS")
    chat.send_message("hello")
    assert len(chat.history) == 2

    chat.reset()
    assert chat.history == []


def test_unit_send_message_passes_system_and_prompt(monkeypatch):
    calls = {"system": None, "prompt": None, "temperature": None}

    def fake_generateMock(system, prompt, temperature=0.7):
        calls["system"] = system
        calls["prompt"] = prompt
        calls["temperature"] = temperature
        return "[]"

    monkeypatch.setattr(v2chat.v2Olama, "generateMock", fake_generateMock, raising=True)

    chat = v2chat.V2OlamaChat(system="SYS_123")
    chat.send_message("PROMPT_ABC", temperature=0.12)

    assert calls["system"] == "SYS_123"
    assert calls["prompt"] == "PROMPT_ABC"
    assert calls["temperature"] == 0.12
