"""
Modulo di esempio per testare la pipeline CI.

Contiene una semplice funzione `add` che somma due numeri.
Serve unicamente per verificare che la pipeline (pytest + behave)
venga eseguita correttamente.
"""

def add(a: int, b: int) -> int:
    """Restituisce la somma di due numeri."""
    return a + b


if __name__ == "__main__":
    # Esecuzione dimostrativa
    print("Esempio:", add(2, 3))
