
Una linea guida:

Mock-swarm/
├── frontend/
│
│
├── src/                        # Il package principale (Codice Sorgente)
│   ├── __init__.py              # Espone le funzioni per l'uso come libreria
│   │
│   ├── generators/              # Pattern Strategy: diversi modi di generare dati
│   │   ├── __init__.py
│   │   ├── base.py              # Classe astratta/interfaccia per i generatori
│   │   ├── algorithmic.py       # Generazione deterministica (Faker, Random)
│   │   ├── engine.py            
│   │   └── schema_parser.py     # Parsing e validazione del JSON Schema
│   │
│   └── llm/                   # llm
│       ├── __init__.py
|       ├── v2Olama.py
│       └── v2olama_chat.py       
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