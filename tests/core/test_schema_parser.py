import pytest
import json
import os
from src.core.schema_parser import SchemaParser, SchemaError

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
