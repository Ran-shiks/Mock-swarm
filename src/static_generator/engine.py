import json
from .schema_parser import SchemaParser
from .algorithmic import get_generator

class MockEngine:
    def __init__(self, schema_path):
        self.parser = SchemaParser(schema_path)
        self.fields = self.parser.get_fields()

    def generate_record(self):
        record = {}
        for fname, fprops in self.fields.items():
            gen = get_generator(fname, fprops)
            record[fname] = gen.generate()
        return record

    def generate(self, n=1):
        return [self.generate_record() for _ in range(n)]


