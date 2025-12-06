import pytest
from src.static_generator.algorithmic import get_generator

def test_uuid_generator_wect_valido():
    gen = get_generator("id", {"type": "uuid"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) == 36
    assert value.count('-') == 4

def test_choice_generator_wect_valido():
    gen = get_generator("scelta", {"type": "choice", "options": ["A", "B", "C"]})
    value = gen.generate()
    assert value in ["A", "B", "C"]

def test_choice_generator_wect_non_valido():
    gen = get_generator("scelta", {"type": "choice"})
    value = gen.generate()
    assert value is None or value == []

def test_float_generator_bva_minimo():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 1.0})
    value = gen.generate()
    assert 0.0 <= value <= 1.0

def test_float_generator_bva_massimo():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 1.0})
    value = gen.generate()
    assert 0.0 <= value <= 1.0

def test_float_generator_bva_minimo_meno_1():
    gen = get_generator("score", {"type": "float", "min_value": -1.0, "max_value": 1.0})
    value = gen.generate()
    assert -1.0 <= value <= 1.0

def test_float_generator_bva_massimo_piu_1():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 2.0})
    value = gen.generate()
    assert 0.0 <= value <= 2.0

def test_string_generator_address():
    gen = get_generator("indirizzo", {"type": "string", "generator": "address.street_address"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

def test_string_generator_city():
    gen = get_generator("citta", {"type": "string", "generator": "address.city"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

def test_string_generator_non_supportato():
    gen = get_generator("parola", {"type": "string", "generator": "unknown"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

def test_object_generator_wect_valido():
    gen = get_generator("obj", {"type": "object", "fields": {"id": {"type": "uuid"}, "score": {"type": "float"}}})
    value = gen.generate()
    assert isinstance(value, dict)
    assert "id" in value and "score" in value

def test_object_generator_wect_non_valido():
    gen = get_generator("obj", {"type": "object"})
    value = gen.generate()
    assert isinstance(value, dict)
    assert value == {}

def test_array_generator_wect_valido():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "item_options": ["X", "Y", "Z"], "min_items": 2, "max_items": 2})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 2
    for v in value:
        assert v in ["X", "Y", "Z"]

def test_array_generator_bva_minimo():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 0, "max_items": 0})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 0

def test_array_generator_bva_massimo():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 1, "max_items": 10})
    value = gen.generate()
    assert isinstance(value, list)
    assert 1 <= len(value) <= 10

def test_tipo_non_supportato_errore():
    with pytest.raises(ValueError):
        get_generator("campo", {"type": "unknown"})

def test_proprieta_mancante_type_errore():
    with pytest.raises(KeyError):
        get_generator("campo", {})

def test_input_non_dizionario_errore():
    with pytest.raises(TypeError):
        get_generator("campo", "type: uuid")

def test_float_generator_happy_path():
    gen = get_generator("score", {"type": "float", "min_value": 10.0, "max_value": 20.0, "decimal_places": 1})
    value = gen.generate()
    assert 10.0 <= value <= 20.0
    assert isinstance(value, float)
    assert len(str(value).split('.')[-1]) <= 1

def test_array_generator_happy_path():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "item_options": ["A", "B"], "min_items": 1, "max_items": 2})
    value = gen.generate()
    assert isinstance(value, list)
    assert 1 <= len(value) <= 2
    for v in value:
        assert v in ["A", "B"]