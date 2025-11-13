"""
Test unitario di esempio per la pipeline CI.

Usa pytest per verificare il corretto funzionamento della funzione add.
"""

from src.test_pipeline import add

def test_addition():
    """Verifica che la funzione add sommi correttamente due numeri."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
