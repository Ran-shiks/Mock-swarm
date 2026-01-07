import sys
import os
import logging
import traceback  # <--- AGGIUNTO QUESTO IMPORT

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# =============================================================================
# SETUP PATH (Necessario se lanci lo script direttamente senza installare il package)
# =============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import dei nuovi moduli modulari
from src.static_generator.cli_parser import parse_arguments
from src.static_generator.controller import run_generation_process


def main():
    try:
        # 1. Parsing
        args = parse_arguments()

        # 2. Configurazione Logging
        # Se --verbose è presente, livello DEBUG, altrimenti INFO
        log_level = logging.DEBUG if args.verbose else logging.INFO

        # Configuro il formato in modo che il test riconosca "[DEBUG]"
        logging.basicConfig(
            level=log_level,
            format='[%(levelname)s] %(message)s',
            stream=sys.stderr  # I log di solito vanno su stderr per non sporcare stdout (es. json pipe)
        )

        # Log di avvio (visibile solo se verbose)
        logging.debug(f"Avvio MockGen con argomenti: {args}")

        # 3. Esecuzione (Delegata al Controller)
        run_generation_process(args)

    except Exception as e:
        # Gestione errori fatale "Last Resort" per la CLI
        print("\n--- INIZIO DETTAGLIO ERRORE ---", file=sys.stderr)
        traceback.print_exc()  # <--- QUESTA È LA RIGA MAGICA
        print("--- FINE DETTAGLIO ERRORE ---\n", file=sys.stderr)

        print(f"Critical Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()