
Una linea guida:

Mock-swarm/
│
├── src/                        # Il package principale (Codice Sorgente)
│   ├── __init__.py              # Espone le funzioni per l'uso come libreria
│   ├── __main__.py              # Entry point per eseguire il modulo (python -m mockgen)
│   ├── cli.py                   # Logica della Command Line Interface (Click/Argparse)
│   │
│   ├── core/                    # Logica "Core" del sistema
│   │   ├── __init__.py
│   │   ├── engine.py            # Il direttore d'orchestra che decide quale generatore usare
│   │   └── schema_parser.py     # Parsing e validazione del JSON Schema
│   │
│   ├── generators/              # Pattern Strategy: diversi modi di generare dati
│   │   ├── __init__.py
│   │   ├── base.py              # Classe astratta/interfaccia per i generatori
│   │   ├── algorithmic.py       # Generazione deterministica (Faker, Random)
│   │   └── smart.py             # Generazione AI (chiama i provider)
│   │
│   ├── providers/               # Pattern Adapter: astrazione degli LLM
│   │   ├── __init__.py
│   │   ├── llm_interface.py     # Interfaccia comune (es. generate_json(schema, prompt))
│   │   ├── openai_provider.py   # Implementazione per OpenAI
│   │   └── ollama_provider.py   # Implementazione per modelli locali (Ollama)
│   │
│   └── utils/                   # Utility trasversali
│       ├── file_io.py           # Lettura/Scrittura file (JSON, CSV)
│       └── formatters.py        # Formattazione output (Minify JSON, CSV conversion)
│
├── tests/                       # Unit Tests e Integration Tests classici
│   ├── __init__.py
│   ├── test_schema_parser.py
│   └── test_algorithmic.py
│
├── features/                    # BDD Tests (Gherkin + Behave)
│   ├── steps/                   # I file Python con gli step definitions generati prima
│   ├── 01_core_engine.feature
│   ├── 02_ai_integration.feature
│   └── ...
│
├── pyproject.toml               # Gestione dipendenze e metadati (moderno standard Python)
├── README.md                    # Documentazione
├── .env.example                 # Template per le variabili d'ambiente (API Keys)
└── .gitignore