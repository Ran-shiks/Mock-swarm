# https://docs.python.org/3/library/json.html


import json
import os
from typing import Any, Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import validator_for



class SchemaError(Exception):
    """Eccezione personalizzata per errori di schema."""
    pass


class SchemaParser:
    """
    Parser e validatore per JSON Schema.
    Permette di caricare, validare e ispezionare uno schema JSON.
    """

    def __init__(self, schema_path: str = None, schema: dict = None, encoding: str = "utf-8"):
        """
        Inizializza il parser. Può ricevere un path a file o direttamente un dict schema.
        """
        if schema is not None:
            self.schema = schema
        elif schema_path is not None:
            try:
                with open(schema_path, 'r', encoding=encoding) as f:
                    self.schema = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                raise FileNotFoundError(f"Errore nel caricamento dello schema: {e}")
        else:
            raise ValueError("Fornire almeno uno tra schema_path o schema.")
        self.validate_schema(self.schema)

    @staticmethod
    def validate_schema(schema: dict) -> None:
        """
        Valida la struttura di uno schema JSON secondo le regole base e JSON Schema.
        """
        if not isinstance(schema, dict):
            raise SchemaError("Lo schema deve essere un oggetto JSON.")
        if "type" not in schema or schema["type"] != "object":
            raise SchemaError("Lo schema deve avere 'type': 'object'.")
        if "properties" not in schema or not isinstance(schema["properties"], dict):
            raise SchemaError("Lo schema deve avere una proprietà 'properties' di tipo oggetto.")
        if "required" in schema and not isinstance(schema["required"], list):
            raise SchemaError("La proprietà 'required' deve essere una lista.")
        # Validazione secondo specifica JSON Schema
        try:
            cls = validator_for(schema)
            cls.check_schema(schema)
        except ValidationError as e:
            raise SchemaError(f"Lo schema fornito non è valido secondo le specifiche JSON Schema: {e.message}")
        except Exception as e:
            raise SchemaError(f"Errore imprevisto nella validazione dello schema: {str(e)}")

    def get_fields(self) -> Dict[str, Any]:
        """
        Restituisce le proprietà dello schema.
        """
        return self.schema.get("properties", {})

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Carica e valida un file dati rispetto allo schema.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaError(f"File JSON non valido: {e}")
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            raise SchemaError(f"Errore di validazione dei dati: {e.message}")
        return data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def from_dict(cls, schema_dict: dict) -> "SchemaParser":
        """
        Crea un parser direttamente da un dict schema.
        """
        return cls(schema=schema_dict)