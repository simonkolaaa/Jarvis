import shutil
import os
from pathlib import Path

source_dir = Path(r"C:\Users\Utente\Desktop\Jarvis\Jarvis")
target_dir = Path(r"C:\Users\Utente\Desktop\portfolio-backend")

def copy_items():
    items = [
        ("core", "core"),
        ("databases", "databases"),
        ("config.py", "config.py"),
        (".env", ".env")
    ]
    
    for src_name, dst_name in items:
        src = source_dir / src_name
        dst = target_dir / dst_name
        
        try:
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"✅ Cartella {src_name} copiata in {target_dir}")
            elif src.is_file():
                shutil.copy2(src, dst)
                print(f"✅ File {src_name} copiato in {target_dir}")
        except Exception as e:
            print(f"❌ Errore in {src_name}: {e}")

if __name__ == "__main__":
    copy_items()
