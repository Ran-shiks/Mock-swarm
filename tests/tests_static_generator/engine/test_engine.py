import pytest
import os
from src.static_generator.engine import MockEngine

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")

def schema_path(name):
    return os.path.join(SCHEMA_DIR, name)

# TC-001: WECT Valido
def test_generate_single_record_valid_schema():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(1)
    assert isinstance(records, list)
    assert len(records) == 1
    assert isinstance(records[0], dict)

# TC-002: WECT Non Valido (schema non esistente)
def test_generate_missing_schema():
    with pytest.raises(FileNotFoundError):
        MockEngine(schema_path("missing_schema.json"))

# TC-003: WECT Non Valido (schema malformato)
def test_generate_malformed_schema():
    with pytest.raises(Exception):  # Puoi specificare json.JSONDecodeError se usi json puro
        MockEngine(schema_path("malformed_schema.json"))

# TC-004: BVA Minimo (n=0)
def test_generate_zero_records():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(0)
    assert records == []

# TC-005: BVA Minimo-1 (n=-1)
def test_generate_negative_records():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(-1)
    assert records == []

# TC-006: BVA Tipico (n=10)
def test_generate_typical_records():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(10)
    assert isinstance(records, list)
    assert len(records) == 10

# TC-007: BVA Massimo (n=1000)
def test_generate_max_records():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(1000)
    assert isinstance(records, list)
    assert len(records) == 1000

# TC-008: BVA Massimo+1 (n=1001)
def test_generate_max_plus_one_records():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(1001)
    assert isinstance(records, list)
    assert len(records) == 1001

# TC-009: Errore (n non numerico)
@pytest.mark.parametrize("bad_n", ["dieci", 3.14, [], {}])
def test_generate_non_numeric_n(bad_n):
    engine = MockEngine(schema_path("valid_schema.json"))
    with pytest.raises(TypeError):
        engine.generate(bad_n)

# TC-010: Errore (n=None)
def test_generate_none_n():
    engine = MockEngine(schema_path("valid_schema.json"))
    with pytest.raises(TypeError):
        engine.generate(None)

# TC-011: Happy Path (n=5)
def test_generate_happy_path():
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(5)
    assert isinstance(records, list)
    assert len(records) == 5
    for rec in records:
        assert isinstance(rec, dict)

# TC-012: Errore (tipo non supportato nello schema)
def test_generate_unsupported_type():
    engine = MockEngine(schema_path("unsupported_type_schema.json"))
    with pytest.raises(Exception):
        engine.generate(1)