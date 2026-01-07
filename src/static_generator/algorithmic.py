from faker import Faker
import uuid
import random
from typing import Any, Dict
from .base import FieldGenerator

fake = Faker('it_IT')

class UUIDGenerator(FieldGenerator):
    """Generatore per UUID."""
    def generate(self) -> str:
        #return str(uuid.uuid4())
        return fake.uuid4()

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
    """
    Generatore per stringhe, con supporto dinamico completo a Faker.
    Supporta sia i formati standard JSON Schema che i metodi diretti di Faker.
    """
    def generate(self) -> str:
        # 1. Recupera la chiave di formato
        method_name = self.props.get("faker") or self.props.get("format") or self.props.get("generator")

        # Fallback rapido se nullo
        if not method_name:
            return fake.word()

        # 2. Dispatch Dinamico
        if hasattr(fake, method_name):
            try:
                faker_func = getattr(fake, method_name)
                return str(faker_func())
            except Exception:
                # Fallback se il metodo Faker fallisce (es. argomenti mancanti)
                return fake.word()

        # 3. Fallback finale (metodo non trovato)
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

