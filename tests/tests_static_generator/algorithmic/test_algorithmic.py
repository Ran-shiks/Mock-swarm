import pytest
from unittest.mock import patch
from src.static_generator.algorithmic import get_generator, fake

# ==============================================================================
# TEST SUITE: ALGORITHMIC GENERATOR
# ==============================================================================

# ==============================================================================
# TC-001: WECT (Valid Input) - Generazione UUID
# Verifica che il formato sia una stringa valida di 36 caratteri (formato UUID).
# ==============================================================================
def test_uuid_generator_wect_valido():
    gen = get_generator("id", {"type": "uuid"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) == 36
    assert value.count('-') == 4

# ==============================================================================
# TC-002: WECT (Valid Input) - Scelta da lista
# Verifica che il valore generato sia presente nelle opzioni fornite.
# ==============================================================================
def test_choice_generator_wect_valido():
    gen = get_generator("scelta", {"type": "choice", "options": ["A", "B", "C"]})
    value = gen.generate()
    assert value in ["A", "B", "C"]

# ==============================================================================
# TC-003: WECT (Invalid Input) - Scelta senza opzioni
# Verifica il comportamento di fallback (None o lista vuota) se mancano opzioni.
# ==============================================================================
def test_choice_generator_wect_non_valido():
    gen = get_generator("scelta", {"type": "choice"})
    value = gen.generate()
    assert value is None or value == []

# ==============================================================================
# TC-004: BVA (Boundary Value Analysis) - Float Minimo
# Verifica che il valore generato non sia inferiore al minimo consentito.
# ==============================================================================
def test_float_generator_bva_minimo():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 1.0})
    value = gen.generate()
    assert 0.0 <= value <= 1.0

# ==============================================================================
# TC-005: BVA (Boundary Value Analysis) - Float Massimo
# Verifica che il valore generato non superi il massimo consentito.
# ==============================================================================
def test_float_generator_bva_massimo():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 1.0})
    value = gen.generate()
    assert 0.0 <= value <= 1.0

# ==============================================================================
# TC-006: BVA (Boundary Value Analysis) - Float con Minimo Negativo
# Verifica la gestione corretta di intervalli che includono numeri negativi.
# ==============================================================================
def test_float_generator_bva_minimo_meno_1():
    gen = get_generator("score", {"type": "float", "min_value": -1.0, "max_value": 1.0})
    value = gen.generate()
    assert -1.0 <= value <= 1.0

# ==============================================================================
# TC-007: BVA (Boundary Value Analysis) - Float con Massimo > 1
# Verifica la gestione corretta di intervalli superiori all'unità standard.
# ==============================================================================
def test_float_generator_bva_massimo_piu_1():
    gen = get_generator("score", {"type": "float", "min_value": 0.0, "max_value": 2.0})
    value = gen.generate()
    assert 0.0 <= value <= 2.0

# ==============================================================================
# TC-008: WECT (Valid Input) - Stringa Indirizzo (Faker Integration)
# Verifica l'integrazione dinamica con il metodo 'street_address' di Faker.
# ==============================================================================
def test_string_generator_address():
    gen = get_generator("indirizzo", {"type": "string", "generator": "street_address"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

# ==============================================================================
# TC-009: WECT (Valid Input) - Stringa Città (Faker Integration)
# Verifica l'integrazione dinamica con il metodo 'city' di Faker.
# ==============================================================================
def test_string_generator_city():
    gen = get_generator("citta", {"type": "string", "generator": "city"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

# ==============================================================================
# TC-010: Robustness (Invalid Input) - Metodo Faker inesistente
# Verifica che il sistema non crashi ma usi un fallback se il generatore è ignoto.
# ==============================================================================
def test_string_generator_non_supportato():
    gen = get_generator("parola", {"type": "string", "generator": "unknown"})
    value = gen.generate()
    assert isinstance(value, str)
    assert len(value) > 0

# ==============================================================================
# TC-011: WECT (Valid Input) - Oggetto Annidato
# Verifica la ricorsione nella generazione di oggetti complessi (Dict).
# ==============================================================================
def test_object_generator_wect_valido():
    gen = get_generator("obj", {"type": "object", "fields": {"id": {"type": "uuid"}, "score": {"type": "float"}}})
    value = gen.generate()
    assert isinstance(value, dict)
    assert "id" in value and "score" in value

# ==============================================================================
# TC-012: WECT (Invalid Input) - Oggetto Vuoto
# Verifica che un oggetto senza campi restituisca un dizionario vuoto.
# ==============================================================================
def test_object_generator_wect_non_valido():
    gen = get_generator("obj", {"type": "object"})
    value = gen.generate()
    assert isinstance(value, dict)
    assert value == {}

# ==============================================================================
# TC-013: WECT (Valid Input) - Array da Opzioni
# Verifica la generazione di una lista campionando da un set di opzioni definito.
# ==============================================================================
def test_array_generator_wect_valido():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "item_options": ["X", "Y", "Z"], "min_items": 2, "max_items": 2})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 2
    for v in value:
        assert v in ["X", "Y", "Z"]

# ==============================================================================
# TC-014: BVA (Boundary Value Analysis) - Array Vuoto
# Verifica il comportamento limite con 0 elementi richiesti.
# ==============================================================================
def test_array_generator_bva_minimo():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 0, "max_items": 0})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 0

