import io
import json
import pytest
from unittest.mock import MagicMock
# Assicurati che l'import sia corretto in base alla tua struttura
from src.static_generator.exporter import DataExporter


# Dati di prova comuni (Fixture leggera)
@pytest.fixture
def sample_data():
    return [
        {"id": 1, "name": "Alice", "active": True},
        {"id": 2, "name": "Bob", "active": False}
    ]


# =============================================================================
# SUITE: DataExporter
# STRATEGY: WECT (Formats), BVA (Data Content), Robustness
# =============================================================================

# TC-E01: WECT Valid (Formato JSON)
# Obiettivo: Verificare che l'output sia un JSON valido e ben formattato.
def test_export_json(sample_data):
    # Setup: Usiamo StringIO come "finto file" in memoria
    output = io.StringIO()

    # Action
    DataExporter.export(sample_data, "json", output)

    # Assert
    content = output.getvalue()
    # Verifichiamo che sia parsabile
    loaded = json.loads(content)
    assert len(loaded) == 2
    assert loaded[0]["name"] == "Alice"


# TC-E02: WECT Valid (Formato CSV)
# Obiettivo: Verificare presenza header e righe corrette.
def test_export_csv(sample_data):
    output = io.StringIO()

    DataExporter.export(sample_data, "csv", output)

    content = output.getvalue()
    lines = content.strip().split("\n")

    # Verifica Header
    assert "id,name,active" in lines[0]
    # Verifica Dati
    assert "1,Alice,True" in lines[1]
    assert "2,Bob,False" in lines[2]


# TC-E03: WECT Valid (Formato NDJSON)
# Obiettivo: Verificare formato Newline Delimited JSON (una riga = un oggetto).
def test_export_ndjson(sample_data):
    output = io.StringIO()

    DataExporter.export(sample_data, "ndjson", output)

    content = output.getvalue().strip()
    lines = content.split("\n")

    assert len(lines) == 2
    # Ogni riga deve essere un JSON autonomo
    obj1 = json.loads(lines[0])
    assert obj1["name"] == "Alice"


# TC-E04: WECT Valid (Formato SQL Base)
# Obiettivo: Verificare la sintassi INSERT INTO.
def test_export_sql_basic(sample_data):
    output = io.StringIO()

    DataExporter.export(sample_data, "sql", output, table_name="users")

    content = output.getvalue()
    # Verifica sintassi
    assert "INSERT INTO users (id, name, active)" in content
    assert "VALUES (1, 'Alice', TRUE);" in content


# TC-E05: BVA / WECT (SQL Complex Types & Escaping)
# Obiettivo: Testare i casi limite della conversione valori SQL (Null, Apici, Bool).
# Questo è CRITICO per evitare SQL Injection o query rotte.
def test_export_sql_complex_types():
    # Dati "sporchi" per testare l'helper _format_sql_value
    tricky_data = [
        {
            "text": "O'Reilly",  # Caso limite: Apice singolo (deve diventare '')
            "nothing": None,  # Caso limite: None (deve diventare NULL)
            "flag": True,  # Caso bool
            "num": 10.5  # Caso float
        }
    ]
    output = io.StringIO()

    DataExporter.export(tricky_data, "sql", output, table_name="test")

    content = output.getvalue()

    # Assert puntuali sui valori convertiti
    assert "'O''Reilly'" in content  # Verifica escaping
    assert "NULL" in content  # Verifica None
    assert "TRUE" in content  # Verifica Bool
    assert "10.5" in content  # Verifica Float


# TC-E06: BVA Minimo (Lista Vuota)
# Obiettivo: Se la lista dati è vuota, non deve scrivere nulla ne crashare.
def test_export_empty_list():
    output = io.StringIO()
    DataExporter.export([], "json", output)

    # Assert: Il buffer deve essere vuoto
    assert output.getvalue() == ""


# TC-E07: WECT Invalid (Formato Sconosciuto)
# Obiettivo: Verificare che venga sollevato errore per formati non supportati.
def test_export_invalid_format(sample_data):
    output = io.StringIO()
    with pytest.raises(ValueError, match="Formato non supportato"):
        DataExporter.export(sample_data, "xml", output)


