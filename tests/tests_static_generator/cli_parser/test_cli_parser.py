import pytest
import sys
from unittest.mock import patch
# Assicurati che l'import punti correttamente alla tua struttura progetto
from src.static_generator.cli_parser import parse_arguments


# =============================================================================
# SUITE: CLI Argument Parser
# MODULE: cli_parser.py
# STRATEGY: WECT (Valid/Invalid Inputs), BVA (Boundaries), Robustness, Mocking
# =============================================================================

# --- SEZIONE 1: WECT VALID (Happy Paths) ---

# TC-P01: WECT Valid (Input Minimo)
# Obiettivo: Verificare che basti il parametro obbligatorio (--schema)
# e che tutti i valori di DEFAULT siano assegnati correttamente.
def test_parse_args_minimal():
    args = parse_arguments(['--schema', 'data.json'])

    assert args.schema == 'data.json'
    # Verifica Defaults
    assert args.count == 1
    assert args.seed is None
    assert args.out is None
    assert args.format == 'json'
    assert args.table_name == 'my_table'
    assert args.verbose is False


# TC-P02: WECT Valid (Override Completo)
# Obiettivo: Verificare che ogni singolo argomento sovrascriva correttamente il default.
def test_parse_args_full_override():
    input_args = [
        '--schema', 'input.json',
        '--count', '100',
        '--seed', '42',
        '--out', 'output.sql',
        '--format', 'sql',
        '--table-name', 'users',
        '--verbose'
    ]

    args = parse_arguments(input_args)

    assert args.schema == 'input.json'
    assert args.count == 100
    assert args.seed == 42
    assert args.out == 'output.sql'
    assert args.format == 'sql'
    assert args.table_name == 'users'
    assert args.verbose is True


# TC-P03: WECT Valid (Tutti i Formati Supportati)
# Obiettivo: Verificare che l'Enum 'choices' accetti tutte le opzioni permesse.
@pytest.mark.parametrize("fmt", ['json', 'csv', 'ndjson', 'sql']) # - Test Parametrizzato per tutti i formati validi
def test_parse_args_valid_formats(fmt):
    args = parse_arguments(['--schema', 's.json', '--format', fmt])
    assert args.format == fmt


# --- SEZIONE 2: WECT INVALID (Input Errati) ---

# TC-P04: WECT Invalid (Manca Parametro Required)
# Obiettivo: Verificare uscita con codice errore 2 se manca --schema.
def test_parse_args_missing_schema(capsys):
    # Argparse chiama sys.exit(2) quando mancano argomenti required
    with pytest.raises(SystemExit) as excinfo:
        parse_arguments([])  # Lista argomenti vuota

    assert excinfo.value.code == 2

    # Verifica che il messaggio di errore su stderr sia esplicativo
    captured = capsys.readouterr()
    assert "required" in captured.err
    assert "--schema" in captured.err


# TC-P05: WECT Invalid (Tipo Errato - Int vs Str)
# Obiettivo: Verificare che --count rifiuti stringhe non numeriche.
def test_parse_args_invalid_type_int(capsys):
    with pytest.raises(SystemExit):
        parse_arguments(['--schema', 's.json', '--count', 'dieci'])

    captured = capsys.readouterr()
    assert "invalid int value" in captured.err


# TC-P06: WECT Invalid (Scelta non in Enum)
# Obiettivo: Verificare che --format rifiuti valori fuori dalla whitelist.
def test_parse_args_invalid_choice_format(capsys):
    with pytest.raises(SystemExit):
        parse_arguments(['--schema', 's.json', '--format', 'xml'])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "xml" in captured.err


# TC-P07: Robustness (Flag Sconosciuto)
# Obiettivo: Verificare che il parser non ignori flag errati (protezione typo).
def test_parse_args_unknown_flag(capsys):
    with pytest.raises(SystemExit):
        parse_arguments(['--schema', 's.json', '--velocissimo'])

    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err


# --- SEZIONE 3: BVA (Boundary Value Analysis) ---

# TC-P08: BVA Boundary (Zero e Negativi - Sintassi)
# Obiettivo: Verificare che il PARSER accetti int negativi (perché type=int lo permette).
# NOTA: La validazione logica (es. count > 0) è responsabilità dell'Engine, NON del Parser.
def test_parse_args_boundary_int_values():
    # Test Zero
    args_zero = parse_arguments(['--schema', 's.json', '--count', '0'])
    assert args_zero.count == 0

    # Test Negativo (Argparse lo accetta sintatticamente)
    args_neg = parse_arguments(['--schema', 's.json', '--count', '-5'])
    assert args_neg.count == -5


# TC-P09: BVA Boundary (Stringa Vuota)
# Obiettivo: Verificare che una stringa vuota sia accettata come path valido sintatticamente.
def test_parse_args_boundary_empty_string_out():
    args = parse_arguments(['--schema', 's.json', '--out', ''])
    assert args.out == ''


# TC-P10: BVA / Robustness (Cross-Parameter logic)
# Obiettivo: Verificare che parametri specifici (table-name) siano accettati
# anche se il contesto (format json) non li userebbe. Il parser è "agnostico".
def test_parse_args_table_name_with_json():
    args = parse_arguments(['--schema', 's.json', '--format', 'json', '--table-name', 'users'])
    assert args.table_name == 'users'
    assert args.format == 'json'


# --- SEZIONE 4: SYSTEM & MOCKING TESTS ---

# TC-P11: System Integration (Sys.argv Fallback)
# Obiettivo: Verificare che se chiamo parse_arguments(None), legga sys.argv reale.
# Usiamo patch per simulare i parametri da riga di comando del sistema.
def test_parse_args_sys_argv_default():
    fake_argv = ['prog_name', '--schema', 'sys_argv.json', '--count', '5']
    with patch.object(sys, 'argv', fake_argv):
        args = parse_arguments(None)  # Argv=None fa scattare il fallback
        assert args.schema == 'sys_argv.json'
        assert args.count == 5


# TC-P12: Smoke Test (Help Message)
# Obiettivo: Verificare che --help esca con codice 0 (Successo) e mostri la descrizione.
def test_parse_args_help(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse_arguments(['--help'])

    # Help esce con 0, non con errore
    assert excinfo.value.code == 0

    captured = capsys.readouterr()
    assert "Schema-Driven Smart Mock Generator" in captured.out


# TC-P13: Robustness (Repeated Arguments - Last Wins)
# Obiettivo: Verificare che se un argomento viene ripetuto, l'ultimo valore sovrascriva i precedenti.
# Comportamento standard di argparse per store action.
def test_parse_args_repeated_arguments():
    # L'utente passa count 5 e poi count 10
    args = parse_arguments(['--schema', 's.json', '--count', '5', '--count', '10'])

    # Ci aspettiamo che vinca l'ultimo (10)
    assert args.count == 10


# TC-P14: WECT Valid (Equals Syntax)
# Obiettivo: Verificare che il parser accetti la sintassi --key=value (senza spazi).
def test_parse_args_equals_syntax():
    args = parse_arguments(['--schema=data.json', '--count=50'])

    assert args.schema == 'data.json'
    assert args.count == 50



# TC-P15: WECT Invalid (No Short Flags)
# Obiettivo: Documentare che i flag brevi (es. -s) NON sono supportati e generano errore.
def test_parse_args_no_short_flags(capsys):
    with pytest.raises(SystemExit):
        parse_arguments(['--schema', 'data.json', '-s'])  # Utente prova shortcut

    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err