# ==============================================================================
# TC-015: BVA (Boundary Value Analysis) - Array Multiplo
# Verifica che la dimensione dell'array sia entro i limiti min/max.
# ==============================================================================
def test_array_generator_bva_massimo():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 1, "max_items": 10})
    value = gen.generate()
    assert isinstance(value, list)
    assert 1 <= len(value) <= 10

# ==============================================================================
# TC-016: Error Handling - Tipo non supportato
# Verifica che venga sollevata ValueError se il 'type' non esiste nella factory.
# ==============================================================================
def test_tipo_non_supportato_errore():
    with pytest.raises(ValueError):
        get_generator("campo", {"type": "unknown"})

# ==============================================================================
# TC-017: Error Handling - Proprietà mancante
# Verifica che venga sollevata un'eccezione se manca la chiave 'type' nel dict.
# ==============================================================================
def test_proprieta_mancante_type_errore():
    with pytest.raises(ValueError):
        get_generator("campo", {})

# ==============================================================================
# TC-018: Error Handling - Input Malformato
# Verifica la robustezza contro input che non sono dizionari.
# ==============================================================================
def test_input_non_dizionario_errore():
    with pytest.raises(AttributeError):
        get_generator("campo", "type: uuid")

# ==============================================================================
# TC-019: Happy Path - Float Tipico
# Scenario d'uso standard per generazione numeri decimali.
# ==============================================================================
def test_float_generator_happy_path():
    gen = get_generator("score", {"type": "float", "min_value": 10.0, "max_value": 20.0, "decimal_places": 1})
    value = gen.generate()
    assert 10.0 <= value <= 20.0
    assert isinstance(value, float)
    assert len(str(value).split('.')[-1]) <= 1

# ==============================================================================
# TC-020: Happy Path - Array Tipico
# Scenario d'uso standard per generazione liste.
# ==============================================================================
def test_array_generator_happy_path():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "item_options": ["A", "B"], "min_items": 1, "max_items": 2})
    value = gen.generate()
    assert isinstance(value, list)
    assert 1 <= len(value) <= 2
    for v in value:
        assert v in ["A", "B"]

# ==============================================================================
# TC-021: WECT (Extended Formats) - Copertura Formati Speciali
# Copre i rami if/elif espliciti per email, date, ipv4, uri.
# ==============================================================================
def test_string_generator_formats_extended():
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

# ==============================================================================
# TC-022: White Box (Fault Injection) - Gestione Crash Interno
# Simula un crash interno di Faker per verificare che il try/except funzioni.
# (Sostituisce il vecchio test ridondante su metodo non esistente)
# ==============================================================================
def test_string_generator_exception_handling():
    with patch.object(fake, 'first_name', side_effect=Exception("Boom!")):
        props = {"type": "string", "format": "first_name"}
        gen = get_generator("test_crash", props)
        value = gen.generate()
        assert isinstance(value, str)
        assert len(value) > 0

# ==============================================================================
# TC-023: White Box (Robustness) - Array Min/Max invertiti
# Verifica che il codice corregga automaticamente se max_items < min_items.
# ==============================================================================
def test_array_generator_fix_inverted_min_max():
    gen = get_generator("arr", {"type": "array", "item_type": "string", "min_items": 5, "max_items": 1})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 5

# ==============================================================================
# TC-024: Black Box (Recursive WECT) - Array di Tipi Complessi
# Verifica la generazione di array contenenti tipi non stringa (es. integer).
# ==============================================================================
def test_array_generator_complex_item_type():
    gen = get_generator("voti", {"type": "array", "item_type": "integer", "min_items": 3, "max_items": 3})
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 3
    assert all(isinstance(x, int) for x in value)

# ==============================================================================
# TC-025: White Box (Robustness) - Array senza item_type (Default Fallback)
# Verifica il ramo 'else' finale: array generico di parole se non specificato tipo.
# ==============================================================================
def test_array_generator_default_fallback():
    props = {"type": "array", "min_items": 3, "max_items": 3}
    gen = get_generator("test_array_fallback", props)
    value = gen.generate()
    assert isinstance(value, list)
    assert len(value) == 3
    assert isinstance(value[0], str)