# TC-E08: Robustness (Stream Error)
# Obiettivo: Verificare che eccezioni durante la scrittura vengano wrappate in RuntimeError.
def test_export_stream_error(sample_data):
    # Mockiamo lo stream per lanciare un'eccezione quando si chiama write()
    bad_stream = MagicMock()
    bad_stream.write.side_effect = IOError("Disk full")

    with pytest.raises(RuntimeError, match="Errore durante l'export"):
        DataExporter.export(sample_data, "json", bad_stream)


# TC-E09: WECT Valid (SQL Complex/JSON Value)
# Obiettivo: Verificare che liste/dict vengano serializzati come stringhe JSON per SQL.
def test_export_sql_json_column():
    data = [{
        "id": 1,
        "metadata": {"color": "red", "tags": [1, 2]}  # Valore complesso
    }]
    output = io.StringIO()

    DataExporter.export(data, "sql", output)

    content = output.getvalue()
    # Ci aspettiamo che il dizionario sia diventato una stringa: '{"color": "red"...}'
    assert "'{\"color\": \"red\", \"tags\": [1, 2]}'" in content


# TC-E10: Robustness (CSV Inconsistent Data)
# Obiettivo: Verificare comportamento se la seconda riga ha chiavi diverse dalla prima.
# Analisi: DictWriter usa i fieldnames della prima riga. Se trova chiavi extra, solleva ValueError.
def test_export_csv_inconsistent_schema():
    data = [
        {"id": 1, "name": "Alice"},  # Definisce lo schema
        {"id": 2, "name": "Bob", "age": 30}  # Ha un campo extra "age"
    ]
    output = io.StringIO()

    # Ci aspettiamo che il metodo wrappi l'errore in RuntimeError o che DictWriter sollevi ValueError
    # Dato che il tuo codice cattura Exception e rilancia RuntimeError:
    with pytest.raises(RuntimeError, match="Errore durante l'export in csv"):
        DataExporter.export(data, "csv", output)


# TC-E11: WECT Valid (SQL Default Table Name)
# Obiettivo: Verificare che se non passo table_name, usi il default 'my_table'.
def test_export_sql_default_tablename(sample_data):
    output = io.StringIO()

    # NON passiamo table_name nei kwargs
    DataExporter.export(sample_data, "sql", output)

    content = output.getvalue()
    assert "INSERT INTO my_table" in content


# TC-E12: WECT Valid (Unicode & Emoji)
# Obiettivo: Verificare che caratteri non-ASCII (Emoji, Cinese, Accenti) non vengano corrotti.
def test_export_unicode_support():
    data = [{"id": 1, "msg": "Ciao àèìòù 🚀 hǎo"}]
    output = io.StringIO()

    # Testiamo JSON (che ha il flag ensure_ascii=False)
    DataExporter.export(data, "json", output)
    content = output.getvalue()

    # Assert: Le emoji e caratteri speciali devono essere leggibili, non \uXXXX
    assert "🚀" in content
    assert "hǎo" in content


# TC-E13: BVA Internal (CSV Escaping)
# Obiettivo: Verificare che virgole e newline all'interno dei valori vengano gestiti (quote automatico).
def test_export_csv_escaping():
    data = [{"id": 1, "note": "Riga1,\nRiga2"}]  # Virgola E Newline nel valore
    output = io.StringIO()

    DataExporter.export(data, "csv", output)
    content = output.getvalue()

    # Assert: Il valore deve essere racchiuso tra virgolette nel formato CSV standard
    # Output atteso: 1,"Riga1,\nRiga2"
    assert '"Riga1,\nRiga2"' in content


# TC-E14: BVA Complex (SQL Nasty String)
# Obiettivo: Combinazione di caratteri pericolosi per SQL.
def test_export_sql_nasty_string():
    # Una stringa con: apice, doppio apice, backslash, newline
    nasty_val = r"O'Reilly said: \"Hello\" \n Newline"
    data = [{"val": nasty_val}]
    output = io.StringIO()

    DataExporter.export(data, "sql", output)
    content = output.getvalue()

    # Verifica che l'unico escaping fatto sia sull'apice singolo (O''Reilly)
    # Il resto viene passato raw (che è corretto per lo standard SQL ANSI,
    # anche se DB specifici potrebbero richiedere altro)
    assert "O''Reilly" in content
    assert 'said: \\"Hello\\"' in content  # Verifica che il resto sia intatto


