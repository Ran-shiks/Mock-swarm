# https://docs.python.org/3/library/json.html


import json
import os
from typing import Any, Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import validator_for


class SchemaParser:

    def __init__(self, schema_path: str):
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        self.validate_schema()

    def validate_schema(self):
        # Lo schema deve essere conforme a JSON Schema
        if not isinstance(self.schema, dict):
            raise SchemaError("Lo schema deve essere un oggetto JSON.")
        if "type" not in self.schema or self.schema["type"] != "object":
            raise SchemaError("Lo schema deve avere 'type': 'object'.")
        if "properties" not in self.schema or not isinstance(self.schema["properties"], dict):
            raise SchemaError("Lo schema deve avere una proprietà 'properties' di tipo oggetto.")
        # Opzionale: controlla che 'required' sia una lista se presente
        if "required" in self.schema and not isinstance(self.schema["required"], list):
            raise SchemaError("La proprietà 'required' deve essere una lista.")

    def get_fields(self):
        # Restituisce le proprietà dello schema
        return self.schema.get("properties", {})

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Schema not found in {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaError(f"Invalid file {e}")
        self._validate_structure(self.schema)
        try:
            validate(instance=schema_data, schema=self.schema)
        except ValidationError as e:
            raise SchemaError(f"Errore di validazione dei dati: {e.message}")
        return schema_data

    def _validate_structure(self, schema: Dict[str, Any]):
        try:
            cls = validator_for(schema)
            cls.check_schema(schema)
        except ValidationError as e:
            raise SchemaError(f"Lo schema fornito non è valido secondo le specifiche JSON Schema: {e.message}")
        except Exception as e:
            raise SchemaError(f"Errore imprevisto nella validazione dello schema: {str(e)}")    


class SchemaError(Exception):
    """Eccezione"""
    pass