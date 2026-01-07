import os
import json
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.static_generator.utils import (
    generate_data_from_schema_dict,
    run_cli_command,
    create_temp_schema,
    clean_files,
    prepare_output_dir,
    load_json_file
)


# =============================================================================
# SUITE: Test Utility Functions
# STRATEGY: White Box, WECT (Weak Equivalence Class), BVA (Boundary Value), Robustness
# =============================================================================


# =====================================================================================================================
# TC-U01: Happy Path (WECT Valido)
# =====================================================================================================================
# Obiettivo: Verificare che l'helper generi correttamente un record quando tutto funziona.
@patch('src.static_generator.engine.MockEngine')
def test_generate_data_happy_path(MockEngineMock, tmp_path):
    # Setup
    mock_instance = MockEngineMock.return_value
    mock_instance.generate.return_value = [{"id": 1}]

    # Action
    result = generate_data_from_schema_dict({"type": "object"})

    # Assert
    assert result == {"id": 1}
    args, _ = MockEngineMock.call_args
    assert args[0].endswith(".json")  # Verifica passaggio file


# =====================================================================================================================
# TC-U02: BVA (Risultato Vuoto)
# =====================================================================================================================
# Obiettivo: Verificare il comportamento ai limiti quando l'engine restituisce una lista vuota.
@patch('src.static_generator.engine.MockEngine')
def test_generate_data_empty_results(MockEngineMock):
    # Setup
    mock_instance = MockEngineMock.return_value
    mock_instance.generate.return_value = []  # Limite: 0 risultati

    # Action
    result = generate_data_from_schema_dict({"type": "object"})

    # Assert
    assert result is None


# =====================================================================================================================
# TC-U03: Robustness (Gestione Eccezioni e Pulizia)
# =====================================================================================================================
# Obiettivo: Verificare che il file temporaneo venga rimosso anche in caso di crash critico.
@patch('src.static_generator.engine.MockEngine')
def test_generate_data_cleanup_on_error(MockEngineMock):
    # Setup: Simula crash dell'engine
    mock_instance = MockEngineMock.return_value
    mock_instance.generate.side_effect = Exception("Critical Failure")

    with patch('os.remove') as mock_remove:
        with pytest.raises(Exception, match="Critical Failure"):
            generate_data_from_schema_dict({"type": "object"})

        # Assert: La pulizia deve avvenire comunque (blocco finally)
        assert mock_remove.called


# =====================================================================================================================
# TC-U04: White Box (Logica Interna Costruzione Comando)
# =====================================================================================================================
# Obiettivo: Verificare la corretta manipolazione delle stringhe e la pulizia degli argomenti.
@patch('subprocess.run')
def test_run_cli_command_construction(mock_subprocess):
    mock_subprocess.return_value.stdout = "OK"
    command_input = "mockgen generate --schema test.json"

    run_cli_command(command_input)

    args, _ = mock_subprocess.call_args
    cmd_list = args[0]

    # Assert: Verifica rimozione parole chiave e costruzione path
    assert sys.executable in cmd_list[0]
    assert "__main_cli__.py" in cmd_list[1]
    assert "mockgen" not in cmd_list
    assert "--schema" in cmd_list


# =====================================================================================================================
# TC-U05: WECT Valido (File Esistente)
# =====================================================================================================================
# Obiettivo: Verificare la rimozione di un file presente su disco.
def test_clean_files_exists(tmp_path):
    f = tmp_path / "test_file.txt"
    f.write_text("content")

    assert f.exists()
    clean_files([str(f)])
    assert not f.exists()


# =====================================================================================================================
# TC-U06: WECT Invalido (File Non Esistente)
# =====================================================================================================================
# Obiettivo: Verificare che il sistema non crashi se si tenta di cancellare un file fantasma.
def test_clean_files_not_exists():
    # Action: Passiamo un file che sicuramente non esiste
    path_fantasma = "/path/ghost_file_che_non_esiste.json"

    # Mockiamo os.path.exists per essere sicuri che ritorni False (il ramo 'else' implicito)
    with patch('src.static_generator.utils.os.path.exists', return_value=False):
        clean_files([path_fantasma])


