# gesture_classifier.py
# Alfabeto manual A-Z: cada gesto -> una letra (100% entendibles).
# E,M,N,S por posicion del pulgar; V,U,H,R por disposicion de indice y medio.

from typing import Optional

from .finger_analyzer import FingerState


class GestureClassifier:
    """
    Una letra por gesto. Sin ciclos salvo D/Z (Z con movimiento) e I/J (J con movimiento).
    """

    _RULES = [
        ((True, True, True, True, True), "touch_index", None, "F"),
        ((True, True, True, True, True), "", None, "C"),
        ((True, True, True, True, False), "", None, "P"),
        ((False, True, True, True, True), "", None, "B"),
        ((False, True, True, True, False), "", None, "W"),
        ((True, True, True, False, False), "", None, "K"),
        ((True, True, False, False, False), "touch_index", None, "Q"),
        ((True, True, False, False, False), "extended_up", None, "L"),
        ((True, True, False, False, False), "extended_side", None, "G"),
        ((True, True, False, False, False), "", None, "L"),
        ((True, False, False, False, True), "", None, "Y"),
        ((False, True, False, False, False), "", True, "X"),
        ((True, False, False, False, False), "between", None, "T"),
        ((True, False, False, False, False), "", None, "O"),
        ((False, False, False, False, False), "side", None, "A"),
        ((False, False, False, False, False), "unknown", None, "A"),
    ]

    _FIST_LETTER = {"inside_top": "E", "inside_front": "S", "inside_over2": "N", "inside_over3": "M"}
    _TWO_FINGER_LETTER = {"together_up": "U", "apart_up": "V", "horizontal": "H", "crossed": "R"}
    _CYCLE_D_Z = ["D", "Z"]
    _CYCLE_I_J = ["I", "J"]
    _CYCLE_FRAMES = 50

    def __init__(self) -> None:
        self._last_letter: Optional[str] = None
        self._stability_count = 0
        self._STABILITY_THRESHOLD = 2
        self._frames_same = 0
        self._last_pattern: Optional[tuple] = None

    def _match_thumb(self, rule: str, actual: str) -> bool:
        return not rule or rule == "" or rule == actual

    def _match_bent(self, rule: Optional[bool], actual: bool) -> bool:
        return rule is None or rule == actual

    def classify(self, finger_state: Optional[FingerState]) -> Optional[str]:
        if finger_state is None:
            return None
        t = finger_state.as_tuple()
        tp = finger_state.thumb_position
        ib = finger_state.index_bent
        two = finger_state.two_finger_pose

        if t == (True, True, True, False, False):
            if two == "horizontal":
                return "H"
            return "K"

        for pattern, r_thumb, r_bent, letter in self._RULES:
            if t != pattern:
                continue
            if not self._match_thumb(r_thumb, tp) or not self._match_bent(r_bent, ib):
                continue
            if t != self._last_pattern:
                self._last_pattern = t
                self._frames_same = 0
            return letter

        fist = (False, False, False, False, False)
        if t == fist:
            letter = self._FIST_LETTER.get(tp)
            if letter:
                return letter
            return "A"

        if t == (False, True, False, False, False) and not ib:
            if t != self._last_pattern:
                self._last_pattern = t
                self._frames_same = 0
            self._frames_same += 1
            i = (self._frames_same // self._CYCLE_FRAMES) % len(self._CYCLE_D_Z)
            return self._CYCLE_D_Z[i]

        if t == (False, True, False, False, False) and ib:
            return "X"

        if t == (False, False, False, False, True):
            if t != self._last_pattern:
                self._last_pattern = t
                self._frames_same = 0
            self._frames_same += 1
            i = (self._frames_same // self._CYCLE_FRAMES) % len(self._CYCLE_I_J)
            return self._CYCLE_I_J[i]

        if t == (False, True, True, False, False):
            letter = self._TWO_FINGER_LETTER.get(two)
            if letter:
                return letter
            return "V"

        self._last_pattern = t
        return None

    def classify_with_stability(self, finger_state: Optional[FingerState]) -> Optional[str]:
        letter = self.classify(finger_state)
        if letter is None:
            self._stability_count = 0
            self._last_letter = None
            return None
        if letter == self._last_letter:
            self._stability_count += 1
            if self._stability_count >= self._STABILITY_THRESHOLD:
                return letter
        else:
            self._last_letter = letter
            self._stability_count = 1
        return None

    def reset_stability(self) -> None:
        self._last_letter = None
        self._stability_count = 0
        self._last_pattern = None
        self._frames_same = 0
