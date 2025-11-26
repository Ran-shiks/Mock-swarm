import random
from typing import Dict, Any, Optional, List
from faker import Faker
from .base import BaseGenerator

class AlgorithmicGenerator(BaseGenerator):
    """
    Generatore deterministico/casuale basato su librerie standard (Faker)
    e logica di parsing dello schema. Non usa LLM.
    """

    def __init__(self, seed: Optional[int] = None, locale: str = 'en_US'):
        self.faker = Faker(locale)
        self.seed = seed
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def generate(self, schema: Dict[str, Any], context: Optional[str] = None) -> Any:
        return self._process_node(schema)

    def _process_node(self, node: Dict[str, Any]) -> Any:
        """
        Metodo ricorsivo centrale. Analizza il 'type' del nodo corrente
        e smista la chiamata al generatore specifico.
        """
        # 1. Gestione Enum (se presente, vince su tutto)
        if "enum" in node:
            return random.choice(node["enum"])
        
        # 2. Gestione Const
        if "const" in node:
            return node["const"]

        node_type = node.get("type", "string") # Default a string se non specificato

        if node_type == "object":
            return self._generate_object(node)
        elif node_type == "array":
            return self._generate_array(node)
        elif node_type == "string":
            return self._generate_string(node)
        elif node_type == "integer":
            return self._generate_integer(node)
        elif node_type == "number":
            return self._generate_number(node)
        elif node_type == "boolean":
            return random.choice([True, False])
        elif node_type == "null":
            return None
        
        return None

    def _generate_object(self, node: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        properties = node.get("properties", {})
        required = node.get("required", [])

        for key, prop_schema in properties.items():
            # Semplificazione: per ora generiamo sempre tutti i campi, 
            # in futuro potremmo omettere i campi non 'required' casualmente.
            result[key] = self._process_node(prop_schema)
            
        return result

    def _generate_array(self, node: Dict[str, Any]) -> List[Any]:
        items_schema = node.get("items", {})
        min_items = node.get("minItems", 1)
        max_items = node.get("maxItems", 5)
        
        # Determina la lunghezza casuale rispettando i vincoli
        length = random.randint(min_items, max_items)
        
        return [self._process_node(items_schema) for _ in range(length)]

    def _generate_string(self, node: Dict[str, Any]) -> str:
        fmt = node.get("format")
        
        # Mappatura formati speciali -> Faker
        if fmt == "email":
            return self.faker.email()
        elif fmt == "uuid":
            return self.faker.uuid4()
        elif fmt == "date":
            return self.faker.date()
        elif fmt == "date-time":
            return self.faker.iso8601()
        elif fmt == "ipv4":
            return self.faker.ipv4()
        elif fmt == "uri" or fmt == "url":
            return self.faker.url()
            
        # Gestione lunghezza
        min_len = node.get("minLength", 5)
        max_len = node.get("maxLength", 20)
        
        return self.faker.text(max_nb_chars=max_len).strip()[:max_len]

    def _generate_integer(self, node: Dict[str, Any]) -> int:
        min_val = node.get("minimum", 0)
        max_val = node.get("maximum", 1000)
        return random.randint(min_val, max_val)

    def _generate_number(self, node: Dict[str, Any]) -> float:
        min_val = node.get("minimum", 0.0)
        max_val = node.get("maximum", 1000.0)
        return random.uniform(min_val, max_val)