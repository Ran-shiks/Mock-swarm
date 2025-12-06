from faker import Faker
import uuid
import random
from .base import FieldGenerator

fake = Faker('it_IT')

class UUIDGenerator(FieldGenerator):
    def generate(self):
        return str(uuid.uuid4())

class ChoiceGenerator(FieldGenerator):
    def generate(self):
        options = self.props.get("options", [])
        if not options:
            return [] 
        weights = self.props.get("weights", [1] * len(options))
        return random.choices(options, weights=weights, k=1)[0]

class FloatGenerator(FieldGenerator):
    def generate(self):
        min_v = self.props.get("min_value", 0.0)
        max_v = self.props.get("max_value", 1.0)
        dec = self.props.get("decimal_places", 2)
        value = random.uniform(min_v, max_v)
        return round(value, dec)

class StringGenerator(FieldGenerator):
    def generate(self):
        gen = self.props.get("generator")
        if gen == "address.street_address":
            return fake.street_address()
        elif gen == "address.city":
            return fake.city()
        elif gen == "address.postcode":
            return fake.postcode()
        else:
            return fake.word()

class ObjectGenerator(FieldGenerator):
    def generate(self):
        fields = self.props.get("fields", {})
        result = {}
        for fname, fprops in fields.items():
            gen = get_generator(fname, fprops)
            result[fname] = gen.generate()
        return result

class ArrayGenerator(FieldGenerator):
    def generate(self):
        min_items = self.props.get("min_items", 1)
        max_items = self.props.get("max_items", 5)
        n = random.randint(min_items, max_items)
        item_type = self.props.get("item_type")
        item_options = self.props.get("item_options", [])
        result = []
        if item_type == "string" and item_options:
            result = random.sample(item_options, k=n)
        else:
            # fallback: string random
            for _ in range(n):
                result.append(fake.word())
        return result

class IntegerGenerator(FieldGenerator):
    def generate(self):
        min_v = self.props.get("min_value", 0)
        max_v = self.props.get("max_value", 100)
        return random.randint(min_v, max_v)

def get_generator(field_name, field_props):
    t = field_props["type"]
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
    else:
        raise ValueError(f"Tipo non supportato: {t}")