# =====================================================================================================================
# TC-U07: Robustness (Errore di Sistema/Permessi)
# =====================================================================================================================
# Obiettivo: Verificare che OSError venga catturato silenziosamente.
@patch('os.remove')
def test_clean_files_oserror(mock_remove, tmp_path):
    f = tmp_path / "dummy.txt"
    f.write_text("x")
    # Setup: Simula errore di permessi
    mock_remove.side_effect = OSError("Access denied")

    clean_files([str(f)])

    assert mock_remove.called  # Verifica che il tentativo sia stato fatto


# =====================================================================================================================
# TC-U08: WECT Valido (Output Directory)
# =====================================================================================================================
# Obiettivo: Verificare che la cartella venga ripulita (cancellata e ricreata).
def test_prepare_output_dir_recreates(tmp_path):
    d = tmp_path / "out_dir"
    d.mkdir()
    (d / "old_file.txt").write_text("vecchio")

    prepare_output_dir(str(d))

    assert d.exists()
    assert not (d / "old_file.txt").exists()


# =====================================================================================================================
# TC-U09: WECT Valido (Lettura JSON)
# =====================================================================================================================
# Obiettivo: Verificare il corretto caricamento di un file JSON valido.
def test_load_json_file_valid(tmp_path):
    f = tmp_path / "data.json"
    content = {"key": "value"}
    with open(f, "w") as fp:
        json.dump(content, fp)

    loaded = load_json_file(str(f))
    assert loaded == content


# =====================================================================================================================
# TC-U10: WECT Valido (Creazione Schema Temp)
# =====================================================================================================================
# Obiettivo: Verificare la creazione fisica del file su disco e il ritorno del path corretto.
def test_create_temp_schema(tmp_path):
    dest_file = tmp_path / "schema_test.json"
    content = {"foo": "bar"}

    returned_path = create_temp_schema(str(dest_file), content)

    assert dest_file.exists()
    with open(dest_file, 'r') as f:
        assert json.load(f) == content
    assert returned_path == str(dest_file)


# =====================================================================================================================
# TC-U11: BVA Minimo (Lista Input Vuota)
# =====================================================================================================================
# Obiettivo: Verificare clean_files con input al limite minimo (lista vuota).
# Analisi BVA: Input len=0 -> Nessuna azione, nessun crash.
def test_clean_files_boundary_empty_list():
    try:
        clean_files([])
    except Exception as e:
        pytest.fail(f"Crash su lista vuota (BVA failure): {e}")


# =====================================================================================================================
# TC-U12: BVA Massimo (Lista Input Numerosa)
# =====================================================================================================================
# Obiettivo: Verificare che la funzione gestisca un numero elevato di elementi senza errori logici.
# Analisi BVA: Input len=1000 -> Gestione corretta, performance accettabile.
@patch('os.path.exists') # <--- 1. Mockiamo il controllo di esistenza
@patch('os.remove')      # <--- 2. Mockiamo la cancellazione
def test_clean_files_boundary_large_list(mock_remove, tmp_path):
    # Generiamo una lista "grande" ma gestibile in memoria per un unit test veloce
    large_n = 1000

    # Creiamo una lista di path fittizi (non serve creare i file fisici se mockiamo os.remove)
    # Nota: Mockare os.remove è fondamentale qui, altrimenti il test sarebbe lentissimo (I/O disco)
    fake_files = [f"/tmp/fake_file_{i}.txt" for i in range(large_n)]

    # Esecuzione
    clean_files(fake_files)

    # Assert: Verifichiamo che os.remove sia stato chiamato esattamente 1000 volte
    assert mock_remove.call_count == large_n

# =====================================================================================================================
# TC-U13: BVA Minimo (Comando Vuoto)
# =====================================================================================================================
# Obiettivo: Verificare che run_cli_command non crashi se riceve una stringa vuota.
# Analisi BVA: Lunghezza stringa = 0.
@patch('subprocess.run')
def test_run_cli_boundary_empty_string(mock_subprocess):
    # Action
    run_cli_command("")

    # Assert
    args, _ = mock_subprocess.call_args
    cmd_list = args[0]

    # Verifica: Deve comunque chiamare python e lo script main, anche senza argomenti extra
    assert sys.executable in cmd_list[0]
    assert "__main_cli__.py" in cmd_list[1]
    # La parte degli argomenti deve essere vuota (o solo lo script)
    assert len(cmd_list) == 2


