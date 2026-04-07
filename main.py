"""
Jarvis - Main Entry Point (Legacy CLI)
Interfaccia CLI interattiva per il tuo assistente AI personale.
"""
import sys
import os

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.brain import ask_ai, switch_jarvis_mode
from core.memory import rebuild_agent_memory, get_vectorstore, get_relevant_context

# ─── Colori ANSI per il terminale ────────────────────────────────────
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    banner = fr"""
{Colors.CYAN}{Colors.BOLD}
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.GREEN}  🤖 Assistente AI Personale v2.0 (Jarvis CLI){Colors.RESET}
{Colors.DIM}  Digita /help per vedere i comandi disponibili{Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
"""
    print(banner)


def print_help():
    help_text = f"""
{Colors.CYAN}{Colors.BOLD}📋 Comandi Disponibili:{Colors.RESET}
  {Colors.YELLOW}/help{Colors.RESET}           → Mostra questo messaggio
  {Colors.YELLOW}/mode{Colors.RESET}           → Mostra la modalità corrente
  {Colors.YELLOW}/mode offline{Colors.RESET}   → Passa alla modalità offline (Ollama)
  {Colors.YELLOW}/mode online{Colors.RESET}    → Passa alla modalità online (Gemini)
  {Colors.YELLOW}/learn{Colors.RESET}          → Ricarica i documenti dalla cartella data/public/
  {Colors.YELLOW}/status{Colors.RESET}         → Mostra lo stato del sistema
  {Colors.YELLOW}/clear{Colors.RESET}          → Pulisce lo schermo
  {Colors.YELLOW}/quit{Colors.RESET}           → Esci da Jarvis
"""
    print(help_text)


def main():
    if sys.platform == "win32":
        os.system("color")
    
    print_banner()
    
    mode_icon = "🔒" if config.MODE == "offline" else "🌐"
    mode_name = f"{config.OFFLINE_MODEL}" if config.MODE == "offline" else f"{config.ONLINE_MODEL}"
    print(f"  {mode_icon} Modalità: {Colors.BOLD}{config.MODE.upper()}{Colors.RESET} ({mode_name})")
    
    # Prova a caricare il vectorstore esistente di Jarvis (solo dati public)
    vectorstore = get_vectorstore(config.CHROMA_JARVIS_DIR)
    
    if vectorstore:
        print(f"  ✅ Memoria RAG Pubblica trovata (Usa /learn per aggiornarla se hai aggiunto file).")
    else:
        print(f"  📭 Nessuna memoria trovata. Provo a costruirla da config.DATA_PUBLIC_DIR...")
        # Auto build al primo avvio se non c'è DB
        if config.DATA_PUBLIC_DIR.exists() and any(config.DATA_PUBLIC_DIR.iterdir()):
             vectorstore = rebuild_agent_memory("jarvis")

    print(f"\n{Colors.GREEN}  Jarvis è pronto. Come posso aiutarti?{Colors.RESET}\n")
    
    while True:
        try:
            user_input = input(f"{Colors.BLUE}{Colors.BOLD}  Tu → {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.CYAN}  👋 Alla prossima! — Jarvis{Colors.RESET}\n")
            break
        
        if not user_input:
            continue
        
        command = user_input.lower()
        
        if command in ("/quit", "/esci", "/exit", "/q"):
            print(f"\n{Colors.CYAN}  👋 Alla prossima! — Jarvis{Colors.RESET}\n")
            break
        elif command == "/help":
            print_help()
            continue
        elif command == "/mode":
            mode_icon = "🔒" if config.MODE == "offline" else "🌐"
            print(f"\n  {mode_icon} Modalità: {Colors.BOLD}{config.MODE.upper()}{Colors.RESET}\n")
            continue
        elif command.startswith("/mode "):
            res = switch_jarvis_mode(command.split("/mode ", 1)[1])
            print(f"\n  {res}\n")
            continue
        elif command == "/learn":
            vectorstore = rebuild_agent_memory("jarvis")
            continue
        elif command == "/status":
            mem = "Attiva" if vectorstore else "Inattiva"
            print(f"\n  Stato: {config.MODE.upper()} | DB: {mem} | Cartella: {config.DATA_PUBLIC_DIR.name}\n")
            continue
        elif command == "/clear":
            os.system("cls" if sys.platform == "win32" else "clear")
            print_banner()
            continue
        elif command.startswith("/"):
            print(f"\n  ⚠️ Comando sconosciuto. Digita /help.\n")
            continue
        
        context = ""
        if vectorstore:
            # Ricerca contesto
            context = get_relevant_context(user_input, vectorstore, top_k=config.JARVIS_RAG_TOP_K)
        
        print(f"\n{Colors.DIM}  ⏳ Jarvis sta pensando...{Colors.RESET}")
        
        response = ask_ai("jarvis", user_input, context)
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}  Jarvis →{Colors.RESET}")
        for line in response.split("\n"):
            print(f"  {line}")
            
        if context:
            print(f"\n  {Colors.DIM}📚 (Fonti consultate da data/public/){Colors.RESET}")
        print()

if __name__ == "__main__":
    main()
