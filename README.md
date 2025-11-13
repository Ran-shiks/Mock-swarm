# 🧩 Schema-Driven Mock Data Generator

![CI Pipeline](https://github.com/Ran-shiks/Mock-swarm/actions/workflows/ci.yml/badge.svg)


> Un generatore di dati fittizi **intelligente** e **basato su schema**, progettato per creare mock data **validi e realistici** a partire da definizioni di modelli (JSON Schema, OpenAPI, classi, ecc.).

---

## 🚀 Introduzione

Quando si sviluppano **API**, si scrivono **test automatici** o si creano **prototipi**, servono dati realistici.
Scriverli a mano è noioso e soggetto a errori, mentre generarli in modo casuale raramente rispetta i vincoli del modello (es. un campo `email` deve sembrare davvero un’email).

**Schema-Driven Mock Data Generator** risolve questo problema:
analizza automaticamente lo **schema di input** e genera dati **coerenti e validi**, pronti per essere usati in test, mock server o ambienti di sviluppo.

---

## 📦 Possibili Estensioni Future

* Supporto diretto a **classi Python**, **Java** o **TypeScript**
* Generazione basata su **OpenAPI endpoints**
* Mock di **relazioni tra oggetti** (es. `User` → `Address`)
* Integrazione con **Faker** o librerie di dati sintetici
* Interfaccia **web o GUI**

---

## Struttura Esempio di Progetto
.
├── src/
│   ├── mockgen/
│   ├── generators/
│   └── ...
├── tests/
│   └── test_generators.py
├── features/                 ← cartella per i test behave
│   ├── schema_generation.feature
│   └── steps/
│       └── test_schema_steps.py
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml
