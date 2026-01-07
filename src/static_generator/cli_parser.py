import argparse


def parse_arguments(argv=None):
    """
    Parsa gli argomenti della riga di comando.

    :param argv: Lista di stringhe (es. ['--schema', 'file.json']).
                 Se None, usa sys.argv automaticamente.
    :return: Namespace con gli argomenti parsati.
    """
    parser = argparse.ArgumentParser(description="Schema-Driven Smart Mock Generator")

    # Input obbligatori
    # Schema
    parser.add_argument('--schema', type=str, required=True,
                        help="Path to the JSON schema file")

    # Configurazione generazione
    parser.add_argument('--count', type=int, default=1,
                        help="Number of records to generate")
    parser.add_argument('--seed', type=int, default=None,
                        help="Seed for deterministic generation")

    # Configurazione output
    parser.add_argument('--out', type=str, default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument('--format',
                        type=str, choices=['json', 'csv', 'ndjson', 'sql'],
                        default='json',
                        help="Output format")
    parser.add_argument('--table-name', type=str, default='my_table',
                        help="Target table name (only for SQL format)")

    parser.add_argument('--verbose', action='store_true',
                        help="Enable verbose logging")

    return parser.parse_args(argv)