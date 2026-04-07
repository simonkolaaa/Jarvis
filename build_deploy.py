"""
Jarvis-2 / Arus - Deployment Builder
Questo script crea un archivio ZIP contenente ESCLUSIVAMENTE 
i file necessari per far girare Arus su PythonAnywhere.
I file sensibili e il database di Linda vengono automaticamente esclusi.
"""
import os
import zipfile
from pathlib import Path

def build_deploy():
    base_dir = Path(__file__).parent
    deploy_filename = "deploy_arus.zip"
    deploy_path = base_dir / deploy_filename
    
    # File e directory autorizzati per il cloud
    allowed_files = [
        "api_server.py",
        "wsgi.py",
        "config.py",
        "requirements.txt",
    ]
    
    allowed_dirs = [
        "core",
        "databases/chroma_jarvis", # Solo il database RAG pubblico
        "web"
    ]

    print(f"📦 Avvio procedura di pacchettizzazione per PythonAnywhere...")
    
    with zipfile.ZipFile(deploy_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Aggiungi file singoli
        for f_name in allowed_files:
            file_path = base_dir / f_name
            if file_path.exists():
                zipf.write(file_path, arcname=f_name)
                print(f"  + Aggiunto: {f_name}")
            else:
                print(f"  ! Attenzione: {f_name} mancante.")

        # Aggiungi cartelle ricorsivamente
        for d_name in allowed_dirs:
            dir_path = base_dir / d_name
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    # Salta cartelle cache
                    if '__pycache__' in root:
                        continue
                        
                    for file in files:
                        full_path = Path(root) / file
                        # Calcola il path relativo per lo zip
                        rel_path = full_path.relative_to(base_dir)
                        zipf.write(full_path, arcname=str(rel_path))
                print(f"  + Aggiunta directory: {d_name}")
            else:
                print(f"  ! Attenzione: Directory {d_name} mancante.")

    print(f"\n✅ Build completata!")
    print(f"File protetto e pronto per l'upload: {deploy_filename}")
    print("\n--- ISTRUZIONI PYTHONANYWHERE ---")
    print("1. Nel pannello di PythonAnywhere vai su Files e ricarica il file zip dentro la tua app.")
    print("2. Usa l'apposita console per spacchettarlo (unzip deploy_arus.zip).")
    print("3. Crea a mano (o usa l'uploader) un file .env lì inserendo la tua GEMINI_API_KEY e MODE=online.")
    print("4. Installa i requirements dal terminale PA (pip install -r requirements.txt --user).")
    print("5. Aggiorna il file WSGI dal loro pannello 'Web' per caricare 'application' da wsgi.py")

if __name__ == "__main__":
    build_deploy()
