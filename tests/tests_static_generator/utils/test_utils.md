Certo!
Di seguito trovi **le stesse tabelle**, ma ora **ogni tabella ha il proprio titolo markdown separato**, così quando copi/incolli nel README sono facilmente distinguibili.

Puoi incollare direttamente tutto.

---

# 📄 **DOCUMENTAZIONE TEST – VERSIONE CON TITOLI DELLE TABELLE**

---

# 🔧 **Funzione `generate_data_from_schema_dict`**

### **Tabella Test – generate_data_from_schema_dict**

| Test ID    | Tipo Test                        | Input                                         | Output Atteso                                        | Descrizione                                                                          |
| ---------- | -------------------------------- | --------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **TC-U01** | Black Box – Happy Path           | Schema dict valido                            | Lista di record generati + rimozione file temporaneo | Verifica il flusso corretto: creazione file schema, generazione dati e cleanup.      |
| **TC-U02** | Black Box – BVA (empty result)   | Schema che genera 0 elementi                  | `None`                                               | Se la generazione non produce dati, la funzione deve restituire `None`.              |
| **TC-U03** | White Box – Robustness + Finally | Schema valido, errore simulato in `MagicMock` | Cleanup eseguito comunque                            | Verifica che il blocco `finally` esegua sempre `remove`, anche in caso di eccezioni. |
| **TC-U19** | White Box – Cleanup failure      | Errore in `os.remove`                         | Nessuna eccezione propagata                          | Testa il ramo `except OSError` nel cleanup, garantendo robustezza.                   |

---

# 🔧 **Funzione `run_cli_command`**

### **Tabella Test – run_cli_command**

| Test ID    | Tipo Test                     | Input                                                       | Output Atteso                                        | Descrizione                                                                             |
| ---------- | ----------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **TC-U04** | White Box – String Processing | path schema `"models"`, path data `"out"`, args="--count 5" | Comando CLI composto correttamente                   | Verifica la manipolazione interna della stringa e che le parole chiave vengano rimosse. |
| **TC-U13** | BVA – Empty String            | args vuote                                                  | Comando minimale valido                              | Verifica il comportamento con input minimo (weak equivalence class).                    |
| **TC-U18** | White Box – Error Capture     | stdout/stderr simulati                                      | Restituzione dell'oggetto `CompletedProcess` mockato | Testa il percorso interno di cattura errori.                                            |

---

# 🔧 **Funzione `clean_files`**

### **Tabella Test – clean_files**

| Test ID    | Tipo Test                  | Input                      | Output atteso                          | Descrizione                                              |
| ---------- | -------------------------- | -------------------------- | -------------------------------------- | -------------------------------------------------------- |
| **TC-U05** | WECT – File exists         | Lista con file esistente   | `os.remove` eseguito                   | Verifica comportamento in classe “file presente”.        |
| **TC-U06** | WECT – File NOT exists     | Lista con file inesistente | Nessun crash                           | Verifica comportamento nella classe “file non presente”. |
| **TC-U07** | White Box – Error Handling | File che genera `OSError`  | Nessuna eccezione                      | Verifica il ramo `except OSError`.                       |
| **TC-U11** | BVA – Empty List           | `[]`                       | Nessuna azione                         | Classe di equivalenza “input minimo”.                    |
| **TC-U12** | Performance Test (Mocked)  | 1000 file                  | Rimozione simulata senza rallentamenti | Stress test del ciclo interno.                           |
| **TC-U17** | Black Box – Invalid Input  | `None`                     | TypeError                              | Verifica robustezza su input non valido.                 |

---

# 🔧 **Funzione `prepare_output_dir`**

### **Tabella Test – prepare_output_dir**

| Test ID    | Tipo Test               | Input                     | Output Atteso                 | Descrizione                                              |
| ---------- | ----------------------- | ------------------------- | ----------------------------- | -------------------------------------------------------- |
| **TC-U08** | Black Box – State Reset | Directory contenente file | Directory ripulita e ricreata | Verifica che la funzione resetti totalmente la cartella. |

---

# 🔧 **Funzione `load_json_file`**

### **Tabella Test – load_json_file**

| Test ID    | Tipo Test                  | Input                    | Output Atteso               | Descrizione                               |
| ---------- | -------------------------- | ------------------------ | --------------------------- | ----------------------------------------- |
| **TC-U09** | Black Box – Valid JSON     | File JSON valido         | Dict correttamente caricato | Verifica funzionalità standard.           |
| **TC-U14** | BVA/Malicious – Empty File | JSON 0 byte              | JSONDecodeError             | Testa la robustezza sul contenuto minimo. |
| **TC-U16** | Robustness – Invalid JSON  | File con sintassi errata | JSONDecodeError             | Verifica gestione errori standard JSON.   |

---

# 🔧 **Funzione `create_temp_schema`**

### **Tabella Test – create_temp_schema**

| Test ID    | Tipo Test               | Input       | Output Atteso                            | Descrizione                                         |
| ---------- | ----------------------- | ----------- | ---------------------------------------- | --------------------------------------------------- |
| **TC-U10** | Black Box – Normal Case | Dict schema | File temporaneo scritto con il contenuto | Verifica creazione e persistenza corretta del file. |
| **TC-U15** | BVA – Empty Dict        | `{}`        | File JSON valido e vuoto                 | Controlla il comportamento su input minimo.         |

---

