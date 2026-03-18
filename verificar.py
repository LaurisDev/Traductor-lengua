# verificar.py
# Comprueba que las dependencias y modulos del proyecto esten listos.
# Ejecutar desde la raiz del proyecto: python verificar.py

import os
import sys

def main():
    errors = []
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    print("1. Comprobando Python...")
    if sys.version_info < (3, 8):
        errors.append("Se requiere Python 3.8 o superior.")
    else:
        print("   OK (Python {}.{}.{})".format(*sys.version_info[:3]))

    print("2. Comprobando dependencias...")
    deps = ["cv2", "mediapipe", "PIL"]
    for mod in deps:
        try:
            __import__(mod)
            print("   OK {}".format(mod))
        except ImportError as e:
            errors.append("Falta dependencia: {}. Ejecute: pip install -r requirements.txt".format(mod))

    print("3. Comprobando modulos del proyecto...")
    try:
        from src.database import DatabaseManager
        from src.auth import AuthService
        from src.config import APP_TITLE
        from src.gui import App
        from src.camera import CameraCapture
        from src.image_processing import HandDetector
        from src.sign_language import FingerAnalyzer, GestureClassifier
        print("   OK todos los modulos")
    except Exception as e:
        errors.append("Error al importar modulos: {}".format(e))

    print("4. Comprobando base de datos...")
    try:
        db = DatabaseManager()
        db.init_database()
        ok, msg = db.register_user("_verificar_", "temp123")
        print("   OK (tabla y escritura)")
    except Exception as e:
        errors.append("Error en base de datos: {}".format(e))

    print("")
    if errors:
        print("VERIFICACION FALLIDA:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    else:
        print("Verificacion OK. Puede ejecutar: python run.py")
        sys.exit(0)

if __name__ == "__main__":
    main()
