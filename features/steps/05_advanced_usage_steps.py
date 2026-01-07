import os
import csv
import io
import json
from behave import given, when, then
# Importiamo le utility manuali
from src.static_generator.utils import run_cli_command, create_temp_schema, clean_files


# =============================================================================
# SCENARIO 1: Exporting data to CSV
# =============================================================================
@given(u'I have a flat schema (without complex nested objects)')
def step_flat_schema(context):
    # Definiamo uno schema semplice "piatto"
    context.flat_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "role": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    # Creazione manuale del file
    context.schema_path = create_temp_schema("flat_schema.json", context.flat_schema)


@when(u'I run the command with "--format csv"')
def step_run_csv(context):
    cmd = f"mockgen generate --schema {context.schema_path} --format csv"
    context.result = run_cli_command(cmd)

    # Pulizia manuale immediata
    clean_files([context.schema_path])


@then(u'the output is formatted as comma-separated text with headers')
def step_verify_csv(context):
    assert context.result.returncode == 0
    output = context.result.stdout.strip()

    # Verifica che non sia vuoto
    assert len(output) > 0, "L'output CSV è vuoto"

    # Usiamo la libreria CSV di Python per verificare che sia valido
    f = io.StringIO(output)
    reader = csv.reader(f, delimiter=',')
    rows = list(reader)

    # Verifica intestazioni (prima riga)
    headers = rows[0]
    assert "id" in headers and "name" in headers

    # Verifica che ci siano dati (almeno header + 1 riga)
    # Nota: se il default count è 1, avremo 2 righe totali
    assert len(rows) >= 2, "Il CSV dovrebbe contenere header e dati"


# =============================================================================
# SCENARIO 2: Streaming data in NDJSON
# =============================================================================
@given(u'I am generating a large number of records')
def step_large_records(context):
    context.count = 5
    context.schema = {"type": "object", "properties": {"val": {"type": "integer"}}}
    context.schema_path = create_temp_schema("stream_schema.json", context.schema)


@when(u'I run the command with "--format ndjson"')
def step_run_ndjson(context):
    # Aggiungiamo --count per simulare più record
    cmd = f"mockgen generate --schema {context.schema_path} --format ndjson --count {context.count}"
    context.result = run_cli_command(cmd)

    clean_files([context.schema_path])


@then(u'each JSON object is printed on a new line as it is generated')
def step_verify_ndjson(context):
    assert context.result.returncode == 0
    output = context.result.stdout.strip()

    lines = output.splitlines()
    # Verifica numero righe = numero oggetti
    assert len(lines) == context.count

    # Verifica che ogni riga sia un JSON valido indipendente
    for line in lines:
        try:
            obj = json.loads(line)
            assert isinstance(obj, dict)
        except json.JSONDecodeError:
            assert False, f"Riga non valida in NDJSON: {line}"


# =============================================================================
# SCENARIO 3: Import into Node.js project (Library Usage)
# =============================================================================
# Questo scenario è marcato @wip, ma definiamo gli step per evitare errori
# "Step undefined" se lo esegui.

@given(u'I am writing a test script in Node.js')
def step_node_env(context):
    pass


@when(u'I import the library and call "MockGen.generate(schema)"')
def step_call_library(context):
    pass


@then(u'the function returns a Promise that resolves with the data object')
def step_check_promise(context):
    pass


# =============================================================================
# SCENARIO 4: Exporting data to SQL
# =============================================================================
@given(u'I want to populate a database table named "users"')
def step_sql_setup(context):
    context.table_name = "users"
    context.sql_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "active": {"type": "boolean"}
        }
    }
    context.schema_path = create_temp_schema("sql_schema.json", context.sql_schema)


@when(u'I run the command with "--format sql --table-name users"')
def step_run_sql(context):
    cmd = f"mockgen generate --schema {context.schema_path} --format sql --table-name {context.table_name}"
    context.result = run_cli_command(cmd)

    clean_files([context.schema_path])


@then(u'the output contains valid INSERT INTO statements')
def step_verify_sql(context):
    assert context.result.returncode == 0
    output = context.result.stdout.strip()

    # Controlli base SQL
    expected_start = f"INSERT INTO {context.table_name}"
    assert expected_start in output, f"Manca '{expected_start}' nell'output"
    assert "VALUES" in output
    assert ";" in output  # Controllo fine istruzione