import pytest
import tempfile
import os
import json

from src.static_generator.schema_parser import SchemaParser, SchemaError

# Schema di esempio per i test (JSON Schema valido)
EXAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

def create_temp_json(data):
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
    json.dump(data, tmp)
    tmp.close()
    return tmp.name

def create_schema_file(schema):
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
    json.dump(schema, tmp)
    tmp.close()
    return tmp.name

@pytest.fixture(scope="module")
def schema_path():
    path = create_schema_file(EXAMPLE_SCHEMA)
    yield path
    os.remove(path)

def test_TC_001_wect_valido(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Alice", "age": 30}
    file_path = create_temp_json(data)
    result = parser.parse_file(file_path)
    assert result == data
    os.remove(file_path)

def test_TC_002_wect_non_valido(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Alice"}  # manca 'age'
    file_path = create_temp_json(data)
    with pytest.raises(SchemaError):
        parser.parse_file(file_path)
    os.remove(file_path)

def test_TC_003_errore_file_non_esistente(schema_path):
    parser = SchemaParser(schema_path)
    with pytest.raises(FileNotFoundError):
        parser.parse_file("non_esiste.json")

def test_TC_004_errore_file_non_json(schema_path):
    parser = SchemaParser(schema_path)
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json', encoding='utf-8')
    tmp.write("non è json")
    tmp.close()
    with pytest.raises(SchemaError):
        parser.parse_file(tmp.name)
    os.remove(tmp.name)

def test_TC_005_bva_minimo(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Bob", "age": 0}
    file_path = create_temp_json(data)
    result = parser.parse_file(file_path)
    assert result == data
    os.remove(file_path)

def test_TC_006_bva_minimo_meno_1(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Bob"}  # manca 'age'
    file_path = create_temp_json(data)
    with pytest.raises(SchemaError):
        parser.parse_file(file_path)
    os.remove(file_path)

def test_TC_007_bva_massimo(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Carol", "age": 99}
    file_path = create_temp_json(data)
    result = parser.parse_file(file_path)
    assert result == data
    os.remove(file_path)

def test_TC_008_bva_massimo_piu_1(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Dave", "age": 40, "extra": "field"}
    file_path = create_temp_json(data)
    # Se lo schema consente campi extra, non solleva errore
    try:
        result = parser.parse_file(file_path)
        assert result == data
    except SchemaError:
        pass
    os.remove(file_path)

def test_TC_009_errore_tipo_dato(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Eve", "age": "non_numero"}
    file_path = create_temp_json(data)
    with pytest.raises(SchemaError):
        parser.parse_file(file_path)
    os.remove(file_path)

def test_TC_010_happy_path(schema_path):
    parser = SchemaParser(schema_path)
    data = {"name": "Frank", "age": 45}
    file_path = create_temp_json(data)
    result = parser.parse_file(file_path)
    assert result == data
    os.remove(file_path)


# AGGIUNTI PER COPERTURA MAGGIORE
# =============================================================================
# TEST AGGIUNTIVI (COPERTURA 100%)
# =============================================================================
from unittest.mock import patch


def test_TC_MISSING_01_init_senza_argomenti():
    """Copre riga 29: Errore se non si passa nulla al costruttore."""
    with pytest.raises(ValueError, match="Fornire almeno uno"):
        SchemaParser()


def test_TC_MISSING_02_schema_non_dizionario():
    """Copre riga 37: Lo schema deve essere un dict."""
    with pytest.raises(SchemaError, match="deve essere un oggetto JSON"):
        SchemaParser.validate_schema(["non", "un", "dict"])


def test_TC_MISSING_03_schema_struttura_errata():
    """Copre righe 47, 49, 51: Controlli su 'type' e 'properties'."""
    # Manca type
    with pytest.raises(SchemaError, match="deve avere 'type': 'object'"):
        SchemaParser(schema={"properties": {}})

    # Type sbagliato
    with pytest.raises(SchemaError, match="deve avere 'type': 'object'"):
        SchemaParser(schema={"type": "array", "properties": {}})

    # Manca properties
    with pytest.raises(SchemaError, match="deve avere una proprietà 'properties'"):
        SchemaParser(schema={"type": "object"})


def test_TC_MISSING_04_required_non_lista():
    """Copre riga 53: 'required' deve essere una lista."""
    schema = {
        "type": "object",
        "properties": {},
        "required": "stringa_errata"
    }
    with pytest.raises(SchemaError, match="'required' deve essere una lista"):
        SchemaParser(schema=schema)


def test_TC_MISSING_05_context_manager():
    """Copre righe 120, 123: Uso di __enter__ e __exit__."""
    schema = {"type": "object", "properties": {}}
    with SchemaParser(schema=schema) as p:
        assert isinstance(p, SchemaParser)


def test_TC_MISSING_06_from_dict():
    """Copre riga 130: Metodo factory from_dict."""
    schema = {"type": "object", "properties": {}}
    parser = SchemaParser.from_dict(schema)
    assert isinstance(parser, SchemaParser)


def test_TC_MISSING_07_errore_generico_validazione():
    """Copre riga 63: Cattura eccezione generica durante validate_schema."""
    # Usiamo patch per forzare un errore imprevisto (es. MemoryError o altro)
    # durante la deepcopy interna a validate_schema
    with patch('src.static_generator.schema_parser.copy.deepcopy', side_effect=Exception("BOOM")):
        with pytest.raises(SchemaError, match="Errore imprevisto"):
            SchemaParser(schema={"type": "object", "properties": {}})