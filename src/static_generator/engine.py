from typing import Any, Dict, List
from .schema_parser import SchemaParser
from .algorithmic import get_generator, fake
from faker import Faker
import random

class MockEngine:
    """
    Motore per la generazione di dati mock a partire da uno schema JSON.
    """
    def __init__(self, schema_path: str, seed: int = None):
        # 1. Gestione del Seed: Se presente, rendiamo deterministici random e Faker
        # Se l'utente (o il test) ci passa un numero come seed...
        if seed is not None:
            # 1. Blocchiamo il generatore nativo di Python
            random.seed(seed)

            # 2. Blocchiamo il generatore della libreria Faker
            Faker.seed(seed)

            # 3. Blocca l'istanza specifica usata in algorithmic.py
            fake.seed_instance(seed)

        self.parser = SchemaParser(schema_path)
        self.fields = self.parser.get_fields()

    def generate_record(self) -> Dict[str, Any]:
        """
        Genera un singolo record mock.
        """
        record = {}
        for fname, fprops in self.fields.items():
            try:
                gen = get_generator(fname, fprops)
                record[fname] = gen.generate()
            except Exception as e:
                record[fname] = None
        return record

    def generate(self, n: int = 1) -> List[Dict[str, Any]]:
        """
        Genera una lista di record mock.
        """
        return [self.generate_record() for _ in range(n)]


