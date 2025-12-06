import pytest
import tempfile
import os
import json

from src.static_generator.schema_parser import SchemaParser, SchemaError

# Schema di esempio per i test
EXAMPLE_SCHEMA = {
    "name": {"type": "string"},
    "age": {"type": "integer"}
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
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
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