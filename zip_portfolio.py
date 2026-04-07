import os
import zipfile
from pathlib import Path

source = Path(r"C:\Users\Utente\Desktop\portfolio-backend")
dest = Path(r"C:\Users\Utente\Desktop\Jarvis\Jarvis\update_backend.zip")

def create_zip():
    print(f"📦 Zipping {source.name} into {dest.name}...")
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in ('venv', 'node_modules', '.git', '__pycache__')]
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source)
                zipf.write(file_path, arcname)
    print("✅ OK.")

if __name__ == "__main__":
    create_zip()
