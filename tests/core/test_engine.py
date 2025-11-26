import pytest
from src.core.engine import MockGenEngine

'''
Intra Method Testing
Nella classe engine ci sono:
    - __init__
    - generate
    - _get_generator_strategy

    In particolare _get_generator_strategy è un metodo "privato" che viene chiamato da generate.

    Partiamo con il black box testing in cui dobbiamo usare questi criteri di test

    - Classi di equivalenza, in particolare effettuiamo un WECT (Weak Equivalence Class Testing)
    - Analisi dei valori limite (Boundary Value Analysis)
    - Worst Case Testing

    costruttore __init__ posso fare:

    WECT gia fatto nel test_engine_initialization dove si genera uno schema e si prova
    BVA: Provo senza schema, uno schema vuoto, uno con un solo campo, uno con molti campi
    WCT: Per il costruttore non ha molto senso fare WCT, ma per generate si.

    Funzione generate:

    SECT: uso AI si/no, count basso/alto, ai_prompt presente/assente, seed presente/assente
    Qui stiamo facendo anche white box testing perchè conosciamo l'implementazione interna.
    In particolare secondo il criterio di Condition Coverage
    Le combinazioni dei precenti sono:

    AI | count | ai_prompt | seed
    -----------------------------------
    0  | basso | assente   | assente
    0  | basso | assente   | presente
    0  | basso | presente  | assente
    0  | basso | presente  | presente
    0  | alto  | assente   | assente
    0  | alto  | assente   | presente
    0  | alto  | presente  | assente
    0  | alto  | presente  | presente
    1  | basso | assente   | assente
    1  | basso | assente   | presente
    1  | basso | presente  | assente
    1  | basso | presente  | presente
    1  | alto  | assente   | assente
    1  | alto  | assente   | presente
    1  | alto  | presente  | assente
    1  | alto  | presente  | presente
    
    Dove per basso intendiamo 1-10 e per alto 100-1000
    BVA: count 0, 1, 10, 1000
    WCT: Tutte le combinazioni di SECT sopra elencate

    Funzione _get_generator_strategy:
    WECT: use_ai True/False, seed presente/assente
    Qui stiamo facendo anche white box testing perchè conosciamo l'implementazione interna.
    In particolare secondo il criterio di Condition Coverage
    Le combinazioni dei precenti sono:
    use_ai | seed
    ----------------
    0      | assente
    0      | presente
    1      | assente
    1      | presente

    BVA: N/A
    WCT: Tutte le combinazioni di SECT sopra elencate
 '''


SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "age": {"type": "integer", "minimum": 18, "maximum": 90}
    },
    "required": ["username"]
}

def test_engine_initialization():
    """Testa che l'engine si inizializzi correttamente."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    assert engine.schema == SIMPLE_SCHEMA

def test_generate_algorithmic_single_record():
    """Testa la generazione di un singolo record (Algoritmico)."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    results = engine.generate(count=1, use_ai=False)

    assert isinstance(results, list)
    assert len(results) == 1
    record = results[0]
    
    # Verifica che il generatore algoritmico abbia fatto il suo lavoro
    assert "username" in record
    assert isinstance(record["username"], str)
    assert "age" in record
    assert isinstance(record["age"], int)

