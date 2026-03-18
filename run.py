# run.py
# Punto de entrada del proyecto. Ejecutar desde la raiz del proyecto:
#   python run.py

import os
import sys

# Raiz del proyecto (donde esta run.py)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.main import main

if __name__ == "__main__":
    main()
