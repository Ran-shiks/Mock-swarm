import sys
import os
import logging
from .engine import MockEngine
from .exporter import DataExporter

# Otteniamo il logger configurato nel main
logger = logging.getLogger(__name__)


def run_generation_process(args):
    """
    Orchestra il flusso di generazione ed esportazione.
    """
    logger.debug("Inizio fase di orchestrazione...")

    # 1. Istanziazione Engine e Generazione
    logger.info(f"Caricamento schema da: {args.schema}")

    try:
        engine = MockEngine(schema_path=args.schema, seed=args.seed)
        logger.debug(f"Engine inizializzato. Seed: {args.seed}")

        logger.info(f"Generazione di {args.count} record...")
        data = engine.generate(n=args.count)
        logger.debug(f"Generazione completata. {len(data)} record creati in memoria.")

    except Exception as e:
        logger.error(f"Errore durante la generazione: {e}")
        raise e

    # 2. Gestione Stream di Output
    output_stream = sys.stdout
    file_handle = None

    if args.out:
        # FIX: Verifica se c'è una cartella padre prima di provare a crearla
        output_dir = os.path.dirname(args.out)
        if output_dir:  # Se args.out è "file.json", output_dir è "", quindi salta l'IF e non crasha
            os.makedirs(output_dir, exist_ok=True)

        logger.debug(f"Apertura file di output: {args.out}")
      #  os.makedirs(os.path.dirname(args.out), exist_ok=True)
        file_handle = open(args.out, "w", encoding='utf-8', newline='')
        output_stream = file_handle
    else:
        logger.debug("Output diretto su STDOUT")

    # 3. Esportazione
    try:
        logger.debug(f"Esportazione dati in formato: {args.format}")
        DataExporter.export(
            data=data,
            format_type=args.format,
            output_stream=output_stream,
            table_name=args.table_name
        )
        logger.info("Esportazione completata con successo.")
    except Exception as e:
        logger.error(f"Errore durante l'export: {e}")
        raise e
    finally:
        if file_handle:
            file_handle.close()
            logger.debug("File di output chiuso.")