def test_generate_algorithmic_multiple_records():
    """Testa il parametro count."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    count = 5
    results = engine.generate(count=count, use_ai=False)
    
    assert len(results) == count
    # Verifica che siano tutti dizionari
    for res in results:
        assert isinstance(res, dict)

def test_generate_smart_strategy_switch():
    """
    Testa che passando use_ai=True venga usato lo SmartGenerator.
    Verifichiamo l'output 'stub' che abbiamo messo nel file smart.py
    """
    engine = MockGenEngine(SIMPLE_SCHEMA)
    results = engine.generate(count=1, use_ai=True, ai_prompt="Test context")

    assert len(results) == 1
    record = results[0]

    # Verifica basata sul placeholder che abbiamo messo in SmartGenerator.generate
    assert "_ai_metadata" in record
    assert record["context_received"] == "Test context"
    assert engine.generator.__class__.__name__ == "SmartGenerator"

def test_generate_algorithmic_strategy_switch():
    """
    Testa che passando use_ai=False venga usato l'AlgorithmicGenerator.
    """
    engine = MockGenEngine(SIMPLE_SCHEMA)
    results = engine.generate(count=1, use_ai=False)

    assert len(results) == 1
    record = results[0]

    assert engine.generator.__class__.__name__ == "AlgorithmicGenerator"

def test_reproducibility_with_seed():
    """
    Testa che usando lo stesso seed, l'algoritmo generi gli stessi dati.
    """
    seed = 42
    engine1 = MockGenEngine(SIMPLE_SCHEMA)
    res1 = engine1.generate(count=1, seed=seed)[0]

    engine2 = MockGenEngine(SIMPLE_SCHEMA)
    res2 = engine2.generate(count=1, seed=seed)[0]

    # Faker con lo stesso seed deve produrre gli stessi valori
    assert res1 == res2
    
    # Controllo che senza seed (o seed diverso) siano (probabilmente) diversi
    engine3 = MockGenEngine(SIMPLE_SCHEMA)
    res3 = engine3.generate(count=1, seed=43)[0]
    # Nota: c'è una minuscola probabilità che siano uguali per caso, 
    # ma con stringhe e numeri random è trascurabile per questo test.
    assert res1 != res3


'''
Intra Class Testing

Nella classe engine ci sono chiamate ad altre classi (generators).
In particolare nel metodo _get_generator_strategy vengono chiamate le classi
AlgorithmicGenerator e SmartGenerator.
Possiamo fare dei test per verificare che l'integrazione tra engine e generators
funzioni correttamente.
    - Testare che passando use_ai=True venga effettivamente usato SmartGenerator
    - Testare che passando use_ai=False venga effettivamente usato AlgorithmicGenerator
Cosa che gia abbiamo fatto nei test per la funzione sopra.
'''

@pytest.mark.parametrize("schema", [
    None,  # BVA: schema assente
    {},    # BVA: schema vuoto
    {"type": "object", "properties": {"a": {"type": "string"}}},  # BVA: schema con un solo campo
    {"type": "object", "properties": {f"f{i}": {"type": "integer"} for i in range(100)}}  # BVA: schema con molti campi
])
def test_engine_init_bva(schema):
    """Boundary Value Analysis sul costruttore."""
    try:
        engine = MockGenEngine(schema)
        assert engine.schema == schema
    except Exception:
        # Se lo schema è None o vuoto, può sollevare eccezione o passare (sanity check)
        assert schema is None or schema == {}

@pytest.mark.parametrize("count", [0, 1, 10, 1000])
def test_generate_count_bva(count):
    """Boundary Value Analysis sul parametro count."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    results = engine.generate(count=count, use_ai=False)
    assert isinstance(results, list)
    assert len(results) == count

import itertools

@pytest.mark.parametrize("use_ai,count,ai_prompt,seed", [
    (ai, cnt, prompt, sd)
    for ai in [False, True]
    for cnt in [1, 100]
    for prompt in [None, "Prompt di test"]
    for sd in [None, 123]
])
def test_generate_wct(use_ai, count, ai_prompt, seed):
    """Worst Case Testing: tutte le combinazioni di use_ai, count, ai_prompt, seed."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    results = engine.generate(count=count, use_ai=use_ai, ai_prompt=ai_prompt, seed=seed)
    assert isinstance(results, list)
    assert len(results) == count
    for record in results:
        assert isinstance(record, dict)
        if use_ai:
            assert "_ai_metadata" in record
            if ai_prompt:
                assert record.get("context_received") == ai_prompt

@pytest.mark.parametrize("use_ai,seed", [
    (False, None),
    (False, 42),
    (True, None),
    (True, 42)
])
def test_get_generator_strategy_wect(use_ai, seed):
    """WECT: tutte le combinazioni di use_ai e seed per _get_generator_strategy."""
    engine = MockGenEngine(SIMPLE_SCHEMA)
    gen = engine._get_generator_strategy(use_ai, seed)
    if use_ai:
        assert gen.__class__.__name__ == "SmartGenerator"
        # Se seed è passato, dovrebbe essere impostato
        if seed is not None:
            assert hasattr(gen, "seed")
            assert gen.seed == seed
    else:
        assert gen.__class__.__name__ == "AlgorithmicGenerator"
                # Se seed è passato, dovrebbe essere impostato
        if seed is not None:
            assert hasattr(gen, "seed")
            assert gen.seed == seed