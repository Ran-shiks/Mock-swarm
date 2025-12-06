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
        # Validazione base, espandibile
        if not isinstance(self.schema, dict):
            raise ValueError("Lo schema deve essere un oggetto JSON.")
        for field, props in self.schema.items():
            if "type" not in props:
                raise ValueError(f"Il campo '{field}' deve avere una proprietà 'type'.")

    def get_fields(self):
        return self.schema

    def parse_file(self, file_path: str) -> Dict[str, Any]:

        # check path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Schema not found in {file_path}")
        
        # otherwise try to parse file as json
        try:
            with open(file_path, 'r', encoding='utf-8') as f :
                schema_data = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaError(f"Invalid file {e}")
        
        #validate json structure

        self._validate_structure(schema_data)

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