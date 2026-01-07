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
    with pytest.raises(ValueError):
        get_generator("campo", {})

def test_input_non_dizionario_errore():
    with pytest.raises(AttributeError):
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


# AGGIUNTI ALTRI TEST PER COPERTURA COMPLETA
# ----------------------------------------------------------------------------------
# Test Aggiuntivi per Copertura 100%
# ----------------------------------------------------------------------------------

# TIPO: WECT (Specific Formats coverage)
def test_string_generator_formats_extended():
    """
    Copre le righe 38, 40, 42, 44: Gestione formati email, date, ipv4, uri.
    """
    formats = ["email", "date", "ipv4", "uri"]
    for fmt in formats:
        gen = get_generator("campo", {"type": "string", "format": fmt})
        value = gen.generate()
        assert isinstance(value, str)
        assert len(value) > 0
        if fmt == "email":
            assert "@" in value
        if fmt == "ipv4":
            assert value.count(".") == 3


# TIPO: Robustness (Fault Injection)
def test_string_generator_fallback_on_attribute_error():
    """
    Copre la riga 51: Gestione eccezione se il generatore Faker non esiste.
    Deve catturare l'AttributeError e fare fallback su fake.word().
    """
    gen = get_generator("campo", {"type": "string", "generator": "metodo_che_non_esiste_xyz"})
    value = gen.generate()
    # Se non crasha e restituisce una stringa, il fallback ha funzionato
    assert isinstance(value, str)
    assert len(value) > 0


# TIPO: Robustness (Defensive Programming)
def test_array_generator_fix_inverted_min_max():
    """
    Copre la riga 74: Correzione automatica se max_items < min_items.
    """
    # Impostiamo max a 1 e min a 5. Il codice deve forzare max=5.
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 5, "max_items": 1})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 5


# TIPO: WECT (Recursive Generation)
def test_array_generator_complex_item_type():
    """
    Copre le righe 93-94: Generazione array di tipi complessi (es. interi),
    non semplici stringhe da lista opzioni.
    """
    # Chiediamo un array di interi
    gen = get_generator("voti", {"type": "array", "item_type": "integer", "min_items": 3, "max_items": 3})
    value = gen.generate()

    assert isinstance(value, list)
    assert len(value) == 3
    # Verifica che gli elementi interni siano stati generati come interi
    assert all(isinstance(x, int) for x in value)