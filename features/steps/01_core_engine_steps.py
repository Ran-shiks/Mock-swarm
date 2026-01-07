import re
import json

from behave import given, when, then
from src.static_generator.utils import generate_data_from_schema_dict

# --- HELPER INTERNO PER GLI STEP ---
def ensure_schema_exists(context):
    """Inizializza lo schema nel context se non esiste ancora."""
    if not hasattr(context, 'schema'):
        context.schema = {"type": "object", "properties": {}}

# ==========================================================================================================
# SCENARIO 1: Generazione di un oggetto JSON valido da uno schema semplice
# ==========================================================================================================
@given(u'I have a valid schema file "user_schema.json"')
def step_init_schema(context):
    # Inizializziamo uno tipico schema base compatibile con il parser
    context.schema = {
        "type": "object",
        "properties": {
            "id": {"type": "uuid"},
            "name": {"type": "string"}
        },
        "required": ["id"]
    }

@when(u'I run the generation command using this schema')
@when(u'I generate the data')
def step_run_generation(context):
    context.result = generate_data_from_schema_dict(context.schema)
    assert context.result is not None, "Engine non ha generato alcun dato"

@then(u'the system returns a valid JSON object')
def step_verify_dict(context):
    assert isinstance(context.result, dict), "L'output non è un dizionario"

@then(u'the object keys correspond to the schema properties')
def step_verify_keys(context):
    for key in context.schema["properties"].keys():
        assert key in context.result, f"Manca la chiave {key} nel risultato"


# ===========================================================================================================
# SCENARIO 2: Rispetto dei vincoli numeri
# ============================================================================================================
@given(u'the schema defines a property "{field}" of type integer')
def step_def_int(context, field):
    #if not hasattr(context, 'schema'):
     #   context.schema = {"type": "object", "properties": {}}
    ensure_schema_exists(context)
    context.schema["properties"][field] = {"type": "integer"}
    # Salviamo il campo corrente per usi futuri nella stessa feature(es. array constraints)
    context.last_field = field

@given(u'the property "{field}" has minimum {min_val:d} and maximum {max_val:d}')
def step_def_range(context,field, min_val, max_val):
    context.schema["properties"][field]["min_value"] = min_val
    context.schema["properties"][field]["max_value"] = max_val


@then(u'the value of the field "{field}" is an integer between {min_val:d} and {max_val:d} inclusive')
def step_impl(context, field, min_val, max_val):
    val = context.result.get(field)
    assert isinstance(val, int), f"Valore {val} non è un intero"
    assert min_val <= val <= max_val, f"Valore {val} fuori range ({min_val}-{max_val})"


# =============================================================================================================
# SCENARIO 3: Correttezza formato email
# ==============================================================================================================
@given(u'the schema defines a property "{field}" with format "email"')
def step_def_email(context, field):
    #if not hasattr(context, 'schema'):
     #   context.schema = {"type": "object", "properties": {}}
    ensure_schema_exists(context)
    context.schema["properties"][field] = {"type": "string", "format": "email"}

@then(u'the value of the field "{field}" respects the standard regex for emails')
def step_verify_impl(context, field):
    val = context.result.get(field)
    assert re.match(r"[^@]+@[^@]+\.[^@]+", val), f"{val} non sembra un'email valida"


# ================================================================================================================
# SCENARIO 4: Array con vincoli di lunghezza
# ================================================================================================================
@given(u'the schema defines a property "{field}" of type array')
def step_def_array(context, field):
    #if not hasattr(context, 'schema'):
     #   context.schema = {"type": "object", "properties": {}}
    ensure_schema_exists(context)
    context.schema["properties"][field] = {"type": "array"}
    context.last_field = field

@given(u'the property has minItems set to {min_items:d}')
def step_def_array_constraints(context, min_items):
    # MAPPING: Gherkin "minItems" -> ArrayGenerator "min_items"
    # Nota: Dobbiamo definire anche item_type per evitare crash
    #field_name = "tags"  # Dedotto dallo scenario
    # context.schema["properties"][field_name]["min_items"] = min_items
    # context.schema["properties"][field_name]["item_type"] = "string"

    field_name = getattr(context, 'last_field', 'tags')
    context.schema["properties"][field_name].update({
        "min_items": min_items,
        "item_type": "string"  # Default necessario per evitare crash
    })

@then(u'the array "{field}" in the resulting JSON contains at least {min_items:d} elements')
def step_verify_array_len(context, field, min_items):
    val = context.result.get(field)
    assert isinstance(val, list), f"Il campo {val} non è una lista"
    assert len(val) >= min_items, f"Lista troppo corta: trovati {len(val)}, attesi min {min_items}"

# ===============================================================================================================
# SCENARIO 5: Oggetto innestato
# ================================================================================================================
@given(u'the schema contains an object "{field}" nested inside the main object')
def step_def_nested(context, field):
    #if not hasattr(context, 'schema'):
     #   context.schema = {"type": "object", "properties": {}}
    ensure_schema_exists(context)
        # Creazione schema con oggetto annidato
    context.schema["properties"][field] = {
        "type": "object",
        "fields": {
            "street": {"type": "string"},
            "zip": {"type": "integer"}
        }
    }

@then(u'the JSON output contains the key "{field}"')
def step_verify_key_exists(context, field):
    assert field in context.result, f"Manca la chiave {field} nel risultato"

@then(u'the value of "{field}" is an object with its own sub-properties populated')
def step_verify_nested_struct(context, field):
    val = context.result.get(field)
    assert isinstance(val, dict), f"Il campo '{field}' dovrebbe essere un dict"
    assert "street" in val, "Manca la proprietà 'street' nell'oggetto annidato"
    assert isinstance(val["street"], str), "La proprietà 'street' non è una stringa"

# =================================================================================================================
# SCENARIO 6: Enums
# ==================================================================================================================
@given(u'the schema has a field "{field}" with enum {options_str}')
def step_def_enum(context, field, options_str):
    ensure_schema_exists(context)
    # Convertiamo la stringa '["a","b"]' in lista Python
    options = json.loads(options_str)

    #if not hasattr(context, 'schema'):
     #   context.schema = {"type": "object", "properties": {}}

    # MAPPING: Gherkin "enum" -> ChoiceGenerator "type: choice" + "options"
    context.schema["properties"][field] = {
        "type": "choice",
        "options": options
    }

@then(u'the value of the field "{field}" is exclusively one of the three allowed strings')
def step_verify_enum(context, field):
    val = context.result.get(field)
    # Recuperiamo le opzioni dallo schema per verificare
    allowed = context.schema["properties"][field]["options"]
    assert val in allowed, f"Valore {val} non permesso (ammessi: {allowed})"
