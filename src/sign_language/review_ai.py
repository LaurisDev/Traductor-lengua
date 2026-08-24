# review_ai.py
# Asistente de retroalimentacion inteligente para el modo REPASO.
#
# Este modulo NO reimplementa MediaPipe ni el clasificador de senas: solo
# interpreta la informacion que el proyecto ya calcula en cada frame
# (letra objetivo, letra detectada, confianza, FingerState de
# `finger_analyzer.py` y/o el vector de features de `feature_extractor.py`)
# para explicarle al usuario, en lenguaje natural, que esta fallando en su
# seña y como corregirla.
#
# Uso tipico (dentro del backend, por ejemplo en main.py):
#
#   from src.sign_language.review_ai import ReviewAI
#
#   review_ai = ReviewAI()
#   feedback = review_ai.analyze(
#       target_letter="V",
#       detected_letter="U",
#       confidence=0.81,
#       finger_state=finger_state,          # FingerState ya calculado por FingerAnalyzer
#       features=extract_features(landmarks),  # opcional, vector/():dict de feature_extractor
#       landmarks=landmarks,                # opcional, para revisar encuadre
#   )
#   feedback.as_dict()
#   # {
#   #   "correct": False,
#   #   "category": "dedos",
#   #   "title": "Confusion V / U",
#   #   "message": "Estas formando una U. Separa un poco mas los dedos indice
#   #                y medio para formar la V.",
#   #   "tip": "...",
#   #   "target_letter": "V",
#   #   "detected_letter": "U",
#   #   ...
#   # }

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from .feature_extractor import features_to_dict

# ---------------------------------------------------------------------------
# Utilidades genericas para leer datos que pueden llegar como FingerState
# (dataclass), dict o None, sin acoplarse a un tipo concreto.
# ---------------------------------------------------------------------------


def _get(obj: Any, name: str, default: Any = None) -> Any:
    """Lee un atributo tanto de un dataclass (FingerState) como de un dict."""
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


FINGER_KEYS: Tuple[str, ...] = ("thumb", "index", "middle", "ring", "pinky")

FINGER_NAMES_ES: Dict[str, str] = {
    "thumb": "pulgar",
    "index": "índice",
    "middle": "medio",
    "ring": "anular",
    "pinky": "meñique",
}


def _finger_pattern(finger_state: Any) -> Optional[Tuple[bool, bool, bool, bool, bool]]:
    """Extrae (thumb, index, middle, ring, pinky) de un FingerState o dict."""
    if finger_state is None:
        return None
    values = [_get(finger_state, key) for key in FINGER_KEYS]
    if any(v is None for v in values):
        return None
    return tuple(bool(v) for v in values)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Categorias de retroalimentacion
# ---------------------------------------------------------------------------

CATEGORY_FINGERS = "dedos"
CATEGORY_ORIENTATION = "orientacion"
CATEGORY_POSITION = "posicion_general"
CATEGORY_CORRECT = "correcto"


@dataclass(frozen=True)
class ReviewFeedback:
    """Resultado estructurado del analisis de un intento en modo Repaso."""

    correct: bool
    category: str
    title: str
    message: str
    tip: str
    target_letter: str
    detected_letter: Optional[str]
    confidence: Optional[float] = None
    confusion_pair: bool = False
    details: Tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict:
        return {
            "correct": self.correct,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "tip": self.tip,
            "target_letter": self.target_letter,
            "detected_letter": self.detected_letter,
            "confidence": self.confidence,
            "confusion_pair": self.confusion_pair,
            "details": list(self.details),
        }


# ---------------------------------------------------------------------------
# Base de conocimiento: confusiones frecuentes ya reflejadas en los
# desempates de src/sign_language/sign_classifier.py (_apply_tiebreakers).
# Se reutilizan los MISMOS grupos que el clasificador ya trata como
# "letras parecidas" para no inventar reglas nuevas de reconocimiento.
# ---------------------------------------------------------------------------

CONFUSABLE_GROUPS: Tuple[frozenset, ...] = (
    frozenset({"U", "V"}),
    frozenset({"B", "K"}),
    frozenset({"M", "N"}),
    frozenset({"A", "S", "E", "T"}),
    frozenset({"C", "D", "F", "G", "O"}),
)