# =====================================================================================================================
# TC-U14: BVA Minimo (File Vuoto - 0 Byte)
# =====================================================================================================================
# Obiettivo: Verificare comportamento standard su file vuoto.
# Analisi BVA: Dimensione file = 0.
def test_load_json_boundary_empty_file(tmp_path):
    f = tmp_path / "empty.json"
    f.touch()  # Crea file esistente ma con 0 byte

    # Ci aspettiamo che json.load sollevi JSONDecodeError.
    # Se il tuo utils avesse un try/except, dovremmo assertare None o {},
    # ma visto che è raw, dobbiamo aspettarci l'errore.
    with pytest.raises(json.JSONDecodeError):
        load_json_file(str(f))


# =====================================================================================================================
# TC-U15: BVA Minimo (Schema Vuoto)
# =====================================================================================================================
# Obiettivo: Verificare che si possa scrivere e rileggere un JSON vuoto.
# Analisi BVA: Dict len = 0.
def test_create_temp_schema_boundary_empty_dict(tmp_path):
    dest = tmp_path / "empty_schema.json"
    empty_content = {}

    create_temp_schema(str(dest), empty_content)

    # Deve esistere e contenere {}
    loaded = load_json_file(str(dest))
    assert loaded == {}

# =====================================================================================================================
# TC-U16: Robustness (JSON Malformato)
# =====================================================================================================================
# Obiettivo: Verificare comportamento con file contentente errori di sintassi JSON.
# Analisi: Input = "{ key: " (JSON rotto) -> Deve sollevare JSONDecodeError.
def test_load_json_malformed(tmp_path):
    f = tmp_path / "broken.json"
    f.write_text('{ "chiave_senza_chiusura": 1', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_json_file(str(f))

# =====================================================================================================================
# TC-U17: BVA Invalido (Input None)
# =====================================================================================================================
# Obiettivo: Verificare comportamento se viene passato None invece di una lista.
# Analisi: Input None -> TypeError (perché None non è iterabile).
def test_clean_files_input_none():
    # Poiché la funzione clean_files NON ha un controllo "if list is None",
    # ci aspettiamo che Python sollevi TypeError.
    with pytest.raises(TypeError):
        clean_files(None)

# =====================================================================================================================
# TC-U18: White Box (Cattura Stderr)
# =====================================================================================================================
# Obiettivo: Verificare che se il sottoprocesso fallisce, l'output di errore venga catturato.
@patch('subprocess.run')
def test_run_cli_capture_stderr(mock_subprocess):
    # Simuliamo un processo che fallisce (returncode=1) e scrive in stderr
    mock_subprocess.return_value.returncode = 1
    mock_subprocess.return_value.stderr = "Errore: Parametro mancante"
    mock_subprocess.return_value.stdout = ""

    result = run_cli_command("mockgen invalid")

    assert result.returncode == 1
    assert "Errore" in result.stderr


# =====================================================================================================================
# TC-U19: White Box (Cleanup Error in generate_data) -> COPRE IL FINALLY + EXCEPT
# =====================================================================================================================
# Obiettivo: Coprire il blocco 'except OSError: pass' dentro generate_data_from_schema_dict.
# Simuliamo che, durante la pulizia finale, la rimozione del file fallisca.
def test_generate_data_cleanup_handles_oserror():
    """
    Testa che se la rimozione del file temporaneo fallisce (OSError),
    la funzione lo ignori silenziosamente (pass) senza crashare.
    """
    # 1. Mockiamo MockEngine per evitare che la logica principale faccia cose reali
    with patch('src.static_generator.engine.MockEngine'):

        # 2. Diciamo al sistema: "Sì, il file temporaneo esiste ancora" (entra nell'IF del finally)
        # Importante: patchiamo os.path.exists dentro 'src.static_generator.utils'
        with patch('src.static_generator.utils.os.path.exists', return_value=True):

            # 3. Diciamo al sistema: "Quando provi a cancellarlo, BOOM! Errore!" (entra nell'EXCEPT)
            # Importante: patchiamo os.remove dentro 'src.static_generator.utils'
            with patch('src.static_generator.utils.os.remove', side_effect=OSError("File bloccato")):

                try:
                    # Action: Chiamiamo la funzione
                    result = generate_data_from_schema_dict({"type": "test"})

                    # Se arriviamo qui senza errori, il 'pass' ha funzionato!
                except OSError:
                    pytest.fail("La funzione non ha gestito l'OSError nel blocco finally!")