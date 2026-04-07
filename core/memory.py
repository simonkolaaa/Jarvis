"""
Jarvis-2 - Memory Module Unificato
Gestisce i sistemi RAG paralleli per gli Agenti, instanziando vettori separati 
su cartelle differenti.
"""
from pathlib import Path
from typing import Optional, List

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

import config


def load_documents_from_paths(paths: List[Path]) -> list:
    """
    Carica i file supportati da una lista di cartelle.
    """
    documents = []
    
    for folder in paths:
        if not folder.exists():
            print(f"📁 Cartella {folder} inesistente. Salto...")
            continue
            
        supported_files = []
        for ext in ["*.txt", "*.pdf", "*.docx", "*.md"]:
            supported_files.extend(folder.glob(ext))
            
        for file_path in supported_files:
            try:
                suffix = file_path.suffix.lower()
                if suffix in [".txt", ".md"]:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                elif suffix == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                elif suffix == ".docx":
                    loader = Docx2txtLoader(str(file_path))
                else:
                    continue
                
                docs = loader.load()
                documents.extend(docs)
                print(f"   ✅ Caricato {file_path.name}")
            except Exception as e:
                print(f"   ⚠️ Errore {file_path.name}: {e}")
                
    return documents


def split_documents(documents: list) -> list:
    if not documents:
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
    )
    return splitter.split_documents(documents)


def get_embeddings():
    return OllamaEmbeddings(model=config.EMBEDDING_MODEL)


def get_vectorstore(persist_dir: Path, chunks: list = None) -> Optional[Chroma]:
    """
    Carica (o crea se forniti i chunks) un database Chroma specifico.
    """
    embeddings = get_embeddings()
    str_persist_dir = str(persist_dir)
    
    if chunks:
        # Crea/sovrascrive
        print(f"🧠 Ricreazione indice vettoriale in {persist_dir.name}...")
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=str_persist_dir,
                collection_name="rag_memory",
            )
            return vectorstore
        except Exception as e:
            print(f"❌ Errore ChromaDB: {e}")
            return None
            
    # Prova a caricare l'esistente
    if persist_dir.exists() and any(persist_dir.iterdir()):
        try:
            return Chroma(
                persist_directory=str_persist_dir,
                embedding_function=embeddings,
                collection_name="rag_memory",
            )
        except Exception:
            pass
            
    return None


def get_relevant_context(query: str, vectorstore: Chroma, top_k: int = 4) -> str:
    """Ricerca contestuale sui vettori passati."""
    if vectorstore is None:
        return ""
    
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)
        if not docs:
            return ""
            
        parts = [f"[- {Path(d.metadata.get('source', '')).name}]\n{d.page_content}" for d in docs]
        return "\n\n".join(parts)
    except Exception as e:
        print(f"⚠️ Errore retriever: {e}")
        return ""


def rebuild_agent_memory(agent_name: str) -> Optional[Chroma]:
    """
    Helper ad alto livello per ricostruire da zero l'indice di Jarvis, Linda o Arus.
    Arus usa lo stesso DB di Jarvis (Pubblico).
    """
    if agent_name.lower() == "linda":
        db_path = config.CHROMA_LINDA_DIR
        # Linda legge sia i dati pubblici, sia privati, sia eventuali extra
        target_dirs = [config.DATA_PUBLIC_DIR, config.DATA_PRIVATE_DIR]
        if config.SCUOLA_PATH:
            target_dirs.append(Path(config.SCUOLA_PATH))
        for extra in config.LINDA_EXTRA_PATHS:
            target_dirs.append(Path(extra))
    else:
        # Jarvis legacy e Arus
        db_path = config.CHROMA_JARVIS_DIR
        target_dirs = [config.DATA_PUBLIC_DIR]
        if config.SCUOLA_PATH:
            target_dirs.append(Path(config.SCUOLA_PATH))

    print(f"\n🔄 (Ri)costruzione memoria per [{agent_name.upper()}] in corso...")
    docs = load_documents_from_paths(target_dirs)
    if not docs:
        print("⚠️ Nessun documento trovato nelle cartelle assegnate.")
        return None
        
    chunks = split_documents(docs)
    vs = get_vectorstore(db_path, chunks)
    if vs:
        print("✨ Indice completato con successo!")
    return vs
