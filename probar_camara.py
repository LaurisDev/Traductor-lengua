# probar_camara.py
# Prueba rapida de la camara sin abrir la aplicacion completa.
# Ejecutar desde la raiz: python probar_camara.py
# Si funciona, mostrara "Camara OK (indice X)" y capturara un frame de prueba.

import os
import sys

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    try:
        import cv2
    except ImportError:
        print("OpenCV no esta instalado. Ejecute: pip install opencv-python")
        sys.exit(1)

    backend = getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY)
    for idx in [0, 1, 2]:
        cap = cv2.VideoCapture(idx, backend)
        if not cap.isOpened():
            cap.release()
            continue
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Camara OK (indice {}). La app deberia usar esta camara.".format(idx))
            cap.release()
            sys.exit(0)
        cap.release()

    print("No se pudo acceder a ninguna camara. Compruebe:")
    print("  - Que la camara este conectada y habilitada en Windows.")
    print("  - Configuracion > Privacidad > Camara: permitir acceso a aplicaciones.")
    print("  - Cierre Chrome, Zoom, Teams o cualquier programa que use la camara.")
    sys.exit(1)

if __name__ == "__main__":
    main()
