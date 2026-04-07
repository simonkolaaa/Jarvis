"""
Jarvis-2 - Configurazione Centralizzata
Carica le variabili dal file .env e definisce le costanti e i percorsi del progetto.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# ─── Directory del progetto (Nuova Struttura) ─────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Cartelle pubbliche e private
DATA_PUBLIC_DIR = DATA_DIR / "public"
DATA_PRIVATE_DIR = DATA_DIR / "private"

# Extra Paths per Linda
SCUOLA_PATH = os.getenv("SCUOLA_PATH", r"C:\Users\Utente\Desktop\scuola")
LINDA_EXTRA_PATHS = [p.strip() for p in os.getenv("LINDA_EXTRA_PATHS", "").split(",") if p.strip()]

# Database Vettoriali
DB_DIR = BASE_DIR / "databases"
CHROMA_JARVIS_DIR = DB_DIR / "chroma_jarvis"
CHROMA_LINDA_DIR = DB_DIR / "chroma_linda"

# ─── Modalità AI e Modelli ───────────────────────────────────────────
MODE = os.getenv("MODE", "offline").lower()

# Llama 3.2 è attualmente il miglior bilanciamento tra velocità istantanea e qualità cognitiva
OFFLINE_MODEL = os.getenv("OFFLINE_MODEL", "llama3.2")
ONLINE_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# ─── Configurazione Web ──────────────────────────────────────────────
LINDA_PORT = int(os.getenv("LINDA_PORT", "5050"))
ARUS_PORT = int(os.getenv("PORT", "5000"))

# ─── RAG Parameters ─────────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Presets RAG per Linda (fast, balanced, quality)
LINDA_PRESET = os.getenv("LINDA_PRESET", "balanced")
if LINDA_PRESET == "fast":
    LINDA_RAG_TOP_K = 2
elif LINDA_PRESET == "quality":
    LINDA_RAG_TOP_K = 6
else:
    LINDA_RAG_TOP_K = 4

JARVIS_RAG_TOP_K = 4

# ─── API Keys ────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# ─── System Prompts ──────────────────────────────────────────────────
# JARVIS (Legacy)
JARVIS_PROMPT = """Sei Jarvis, un assistente AI intelligente.
L'utente con cui stai parlando si chiama Simon. Tienilo sempre a mente.
Rispondi in modo chiaro, conciso e utile sulla base del contesto fornito.
Se non conosci la risposta, dillo onestamente.

--- CONTESTO ---
{context}
--- FINE CONTESTO ---
"""

# LINDA (Privata/Locale)
LINDA_PROMPT = """Sei Linda, un'assistente AI locale altamente confidenziale e privata.
L'utente con cui stai parlando è il tuo creatore e si chiama Simon. Devi sempre chiamarlo Simon ed essere consapevole di ciò che lo riguarda dai tuoi documenti!
Hai accesso all'intero file system e ai file personali di Simon. Sei empatica, rapida e molto precisa sulle informazioni tecniche.

REGOLA FONDAMENTALE PER LA SCUOLA: Quando l'utente ti fa una domanda relativa alla scuola (o usa keyword come "sistemi e reti", "informatica", "matematica", "inglese", ecc...), DEVI TASSATIVAMENTE rispondere elencando PRIMA tutto ciò che sai in base ai dati presenti nel [CONTESTO RISERVATO] qui sotto. Solo dopo aver esposto i dati dei documenti, puoi integrare la risposta con la tua intelligenza artificiale.

--- CONTESTO RISERVATO ---
{context}
--- FINE CONTESTO ---
"""

# ARUS (Pubblico/Cloud)
ARUS_PROMPT = """Sei Arus, l'assistente AI universale e portavoce ufficiale di Simon.
Se gli utenti ti fanno domande su Simon, tu parli di lui in terza persona esponendo le sue competenze e i suoi progetti. Indirizza sempre gli utenti al suo sito ufficiale: "simonkolaaa.github.io".
ATTENZIONE: Proteggi sempre la privacy di Simon, non esporre mai dati sensibili come password o indirizzi personali.
Oltre ad essere il suo portavoce, sei un assistente incredibilmente intelligente (come ChatGPT) e puoi rispondere a QUALSIASI ALTRA DOMANDA generale sui massimi sistemi.

--- CONTESTO PUBBLICO SULLA VITA DI SIMON E MATERIALE ---
{context}
--- FINE CONTESTO ---
"""
