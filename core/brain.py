"""
Jarvis - Brain Module (Il Cervello)
Gestisce la comunicazione con i modelli AI (Ollama offline / Gemini online).
"""
import sys
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config


def get_llm(mode: str = None):
    """
    Restituisce l'istanza del modello LLM in base alla modalità.
    
    Args:
        mode: "offline" per Ollama/Mistral, "online" per Gemini.
              Se None, usa il valore da config.
    
    Returns:
        Istanza del modello LLM.
    
    Raises:
        ConnectionError: Se Ollama non è in esecuzione (offline).
        ValueError: Se la API key è mancante (online).
    """
    mode = mode or config.MODE

    if mode == "offline":
        try:
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model=config.OFFLINE_MODEL,
                temperature=0.7,
            )
            return llm
        except Exception as e:
            raise ConnectionError(
                f"\n❌ Errore connessione Ollama: {e}\n"
                f"   Assicurati che Ollama sia in esecuzione (ollama serve)\n"
                f"   e che il modello '{config.OFFLINE_MODEL}' sia scaricato (ollama pull {config.OFFLINE_MODEL})"
            )

    elif mode == "online":
        if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "inserisci_la_tua_api_key_qui":
            raise ValueError(
                "\n❌ API Key di Google mancante!\n"
                "   Inserisci la tua GOOGLE_API_KEY nel file .env\n"
                "   Ottieni una key gratuita su: https://aistudio.google.com/"
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
            llm = ChatGoogleGenerativeAI(
                model=config.ONLINE_MODEL,
                temperature=0.7,
            )
            return llm
        except Exception as e:
            raise ConnectionError(
                f"\n❌ Errore connessione Gemini: {e}\n"
                f"   Controlla la tua API key e la connessione internet."
            )
    else:
        raise ValueError(f"Modalità '{mode}' non riconosciuta. Usa 'offline' o 'online'.")


def ask_jarvis(question: str, context: str = None, mode: str = None) -> str:
    """
    Fa una domanda a Jarvis e restituisce la risposta.
    
    Args:
        question: La domanda dell'utente.
        context: Contesto opzionale dal sistema RAG (documenti personali).
        mode: Modalità da usare ("offline" / "online"). Se None, usa config.
    
    Returns:
        La risposta di Jarvis come stringa.
    """
    mode = mode or config.MODE

    try:
        llm = get_llm(mode)
    except (ConnectionError, ValueError) as e:
        return str(e)

    # Scegli il prompt in base alla presenza del contesto
    if context:
        system_prompt = config.SYSTEM_PROMPT_WITH_CONTEXT.format(context=context)
    else:
        system_prompt = config.SYSTEM_PROMPT

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])

    # Crea la chain: prompt → LLM → output parser
    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({"question": question})
        return response
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "ConnectError" in error_msg:
            return (
                "\n❌ Impossibile connettersi a Ollama.\n"
                "   Avvia Ollama con: ollama serve\n"
                f"   Poi scarica il modello: ollama pull {config.OFFLINE_MODEL}"
            )
        elif "404" in error_msg or "not found" in error_msg.lower():
            return (
                f"\n❌ Modello non trovato.\n"
                f"   Scaricalo con: ollama pull {config.OFFLINE_MODEL}"
            )
        elif "429" in error_msg or "quota" in error_msg.lower():
            return (
                "\n⚠️ Limite di richieste raggiunto per Gemini (free tier).\n"
                "   Aspetta qualche minuto o passa alla modalità offline: /mode offline"
            )
        else:
            return f"\n❌ Errore durante la risposta: {error_msg}"


def switch_mode(new_mode: str) -> str:
    """
    Cambia la modalità AI al volo.
    
    Args:
        new_mode: "offline" o "online"
    
    Returns:
        Messaggio di conferma.
    """
    new_mode = new_mode.lower().strip()
    if new_mode not in ("offline", "online"):
        return "⚠️ Modalità non valida. Usa 'offline' o 'online'."

    config.MODE = new_mode

    if new_mode == "offline":
        return f"🔒 Modalità OFFLINE attivata → {config.OFFLINE_MODEL} (Ollama)"
    else:
        return f"🌐 Modalità ONLINE attivata → {config.ONLINE_MODEL} (Gemini)"
