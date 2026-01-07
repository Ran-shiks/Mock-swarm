import pytest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
from src.static_generator.controller import run_generation_process


# =============================================================================
# SUITE: Controller Orchestration
# MODULE: controller.py
# STRATEGY: Interaction Testing, WECT & Robustness (Mocking dependencies)
# =============================================================================

# ----------------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------------

@pytest.fixture
def mock_args():
    """
    Crea un oggetto mock che simula gli argomenti passati da argparse.
    Stato iniziale: Output su STDOUT (args.out = None).
    """
    args = MagicMock()
    args.schema = "dummy_schema.json"
    args.seed = 42
    args.count = 10
    args.format = "json"
    args.table_name = "test_table"
    args.out = None
    return args


# ----------------------------------------------------------------------------------
# Test Cases
# ----------------------------------------------------------------------------------

# TC-001: Interaction Testing (WECT - Classe Valida: Stream Output)
def test_controller_stdout_happy_path(mock_args):
    """
    Obiettivo: Verificare il flusso 'Happy Path' quando l'utente vuole l'output a video (stdout).
    Verifica che il Controller orchestrino Engine ed Exporter senza toccare il disco.
    """
    # SETUP: Mockiamo le dipendenze per isolare il controller
    with patch("src.static_generator.controller.MockEngine") as MockEngineCls, \
            patch("src.static_generator.controller.DataExporter") as MockExporter:
        # Simuliamo dati generati dall'Engine
        mock_instance = MockEngineCls.return_value
        fake_data = [{"id": 1, "val": "test"}]
        mock_instance.generate.return_value = fake_data

        # ACTION: Eseguiamo il controller
        run_generation_process(mock_args)

        # ASSERT (Verifiche di Interazione):
        # 1. Verifica inizializzazione Engine
        MockEngineCls.assert_called_once_with(schema_path="dummy_schema.json", seed=42)
        # 2. Verifica chiamata generazione
        mock_instance.generate.assert_called_once_with(n=10)
        # 3. Verifica esportazione su sys.stdout
        MockExporter.export.assert_called_once_with(
            data=fake_data,
            format_type="json",
            output_stream=sys.stdout,
            table_name="test_table"
        )


# TC-002: Interaction Testing (WECT - Classe Valida: File Output)
def test_controller_file_output_happy_path(mock_args):
    """
    Obiettivo: Verificare il flusso 'Happy Path' con output su FILE.
    Verifica la corretta gestione delle risorse (apertura, creazione cartelle, chiusura).
    """
    # SETUP: Impostiamo un percorso file di output
    mock_args.out = "output/subdir/data.json"

    with patch("src.static_generator.controller.MockEngine") as MockEngineCls, \
            patch("src.static_generator.controller.DataExporter") as MockExporter, \
            patch("builtins.open", mock_open()) as mocked_file, \
            patch("os.makedirs") as mock_makedirs:
        mock_instance = MockEngineCls.return_value
        mock_instance.generate.return_value = [{"id": 1}]

        # ACTION
        run_generation_process(mock_args)

        # ASSERT (Verifiche I/O):
        # 1. Verifica creazione directory
        mock_makedirs.assert_called_once_with(os.path.dirname("output/subdir/data.json"), exist_ok=True)
        # 2. Verifica apertura file in modalità scrittura ('w')
        mocked_file.assert_called_once_with("output/subdir/data.json", "w", encoding='utf-8', newline='')

        # Recuperiamo l'handle del file finto
        file_handle = mocked_file()

        # 3. Verifica che l'Exporter abbia ricevuto il file handle
        MockExporter.export.assert_called_once_with(
            data=[{"id": 1}],
            format_type="json",
            output_stream=file_handle,
            table_name="test_table"
        )

        # 4. Verifica che il file sia stato CHIUSO
        file_handle.close.assert_called_once()


# TC-003: Robustness Testing (Error Handling - Engine Failure)
def test_controller_engine_error_propagation(mock_args):
    """
    Obiettivo: Verificare che se l'Engine fallisce (es. schema invalido),
    l'eccezione venga propagata e il processo si interrompa prima dell'export.
    """
    # SETUP
    with patch("src.static_generator.controller.MockEngine") as MockEngineCls, \
            patch("src.static_generator.controller.DataExporter") as MockExporter:
        # Simuliamo un crash dell'Engine
        MockEngineCls.side_effect = ValueError("Schema JSON corrotto")

        # ACTION & ASSERT
        with pytest.raises(ValueError, match="Schema JSON corrotto"):
            run_generation_process(mock_args)

        # Verifica che NON si sia tentato di esportare nulla
        MockExporter.export.assert_not_called()


# TC-004: Robustness Testing (Resource Management - Export Failure)
def test_controller_export_error_cleanup(mock_args):
    """
    Obiettivo: Verificare che il file venga chiuso correttamente (nel blocco finally)
    anche se si verifica un errore durante l'esportazione (es. disco pieno).
    """
    # SETUP
    mock_args.out = "output/data.json"

    with patch("src.static_generator.controller.MockEngine"), \
            patch("src.static_generator.controller.DataExporter") as MockExporter, \
            patch("builtins.open", mock_open()) as mocked_file, \
            patch("os.makedirs"):
        # Simuliamo un errore critico durante la scrittura (Export)
        MockExporter.export.side_effect = RuntimeError("Disk full")

        # ACTION & ASSERT
        with pytest.raises(RuntimeError, match="Disk full"):
            run_generation_process(mock_args)

        # VERIFICA CRUCIALE: Il file deve essere chiuso nonostante l'errore
        mocked_file().close.assert_called_once()