# Como formar cada letra (breve), usado tanto para mensajes de confusion
# como de tip general cuando no hay una confusion conocida.
LETTER_HINTS: Dict[str, str] = {
    "A": "Cierra el puño y apoya el pulgar en el costado, sin cruzarlo sobre los dedos.",
    "B": "Estira los cuatro dedos juntos hacia arriba y dobla el pulgar cruzándolo por la palma.",
    "C": "Curva todos los dedos y el pulgar juntos, formando una C abierta.",
    "D": "Levanta solo el índice recto y une la punta del pulgar con el medio y el anular.",
    "E": "Dobla los cuatro dedos hacia la palma dejando el pulgar apoyado por delante.",
    "F": "Une la punta del pulgar con la del índice y estira medio, anular y meñique.",
    "G": "Estira el índice y el pulgar en horizontal, apuntando hacia el costado.",
    "H": "Estira índice y medio juntos y colócalos en horizontal, apuntando hacia el costado.",
    "I": "Levanta solo el meñique y mantén los demás dedos doblados.",
    "J": "Parte de la forma de la I y realiza el movimiento curvo de la J con el meñique.",
    "K": "Levanta índice y medio separados en V, apoyando el pulgar entre ambos.",
    "L": "Estira el pulgar y el índice formando una L, con los otros dedos doblados.",
    "M": "Cierra el puño y mete el pulgar bajo los tres primeros dedos (índice, medio y anular).",
    "N": "Cierra el puño y mete el pulgar bajo los dos primeros dedos (índice y medio).",
    "O": "Une las puntas de todos los dedos con el pulgar formando un círculo cerrado.",
    "P": "Coloca índice y medio con el pulgar entre ellos y orienta la mano hacia abajo.",
    "Q": "Estira pulgar e índice y orienta la mano hacia abajo.",
    "R": "Estira índice y medio y crúzalos entre sí.",
    "S": "Cierra el puño y cruza el pulgar por delante, cubriendo los dedos.",
    "T": "Cierra los dedos y mete el pulgar entre el índice y el medio.",
    "U": "Levanta índice y medio juntos, bien pegados entre sí.",
    "V": "Levanta índice y medio separados, formando una V clara.",
    "W": "Levanta índice, medio y anular; deja el meñique doblado.",
    "X": "Levanta solo el índice y dóblalo en forma de gancho.",
    "Y": "Estira el pulgar y el meñique, manteniendo los otros dedos doblados.",
    "Z": "Levanta el índice y realiza el movimiento de zigzag de la Z.",
}

GROUP_GENERIC_TIP = (
    "Compara con calma la forma de tus dedos contra la imagen de referencia; "
    "estas letras se confunden fácilmente si los dedos no quedan bien marcados."
)

# ---------------------------------------------------------------------------
# Patron de dedos esperado (extendido/flexionado) por letra. Es un patron
# heuristico -- se usa solo para explicar diferencias al usuario, nunca para
# clasificar (eso lo sigue haciendo SignClassifier). Cubre las letras cuyo
# patron de dedos es lo bastante inequivoco como para dar una explicacion
# util; para el resto se recurre al analisis de orientacion/posicion o a un
# mensaje generico.
# ---------------------------------------------------------------------------

LetterPattern = Tuple[bool, bool, bool, bool, bool]  # thumb,index,middle,ring,pinky

LETTER_EXPECTED_FINGERS: Dict[str, LetterPattern] = {
    "A": (False, False, False, False, False),
    "B": (False, True, True, True, True),
    "D": (False, True, False, False, False),
    "F": (False, False, True, True, True),
    "G": (True, True, False, False, False),
    "I": (False, False, False, False, True),
    "K": (True, True, True, False, False),
    "L": (True, True, False, False, False),
    "M": (False, False, False, False, False),
    "N": (False, False, False, False, False),
    "O": (False, False, False, False, False),
    "S": (False, False, False, False, False),
    "T": (False, False, False, False, False),
    "U": (False, True, True, False, False),
    "V": (False, True, True, False, False),
    "W": (False, True, True, True, False),
    "Y": (True, False, False, False, True),
}

# Letras cuya forma habitual requiere mostrar la palma de lado (no de frente
# a la camara). Se usa unicamente para avisos de orientacion, sin bloquear
# ninguna otra logica.
LATERAL_LETTERS = {"G", "Q", "H"}


