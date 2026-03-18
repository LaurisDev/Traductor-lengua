# hand_detector.py
# Deteccion de manos con MediaPipe (API Tasks).
# Compatible con mediapipe 0.10.x instalado desde PyPI.
# Descarga el modelo hand_landmarker.task si no existe.

import os
from typing import List, Optional, Tuple

import cv2

from src.config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

# URL del modelo oficial de MediaPipe (Hand Landmarker)
HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

_HandDetectorImpl = None
_import_error = None
_models_dir = None


# Tamano minimo esperado del modelo descargado (bytes). Evita archivos vacios o placeholders.
_MIN_MODEL_SIZE = 500_000


def _get_models_dir() -> str:
    """
    Ruta del directorio de modelos.
    En Windows usa LOCALAPPDATA para evitar problemas con OneDrive (archivos solo en la nube).
    """
    global _models_dir
    if _models_dir is None:
        if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
            _models_dir = os.path.join(os.environ["LOCALAPPDATA"], "TraductorSenas", "models")
        else:
            _models_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "models"
            )
    return _models_dir


def _download_model(path: str) -> None:
    """Descarga el modelo desde la URL oficial y lo guarda en path."""
    from urllib.request import urlopen, Request

    req = Request(HAND_LANDMARKER_MODEL_URL, headers={"User-Agent": "Python"})
    with urlopen(req, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        if total > 0 and total < _MIN_MODEL_SIZE:
            raise RuntimeError("El modelo remoto parece invalido (tamano muy pequeno).")
        data = resp.read()
    if len(data) < _MIN_MODEL_SIZE:
        raise RuntimeError(
            "El modelo descargado es demasiado pequeno ({} bytes). "
            "Compruebe su conexion.".format(len(data))
        )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def _get_model_path() -> str:
    """Ruta del archivo .task. Descarga el modelo si no existe o esta incompleto."""
    models_dir = _get_models_dir()
    path = os.path.join(models_dir, "hand_landmarker.task")
    if os.path.isfile(path):
        try:
            if os.path.getsize(path) >= _MIN_MODEL_SIZE:
                return path
        except OSError:
            pass
        try:
            os.remove(path)
        except OSError:
            pass
    try:
        _download_model(path)
    except Exception as e:
        raise RuntimeError(
            "No se pudo descargar el modelo de manos. Compruebe su conexion a internet y vuelva a intentar. "
            "Detalle: {}".format(e)
        ) from e
    return path


try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_tasks_python
    from mediapipe.tasks.python import vision as mp_vision

    def _create_detector():
        model_path = _get_model_path()
        base_options = mp_tasks_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            running_mode=mp_vision.RunningMode.VIDEO,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_TRACKING_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        return mp_vision.HandLandmarker.create_from_options(options)

    _HandDetectorImpl = _create_detector
except Exception as e:
    _import_error = e


class HandDetector:
    """
    Detecta manos en un frame y devuelve los 21 puntos de referencia (landmarks).
    Usa MediaPipe Tasks (HandLandmarker). Requiere mediapipe instalado.
    """

    def __init__(
        self,
        min_detection_confidence: float = MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence: float = MIN_TRACKING_CONFIDENCE,
        max_num_hands: int = 1,
    ) -> None:
        if _HandDetectorImpl is None:
            msg = "MediaPipe no se pudo cargar. Compruebe: pip install mediapipe"
            raise RuntimeError(msg) from _import_error
        self._landmarker = _HandDetectorImpl()
        self._frame_timestamp_ms = 0
        self._min_detection_confidence = min_detection_confidence
        self._min_tracking_confidence = min_tracking_confidence
        self._max_num_hands = max_num_hands

    def process(
        self, frame_bgr: any, timestamp_ms: Optional[int] = None
    ) -> Tuple[Optional[List], any]:
        """
        Procesa un frame BGR. Retorna (landmarks de la primera mano o None, frame).
        landmarks: lista de 21 dict con x, y, z normalizados (0-1).
        Para video en tiempo real, pasar timestamp_ms creciente (ej. contador * 33).
        """
        if frame_bgr is None:
            return None, None
        if timestamp_ms is None:
            self._frame_timestamp_ms += 33
            timestamp_ms = self._frame_timestamp_ms
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        try:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        except Exception:
            return None, frame_bgr
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        landmarks = None
        if result.hand_landmarks and len(result.hand_landmarks) > 0:
            hand_landmarks = result.hand_landmarks[0]
            landmarks = []
            for lm in hand_landmarks:
                landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z})
        return landmarks, frame_bgr

    def draw_landmarks(self, frame: any, landmarks: Optional[List]) -> any:
        """Dibuja los puntos de la mano sobre el frame (circulos en cada landmark)."""
        if frame is None or landmarks is None:
            return frame
        h, w = frame.shape[:2]
        for lm in landmarks:
            cx, cy = int(lm["x"] * w), int(lm["y"] * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        return frame

    def close(self) -> None:
        """Libera recursos."""
        if getattr(self, "_landmarker", None) is not None:
            try:
                self._landmarker.close()
            except Exception:
                pass
            self._landmarker = None
