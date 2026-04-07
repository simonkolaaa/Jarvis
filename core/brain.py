"""
Jarvis-2 - Brain Module Unificato
Gestisce la comunicazione con i modelli AI (Ollama offline / Gemini online) 
per tutti gli Agenti: Jarvis, Linda e Arus.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config


def get_llm(mode: str = None):
    """
    Restituisce l'istanza del modello LLM in base alla modalità.
    
    Args:
        mode: "offline" per Ollama, "online" per Gemini.
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
                f"\n❌ Errore connessione Ollama (assicurati che sia in esecuzione): {e}\n"
            )

    elif mode == "online":
        if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY.startswith("inserisci"):
            raise ValueError(
                "\n❌ API Key di Google mancante! Inseriscila in .env o passa a modalità offline."
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
            raise ConnectionError(f"\n❌ Errore connessione Gemini: {e}")
    else:
        raise ValueError(f"Modalità '{mode}' non riconosciuta.")


def ask_ai(persona: str, question: str, context: str = None) -> str:
    """
    Interroga il LLM impersonando lo specifico Agente.
    
    Args:
        persona: "jarvis", "linda" o "arus"
        question: La domanda dell'utente.
        context: Contesto recuperato dal RAG.
    """
    persona = persona.lower()
    
    # Deriva la modalità forzata in base alla persona
    if persona == "linda":
        mode = "offline"
        system_prompt = config.LINDA_PROMPT
    elif persona == "arus":
        mode = "online"
        system_prompt = config.ARUS_PROMPT
    else:
        mode = config.MODE
        system_prompt = config.JARVIS_PROMPT

    # Formattazione prompt col contesto (se c'è, sennò context="")
    formatted_prompt = system_prompt.format(context=context if context else "Al momento non hai ricordi specifici.")

    try:
        llm = get_llm(mode)
    except Exception as e:
        return str(e)

    prompt = ChatPromptTemplate.from_messages([
        ("system", formatted_prompt),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        return chain.invoke({"question": question})
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg:
            return "❌ Impossibile connettersi ad Ollama. È in esecuzione?"
        elif "429" in error_msg:
            return "⚠️ Limite richieste Gemini raggiunto. Riprova più tardi."
        else:
            return f"❌ Errore generico: {error_msg}"

def stream_ai(persona: str, question: str, context: str = None):
    """
    Interroga il LLM restituendo un generatore per il text streaming.
    """
    persona = persona.lower()
    
    if persona == "linda":
        mode = "offline"
        system_prompt = config.LINDA_PROMPT
    elif persona == "arus":
        mode = "online"
        system_prompt = config.ARUS_PROMPT
    else:
        mode = config.MODE
        system_prompt = config.JARVIS_PROMPT

    formatted_prompt = system_prompt.format(context=context if context else "Al momento non hai ricordi specifici.")

    try:
        llm = get_llm(mode)
    except Exception as e:
        yield str(e)
        return

    prompt = ChatPromptTemplate.from_messages([
        ("system", formatted_prompt),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        for chunk in chain.stream({"question": question}):
            yield chunk
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg:
            yield "❌ Impossibile connettersi ad Ollama."
        elif "429" in error_msg:
            yield "⚠️ Limite richieste Gemini raggiunto."
        else:
            yield f"❌ Errore generico: {error_msg}"



def switch_jarvis_mode(new_mode: str) -> str:
    """Cambia la modalità al volo (Solo per Jarvis)."""
    new_mode = new_mode.lower().strip()
    if new_mode not in ("offline", "online"):
        return "⚠️ Modalità non valida. Usa 'offline' o 'online'."

    config.MODE = new_mode
    if new_mode == "offline":
        return f"🔒 JARVIS OFFLINE attivata → {config.OFFLINE_MODEL} (Ollama)"
    else:
        return f"🌐 JARVIS ONLINE attivata → {config.ONLINE_MODEL} (Gemini)"
