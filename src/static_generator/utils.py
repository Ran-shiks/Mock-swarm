import subprocess
import sys
import os
import shlex
import json
import shutil
import tempfile


def generate_data_from_schema_dict(schema_dict):
    """
    Helper per i test del Core Engine.
    1. Prende un dizionario Python (schema).
    2. Lo scrive su un file temporaneo.
    3. Istanzia MockEngine e genera 1 record.
    4. Pulisce e restituisce il record generato.
    """
    # Importiamo MockEngine qui per evitare import circolari se utils è importato altrove
    # (Assicurati che il path di import sia corretto per il tuo progetto)
    from src.static_generator.engine import MockEngine

    fd, path = tempfile.mkstemp(suffix=".json", text=True)
    try:
        # Scrittura schema su disco
        with os.fdopen(fd, 'w') as tmp:
            json.dump(schema_dict, tmp)

        # Invocazione diretta del Core
        engine = MockEngine(path)
        results = engine.generate(n=1)

        if not results:
            return None
        return results[0]  # Ritorniamo il primo dizionario generato

    finally:
        # Pulizia sicura del file temporaneo
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

def run_cli_command(command_str):
    """Esegue il comando costruendo il percorso assoluto per main_cli.py"""
    project_root = os.path.abspath(os.getcwd())

    # Percorso verso il tuo main script
    script_path = os.path.join(project_root, "src", "static_generator", "__main_cli__.py")

    # Puliamo il comando
    #args_part = command_str.replace("mockgen ", "").strip()
    args_part = command_str.replace("mockgen", "").replace("generate", "").strip()

    # Costruiamo il comando completo
    cmd = [sys.executable, script_path] + shlex.split(args_part)

    # Impostiamo PYTHONPATH per evitare errori di import nello script lanciato
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    # Eseguiamo
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env
    )


def create_temp_schema(filename, content):
    """Crea un file JSON su disco e ritorna il percorso relativo."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)
    return filename


def clean_files(file_list):
    """Rimuove i file passati nella lista."""
    for f in file_list:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass


def prepare_output_dir(dirname):
    """Pulisce e ricrea la cartella di output."""
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname, exist_ok=True)



def load_json_file(filepath):
    """Legge un file JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)