# Jarvis-2 — Assistente AI ibrido (locale + cloud)

Monorepo evoluto che espande il progetto base in un ecosistema multi-agente, combinando modelli offline e online per diversi scenari d'uso lavorativi e privati. 

Il sistema combina:

- **Jarvis (CLI legacy)** — Chat da terminale base con switch **offline** (Ollama) / **online** (Gemini) e RAG sui documenti pubblici (indice `chroma_jarvis`).
- **Linda** — Assistente **privata** locale e sicura: basata esclusivamente su Ollama + RAG esteso sia a file pubblici che ai file personali (protetti e mai esposti al cloud). Disponibile sia come **CLI** (`linda_cli.py`) che come potente interfaccia **Web** (`linda_web.py`).
- **Arus** — Assistente **pubblica** veloce e leggera, progettata per essere deployata via cloud (es. PythonAnywhere/Vercel): basata solo su **Gemini** in cloud, esegue il RAG *esclusivamente* sui documenti autorizzati pubblici.

---

## 📂 Architettura e Alberatura

*Nota logica: rispetto all'alberatura piatta, i documenti ed i database vettoriali sono organizzati in maniera schematica per prevenire mix tra RAG pubblico e privato.*

```text
Jarvis-2/
├── config.py                 # File configurazione globale (env, path dati, modelli)
├── main.py                   # JARVIS: Interfaccia CLI
├── linda_cli.py              # LINDA: Interfaccia CLI privata locale
├── linda_web.py              # LINDA: App Web su Flask (localhost)
├── arus_web.py               # ARUS: App Web su Flask per Deploy Cloud
├── requirements.txt          # Dipendenze Python
├── .env                      # Variabili d'ambiente (api keys) e secret
├── .gitignore
│
├── core/                     # Logica centralizzata
│   ├── __init__.py
│   ├── brain.py              # Motore LLM Unificato (Generativo e Persona Prompting)
│   └── memory.py             # Motore RAG Unificato (ChromaDB Routing, Load/Split)
│
├── web/                      # Componenti interfaccia browser
│   ├── templates/            
│   │   └── chat.html         # Front-end per le versioni web
│   └── static/
│       ├── chat.css
│       └── chat.js
│
├── data/                     # Root di tutti i documenti testo e pdf
│   ├── public/               # Dati visibili a tutti i bot (Letto da Jarvis, Arus e Linda)
│   └── private/              # Dati strettamente confidenziali (Letto SOLO da Linda)
│
└── databases/                # Vettori Embeddings
    ├── chroma_jarvis/        # Vector store pubblico
    └── chroma_linda/         # Vector store privato e ibrido
```

---

## 🚀 Passo-passo: ambiente ed esecuzione

### 1. Prerequisiti

- **Python 3.10+**
- **Ollama** ([ollama.com](https://ollama.com)) funzionante e attivo in background sul pc.
- (Opzionale) **Google AI Studio API Key** per usare Arus in cloud o Jarvis in modalità `online`.

### 2. Modelli Ollama necessari (per la modalità Offline / Linda)

Apri il terminale del tuo OS e installa i modelli preferiti:

```bash
ollama pull mistral              # Oppure llama3.2 o il modello impostato nel .env 
ollama pull nomic-embed-text     # Modello embedding per comprendere i documenti
```

### 3. Setup Progetto (VENV & Installazione)

```bash
# Entra nella cartella o clonala
cd Jarvis

# Crea l'ambiente virtuale ed attivalo
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

# Installa tutte le librerie
pip install -r requirements.txt
```

### 4. Configurazione (`.env`)

Crea un file `.env` basandoti sull'esempio `config.py` in cui specificare perlomeno:
- `MODE=offline`
- `GOOGLE_API_KEY=la_tua_key`
- Eventuali porte o override di path (`LINDA_PORT`, `SCUOLA_PATH`).

---

## 🤖 Come avviare gli Agenti

| Eseguibile | Interfaccia | Scenario RAG Autorizzato | Descrizione Principale |
|------------|-------------|----------------------------|-------------------------|
| `python main.py` | Terminale | **Solo file in `data/public`** | L'assistente universale (online/offline). Comandi come `/learn`, `/mode` o `/status`. |
| `python linda_cli.py` | Terminale | **`public` + `private` + Extra** | Assistente ultra-privata e senza restrizioni, usa solo Ollama locale. |
| `python linda_web.py`| Web UI | **`public` + `private` + Extra** | Come sopra, ma accessibile dal tuo Browser su `http://127.0.0.1:5050`. |
| `python arus_web.py` | Web UI | **Solo file in `data/public`** | Per deploy su un sito pubblico come Vercel! Va solo a internet ed API Gemini. |

---

## 🐛 Troubleshooting rapido

- **Se ricevi ConnectionError in terminale**: Ollama non è stato avviato e stai provando ad usare Jarvis Offline o Linda CLI.
- **Se RAG ti dice che non ricorda nulla**: hai inserito i file nelle cartelle `data/` sbagliate, oppure devi lanciare o richiamare prima il comando di re-embedding (es: `/learn`).
- **Se l'app web si blocca**: assicurati che la porta (5050 o 5000) non sia già utilizzata da un antimalware o da IIS/Apache sul tuo Windows.

---
*README revisionato per garantire massima sicurezza ed efficienza dei moduli Jarvis-2.*
