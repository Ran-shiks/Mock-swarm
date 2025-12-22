fake = Faker('it_IT')
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
        n = random.randint(min_items, max_items)
        item_type = self.props.get("item_type")
        item_options = self.props.get("item_options", [])
        result = []
        if item_type == "string" and item_options:
            result = random.sample(item_options, k=n)
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
    """
    Factory per generatori in base al tipo di campo.
    """
    t = field_props.get("type")
    if t == "uuid":
        return UUIDGenerator(field_name, field_props)
    elif t == "choice":
        return ChoiceGenerator(field_name, field_props)
    elif t == "float":
        return FloatGenerator(field_name, field_props)
    elif t == "integer":
        return IntegerGenerator(field_name, field_props)
    elif t == "string":
        return StringGenerator(field_name, field_props)
    elif t == "object":
        return ObjectGenerator(field_name, field_props)
    elif t == "array":
        return ArrayGenerator(field_name, field_props)
    elif t == "string":
        return StringGenerator(field_name, field_props)
    elif t == "object":
        return ObjectGenerator(field_name, field_props)
    elif t == "array":
        return ArrayGenerator(field_name, field_props)
    else:
        raise ValueError(f"Tipo non supportato: {t}")