Certamente. Ecco la sezione completa e aggiornata per il **Controller**.

Ho applicato le correzioni discusse:

1. **Classificazione:** Tutti i test sono ora correttamente indicati come **White Box** (poiché usano Mock e verificano le chiamate interne).
2. **WECT rimosso:** Ho tolto il termine WECT dalla colonna "Tipo Test" per evitare ambiguità, dato che la verifica è strutturale.
3. **Test Case:** Ho mantenuto esattamente i 4 test che mi hai passato nel codice (001, 002 originale, 003, 004).

Puoi incollare questo blocco direttamente nel tuo documento.

---

# 🔧 **Funzione `run_generation_process` (Controller)**

Il Controller funge da orchestratore: non esegue calcoli diretti, ma coordina l'Engine e l'Exporter gestendo le risorse di sistema (I/O). I test utilizzano tecniche di **Mocking** per verificare l'interazione tra i componenti.

### **Tabella Test – Controller Orchestration**

| Test ID | Tipo Test | Input | Output Atteso | Descrizione |
| --- | --- | --- | --- | --- |
| **TC-C01** | White Box – Interaction (Happy Path) | args: `out=None`, `format=json` | Engine invocato, Exporter invocato su `sys.stdout` | Verifica che, in assenza di file di output, il controller diriga il flusso verso lo standard output. |
| **TC-C02** | White Box – Interaction & Resource Management | args: `out="dir/file.json"` | Creazione dir, Apertura File, Export su File, Chiusura | Verifica la gestione completa del ciclo di vita del file: creazione cartelle, apertura stream e chiusura. |
| **TC-C03** | White Box – Error Propagation (Fail Fast) | Engine solleva `ValueError` | Eccezione propagata, Exporter **NON** invocato | Verifica il flusso di controllo: se la generazione fallisce, l'export non deve essere tentato. |
| **TC-C04** | White Box – Finally Block Logic | Exporter solleva `RuntimeError` (es. Disk Full) | Eccezione propagata, File **CHIUSO** nel finally | Verifica che il file handle venga chiuso correttamente anche in caso di crash critico durante la scrittura. |

---

### 📝 **Nota sulla Strategia di Test**

I test del Controller sono classificati come **White Box Interaction Tests**.
Non verificano la correttezza dei dati generati (compito dell'Engine) o la formattazione del file (compito dell'Exporter), ma assicurano che il Controller:

1. Chiami i collaboratori nell'ordine corretto.
2. Gestisca correttamente l'acquisizione e il rilascio delle risorse (pattern `try...finally` per i file).