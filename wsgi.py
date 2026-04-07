"""
Jarvis-2 WSGI Entry Point (Per PythonAnywhere)

PythonAnywhere cerca l'oggetto 'application' all'interno di questo file per 
eseguire correttamente il bind sul server Cloud.
"""
import sys
import os

# Aggiungi il percorso corrente alle variabili d'ambiente per importare correttamente modules
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Importa l'app Flask da api_server e nominala "application" come atteso dai server WSGI standard
from api_server import app as application

# Esempio d'uso su PythonAnywhere - File /var/www/iltuousername_pythonanywhere_com_wsgi.py:
# import sys
# path = '/home/iltuousername/Jarvis'
# if path not in sys.path:
#    sys.path.append(path)
# from wsgi import application
