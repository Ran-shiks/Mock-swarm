import pytest
import sys
import logging
from unittest.mock import patch, MagicMock
# Assicurati che l'import punti correttamente
from src.static_generator.__main_cli__ import main


# =============================================================================
# SUITE: Main CLI Orchestrator
# MODULE: main_cli.py
# STRATEGY: Mocking, Flow Verification, BVA Integration, WECT Invalid
# =============================================================================

# TC-M01: WECT Valid (Happy Path Execution)
@patch('src.static_generator.__main_cli__.parse_arguments')
@patch('src.static_generator.__main_cli__.run_generation_process')
def test_main_execution_flow(mock_run, mock_parse):
    # SETUP: Argomenti validi standard
    mock_args = MagicMock()
    mock_args.verbose = False
    mock_parse.return_value = mock_args

    # EXEC
    main()

    # ASSERT
    mock_parse.assert_called_once()
    mock_run.assert_called_once_with(mock_args)


# TC-M02: WECT Valid (Verbose Logging)
@patch('src.static_generator.__main_cli__.parse_arguments')
@patch('src.static_generator.__main_cli__.run_generation_process')
@patch('src.static_generator.__main_cli__.logging')
def test_main_verbose_logging(mock_logging, mock_run, mock_parse):
    # SETUP: Verbose = True
    mock_args = MagicMock()
    mock_args.verbose = True
    mock_parse.return_value = mock_args

    # EXEC
    main()

    # ASSERT: Verifica livello DEBUG
    mock_logging.basicConfig.assert_called_with(
        level=mock_logging.DEBUG,
        format='[%(levelname)s] %(message)s',
        stream=sys.stderr
    )
    mock_logging.debug.assert_called()


# TC-M03: Robustness (Unhandled Exception Catching)
@patch('src.static_generator.__main_cli__.parse_arguments')
@patch('src.static_generator.__main_cli__.run_generation_process')
def test_main_handle_critical_error(mock_run, mock_parse, capsys):
    # SETUP: Crash generico
    mock_parse.return_value = MagicMock()
    mock_run.side_effect = Exception("Database Connection Failed")

    # EXEC
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Critical Error: Database Connection Failed" in captured.err


# TC-M04: Robustness (Argparse Exit Propagation)
@patch('src.static_generator.__main_cli__.parse_arguments')
def test_main_propagates_system_exit(mock_parse):
    # SETUP: Simuliamo SystemExit (es. --help)
    mock_parse.side_effect = SystemExit(0)

    # EXEC: Non deve stampare "Critical Error", ma uscire pulito
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0


# TC-M05: BVA Integration (Interface Mismatch / Missing Attribute)
# Verifica cosa succede se l'oggetto args non rispetta il contratto (manca .verbose)
@patch('src.static_generator.__main_cli__.parse_arguments')
def test_main_missing_args_attribute(mock_parse, capsys):
    # SETUP: Oggetto vuoto senza attributi
    mock_parse.return_value = type('EmptyArgs', (), {})()

    # EXEC
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    # Verifica che catturi l'AttributeError interno
    assert "Critical Error" in captured.err
    assert "'EmptyArgs' object has no attribute 'verbose'" in captured.err


# TC-M06: WECT Invalid (Logging Setup Failure)
# Verifica resilienza se l'ambiente non permette il logging (es. stderr chiuso)
@patch('src.static_generator.__main_cli__.parse_arguments')
@patch('src.static_generator.__main_cli__.logging')
def test_main_logging_setup_failure(mock_logging, mock_parse, capsys):
    mock_args = MagicMock()
    mock_args.verbose = False
    mock_parse.return_value = mock_args

    # SETUP: basicConfig fallisce
    mock_logging.basicConfig.side_effect = OSError("Stream access denied")

    # EXEC
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Critical Error: Stream access denied" in captured.err


# TC-M07: Robustness (Specific Business Exception)
# Verifica che il catch-all funzioni anche per errori semantici (ValueError)
@patch('src.static_generator.__main_cli__.parse_arguments')
@patch('src.static_generator.__main_cli__.run_generation_process')
def test_main_catch_specific_exception(mock_run, mock_parse, capsys):
    mock_parse.return_value = MagicMock()
    # SETUP: Errore specifico di validazione
    mock_run.side_effect = ValueError("Invalid Schema Structure")

    # EXEC
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Critical Error: Invalid Schema Structure" in captured.err