# TC-E15: Robustness (Circular Reference)
# Obiettivo: Verificare che errori di serializzazione (non I/O) vengano catturati.
def test_export_json_circular_reference():
    # Creiamo un dato ricorsivo che rompe json.dump
    data = {"key": "value"}
    data["loop"] = data
    output = io.StringIO()

    with pytest.raises(RuntimeError, match="Errore durante l'export in json"):
        DataExporter.export([data], "json", output)


# TC-E16: WECT Valid (CSV Missing Keys)
# Obiettivo: Verificare comportamento se mancano chiavi nelle righe successive alla prima.
def test_export_csv_missing_keys():
    data = [
        {"a": 1, "b": 2},  # Definisce header: a,b
        {"a": 3}  # Manca 'b' -> Dovrebbe scrivere "3," (o "3,"" se vuoto)
    ]
    output = io.StringIO()

    DataExporter.export(data, "csv", output)
    content = output.getvalue().strip().split('\n')

    # Header: a,b
    # Riga 1: 1,2
    # Riga 2: 3, (la virgola finale indica il campo vuoto)
    assert "3," in content[2] or "3,""" in content[2]


# TC-E17: Security Awareness (SQL Injection in Keys)
# Obiettivo: Documentare che le chiavi del dizionario vengono inserite RAW nella query.
# Questo test serve a dire: "Attenzione, sanificare l'input a monte!"
def test_export_sql_unsafe_keys():
    # Una chiave che contiene un commento SQL
    unsafe_key = "id) VALUES (1); DROP TABLE users; --"
    data = [{unsafe_key: 1}]
    output = io.StringIO()

    DataExporter.export(data, "sql", output)
    content = output.getvalue()

    # Verifichiamo che la chiave malevola sia finita nella query
    assert "DROP TABLE users" in content


# TC-E18: WECT Invalid (JSON Type Incompatibility)
# Obiettivo: Verificare comportamento con tipi dati non supportati da JSON (es. set).
# Analisi: Python set -> JSON Error -> RuntimeError.
def test_export_json_invalid_type():
    # Il set {1, 2} è valido in Python ma non esiste in standard JSON
    bad_data = [{"id": 1, "tags": {1, 2, 3}}]
    output = io.StringIO()

    with pytest.raises(RuntimeError, match="Errore durante l'export in json"):
        DataExporter.export(bad_data, "json", output)


# TC-E19: WECT Invalid (SQL Syntax Generation)
# Obiettivo: Dimostrare che chiavi con spazi generano SQL sintatticamente invalido (ma non crashano Python).
# Questo è un "Known Issue" o "Limitazione Accettata".
def test_export_sql_invalid_column_syntax():
    # Chiave con spazio: non valida in SQL standard senza doppi apici
    data = [{"nome utente": "Mario"}]
    output = io.StringIO()

    DataExporter.export(data, "sql", output)
    content = output.getvalue()

    # Verifichiamo che il generatore scriva ciecamente la colonna errata
    # Output atteso: INSERT INTO ... (nome utente) ...
    assert "(nome utente)" in content
    # Nota: Questo test serve a dire "Attenzione: i nomi dei campi JSON devono essere compatibili SQL"


# TC-E20: WECT Invalid (NDJSON Partial Failure)
# Obiettivo: Verificare cosa succede se un record a metà lista fallisce la serializzazione.
def test_export_ndjson_partial_failure():
    data = [
        {"id": 1},  # Valido
        {"id": 2, "bad": {1, 2}}  # Invalido (set)
    ]
    output = io.StringIO()

    # Ci aspettiamo un errore globale
    with pytest.raises(RuntimeError):
        DataExporter.export(data, "ndjson", output)

    # MA... verifichiamo che la prima riga sia stata scritta prima del crash!
    content = output.getvalue()
    assert '{"id": 1}' in content
    assert '{"id": 2' not in content  # La seconda riga non deve esserci (o essere incompleta)


