"""
Jarvis - Main Entry Point
Interfaccia CLI interattiva per il tuo assistente AI personale.

Utilizzo:
    python main.py
"""
import sys
import os

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.brain import ask_jarvis, switch_mode
from core.memory import ingest_documents, get_relevant_context, create_or_load_vectorstore, get_document_stats


# ─── Colori ANSI per il terminale ────────────────────────────────────
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    """Stampa il banner di avvio di Jarvis."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.GREEN}  🤖 Assistente AI Personale v1.0{Colors.RESET}
{Colors.DIM}  Digita /help per vedere i comandi disponibili{Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
"""
    print(banner)


def print_help():
    """Stampa la lista dei comandi disponibili."""
    help_text = f"""
{Colors.CYAN}{Colors.BOLD}📋 Comandi Disponibili:{Colors.RESET}

  {Colors.YELLOW}/help{Colors.RESET}           → Mostra questo messaggio
  {Colors.YELLOW}/mode{Colors.RESET}           → Mostra la modalità corrente
  {Colors.YELLOW}/mode offline{Colors.RESET}   → Passa alla modalità offline (Ollama)
  {Colors.YELLOW}/mode online{Colors.RESET}    → Passa alla modalità online (Gemini)
  {Colors.YELLOW}/learn{Colors.RESET}          → Ricarica i documenti dalla cartella data/
  {Colors.YELLOW}/status{Colors.RESET}         → Mostra lo stato del sistema
  {Colors.YELLOW}/clear{Colors.RESET}          → Pulisce lo schermo
  {Colors.YELLOW}/quit{Colors.RESET}           → Esci da Jarvis (anche /esci, /exit)

{Colors.DIM}  Qualsiasi altro testo → Fai una domanda a Jarvis{Colors.RESET}
"""
    print(help_text)


def print_status(vectorstore):
    """Stampa lo stato corrente del sistema."""
    mode_icon = "🔒" if config.MODE == "offline" else "🌐"
    mode_name = f"{config.OFFLINE_MODEL} (Ollama)" if config.MODE == "offline" else f"{config.ONLINE_MODEL} (Gemini)"
    
    stats = get_document_stats()
    
    has_memory = vectorstore is not None
    memory_icon = "✅" if has_memory else "❌"
    
    status_text = f"""
{Colors.CYAN}{Colors.BOLD}📊 Stato di Jarvis:{Colors.RESET}

  {mode_icon} Modalità:      {Colors.BOLD}{config.MODE.upper()}{Colors.RESET} → {mode_name}
  📁 Documenti:     {stats['total']} file ({stats['txt']} txt, {stats['pdf']} pdf, {stats['docx']} docx, {stats['md']} md)
  {memory_icon} Memoria RAG:   {"Attiva" if has_memory else "Non inizializzata (usa /learn)"}
  🧠 Embeddings:    {config.EMBEDDING_MODEL}
  📂 Cartella dati: {config.DATA_DIR}
"""
    print(status_text)


def main():
    """Loop principale di Jarvis."""
    # Abilita colori ANSI su Windows
    if sys.platform == "win32":
        os.system("color")
    
    print_banner()
    
    # Mostra la modalità corrente
    mode_icon = "🔒" if config.MODE == "offline" else "🌐"
    mode_name = f"{config.OFFLINE_MODEL}" if config.MODE == "offline" else f"{config.ONLINE_MODEL}"
    print(f"  {mode_icon} Modalità: {Colors.BOLD}{config.MODE.upper()}{Colors.RESET} ({mode_name})")
    
    # Inizializzazione: prova a caricare il vectorstore esistente
    vectorstore = None
    stats = get_document_stats()
    
    if stats["total"] > 0:
        print(f"  📁 Trovati {stats['total']} documento/i nella cartella data/")
        print(f"  🔄 Caricamento memoria in corso...\n")
        try:
            # Prima prova a caricare un vectorstore esistente
            vectorstore = create_or_load_vectorstore()
            
            # Se non esiste, crea uno nuovo
            if vectorstore is None:
                vectorstore = ingest_documents()
        except Exception as e:
            print(f"  ⚠️ Impossibile caricare la memoria: {e}")
            print(f"  ℹ️ Jarvis funzionerà senza memoria RAG. Usa /learn per riprovare.\n")
    else:
        print(f"  📭 Nessun documento in {config.DATA_DIR}")
        print(f"  ℹ️ Aggiungi file .txt/.pdf/.docx/.md e usa /learn per attivarla\n")
    
    print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"\n{Colors.GREEN}  Jarvis è pronto. Come posso aiutarti?{Colors.RESET}\n")
    
    # ─── Loop principale ─────────────────────────────────────────────
    while True:
        try:
            user_input = input(f"{Colors.BLUE}{Colors.BOLD}  Tu → {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.CYAN}  👋 Alla prossima! — Jarvis{Colors.RESET}\n")
            break
        
        if not user_input:
            continue
        
        # ─── Gestione comandi speciali ────────────────────────────────
        command = user_input.lower()
        
        if command in ("/quit", "/esci", "/exit", "/q"):
            print(f"\n{Colors.CYAN}  👋 Alla prossima! — Jarvis{Colors.RESET}\n")
            break
        
        elif command == "/help":
            print_help()
            continue
        
        elif command == "/mode":
            mode_icon = "🔒" if config.MODE == "offline" else "🌐"
            mode_name = f"{config.OFFLINE_MODEL} (Ollama)" if config.MODE == "offline" else f"{config.ONLINE_MODEL} (Gemini)"
            print(f"\n  {mode_icon} Modalità corrente: {Colors.BOLD}{config.MODE.upper()}{Colors.RESET} → {mode_name}\n")
            continue
        
        elif command.startswith("/mode "):
            new_mode = command.split("/mode ", 1)[1].strip()
            result = switch_mode(new_mode)
            print(f"\n  {result}\n")
            continue
        
        elif command == "/learn":
            print()
            vectorstore = ingest_documents()
            print()
            continue
        
        elif command == "/status":
            print_status(vectorstore)
            continue
        
        elif command == "/clear":
            os.system("cls" if sys.platform == "win32" else "clear")
            print_banner()
            continue
        
        elif command.startswith("/"):
            print(f"\n  ⚠️ Comando sconosciuto: {user_input}")
            print(f"  Digita {Colors.YELLOW}/help{Colors.RESET} per la lista comandi.\n")
            continue
        
        # ─── Domanda normale → Chiedi a Jarvis ───────────────────────
        # Step 1: Cerca contesto rilevante (se il RAG è attivo)
        context = ""
        if vectorstore is not None:
            context = get_relevant_context(user_input, vectorstore)
        
        # Step 2: Chiedi al modello AI
        print(f"\n{Colors.DIM}  ⏳ Jarvis sta pensando...{Colors.RESET}")
        response = ask_jarvis(user_input, context=context if context else None)
        
        # Step 3: Mostra la risposta
        print(f"\n{Colors.CYAN}{Colors.BOLD}  Jarvis →{Colors.RESET}")
        
        # Indenta ogni riga della risposta
        for line in response.split("\n"):
            print(f"  {line}")
        
        # Indicatore se ha usato il RAG
        if context:
            print(f"\n  {Colors.DIM}📚 Risposta arricchita con i tuoi documenti{Colors.RESET}")
        
        print()


if __name__ == "__main__":
    main()
