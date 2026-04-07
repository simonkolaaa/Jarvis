"""
Linda - CLI Entry Point
Interfaccia CLI per l'assistente ultra-privata locale.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.brain import ask_ai
from core.memory import rebuild_agent_memory, get_vectorstore, get_relevant_context

class Colors:
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def print_banner():
    banner = fr"""
{Colors.MAGENTA}{Colors.BOLD}
    __    _____ _   ______  ___ 
   / /   /  _/ | \ / / __ \/   |
  / /    / //  |\|/ / / / / /| |
 / /____/ // /|  / / /_/ / ___ |
/_____/___/_/ |_/_/_____/_/  |_|
{Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.GREEN}  🕵️‍♀️ Linda AI - Modalità Estremamente Riservata{Colors.RESET}
{Colors.DIM}  Accesso file: Globale (Public + Private + Extra){Colors.RESET}
{Colors.DIM}  Connessione: Solo Locale (Nessun dato esce dal PC){Colors.RESET}
{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
"""
    print(banner)

def main():
    if sys.platform == "win32":
        os.system("color")
    
    print_banner()
    
    # Prova a caricare il vectorstore esistente di Linda
    vectorstore = get_vectorstore(config.CHROMA_LINDA_DIR)
    
    if vectorstore:
        print(f"  ✅ Memoria RAG di Linda trovata e caricata.")
    else:
        print(f"  📭 Nessuna memoria trovata per Linda. Inizializzo l'indicizzazione estesa...")
        vectorstore = rebuild_agent_memory("linda")

    print(f"\n{Colors.GREEN}  Linda è in ascolto... Ciao!{Colors.RESET}\n")
    
    while True:
        try:
            user_input = input(f"{Colors.BLUE}{Colors.BOLD}  Tu → {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.MAGENTA}  👋 A presto. — Linda{Colors.RESET}\n")
            break
        
        if not user_input:
            continue
        
        command = user_input.lower()
        if command in ("/quit", "/esci", "/exit", "/q"):
            print(f"\n{Colors.MAGENTA}  👋 A presto. — Linda{Colors.RESET}\n")
            break
        elif command == "/learn":
            vectorstore = rebuild_agent_memory("linda")
            continue
        
        context = ""
        if vectorstore:
            context = get_relevant_context(user_input, vectorstore, top_k=config.LINDA_RAG_TOP_K)
        
        print(f"\n{Colors.DIM}  ⏳ Linda analizza i dati...{Colors.RESET}")
        
        response = ask_ai("linda", user_input, context)
        
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}  Linda →{Colors.RESET}")
        for line in response.split("\n"):
            print(f"  {line}")
            
        if context:
            print(f"\n  {Colors.DIM}📁 (Dati recuperati dagli archivi sicuri){Colors.RESET}")
        print()

if __name__ == "__main__":
    main()
