# https://docs.python.org/3/library/json.html


import json
import os
from typing import Any, Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import validator_for


class SchemaParser:

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


        return True

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