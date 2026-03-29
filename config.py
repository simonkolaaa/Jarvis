"""
Jarvis - Configurazione Centralizzata
Carica le variabili dal file .env e definisce le costanti del progetto.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# ─── Directory del progetto ───────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# ─── Modalità AI ─────────────────────────────────────────────────────
# "offline" = Ollama + Mistral (locale, privato)
# "online"  = Google Gemini (veloce, richiede internet + API key)
MODE = os.getenv("MODE", "offline").lower()

# ─── Modelli ─────────────────────────────────────────────────────────
OFFLINE_MODEL = "mistral"                # Modello Ollama per chat
ONLINE_MODEL = "gemini-2.5-flash"        # Modello Gemini (free tier)
EMBEDDING_MODEL = "nomic-embed-text"     # Modello Ollama per embeddings

# ─── RAG Parameters ─────────────────────────────────────────────────
CHUNK_SIZE = 1000       # Dimensione dei chunk di testo (in caratteri)
CHUNK_OVERLAP = 200     # Sovrapposizione tra chunk adiacenti
TOP_K_RESULTS = 4       # Numero di chunk rilevanti da recuperare

# ─── API Keys ────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ─── System Prompt ───────────────────────────────────────────────────
SYSTEM_PROMPT = """Sei Jarvis, un assistente AI personale intelligente e affidabile.
Rispondi in modo chiaro, conciso e utile. Se ti viene fornito del contesto dai documenti 
dell'utente, usalo per dare risposte più precise e personalizzate.
Se non conosci la risposta, dillo onestamente invece di inventare.
Rispondi nella stessa lingua in cui ti viene posta la domanda."""

SYSTEM_PROMPT_WITH_CONTEXT = """Sei Jarvis, un assistente AI personale intelligente e affidabile.
Hai accesso ai documenti personali dell'utente. Usa il seguente contesto per rispondere 
in modo preciso e personalizzato. Se il contesto non è rilevante alla domanda, 
rispondi comunque con le tue conoscenze generali.

--- CONTESTO DAI TUOI DOCUMENTI ---
{context}
--- FINE CONTESTO ---

Rispondi in modo chiaro, conciso e utile.
Rispondi nella stessa lingua in cui ti viene posta la domanda."""
