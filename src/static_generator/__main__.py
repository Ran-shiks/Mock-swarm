import json
from .engine import MockEngine

if __name__ == "__main__":
    import sys
    schema_path = "./example_schema.json"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    engine = MockEngine(schema_path)
    data = engine.generate(n)
    print(json.dumps(data, indent=2, ensure_ascii=False))