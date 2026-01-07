import os
import json
from behave import given, when, then
from src.static_generator.utils import (
    run_cli_command,
    create_temp_schema,
    prepare_output_dir,
    load_json_file,
    clean_files
)


# =============================================================================
# SCENARIO 1: Lettura di uno schema json locale
# =============================================================================
@given(u'a file "./schemas/order.json" exists on the local disk')
def step_create_schema(context):
    """Crea fisicamente il file dello schema per testare la lettura da disco."""
    schema_content = {
        "type": "object",
        "properties": {
            "order_id": {"type": "integer"},
            "item": {"type": "string"}
        },
        "required": ["order_id"]
    }
    os.makedirs("./schemas", exist_ok=True)
    # Creiamo il file e ci salviamo il percorso
    context.schema_path = create_temp_schema("./schemas/order.json", schema_content)


@when(u'I run "mockgen generate --schema ./schemas/order.json"')
def step_run_basic(context):
    """Esegue il comando puntando al file locale."""
    context.process_result = run_cli_command("mockgen generate --schema ./schemas/order.json")
    # Pulizia manuale
    clean_files(["./schemas/order.json"])
    try:
        os.rmdir("./schemas")
    except OSError:
        pass


@then(u'the system correctly reads the file and does not return a "File not found" error')
def step_check_no_error(context):
    """Verifica che l'esecuzione sia avvenuta senza errori di I/O."""
    # Debug print se fallisce
    if context.process_result.returncode != 0:
        print(f"STDERR: {context.process_result.stderr}")
    assert context.process_result.returncode == 0
    assert "File not found" not in context.process_result.stderr


# =============================================================================
# SCENARIO 2: Salvataggio output su disco
# =============================================================================
@given(u'I want to save the generated data')
def step_prep_output(context):
    """Prepara la cartella di output pulita."""
    prepare_output_dir("./output")
    context.output_file = "./output/data.json"


@when(u'I run the command with the option "--out ./output/data.json"')
def step_run_out(context):
    """Esegue il comando specificando il flag --out."""
    schema_path = create_temp_schema("temp_out.json", {"type": "object", "properties": {"a": {"type": "string"}}})

    cmd = f"mockgen generate --schema {schema_path} --out ./output/data.json"
    context.process_result = run_cli_command(cmd)

    clean_files([schema_path])


@then(u'a file "data.json" is created in the specified folder')
def step_check_exists(context):
    """Controlla l'esistenza fisica del file."""
    assert os.path.exists("./output/data.json")


@then(u'the file contains the generated JSON data')
def step_check_content(context):
    """Legge il file generato e verifica che sia un JSON valido."""
    try:
        content = load_json_file("./output/data.json")
        assert isinstance(content, (list, dict))
    except Exception:
        assert False, "File JSON non valido o illeggibile"


# =============================================================================
# SCENARIO 3: Count
# =============================================================================
@given(u'I need a voluminous dataset')
def step_set_volume_requirement(context):
    """
        Imposta l'aspettativa di volume nel contesto.
        Anche se lo step When ha il numero hardcoded nel testo,
        questo step esplicita l'intento logico.
        """
    context.expected_count = 50


@when(u'I run the command with the option "--count 50"')
def step_run_count(context):
    """Esegue il comando con il flag --count."""
    schema_content = {
        "type": "object",
        "properties": {"dummy_id": {"type": "integer"}}
    }
    schema_path = create_temp_schema("temp_count.json", schema_content)

    cmd = f"mockgen generate --schema {schema_path} --count 50"
    context.process_result = run_cli_command(cmd)

    clean_files([schema_path])


@then(u'the output is a JSON array containing exactly 50 objects')
def step_verify_count(context):
    """Verifica che il numero di oggetti nell'array di output corrisponda."""
    assert context.process_result.returncode == 0

    output = context.process_result.stdout
    expected = getattr(context, 'expected_count', 50)

    try:
        data = json.loads(output)
        assert isinstance(data, list), "L'output dovrebbe essere una lista."
        assert len(data) == expected, f"Attesi {expected} elementi, ottenuti {len(data)}."
    except json.JSONDecodeError:
        assert False, f"Output non valido: {output}"


# =============================================================================
# SCENARIO 4: Verbose/Debug
# =============================================================================
@given(u'I want to analyze the internal behavior of the tool')
def step_set_debug_intent(context):
    """Imposta l'intenzione di debug."""
    context.debug_mode_expected = True


@when(u'I run the command with the "--verbose" flag')
def step_run_verbose(context):
    """Esegue il comando con --verbose."""
    schema_path = create_temp_schema("temp_debug.json", {"type": "object"})

    cmd = f"mockgen generate --schema {schema_path} --verbose"
    context.process_result = run_cli_command(cmd)

    clean_files([schema_path])


@then(u'the console shows details of the request sent to the LLM and response times')
def step_check_logs(context):
    """Analizza stdout e stderr alla ricerca di log di debug."""
    # 1. Uniamo stdout e stderr per cercare ovunque
    full_log = context.process_result.stdout + context.process_result.stderr

    # 2. Definiamo cosa ci aspettiamo di trovare
    # Se il tuo codice usa logging.debug(), cerchiamo "DEBUG"
    keywords = ["DEBUG", "INFO", "Request", "Response time"]

    # 3. Controlliamo se almeno una parola chiave è presente
    found = any(k in full_log for k in keywords)

    # 4. Se non trova nulla, il test fallisce e ci mostra cosa ha stampato (per debug)
    assert found, f"Nessun log di debug trovato!\nOutput ricevuto:\n{full_log}"


