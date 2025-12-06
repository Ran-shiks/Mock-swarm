import pytest
import re
from src.generators.algorithmic import AlgorithmicGenerator

# --- Test Tipi Primitivi ---

def test_generate_string():
    gen = AlgorithmicGenerator()
    schema = {"type": "string"}
    result = gen.generate(schema)
    assert isinstance(result, str)
    assert len(result) > 0

def test_generate_integer_constraints():
    gen = AlgorithmicGenerator()
    min_val, max_val = 10, 20
    schema = {
        "type": "integer", 
        "minimum": min_val, 
        "maximum": max_val
    }
    
    # Eseguiamo più volte per essere sicuri che il range sia rispettato
    for _ in range(50):
        result = gen.generate(schema)
        assert isinstance(result, int)
        assert min_val <= result <= max_val

def test_generate_boolean():
    gen = AlgorithmicGenerator()
    schema = {"type": "boolean"}
    result = gen.generate(schema)
    assert result is True or result is False

# --- Test Formati Speciali ---

def test_generate_email_format():
    gen = AlgorithmicGenerator()
    schema = {"type": "string", "format": "email"}
    result = gen.generate(schema)
    assert isinstance(result, str)
    assert "@" in result
    assert "." in result # Check molto basilare per email

def test_generate_uuid_format():
    gen = AlgorithmicGenerator()
    schema = {"type": "string", "format": "uuid"}
    result = gen.generate(schema)
    # Regex standard per UUID
    uuid_regex = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    assert re.match(uuid_regex, result)

# --- Test Strutture Complesse ---

def test_generate_array_constraints():
    gen = AlgorithmicGenerator()
    min_items = 3
    max_items = 5
    schema = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": min_items,
        "maxItems": max_items
    }
    
    for _ in range(10):
        result = gen.generate(schema)
        assert isinstance(result, list)
        assert min_items <= len(result) <= max_items
        assert isinstance(result[0], str)

def test_generate_nested_object():
    gen = AlgorithmicGenerator()
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "isActive": {"type": "boolean"}
                }
            }
        }
    }
    result = gen.generate(schema)
    
    assert isinstance(result, dict)
    assert "id" in result
    assert isinstance(result["id"], int)
    
    # Verifica annidamento
    assert "user" in result
    assert isinstance(result["user"], dict)
    assert "name" in result["user"]
    assert isinstance(result["user"]["isActive"], bool)

# --- Test Enum e Const ---

def test_generate_enum():
    gen = AlgorithmicGenerator()
    allowed = ["apple", "banana", "cherry"]
    schema = {"enum": allowed}
    
    for _ in range(20):
        result = gen.generate(schema)
        assert result in allowed

def test_generate_const():
    gen = AlgorithmicGenerator()
    schema = {"const": "FIXED_VALUE"}
    result = gen.generate(schema)
    assert result == "FIXED_VALUE"

# --- Test Determinismo (Seed) ---

def test_reproducibility_with_seed():
    """
    Testa che due generatori inizializzati con lo stesso seed
    producano ESATTAMENTE gli stessi dati complessi.
    """
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 1, "maximum": 100},
            "email": {"type": "string", "format": "email"}
        }
    }
    
    seed = 12345
    
    # Generatore A
    gen_a = AlgorithmicGenerator(seed=seed)
    data_a = gen_a.generate(schema)
    
    # Generatore B (nuova istanza, stesso seed)
    gen_b = AlgorithmicGenerator(seed=seed)
    data_b = gen_b.generate(schema)
    
    # Generatore C (seed diverso)
    gen_c = AlgorithmicGenerator(seed=999)
    data_c = gen_c.generate(schema)
    
    assert data_a == data_b, "Con lo stesso seed, i dati devono essere identici"
    assert data_a != data_c, "Con seed diversi, i dati dovrebbero essere diversi"