import pytest
import json
import os
from src.core.schema_parser import SchemaParser, SchemaError


'''
Intra Method Testing
Nella classe schema_parser ci sono:
- parse_file: metodo principale che legge il file e chiama la validazione
- _validate_structure: metodo privato che valida la struttura dello schema

    Partiamo con il black box testing in cui dobbiamo usare questi criteri di test

    - Classi di equivalenza, in particolare effettuiamo un WECT (Weak Equivalence Class Testing)
    - Analisi dei valori limite (Boundary Value Analysis)
    - Worst Case Testing

    Funzione parse_file:
    WECT: file esistente/non esistente, json valido/non valido, schema valido/non valido
    BVA: file vuoto, file con un singolo carattere, file con schema minimo valido
    WCT: Combinazioni di file esistente + json valido + schema valido/ non valido

    Funzione _validate_structure:
    WECT: schema valido/non valido
    BVA: schema minimo valido, schema con un singolo errore
    WCT: Combinazioni di vari tipi di errori nello schema (tipo errato, proprietà mancanti, ecc.)

'''


'''
Intra Class Testing

Per fare intra class testing sulla classe SchemaParser l'unico punto in cui si puo fare questo testing è il metodo _validate_structure
in cui richiamiamo la classe SchemaError. Quindi dobbiamo testare che questa eccezione venga sollevata correttamente in tutti i casi previsti.
'''

# Fixture: crea un parser nuovo per ogni test
@pytest.fixture
def parser():
    return SchemaParser()

def test_parse_valid_schema(parser, tmp_path):
    """Testa il caricamento di un file schema valido."""
    # 1. Creiamo un file temporaneo
    d = tmp_path / "schemas"
    d.mkdir()
    p = d / "valid.json"
    
    schema_content = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    p.write_text(json.dumps(schema_content), encoding='utf-8')

    # 2. Eseguiamo il parsing
    result = parser.parse_file(str(p))

    # 3. Asserzioni
    assert isinstance(result, dict)
    assert result["type"] == "object"
    assert "name" in result["properties"]


def test_file_not_found(parser):
    """Testa che venga sollevato errore se il file non esiste."""
    with pytest.raises(FileNotFoundError):
        parser.parse_file("percorso/inesistente/schema.json")


def test_invalid_json_syntax(parser, tmp_path):
    """Testa che venga sollevato SchemaError se il file non è un JSON valido."""
    p = tmp_path / "broken.json"
    p.write_text("{ questa non è una stringa json valida }", encoding='utf-8')

    with pytest.raises(SchemaError) as excinfo:
        parser.parse_file(str(p))
    
    assert "Invalid file" in str(excinfo.value)


def test_invalid_schema_structure(parser, tmp_path):
    """
    Testa che venga sollevato SchemaError se il JSON è valido
    ma non rispetta le specifiche di JSON Schema (es. tipo sconosciuto).
    """
    p = tmp_path / "bad_schema.json"
    # 'type' deve essere stringa o array, qui mettiamo un numero per rompere la validazione
    bad_content = {"type": 12345} 
    p.write_text(json.dumps(bad_content), encoding='utf-8')

    with pytest.raises(SchemaError) as excinfo:
        parser.parse_file(str(p))
    
    assert "Errore imprevisto nella validazione dello schema" in str(excinfo.value)

# Generazione dei test secondo i criteri richiesti

# Fixture: crea un parser nuovo per ogni test
@pytest.fixture
def parser():
    return SchemaParser()

# --- Boundary Value Analysis (BVA) ---

def test_parse_empty_file(parser, tmp_path):
    """Testa che un file vuoto sollevi SchemaError (boundary: file vuoto)."""
    p = tmp_path / "empty.json"
    p.write_text("", encoding='utf-8')
    with pytest.raises(SchemaError) as excinfo:
        parser.parse_file(str(p))
    assert "Invalid file" in str(excinfo.value)

def test_parse_single_char_file(parser, tmp_path):
    """Testa che un file con un solo carattere non valido sollevi SchemaError."""
    p = tmp_path / "single_char.json"
    p.write_text("{", encoding='utf-8')
    with pytest.raises(SchemaError) as excinfo:
        parser.parse_file(str(p))
    assert "Invalid file" in str(excinfo.value)

def test_parse_minimal_valid_schema(parser, tmp_path):
    """Testa il parsing di uno schema JSON Schema minimo valido (boundary: schema minimo)."""
    p = tmp_path / "minimal.json"
    minimal_schema = {"type": "object"}
    p.write_text(json.dumps(minimal_schema), encoding='utf-8')
    result = parser.parse_file(str(p))
    assert isinstance(result, dict)
    assert result["type"] == "object"

# --- Weak Equivalence Class Testing (WECT) ---

def test_validate_structure_valid(parser):
    """Testa _validate_structure con schema valido."""
    valid_schema = {"type": "object"}
    # Non deve sollevare eccezioni
    parser._validate_structure(valid_schema)

def test_validate_structure_invalid_type(parser):
    """Testa _validate_structure con tipo non valido (WECT: schema non valido)."""
    invalid_schema = {"type": 123}
    with pytest.raises(SchemaError) as excinfo:
        parser._validate_structure(invalid_schema)
    assert "Errore imprevisto nella validazione dello schema" in str(excinfo.value)

def test_validate_structure_missing_type(parser):
    """Testa _validate_structure con proprietà mancante (no 'type')."""
    schema = {"properties": {"foo": {"type": "string"}}}
    # JSON Schema permette schemi senza 'type', quindi non dovrebbe sollevare
    parser._validate_structure(schema)

def test_validate_structure_invalid_property_type(parser):
    """Testa _validate_structure con proprietà con tipo errato."""
    schema = {
        "type": "object",
        "properties": {
            "foo": {"type": 123}
        }
    }
    with pytest.raises(SchemaError) as excinfo:
        parser._validate_structure(schema)
    assert "Errore imprevisto nella validazione dello schema" in str(excinfo.value)

# --- Worst Case Testing (WCT) ---

def test_parse_file_exists_json_invalid_schema_invalid(parser, tmp_path):
    """File esistente, JSON valido, schema non valido (tipo errato)."""
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"type": 123}), encoding='utf-8')
    with pytest.raises(SchemaError):
        parser.parse_file(str(p))

def test_parse_file_exists_json_invalid_schema_valid(parser, tmp_path):
    """File esistente, JSON valido, schema valido."""
    p = tmp_path / "good.json"
    p.write_text(json.dumps({"type": "object"}), encoding='utf-8')
    result = parser.parse_file(str(p))
    assert result["type"] == "object"

def test_parse_file_exists_json_not_valid(parser, tmp_path):
    """File esistente, JSON non valido."""
    p = tmp_path / "not_json.json"
    p.write_text("not a json", encoding='utf-8')
    with pytest.raises(SchemaError):
        parser.parse_file(str(p))

# --- Intra Class Testing: SchemaError coverage ---

def test_schema_error_message():
    """Testa che SchemaError accetti e mostri il messaggio."""
    err = SchemaError("errore di test")
    assert str(err) == "errore di test"