
A. Il Contesto OO (Object-Oriented) e la Classe

Nel paradigma della programmazione orientata agli oggetti , l'unità di base non è la funzione, ma la Classe, che combina dati (attributi) e operazioni (metodi).
Quando testi una classe devi considerare:
    1. Intra-Method Testing: Verificare il funzionamento di un singolo metodo.
    2. Intra-Class Testing: Verificare l'intera classe, focalizzandosi sulle interazioni tra i suoi metodi e sul corretto aggiornamento dello stato interno dell'oggetto.
    3. L'Oracolo: Il risultato atteso (Expected Results) non deve solo confrontare l'input/output, ma deve anche verificare la consistenza dello stato interno dell'oggetto dopo l'esecuzione del metodo, poiché lo stato è incapsulato e osservabile solo tramite le operazioni pubbliche.
B. Lo Scaffolding (Driver e Stub)
Per eseguire l'Unit Testing, è fondamentale l'uso di scaffolding (impalcatura) per isolare i componenti.
    • Test Stub: Un'implementazione parziale di un componente da cui dipende il componente testato. Simula il comportamento di moduli non ancora sviluppati o esterni. In Python, useresti librerie di mocking come Mocking (l'equivalente di Mockito in Java).
    • Test Driver: Un'implementazione parziale di un componente che dipende dal componente testato. Simula la parte chiamante.

Se le funzioni dipendono da risorse esterne (come un database o un servizio web), dovresti usare Mock o Stub per simulare quelle dipendenze e garantire che i test siano ripetibili e isolati. Evitare le dipendenze esterne nei test unitari aiuta a prevenire i Test Smells come Mystery Guest (dipendenza da risorse esterne) e Resource Optimism (presunzione che le risorse siano sempre disponibili).

---

CRITERI DI TESTING BLACK-BOX (FUNZIONALE)

- Partizionamento in Classi di Equivalenza (Equivalence Class Partitioning)

    • Criterio: Dividere il dominio di input in classi di equivalenza (sottoinsiemi di valori che il programma dovrebbe trattare in modo analogo).
    • Requisiti delle Classi: Le classi devono essere mutuamente disgiunte e la loro unione deve coprire l'intero dominio di input.
    • Applicazione: Seleziona almeno un test case che sia rappresentativo di ciascuna classe.
        - **Weak Equivalence Class Testing (WECT)** Si seleziona un solo valore rappresentativo per ogni classe. Riduce i test, ma non copre tutte le interazioni.
        - **Strong Equivalence Class Testing (SECT)** Si costruisce il prodotto cartesiano delle classi, testando tutte le interazioni possibili. Offre maggiore copertura, ma il numero di test è molto più elevato.

