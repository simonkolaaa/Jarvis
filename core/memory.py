"""
Jarvis - Memory Module (La Memoria)
Gestisce il sistema RAG: caricamento documenti, embeddings e ricerca in ChromaDB.
"""
import os
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

import config


def load_documents(data_dir: Path = None) -> list:
    """
    Carica tutti i documenti (.txt, .pdf, .docx, .md) dalla cartella data/.
    
    Args:
        data_dir: Path alla cartella dei documenti. Default: config.DATA_DIR
    
    Returns:
        Lista di oggetti Document di LangChain.
    """
    data_dir = data_dir or config.DATA_DIR
    documents = []
    
    if not data_dir.exists():
        print(f"📁 Cartella {data_dir} non trovata. Creazione in corso...")
        data_dir.mkdir(parents=True, exist_ok=True)
        return documents
    
    # Trova tutti i file supportati
    supported_files = []
    for ext in ["*.txt", "*.pdf", "*.docx", "*.md"]:
        supported_files.extend(data_dir.glob(ext))
    
    if not supported_files:
        print("📭 Nessun documento trovato nella cartella data/")
        return documents
    
    print(f"📖 Caricamento di {len(supported_files)} documento/i...")
    
    for file_path in supported_files:
        try:
            suffix = file_path.suffix.lower()
            if suffix == ".txt" or suffix == ".md":
                loader = TextLoader(str(file_path), encoding="utf-8")
            elif suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif suffix == ".docx":
                loader = Docx2txtLoader(str(file_path))
            else:
                continue
            
            docs = loader.load()
            documents.extend(docs)
            print(f"   ✅ {file_path.name} ({len(docs)} pagina/e)")
        except Exception as e:
            print(f"   ⚠️ Errore caricando {file_path.name}: {e}")
    
    return documents


def split_documents(documents: list) -> list:
    """
    Divide i documenti in chunk più piccoli per il RAG.
    
    Args:
        documents: Lista di Document da dividere.
    
    Returns:
        Lista di Document chunk.
    """
    if not documents:
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = splitter.split_documents(documents)
    print(f"✂️  Documenti divisi in {len(chunks)} chunk")
    return chunks


def get_embeddings():
    """
    Restituisce il modello di embedding (Ollama locale).
    
    Returns:
        OllamaEmbeddings instance.
    """
    return OllamaEmbeddings(model=config.EMBEDDING_MODEL)


def create_or_load_vectorstore(chunks: list = None) -> Optional[Chroma]:
    """
    Crea un nuovo vectorstore o carica quello esistente.
    
    Args:
        chunks: Se forniti, crea un nuovo vectorstore con questi chunk.
                Se None, prova a caricare un vectorstore esistente.
    
    Returns:
        Istanza Chroma del vectorstore, o None se non esiste e non ci sono chunk.
    """
    embeddings = get_embeddings()
    persist_dir = str(config.CHROMA_DIR)
    
    if chunks:
        # Crea nuovo vectorstore (sovrascrive se esiste)
        print(f"🧠 Creazione database vettoriale con {len(chunks)} chunk...")
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=persist_dir,
                collection_name="jarvis_memory",
            )
            print("✅ Database vettoriale creato con successo!")
            return vectorstore
        except Exception as e:
            print(f"❌ Errore creazione vectorstore: {e}")
            print("   Assicurati che Ollama sia in esecuzione con il modello di embedding:")
            print(f"   ollama pull {config.EMBEDDING_MODEL}")
            return None
    
    # Prova a caricare un vectorstore esistente
    if config.CHROMA_DIR.exists() and any(config.CHROMA_DIR.iterdir()):
        try:
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name="jarvis_memory",
            )
            # Verifica che non sia vuoto
            count = vectorstore._collection.count()
            if count > 0:
                print(f"📚 Database vettoriale caricato ({count} chunk in memoria)")
                return vectorstore
        except Exception as e:
            print(f"⚠️ Errore caricamento vectorstore esistente: {e}")
    
    return None


def get_relevant_context(query: str, vectorstore: Chroma, top_k: int = None) -> str:
    """
    Cerca nei documenti il contesto più rilevante per la query.
    
    Args:
        query: La domanda dell'utente.
        vectorstore: Istanza Chroma del vectorstore.
        top_k: Numero di risultati da recuperare. Default: config.TOP_K_RESULTS
    
    Returns:
        Stringa con il contesto rilevante formattato, o stringa vuota se nessun risultato.
    """
    if vectorstore is None:
        return ""
    
    top_k = top_k or config.TOP_K_RESULTS
    
    try:
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )
        
        relevant_docs = retriever.invoke(query)
        
        if not relevant_docs:
            return ""
        
        # Formatta il contesto
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            source = doc.metadata.get("source", "sconosciuto")
            source_name = Path(source).name if source != "sconosciuto" else source
            context_parts.append(
                f"[Documento {i} - {source_name}]\n{doc.page_content}"
            )
        
        return "\n\n".join(context_parts)
    
    except Exception as e:
        print(f"⚠️ Errore durante la ricerca nei documenti: {e}")
        return ""


def ingest_documents() -> Optional[Chroma]:
    """
    Pipeline completa di ingestione documenti:
    Carica → Divide → Crea vectorstore.
    
    Returns:
        Istanza Chroma del vectorstore, o None se fallisce.
    """
    print("\n🔄 Ingestione documenti in corso...\n")
    
    # Step 1: Carica
    documents = load_documents()
    if not documents:
        print("\n⚠️ Nessun documento da processare.")
        print(f"   Aggiungi file .txt, .pdf, .docx o .md nella cartella: {config.DATA_DIR}")
        return None
    
    # Step 2: Dividi
    chunks = split_documents(documents)
    if not chunks:
        print("\n⚠️ Impossibile dividere i documenti in chunk.")
        return None
    
    # Step 3: Crea vectorstore
    vectorstore = create_or_load_vectorstore(chunks)
    
    if vectorstore:
        print("\n🎉 Documenti caricati in memoria con successo!")
    
    return vectorstore


def get_document_stats() -> dict:
    """
    Restituisce statistiche sui documenti nella cartella data/.
    
    Returns:
        Dict con conteggi dei file per tipo.
    """
    data_dir = config.DATA_DIR
    stats = {"txt": 0, "pdf": 0, "docx": 0, "md": 0, "total": 0}
    
    if not data_dir.exists():
        return stats
    
    for f in data_dir.iterdir():
        if f.suffix.lower() == ".txt":
            stats["txt"] += 1
        elif f.suffix.lower() == ".pdf":
            stats["pdf"] += 1
        elif f.suffix.lower() == ".docx":
            stats["docx"] += 1
        elif f.suffix.lower() == ".md":
            stats["md"] += 1
    
    stats["total"] = stats["txt"] + stats["pdf"] + stats["docx"] + stats["md"]
    return stats
