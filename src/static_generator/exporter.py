import csv
import json
import sys


class DataExporter:

    # --- HELPER PRIVATI ---

    @staticmethod
    def _format_sql_value(value):
        """Helper per formattare i valori SQL."""
        if value is None: return "NULL"
        if isinstance(value, bool): return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)): return str(value)
        # Escape delle virgolette singole per SQL standard
        if isinstance(value, str): return f"'{value.replace("'", "''")}'"
        return f"'{json.dumps(value)}'"

    # --- IMPLEMENTAZIONI SPECIFICHE ---

    @staticmethod
    def _to_json(data, stream, **kwargs):
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    @staticmethod
    def _to_ndjson(data, stream, **kwargs):
        for item in data:
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")

    @staticmethod
    def _to_csv(data, stream, **kwargs):
        keys = data[0].keys()
        # IMPORTANTE: lineterminator='\n' risolve il bug delle righe vuote su Windows
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator='\n')
        writer.writeheader()
        writer.writerows(data)

    @staticmethod
    def _to_sql(data, stream, **kwargs):
        table_name = kwargs.get('table_name', 'my_table')
        columns = ", ".join(data[0].keys())

        # Scrive un blocco di insert.
        # Nota: Ho mantenuto la tua logica row-by-row che è sicura e chiara.
        for row in data:
            values = [DataExporter._format_sql_value(row[col]) for col in data[0].keys()]
            vals_str = ", ".join(values)
            stream.write(f"INSERT INTO {table_name} ({columns}) VALUES ({vals_str});\n")

    # --- METODO PUBBLICO PRINCIPALE ---

    @staticmethod
    def export(data: list, format_type: str, output_stream=sys.stdout, **kwargs):
        """
        Entry point unico.
        kwargs raccoglie argomenti extra come 'table_name'.
        """
        if not data:
            return

        # MAPPING (Il "Dispatcher")
        strategies = {
            'json': DataExporter._to_json,
            'ndjson': DataExporter._to_ndjson,
            'csv': DataExporter._to_csv,
            'sql': DataExporter._to_sql
        }

        exporter_func = strategies.get(format_type)

        if not exporter_func:
            raise ValueError(f"Formato non supportato: {format_type}")

        try:
            # Chiamata dinamica alla funzione giusta
            exporter_func(data, output_stream, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Errore durante l'export in {format_type}: {e}")