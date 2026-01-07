from unittest.mock import patch

from jsonschema import SchemaError, ValidationError
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
    """
    Test the happy path for the `generate` method of the `MockEngine` class.

    This test verifies that the `generate` method:
    - Returns a list of records.
    - Produces the correct number of records as specified by the input.
    - Ensures each record in the list is a dictionary.

    Preconditions:
    - A valid schema file ("valid_schema.json") must exist at the specified schema path.

    Assertions:
    - The returned value is a list.
    - The length of the list matches the requested number of records.
    - Each item in the list is a dictionary.
    """
    engine = MockEngine(schema_path("valid_schema.json"))
    records = engine.generate(5)
    assert isinstance(records, list)
    assert len(records) == 5
    for rec in records:
        assert isinstance(rec, dict)

# TC-012: Errore (tipo non supportato nello schema)
def test_generate_unsupported_type():
    """
         Obiettivo: Verificare che se il generatore interno lancia un'eccezione
         (es. tipo non gestito logicamente, anche se lo schema è valido),
         l'engine NON crashi ma metta None nel campo.
         """
    # 1. Usiamo uno schema SINTATTICAMENTE VALIDO per passare il check del Parser
    # (Così evitiamo lo SchemaError iniziale)
    engine = MockEngine(schema_path("valid_schema.json"))

    # 2. "Sabotiamo" la funzione get_generator interna usando il Mock.
    # Le diciamo: "Qualsiasi cosa ti chiedano, lancia un'eccezione generica".
    # IMPORTANTE: Il path nel patch deve puntare a dove viene USATA la funzione, non dove è definita.
    with patch('src.static_generator.engine.get_generator') as mock_gen:
        mock_gen.side_effect = Exception("Generatore non trovato o rotto")

        # 3. Eseguiamo la generazione
        records = engine.generate(1)

    # 4. Asserzioni
    assert len(records) == 1
    record = records[0]

    # Verifica: L'engine non è crashato, e i campi sono stati popolati con None
    # a causa dell'eccezione nel generatore.
    for key, value in record.items():
        assert value is None, f"Il campo {key} dovrebbe essere None a causa del fail-safe"

# AGGIUNTO DOPO LA MODIFICA DI MOCK ENGINE(SEED)
# TC-013: White Box - Generazione Deterministica con Seed
def test_generate_determinism_with_seed():
    """
    White Box: Verifica che passando un seed, l'output sia deterministico
    (ovvero identico se rieseguito), coprendo il ramo 'if seed is not None'.
    """
    schema = schema_path("valid_schema.json")

    # Istanza 1 con seed 42
    engine1 = MockEngine(schema, seed=42)
    result1 = engine1.generate(1)

    # Istanza 2 con seed 42
    engine2 = MockEngine(schema, seed=42)
    result2 = engine2.generate(1)

    # Istanza 3 con seed DIVERSO
    engine3 = MockEngine(schema, seed=999)
    result3 = engine3.generate(1)

    # Verifica White Box
    assert result1 == result2, "Con lo stesso seed, l'output DEVE essere identico"
    assert result1 != result3, "Con seed diversi, l'output DOVREBBE essere diverso"

    from unittest.mock import patch