# ---------------------------------------------------------------------------
# ReviewAI: motor de analisis
# ---------------------------------------------------------------------------


class ReviewAI:
    """
    Analiza un intento confirmado del modo Repaso y devuelve retroalimentacion
    estructurada y accionable, sin depender de la interfaz ni de la base de
    datos (igual que LearningPerformanceAnalyzer).
    """

    def analyze(
        self,
        target_letter: str,
        detected_letter: Optional[str],
        confidence: Optional[float] = None,
        finger_state: Any = None,
        features: Any = None,
        landmarks: Optional[Sequence[Any]] = None,
    ) -> ReviewFeedback:
        target = (target_letter or "").strip().upper()
        detected = (detected_letter or "").strip().upper() or None

        feat = self._normalize_features(features)

        # 1) Sin deteccion clara: no hay seña que analizar.
        if detected is None:
            return self._no_detection_feedback(target, confidence)

        # 2) Acierto.
        if detected == target:
            return self._correct_feedback(target, confidence)

        # 3) Confusion conocida entre letras (misma familia que el clasificador
        #    ya trata como ambiguas en sus desempates).
        confusion = self._match_known_confusion(target, detected, finger_state, feat)
        if confusion is not None:
            return confusion

        # 4) Diferencia de patron de dedos (posicion/forma) contra la letra
        #    objetivo, usando el FingerState ya calculado por FingerAnalyzer.
        finger_feedback = self._finger_pattern_feedback(
            target, detected, confidence, finger_state
        )
        if finger_feedback is not None:
            return finger_feedback

        # 5) Orientacion de la mano/palma.
        orientation_feedback = self._orientation_feedback(
            target, detected, confidence, finger_state
        )
        if orientation_feedback is not None:
            return orientation_feedback

        # 6) Posicion general de la mano en el encuadre (usa landmarks y/o
        #    features de compacidad si estan disponibles).
        position_feedback = self._general_position_feedback(
            target, detected, confidence, finger_state, feat, landmarks
        )
        if position_feedback is not None:
            return position_feedback

        # 7) Fallback generico: no se pudo aislar una causa especifica.
        return self._generic_feedback(target, detected, confidence)

    def analyze_attempts(self, attempts: Sequence[Mapping[str, Any]]) -> ReviewFeedback:
        """Compara intentos confirmados de Repaso y destaca el error repetido.

        Cada intento se analiza primero con :meth:`analyze`, por lo que este
        metodo conserva las mismas reglas de dedos, orientacion, posicion y
        confusiones del analisis individual. No clasifica ni calcula features
        nuevos; solo encuentra el diagnostico que mas se repite.
        """
        analyzed: List[ReviewFeedback] = []
        for attempt in attempts:
            if not isinstance(attempt, Mapping):
                continue
            analyzed.append(
                self.analyze(
                    target_letter=str(attempt.get("target_letter", "")),
                    detected_letter=attempt.get("detected_letter"),
                    confidence=attempt.get("confidence"),
                    finger_state=attempt.get("finger_state"),
                    features=attempt.get("features"),
                    landmarks=attempt.get("landmarks"),
                )
            )

        if not analyzed:
            return self._comparative_generic_feedback("", None, None, 0)

        # Los aciertos no son errores a priorizar. Si todos fueron correctos,
        # se conserva el feedback positivo del ultimo intento.
        incorrect = [feedback for feedback in analyzed if not feedback.correct]
        if not incorrect:
            return self._with_comparison_details(analyzed[-1], len(analyzed), "correcto")

        groups: Dict[Tuple[str, str], List[ReviewFeedback]] = {}
        for feedback in incorrect:
            error_key = self._comparison_error_key(feedback)
            if error_key is None:
                continue
            groups.setdefault(error_key, []).append(feedback)

        if groups:
            repeated_key, repeated_feedback = max(
                groups.items(), key=lambda item: len(item[1])
            )
            # Un solo caso no demuestra un patron: evita atribuir una causa
            # especifica cuando los cinco errores fueron distintos.
            if len(repeated_feedback) >= 2:
                return self._with_comparison_details(
                    repeated_feedback[-1], len(analyzed), repeated_key[1]
                )

        last = incorrect[-1]
        return self._comparative_generic_feedback(
            last.target_letter,
            last.detected_letter,
            last.confidence,
            len(analyzed),
        )

    @staticmethod
    def _comparison_error_key(feedback: ReviewFeedback) -> Optional[Tuple[str, str]]:
        """Devuelve una clave de causa ya diagnosticada por el analisis base."""
        if feedback.confusion_pair:
            return ("confusion", f"{feedback.detected_letter}/{feedback.target_letter}")

        if feedback.category == CATEGORY_FINGERS:
            # Los detalles de _finger_pattern_feedback contienen la primera
            # diferencia concreta, por ejemplo ``index: deberia ...``.
            for detail in feedback.details:
                if ": deberia" in detail:
                    return ("dedo", detail.split(":", 1)[0])
            return None

        if feedback.category == CATEGORY_ORIENTATION:
            for detail in feedback.details:
                if detail.startswith("palm_orientation="):
                    return ("orientacion", detail)
            return None

        if feedback.category == CATEGORY_POSITION:
            for detail in feedback.details:
                if detail == "hand_near_frame_edge":
                    return ("posicion", detail)
                if detail.startswith("fist_compactness="):
                    return ("posicion", feedback.title)
        return None

    @staticmethod
    def _with_comparison_details(
        feedback: ReviewFeedback, attempts_analyzed: int, repeated_error: str
    ) -> ReviewFeedback:
        return ReviewFeedback(
            correct=feedback.correct,
            category=feedback.category,
            title=feedback.title,
            message=feedback.message,
            tip=feedback.tip,
            target_letter=feedback.target_letter,
            detected_letter=feedback.detected_letter,
            confidence=feedback.confidence,
            confusion_pair=feedback.confusion_pair,
            details=feedback.details + (
                f"attempts_analyzed={attempts_analyzed}",
                f"repeated_error={repeated_error}",
            ),
        )

    @staticmethod
    def _comparative_generic_feedback(
        target: str,
        detected: Optional[str],
        confidence: Optional[float],
        attempts_analyzed: int,
    ) -> ReviewFeedback:
        hint = LETTER_HINTS.get(target)
        message = (
            "Los intentos no muestran un mismo problema con suficiente "
            "claridad para señalar una causa específica."
        )
        tip = "Compara tu mano con la imagen de referencia y vuelve a intentarlo."
        if hint:
            message += f" Como referencia para la letra {target}: {hint}"
            tip = f"Para la letra {target}, {hint}"

        return ReviewFeedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title="No encontré un error único que se repita",
            message=message,
            tip=tip,
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
            details=(
                f"attempts_analyzed={attempts_analyzed}",
                "repeated_error=none",
            ),
        )

    # ------------------------------------------------------------------
    # Casos base
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_features(features: Any) -> Dict[str, float]:
        if features is None:
            return {}
        if isinstance(features, Mapping):
            return dict(features)
        try:
            return features_to_dict(features)
        except Exception:
            return {}

    @staticmethod
    def _no_detection_feedback(target: str, confidence: Optional[float]) -> ReviewFeedback:
        return ReviewFeedback(
            correct=False,
            category=CATEGORY_POSITION,
            title="No pude analizar completamente tu mano",
            message="No pude analizar completamente tu mano. Intenta colocarla frente a la cámara.",
            tip="Centra tu mano en el encuadre, con buena luz y sin objetos detrás.",
            target_letter=target,
            detected_letter=None,
            confidence=confidence,
        )

    @staticmethod
    def _correct_feedback(target: str, confidence: Optional[float]) -> ReviewFeedback:
        extra = ""
        if confidence is not None and confidence < 0.7:
            extra = " Aun asi, intenta mantener la seña un poco mas firme para que se reconozca con mayor seguridad."
        return ReviewFeedback(
            correct=True,
            category=CATEGORY_CORRECT,
            title="¡Buen trabajo!",
            message=f"¡Buen trabajo! Formaste correctamente la letra {target}.{extra}",
            tip="Sigue así. Puedes continuar con la siguiente letra.",
            target_letter=target,
            detected_letter=target,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Confusiones conocidas
    # ------------------------------------------------------------------

    def _match_known_confusion(
        self,
        target: str,
        detected: str,
        finger_state: Any = None,
        features: Optional[Mapping[str, float]] = None,
    ) -> Optional[ReviewFeedback]:
        for group in CONFUSABLE_GROUPS:
            if target in group and detected in group:
                explanation = self._known_confusion_explanation(
                    target, detected, finger_state, features or {}
                )
                if explanation is not None:
                    message, tip, detail = explanation
                else:
                    # La letra detectada por si sola no demuestra que rasgo
                    # geometrico esta fallando. No se inventa una causa.
                    message = (
                        f"Estás formando una {detected}, pero no tengo datos "
                        "suficientes para confirmar qué diferencia exacta de "
                        "la mano está causando la confusión."
                    )
                    target_hint = LETTER_HINTS.get(target)
                    if target_hint:
                        message += f" Como referencia para la {target}: {target_hint}"
                        tip = f"Para la {target}, {target_hint}"
                    else:
                        tip = "Compara tu mano con la imagen de referencia y ajusta la forma."
                    detail = "confusion_difference=not_available"
                return ReviewFeedback(
                    correct=False,
                    category=CATEGORY_FINGERS,
                    title=f"Confusión {detected} / {target}",
                    message=message,
                    tip=tip,
                    target_letter=target,
                    detected_letter=detected,
                    confusion_pair=True,
                    details=(f"grupo_confusion={'/'.join(sorted(group))}", detail),
                )
        return None

    @staticmethod
    def _known_confusion_explanation(
        target: str,
        detected: str,
        finger_state: Any,
        features: Mapping[str, float],
    ) -> Optional[Tuple[str, str, str]]:
        """Explica solo diferencias que los rasgos actuales pueden comprobar.

        Estas condiciones reflejan los desempates de ``sign_classifier.py``;
        no participan en la clasificacion ni introducen reglas nuevas.
        """
        two_finger_pose = _get(finger_state, "two_finger_pose")
        thumb_between = _get(finger_state, "thumb_between")
        four_fingers_up = _get(finger_state, "four_fingers_up")
        ring = _get(finger_state, "ring")
        pinky = _get(finger_state, "pinky")
        thumb_cover_count = _get(finger_state, "thumb_cover_count")

        separation = features.get("index_middle_sep")
        try:
            separation = float(separation) if separation is not None else None
        except (TypeError, ValueError):
            separation = None

        # U/V: el clasificador usa ``index_middle_sep`` y el analizador ya
        # expone su equivalente discreto en ``two_finger_pose``.
        fingers_together = two_finger_pose == "together_up" or (
            separation is not None and separation < 0.22
        )
        fingers_apart = two_finger_pose == "apart_up" or (
            separation is not None and separation > 0.32
        )
        if target == "V" and detected == "U" and fingers_together:
            return (
                "Estás formando una U: el índice y el medio están demasiado juntos.",
                "Separa un poco más los dedos índice y medio para formar una V.",
                "confusion_difference=index_middle_together",
            )
        if target == "U" and detected == "V" and fingers_apart:
            return (
                "Estás formando una V: el índice y el medio están demasiado separados.",
                "Junta un poco más los dedos índice y medio para formar una U.",
                "confusion_difference=index_middle_apart",
            )

        # B/K: el desempate existente revisa cuatro dedos extendidos y la
        # posicion del pulgar entre indice y medio.
        if target == "B" and detected == "K":
            if thumb_between is True:
                return (
                    "Estás formando una K: el pulgar está entre el índice y el medio.",
                    "Para formar la B, coloca el pulgar cruzado sobre la palma.",
                    "confusion_difference=thumb_between",
                )
            if ring is False or pinky is False:
                return (
                    "Para la B, el anular y el meñique también deben quedar extendidos.",
                    "Estira los cuatro dedos y mantenlos juntos hacia arriba.",
                    "confusion_difference=four_fingers_up",
                )
        if target == "K" and detected == "B":
            if four_fingers_up is True:
                return (
                    "Estás formando una B: tienes los cuatro dedos extendidos.",
                    "Para formar la K, dobla el anular y el meñique.",
                    "confusion_difference=four_fingers_up",
                )
            if thumb_between is False:
                return (
                    "El pulgar no está en la posición que usa la K.",
                    "Coloca el pulgar entre el índice y el medio.",
                    "confusion_difference=thumb_not_between",
                )

        # M/N: el clasificador compara cuántos dedos cubre el pulgar.
        if target == "M" and detected == "N" and isinstance(thumb_cover_count, int) and thumb_cover_count < 3:
            return (
                "El pulgar no está cubriendo suficientes dedos para formar la M.",
                "Mételo bajo índice, medio y anular.",
                "confusion_difference=thumb_cover_count_low",
            )
        if target == "N" and detected == "M" and isinstance(thumb_cover_count, int) and thumb_cover_count >= 3:
            return (
                "El pulgar está cubriendo demasiados dedos para formar la N.",
                "Déjalo bajo el índice y el medio, sin cubrir el anular.",
                "confusion_difference=thumb_cover_count_high",
            )

        # T/S: el clasificador distingue T por el pulgar entre los dedos.
        if target == "T" and detected == "S" and thumb_between is False:
            return (
                "El pulgar no está entre el índice y el medio, como requiere la T.",
                "Mete el pulgar entre el índice y el medio.",
                "confusion_difference=thumb_not_between",
            )
        if target == "S" and detected == "T" and thumb_between is True:
            return (
                "El pulgar está entre el índice y el medio, una característica de la T.",
                "Para la S, cruza el pulgar por delante de los dedos.",
                "confusion_difference=thumb_between",
            )

        return None

    # ------------------------------------------------------------------
    # Posicion / forma de los dedos
    # ------------------------------------------------------------------

    def _finger_pattern_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
    ) -> Optional[ReviewFeedback]:
        expected = LETTER_EXPECTED_FINGERS.get(target)
        current = _finger_pattern(finger_state)
        if expected is None or current is None:
            return None

        mismatches: List[str] = []
        detail_list: List[str] = []
        for key, expected_val, actual_val in zip(FINGER_KEYS, expected, current):
            if expected_val == actual_val:
                continue
            name_es = FINGER_NAMES_ES[key]
            if expected_val and not actual_val:
                if key == "index" and _get(finger_state, "index_bent"):
                    mismatches.append(f"Tu dedo {name_es} está demasiado doblado.")
                else:
                    mismatches.append(f"Tu dedo {name_es} no está lo suficientemente extendido.")
                detail_list.append(f"{key}: deberia estar extendido")
            else:
                mismatches.append(f"Tu dedo {name_es} debería estar doblado hacia la palma.")
                detail_list.append(f"{key}: deberia estar flexionado")

        if not mismatches:
            return None

        message = mismatches[0]
        if len(mismatches) > 1:
            message += " " + mismatches[1]

        tip_finger_key = None
        for key, expected_val, actual_val in zip(FINGER_KEYS, expected, current):
            if expected_val != actual_val:
                tip_finger_key = key
                break
        if tip_finger_key:
            tip = f"Intenta {'estirarlo' if expected[FINGER_KEYS.index(tip_finger_key)] else 'doblarlo'} y mantenerlo más {'recto' if expected[FINGER_KEYS.index(tip_finger_key)] else 'cerrado'}."
        else:
            tip = "Ajusta la posición de los dedos comparando con la imagen de referencia."

        return ReviewFeedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title="Revisa tus dedos",
            message=message,
            tip=tip,
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
            details=tuple(detail_list),
        )

    # ------------------------------------------------------------------
    # Orientacion de la mano
    # ------------------------------------------------------------------

    def _orientation_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
    ) -> Optional[ReviewFeedback]:
        palm_orientation = _get(finger_state, "palm_orientation")
        if palm_orientation is None:
            return None

        expects_lateral = target in LATERAL_LETTERS

        if palm_orientation == "down" and not expects_lateral:
            return ReviewFeedback(
                correct=False,
                category=CATEGORY_ORIENTATION,
                title="Orienta la palma hacia la cámara",
                message="Tu palma está apuntando hacia abajo y esa letra se hace mostrando la palma de frente.",
                tip="Gira la muñeca para que la cámara vea la palma de tu mano.",
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("palm_orientation=down",),
            )

        if palm_orientation == "lateral" and not expects_lateral:
            return ReviewFeedback(
                correct=False,
                category=CATEGORY_ORIENTATION,
                title="Gira la mano hacia la cámara",
                message="Tu mano está de lado y esa letra requiere mostrar la palma frontal.",
                tip="Rota la muñeca hasta que la palma quede de frente a la cámara.",
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("palm_orientation=lateral",),
            )

        if palm_orientation == "frontal" and expects_lateral:
            return ReviewFeedback(
                correct=False,
                category=CATEGORY_ORIENTATION,
                title="Gira la mano de lado",
                message="Esa letra se forma con la mano de perfil, no con la palma de frente.",
                tip="Gira la muñeca para mostrar el canto de la mano hacia la cámara.",
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("palm_orientation=frontal",),
            )

        return None

    # ------------------------------------------------------------------
    # Posicion general de la mano (encuadre / cercania a la camara)
    # ------------------------------------------------------------------

    def _general_position_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
        features: Dict[str, float],
        landmarks: Optional[Sequence[Any]],
    ) -> Optional[ReviewFeedback]:
        bbox_warning = self._frame_edge_warning(landmarks)
        if bbox_warning is not None:
            return ReviewFeedback(
                correct=False,
                category=CATEGORY_POSITION,
                title="Centra tu mano en la cámara",
                message=bbox_warning,
                tip="Ubica tu mano en el centro del cuadro, a una distancia similar a la de la imagen de referencia.",
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("hand_near_frame_edge",),
            )

        fist_compact = features.get("fist_compactness") if features else None
        if fist_compact is not None:
            if fist_compact < 0.55:
                return ReviewFeedback(
                    correct=False,
                    category=CATEGORY_POSITION,
                    title="Acerca un poco la mano",
                    message="Tu mano se ve muy pequeña o muy cerrada para que se distinga bien la seña.",
                    tip="Acércate un poco a la cámara o abre la mano lo necesario para la letra.",
                    target_letter=target,
                    detected_letter=detected,
                    confidence=confidence,
                    details=(f"fist_compactness={fist_compact:.2f}",),
                )
            if fist_compact > 1.6:
                return ReviewFeedback(
                    correct=False,
                    category=CATEGORY_POSITION,
                    title="Aléjate un poco de la cámara",
                    message="Tu mano ocupa casi todo el encuadre, lo que dificulta reconocer la forma completa.",
                    tip="Aléjate un poco de la cámara para que se vea toda la mano.",
                    target_letter=target,
                    detected_letter=detected,
                    confidence=confidence,
                    details=(f"fist_compactness={fist_compact:.2f}",),
                )

        return None

    @staticmethod
    def _frame_edge_warning(landmarks: Optional[Sequence[Any]]) -> Optional[str]:
        if not landmarks:
            return None
        try:
            xs = [float(_get(lm, "x", lm.get("x") if isinstance(lm, Mapping) else None)) for lm in landmarks]
            ys = [float(_get(lm, "y", lm.get("y") if isinstance(lm, Mapping) else None)) for lm in landmarks]
        except Exception:
            return None
        if not xs or not ys:
            return None
        margin = 0.04
        if min(xs) < margin or max(xs) > 1.0 - margin or min(ys) < margin or max(ys) > 1.0 - margin:
            return "Parte de tu mano está saliendo del cuadro de la cámara."
        return None

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _generic_feedback(
        target: str, detected: str, confidence: Optional[float]
    ) -> ReviewFeedback:
        hint = LETTER_HINTS.get(target)
        message = f"Formaste una {detected} en lugar de la {target}."
        tip = hint or f"Compara tu mano con la imagen de referencia de la letra {target} y ajusta la forma."
        return ReviewFeedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title="Revisa tu seña",
            message=message,
            tip=tip,
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
        )


# ---------------------------------------------------------------------------
# Funcion de conveniencia a nivel de modulo (mismo patron que
# performance_analyzer.py, para poder usarla sin instanciar la clase).
# ---------------------------------------------------------------------------

_default_review_ai = ReviewAI()


def analyze_review_attempt(
    target_letter: str,
    detected_letter: Optional[str],
    confidence: Optional[float] = None,
    finger_state: Any = None,
    features: Any = None,
    landmarks: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    """Atajo funcional: analiza un intento y devuelve un dict listo para JSON."""
    feedback = _default_review_ai.analyze(
        target_letter=target_letter,
        detected_letter=detected_letter,
        confidence=confidence,
        finger_state=finger_state,
        features=features,
        landmarks=landmarks,
    )
    return feedback.as_dict()
