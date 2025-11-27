from typing import List, Optional
import sys
import os

# Supporta sia import relativo (quando usato come modulo) che assoluto (quando eseguito direttamente)
try:
    from . import v2Olama
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    import v2Olama


class V2OlamaChat:
    

    def __init__(self, model: Optional[str] = None, system: Optional[str] = None):
        """
        Inizializza la sessione di chat.
        
        Args:
            model: Nome del modello (se None, usa il default da v2Olama).
            system: Prompt di sistema iniziale.
        """
        self.model = model or v2Olama.LLM_MODEL
        self.system = system or ""
        self.history: List[tuple[str, str]] = []  # (role, text) - role in {"user", "assistant"}

    def set_system(self, system_text: str) -> None:
        """Imposta il prompt di sistema per questa sessione di chat."""
        self.system = system_text

    def reset(self) -> None:
        """Resetta la cronologia del dialogo."""
        self.history = []

    def send_message(self, user_message: str, temperature: float = 0.7) -> str:
        """
        Invia un messaggio utente al modello e ritorna la risposta.
        
        Utilizza il metodo generateMock() di v2Olama per generare la risposta.
        
        Args:
            user_message: Il messaggio da inviare.
            temperature: Temperatura per la generazione (default 0.7).
        
        Returns:
            La risposta del modello come stringa.
        """
        # Aggiungi il messaggio utente alla cronologia
        self.history.append(("user", user_message))

        # Richiama generateMock di v2Olama con system prompt e user message
        response = v2Olama.generateMock(
            system=self.system,
            prompt=user_message,
            temperature=temperature
        )

        # Aggiungi la risposta dell'assistente alla cronologia
        self.history.append(("assistant", response))
        return response

    def get_history(self) -> List[tuple[str, str]]:
        """Ritorna la cronologia completa del dialogo."""
        return self.history.copy()

    def embed_message(self, text: str) -> List[float]:
        """
        Genera un embedding per un testo utilizzando il modello di embedding di v2Olama.
        
        Args:
            text: Testo da embeddare.
        
        Returns:
            L'embedding come lista di float.
        """
        return v2Olama.embed(text)


if __name__ == "__main__":
    # Demo CLI: dialogo interattivo usando i metodi di v2Olama
    chat = V2OlamaChat(system="Sei un assistente utile, conciso e amichevole.")

    print("Avviata sessione chat. Scrivi 'exit' per uscire.")
    print("=" * 50)
    try:
        while True:
            user_in = input("\nUtente> ").strip()
            if user_in.lower() in {"exit", "quit"}:
                print("Arrivederci!")
                break
            if not user_in:
                continue
            
            reply = chat.send_message(user_in)
            print(f"Assistente> {reply}")
            
    except KeyboardInterrupt:
        print("\n\nSessione terminata dall'utente.")