- **Boundary Value Testing** (Analisi dei Valori Limite)

    L'osservazione empirica suggerisce che molti faults si manifestano in corrispondenza dei valori limite (o confini) del dominio degli input.
        • Criterio: Dopo aver definito le classi di equivalenza, concentrati sui confini.
        • Valori da Scegliere: Per ogni variabile di input, si considerano tipicamente cinque valori:
            1. Il minimo (limite inferiore).
            2. Il minimo incrementato di una piccola quantità (min+).
            3. Un valore nominale (interno all'intervallo).
            4. Il massimo decrementato (max−).
            5. Il massimo (limite superiore).
        • Test Case: La tecnica richiede 4n + 1 casi di test per una funzione con n variabili, mantenendo fisse le altre variabili sul valore nominale e variando una sola variabile alla volta. È particolarmente efficace per variabili che rappresentano intervalli numerici.

- Robustness Testing e Worst Case Testing (WCT)
    Queste tecniche estendono il Boundary Testing, considerando scenari più estremi.
        • Robustness Testing: Valuta la stabilità del sistema in condizioni di input limite multipli.
        • **Worst Case Testing (WCT)**: Genera 5^n test case creando il prodotto cartesiano dei cinque valori estremi ({min, min+, nom, max−, max}) per tutte le n variabili, testando le combinazioni in cui più variabili assumono contemporaneamente valori estremi.

- Fasi del Category-Partition Testing:
    1. Identificazione delle funzioni da testare: Scomponi il sistema in unità funzionali indipendenti.
    2. Individuazione dei parametri e delle condizioni ambientali: Analizza gli input e le variabili di contesto che influenzano la funzione.
    3. Definizione delle categorie e delle scelte:
        ◦ Categoria: Le proprietà significative dei parametri (es. lunghezza, segno).
        ◦ Scelte (Choices): I possibili valori o situazioni che ogni categoria può assumere (come le classi di equivalenza).
    4. Definizione dei vincoli (Constraints): Specifica le relazioni di dipendenza tra le scelte (ad esempio, se una stringa è vuota, il contenuto è irrilevante). Si usano marcatori come [error] per scelte che causano un errore e [single] per scelte che non necessitano combinazioni multiple.
    5. Generazione dei test frame: Costruisci le combinazioni ammissibili di scelte, rispettando i vincoli.
    6. Derivazione dei casi di test concreti: Traduci i test frame in test case effettivi, specificando input e output attesi.
    Criteri di Combinazione (Riduzione dei Test Frame):
        • Each Choice (EC): Assicura che ogni scelta compaia almeno una volta. Molto efficiente nella riduzione dei test.
        • Base Choice (BC): Scegli una combinazione "base" (tipica) e varia una categoria alla volta mantenendo le altre fisse. Ottimo compromesso tra completezza e costo.

---

CRITERI DI TESTING WHITE-BOX (STRUTTURALE)

Il White-Box Testing (o Testing Strutturale) si basa sull'analisi del codice sorgente e del suo Control Flow Graph (CFG) per garantire che tutte le parti del codice vengano eseguite.
L'obiettivo è misurare la copertura strutturale dopo aver eseguito i test funzionali. Se la copertura è insufficiente, si generano nuovi test funzionali mirati a coprire il codice non eseguito, seguendo l'approccio raccomandato da Brian Marick: "La forma deve seguire la funzione".

I principali criteri di copertura strutturale sono gerarchici:
    4.1 Statement (Node) Coverage
        • Criterio: Ogni istruzione (o nodo nel CFG) deve essere eseguita almeno una volta.
        • Limiti: È il criterio più debole. Non garantisce che tutti i percorsi di esecuzione o le condizioni logiche siano testate.
    4.2 Edge (Branch) Coverage
        • Criterio: Ogni arco (trasferimento di controllo) nel CFG deve essere attraversato almeno una volta.
        • Significato: Ogni decisione logica (if, while) deve essere valutata sia nel caso Vero che Falso.
        • Relazione: Questo criterio sussume (è più forte di) lo Statement Coverage, poiché coprire tutti gli archi garantisce che tutti i nodi siano visitati.
    4.3 **Condition Coverage (Copertura di Condizione)**
        • Criterio: In presenza di condizioni composte (es. A AND B), ogni costituente elementare (A e B) deve essere valutato almeno una volta come Vero e una volta come Falso.
        • Limiti: Può non coprire tutti i rami del programma, quindi non sussume necessariamente il Branch Coverage.
    4.4 MC/DC (Modified Condition/Decision Coverage)
        Questo è il criterio più rigoroso e pratico, richiesto per i sistemi safety-critical (es. avionica).
            • Criterio: Per ogni condizione elementare C, devono esistere almeno due test case in cui il valore di C influenza in modo indipendente il risultato finale dell'intera espressione decisionale. Questo significa che l'espressione deve assumere i valori Vero e Falso a causa unicamente del valore di C, mentre le altre condizioni elementari rimangono costanti.
            • Efficacia: È un compromesso eccellente, poiché richiede solo N+1 test case (dove N è il numero di condizioni elementari), un numero drasticamente inferiore rispetto alle 2 N combinazioni possibili. Sussume sia il Branch Coverage che il Condition Coverage.
    4.5 Data Flow Testing Criteria
        Questi criteri analizzano come i valori delle variabili vengono definiti (DEF) e utilizzati (USE) all'interno del programma.
        • Concetto: Un du-path (definition-use path) è un percorso che collega una definizione di una variabile al suo utilizzo, senza ridefinizioni intermedie.
        • Criteri Comuni:
            ◦ All Definitions: Ogni definizione di una variabile è accoppiata con almeno un uso.
            ◦ All Uses: Ogni definizione è accoppiata con tutti gli utilizzi raggiungibili (più forte di All Definitions).
            ◦ All DU Paths: Copre tutti i percorsi (non contenenti cicli) tra una definizione e un utilizzo.

---

INTEGRAZIONE DEI MODULI E TESTING INTER-CLASSE

Quando passi dall'Unit Testing a testare più classi insieme, devi eseguire l'Integration Testing. L'obiettivo è verificare il corretto funzionamento delle interazioni e interfacce tra i moduli (classi).
Dato che si sta lavorando in un contesto Agile, l'integrazione dovrebbe avvenire in modo incrementale, non con l'approccio Big-Bang (integrazione simultanea di tutti i moduli) che è sconsigliato perché rende difficile isolare la causa dei failures.
    A. **Strategie di Integrazione Incrementale**
        1. **Bottom-Up**: Inizi dai moduli di basso livello e integri progressivamente quelli superiori.
            ◦ Vantaggi: Facile isolamento dei faults.
            ◦ Svantaggi: I moduli di alto livello (la funzionalità complessiva) vengono testati tardi.
        2. Top-Down: Inizi dai moduli di alto livello (quelli che realizzano le user stories principali) e scendi.
            ◦ Vantaggi: Consente di testare l'interfaccia utente (se presente) e le scelte di design subito.
            ◦ Svantaggi: Richiede l'uso di stub (componenti fittizi per simulare i moduli mancanti) che sono costosi da creare.
        3. Sandwich Testing: Approccio ibrido. Si testano separatamente i moduli di alto e basso livello, per poi integrarli con i moduli intermedi.

    B. **Criteri di Copertura per l'Integrazione**(Coupling-Based Criteria)
    Questi criteri sono essenziali per il testing inter-classe (inter-class testing):
        • **Call Coupling**: Coprire tutti i punti di contatto (punti di invocazione) tra i moduli.
        • All-coupling-uses: Coprire almeno un percorso chiaro dall’ultima definizione nel chiamante (last definition) a tutti i possibili utilizzi (first uses) nel chiamato.
