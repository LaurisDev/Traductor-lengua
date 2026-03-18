# camera_capture.py
# Captura de video desde camara web.
# Responsabilidad unica: abrir/cerrar camara y entregar frames.
# Paradigma: encapsulamiento del acceso a OpenCV.

import cv2
from typing import Optional, Tuple, List

from src.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

# Indices a probar si el por defecto falla (0 = primera camara, 1 = segunda, etc.)
CAMERA_INDICES_TO_TRY: List[int] = [0, 1, 2]


class CameraCapture:
    """
    Gestiona la captura de frames desde la camara.
    Encapsula OpenCV VideoCapture.
    Prueba varios indices de camara si el primero no entrega frames.
    """

    def __init__(
        self,
        camera_index: Optional[int] = None,
        width: int = FRAME_WIDTH,
        height: int = FRAME_HEIGHT
    ) -> None:
        self._camera_index = camera_index if camera_index is not None else CAMERA_INDEX
        self._width = width
        self._height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        """
        Abre la camara. Prueba indices 0, 1, 2 hasta que uno abra y devuelva al menos un frame.
        Retorna True si hay exito.
        """
        backend = getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY)
        indices = [self._camera_index] + [i for i in CAMERA_INDICES_TO_TRY if i != self._camera_index]
        for idx in indices:
            self._cap = cv2.VideoCapture(idx, backend)
            if not self._cap.isOpened():
                self._cap.release()
                self._cap = None
                continue
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            if self._read_test_frame():
                self._camera_index = idx
                return True
            self._cap.release()
            self._cap = None
        return False

    def _read_test_frame(self) -> bool:
        """Intenta leer un frame para comprobar que la camara entrega imagen."""
        if self._cap is None:
            return False
        for _ in range(5):
            ret, frame = self._cap.read()
            if ret and frame is not None:
                return True
        return False

    def read(self) -> Tuple[bool, Optional[any]]:
        """
        Lee un frame. Retorna (exito, frame).
        frame es numpy array BGR o None si falla.
        """
        if self._cap is None or not self._cap.isOpened():
            return False, None
        ret, frame = self._cap.read()
        if not ret or frame is None:
            return False, None
        return True, frame

    def release(self) -> None:
        """Libera el recurso de la camara."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def is_opened(self) -> bool:
        """Indica si la camara esta abierta."""
        return self._cap is not None and self._cap.isOpened()
