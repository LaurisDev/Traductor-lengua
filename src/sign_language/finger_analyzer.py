# finger_analyzer.py
# Analisis geometrico de la mano: estado de cada dedo (extendido/doblado).
# Responsabilidad unica: interpretar landmarks y devolver estado de dedos.
# Paradigma: reglas logicas, programacion imperativa.

from dataclasses import dataclass
from typing import List, Optional

# MediaPipe Hands: 21 landmarks
# 0: muneca, 1-4: pulgar, 5-8: indice, 9-12: medio, 13-16: anular, 17-20: menique
# Por dedo: base MCP, PIP, DIP, tip (indices varian por dedo)


@dataclass
class FingerState:
    """
    Estado de los cinco dedos: True = extendido, False = cerrado/doblado.
    thumb_position e index_bent permiten distinguir mas letras (A-Z).
    """
    thumb: bool
    index: bool
    middle: bool
    ring: bool
    pinky: bool
    thumb_position: str = "unknown"
    index_bent: bool = False
    two_finger_pose: str = ""   # "together_up"(U), "apart_up"(V), "horizontal"(H), "crossed"(R)

    def as_tuple(self) -> tuple:
        return (self.thumb, self.index, self.middle, self.ring, self.pinky)


class FingerAnalyzer:
    """
    Determina si cada dedo esta extendido o doblado a partir de los 21 landmarks.
    Criterio geometrico: comparar posicion de la punta con la base del dedo.
    En coordenadas normalizadas, y crece hacia abajo; dedo extendido hacia arriba
    implica punta con y menor que la base.
    """

    # Indices de landmarks (tip, base para cada dedo)
    # Pulgar: tip 4, base 2 (o 3); Indice: tip 8, base 5; Medio: tip 12, base 9;
    # Anular: tip 16, base 13; Menique: tip 20, base 17
    FINGER_TIPS = [4, 8, 12, 16, 20]
    FINGER_BASES = [2, 5, 9, 13, 17]

    def __init__(self, extension_threshold: float = 0.03) -> None:
        """
        extension_threshold: diferencia minima en y (normalizada) para considerar
        dedo extendido (tip.y < base.y - threshold para dedos 1-4; pulgar usa criterio x).
        """
        self._threshold = extension_threshold

    def analyze(self, landmarks: Optional[List]) -> Optional[FingerState]:
        """
        Analiza los landmarks y retorna el estado de cada dedo.
        Incluye thumb_position e index_bent para distinguir todas las letras A-Z.
        Retorna None si no hay 21 landmarks.
        """
        if landmarks is None or len(landmarks) < 21:
            return None

        thumb = self._is_thumb_extended(landmarks)
        index = self._is_finger_extended(landmarks, 1)
        middle = self._is_finger_extended(landmarks, 2)
        ring = self._is_finger_extended(landmarks, 3)
        pinky = self._is_finger_extended(landmarks, 4)

        thumb_pos = self._thumb_position(landmarks, thumb)
        idx_bent = self._is_index_bent(landmarks)
        two_pose = self._two_finger_pose(landmarks, index, middle) if (index and middle) else ""

        return FingerState(
            thumb=thumb, index=index, middle=middle, ring=ring, pinky=pinky,
            thumb_position=thumb_pos, index_bent=idx_bent, two_finger_pose=two_pose
        )

    def _thumb_position(self, lm: List, thumb_extended: bool) -> str:
        """Pulgar: side (A), inside (E,M,N,S), between (T), touch_index (O,F,Q), extended_up (L), extended_side (G)."""
        t4 = lm[4]
        i5 = lm[5]
        i8 = lm[8]
        m12 = lm[12]
        w0 = lm[0]
        if thumb_extended:
            if abs(t4["x"] - i8["x"]) < 0.08 and abs(t4["y"] - i8["y"]) < 0.08:
                return "touch_index"
            if (i8["x"] - 0.02 <= t4["x"] <= m12["x"] + 0.02) or (m12["x"] - 0.02 <= t4["x"] <= i8["x"] + 0.02):
                return "between"
            if t4["y"] < w0["y"] - 0.02:
                return "extended_up"
            return "extended_side"
        if abs(t4["x"] - i5["x"]) > 0.12:
            return "side"
        i9 = lm[9]
        r13 = lm[13]
        if t4["y"] > w0["y"] - 0.05 or t4["x"] > w0["x"] - 0.02:
            if t4["y"] < w0["y"] - 0.04:
                return "inside_top"
            if t4.get("z", 0) < w0.get("z", 0) - 0.015:
                return "inside_front"
            if i5["x"] <= t4["x"] <= i9["x"] or i9["x"] <= t4["x"] <= i5["x"]:
                return "inside_over2"
            if i9["x"] <= t4["x"] <= r13["x"] or r13["x"] <= t4["x"] <= i9["x"]:
                return "inside_over3"
            return "inside_front"
        return "unknown"

    def _two_finger_pose(self, lm: List, index_ext: bool, middle_ext: bool) -> str:
        """Cuando indice y medio extendidos: together_up (U), apart_up (V), horizontal (H), crossed (R)."""
        if not index_ext or not middle_ext:
            return ""
        i5, i8 = lm[5], lm[8]
        m9, m12 = lm[9], lm[12]
        dx = i8["x"] - m12["x"]
        dy = i8["y"] - m12["y"]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 0.035 and (i8["x"] - m9["x"]) * (m12["x"] - i5["x"]) > 0.01:
            return "crossed"
        if dist < 0.06:
            iy = (i8["y"] + m12["y"]) / 2
            by = (i5["y"] + m9["y"]) / 2
            if iy < by - 0.02:
                return "together_up"
            return "horizontal"
        if dist > 0.08:
            return "apart_up"
        return "together_up"

    def _is_index_bent(self, lm: List) -> bool:
        """Indice doblado (X) vs recto (D): punta por debajo del PIP."""
        tip_y = lm[8]["y"]
        pip_y = lm[6]["y"]
        return tip_y > pip_y + self._threshold

    def _is_finger_extended(self, lm: List, finger_index: int) -> bool:
        """Dedo extendido si la punta esta por encima (y menor) que la base."""
        tip_idx = self.FINGER_TIPS[finger_index]
        base_idx = self.FINGER_BASES[finger_index]
        tip_y = lm[tip_idx]["y"]
        base_y = lm[base_idx]["y"]
        return tip_y < base_y - self._threshold

    def _is_thumb_extended(self, lm: List) -> bool:
        """Pulgar: criterio en x (abierto hacia afuera respecto a la mano)."""
        tip_x = lm[4]["x"]
        base_x = lm[2]["x"]
        # Si la mano es derecha, pulgar extendido suele tener tip_x menor que base
        # Usamos distancia en x para evitar dependencia de mano izq/der
        return abs(tip_x - base_x) > self._threshold
