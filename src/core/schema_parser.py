# https://docs.python.org/3/library/json.html


import json
import os
from typing import Any, Dict



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



        return True
    

class SchemaError(Exception):
    """Eccezione"""
    pass