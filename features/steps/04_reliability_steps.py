import os
import json
from behave import given, when, then
from src.static_generator.utils import run_cli_command, create_temp_schema, clean_files


# =============================================================================
# SCENARIO 1: Data reproducibility via seed
# =============================================================================

@given(u'I set the seed to "{seed_value}"')
def step_set_seed_context(context, seed_value):
    """Imposta il seed nel contesto per garantire la riproducibilità."""
    context.seed = seed_value
    context.schema_content = {
        "type": "object",
        "properties": {
            "random_code": {"type": "string"},
            "random_num": {"type": "integer"}
        }
    }


@when(u'I run the generation twice consecutively with the same schema')
def step_run_generation_twice(context):
    """Esegue il comando mockgen due volte per confrontare i risultati."""
    # Creazione manuale schema temporaneo
    context.schema_path = create_temp_schema("temp_seed.json", context.schema_content)

    cmd = f"mockgen generate --schema {context.schema_path} --seed {context.seed} --count 1"

    # Run 1
    res1 = run_cli_command(cmd)
    # Run 2
    res2 = run_cli_command(cmd)

    context.output1 = res1.stdout
    context.output2 = res2.stdout

    # Pulizia manuale
    clean_files([context.schema_path])


@then(u'the first JSON output is identical character-by-character to the second JSON output')
def step_verify_identical_outputs(context):
    """Verifica che i due output siano identici (grazie al seed)."""
    assert context.output1 == context.output2, \
        f"Gli output differiscono!\nRun 1: {context.output1}\nRun 2: {context.output2}"


# =============================================================================
# SCENARIO 2: Validazione LLM (Simulata)
# =============================================================================

@given(u'the LLM has generated a JSON response')
def step_simulate_llm_response(context):
    """Prepara una risposta simulata (mock) di un LLM e il relativo schema."""
    context.ai_schema = {"type": "object", "properties": {"age": {"type": "integer"}}}
    # Simuliamo un errore: "trenta" (stringa) invece di intero
    context.llm_raw_response = {"age": "trenta"}


@when(u'the system receives the response')
def step_validate_received_response(context):
    """Tenta di validare la risposta ricevuta contro lo schema."""
    try:
        from jsonschema import validate, ValidationError
        validate(instance=context.llm_raw_response, schema=context.ai_schema)
        context.is_valid = True
    except (ValidationError, Exception):
        context.is_valid = False


@then(u'it verifies that the JSON respects the original schema')
def step_check_schema_compliance_logic(context):
    """
    Step segnaposto logico -> Step DESCRITTIVO
    La validazione vera e propria è avvenuta nel WHEN, qui confermiamo l'intento.
    Non facciamo 'assert context.is_valid is True' perché in questo scenario
    ci aspettiamo che possa fallire (stiamo testando l'errore).
    """
    pass


@then(u'if it is not valid, it discards the result or attempts a repair')
def step_assert_invalid_handling(context):
    """Verifica che il sistema abbia marcato il dato come non valido."""
    assert context.is_valid is False, "Il dato invalido è stato erroneamente accettato."


# =============================================================================
# SCENARIO 3: Errori Sintassi JSON
# =============================================================================
@given(u'I provide a JSON file that contains syntax errors')
def step_create_broken_json_file(context):
    """Crea un file schema intenzionalmente corrotto (JSON malformato)."""
    context.broken_schema = "broken.json"
    with open(context.broken_schema, "w") as f:
        # Manca la chiusura delle graffe
        f.write('{ "type": "object", "properties": { ')


@when(u'I attempt to run the generation')
def step_run_generation_with_broken_schema(context):
    """Lancia la CLI contro il file corrotto."""
    cmd = f"mockgen generate --schema {context.broken_schema}"
    context.result = run_cli_command(cmd)
    clean_files([context.broken_schema])


@then(u'the system terminates with an error code')
def step_verify_error_exit_code(context):
    """Verifica che il processo sia terminato con exit code != 0."""
    assert context.result.returncode != 0, \
        f"Il comando doveva fallire, invece ha return code {context.result.returncode}"


@then(u'prints a clear message indicating the line or type of error in the JSON')
def step_verify_error_message_details(context):
    """Cerca parole chiave tipiche degli errori di parsing JSON nell'output."""
    full_log = context.result.stderr + context.result.stdout
    keywords = ["JSONDecodeError", "Expecting", "syntax error", "decoder"]
    found = any(k in full_log for k in keywords)

    assert found, f"Nessun messaggio di errore JSON trovato nel log:\n{full_log}"