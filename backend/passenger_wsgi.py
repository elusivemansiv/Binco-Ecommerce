import os
import sys

# Force the server to look in the exact current directory
sys.path.insert(0, os.path.dirname(__file__))

from bincoecom.wsgi import application
