from faker import Faker
import uuid
import random
from typing import Any, Dict
from .base import FieldGenerator

fake = Faker('it_IT')

class UUIDGenerator(FieldGenerator):
    """Generatore per UUID."""
    def generate(self) -> str:
        return str(uuid.uuid4())

class ChoiceGenerator(FieldGenerator):
    """Generatore per scelta casuale da una lista di opzioni."""
    def generate(self) -> Any:
        options = self.props.get("options", [])
        if not options:
            return None
        weights = self.props.get("weights", [1] * len(options))
        return random.choices(options, weights=weights, k=1)[0]

class FloatGenerator(FieldGenerator):
    """Generatore per numeri float."""
    def generate(self) -> float:
        min_v = self.props.get("min_value", 0.0)
        max_v = self.props.get("max_value", 1.0)
        dec = self.props.get("decimal_places", 2)
        value = random.uniform(min_v, max_v)
        return round(value, dec)

class StringGenerator(FieldGenerator):
    """Generatore per stringhe, con supporto a vari tipi tramite Faker."""
    def generate(self) -> str:
        # 1. Gestione standard JSON Schema "format"
        fmt = self.props.get("format")
        if fmt == "email":
            return fake.email()
        elif fmt == "date":
            return fake.date()
        elif fmt == "ipv4":
            return fake.ipv4()
        elif fmt == "uri":
            return fake.uri()

        gen = self.props.get("generator")
        if gen:
            # Supporto dinamico per generatori faker
            try:
                faker_func = getattr(fake, gen)
                return faker_func()
            except AttributeError:
                pass
        return fake.word()

class ObjectGenerator(FieldGenerator):
    """Generatore per oggetti annidati."""
    def generate(self) -> Dict[str, Any]:
        fields = self.props.get("fields", {})
        result = {}
        for fname, fprops in fields.items():
            gen = get_generator(fname, fprops)
            result[fname] = gen.generate()
        return result

class ArrayGenerator(FieldGenerator):
    """Generatore per array di elementi."""
    def generate(self) -> list:
        min_items = self.props.get("min_items", 1)
        max_items = self.props.get("max_items", 5)

        # Assicura che max non sia minore di min
        if max_items < min_items:
            max_items = min_items

        n = random.randint(min_items, max_items)
        item_type = self.props.get("item_type")
        item_options = self.props.get("item_options", [])
        result = []
        if item_type == "string" and item_options:
            result = random.sample(item_options, k=n)
        # Caso generico: Usiamo la factory per creare gli item
        # Questo è molto più potente: permette array di oggetti, di interi, etc.
        elif item_type:
            # Creiamo una "property" fittizia per l'item
            item_props = {"type": item_type}
            # Passiamo eventuali altre proprietà dell'item se presenti nello schema

            generator = get_generator("item", item_props)
            for _ in range(n):
                result.append(generator.generate())
        else:
            for _ in range(n):
                result.append(fake.word())
        return result

class IntegerGenerator(FieldGenerator):
    """Generatore per numeri interi."""
    def generate(self) -> int:
        min_v = self.props.get("min_value", 0)
        max_v = self.props.get("max_value", 100)
        return random.randint(min_v, max_v)

def get_generator(field_name: str, field_props: dict) -> FieldGenerator:
    """Factory per ottenere il generatore corretto in base al tipo di campo."""
    t = field_props.get("type")
    # Mapping diretto
    generators_map = {
        "uuid": UUIDGenerator,
        "choice": ChoiceGenerator,
        "float": FloatGenerator,
        "integer": IntegerGenerator,
        "string": StringGenerator,
        "object": ObjectGenerator,
        "array": ArrayGenerator
    }
    gen_class = generators_map.get(t)
    if gen_class:
        return gen_class(field_name, field_props)

    raise ValueError(f"Tipo non supportato: {t}")