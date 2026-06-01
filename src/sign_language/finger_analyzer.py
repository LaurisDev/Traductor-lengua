# finger_analyzer.py
# Extrae rasgos de la mano (angulos, pulgar, orientacion) para clasificar A-Z.

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

_JOINTS = {
    "thumb": (1, 2, 3, 4),
    "index": (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring": (13, 14, 15, 16),
    "pinky": (17, 18, 19, 20),
}


@dataclass
class FingerState:
    """Rasgos geometricos de la mano para el clasificador por puntuacion."""

    thumb: bool
    index: bool
    middle: bool
    ring: bool
    pinky: bool

    thumb_position: str = ""
    index_bent: bool = False
    two_finger_pose: str = ""
    palm_orientation: str = ""
    gesture_direction: str = ""
    hand_curve: str = ""

    thumb_index_touch: bool = False
    thumb_middle_touch: bool = False
    thumb_cover_count: int = 0
    thumb_over_fingers: bool = False
    has_inner_gap: bool = False
    finger_compact: bool = False

    index_direction: str = ""
    pinky_direction: str = ""
    palm_width: float = 0.01
    index_tip: Tuple[float, float] = (0.0, 0.0)
    pinky_tip: Tuple[float, float] = (0.0, 0.0)

    # Rasgos derivados (reglas A-Z)
    fist_closed: bool = False
    thumb_side: bool = False
    thumb_between: bool = False
    thumb_over: bool = False
    circle_closed: bool = False
    circle_small: bool = False
    open_curve: bool = False
    index_up: bool = False
    index_horizontal: bool = False
    index_down: bool = False
    palm_frontal: bool = True
    palm_down: bool = False
    four_fingers_up: bool = False

    def as_tuple(self) -> tuple:
        return (self.thumb, self.index, self.middle, self.ring, self.pinky)

    @property
    def extended_count(self) -> int:
        return sum(int(v) for v in self.as_tuple())


class FingerAnalyzer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _angle(lm, a, b, c) -> float:
        ax, ay = lm[a]["x"], lm[a]["y"]
        bx, by = lm[b]["x"], lm[b]["y"]
        cx, cy = lm[c]["x"], lm[c]["y"]
        ba = (ax - bx, ay - by)
        bc = (cx - bx, cy - by)
        dot = ba[0] * bc[0] + ba[1] * bc[1]
        m1, m2 = math.hypot(*ba), math.hypot(*bc)
        if m1 * m2 < 1e-9:
            return 180.0
        return math.degrees(math.acos(max(-1.0, min(1.0, dot / (m1 * m2)))))

    @staticmethod
    def _dist(lm, a, b) -> float:
        return math.hypot(lm[a]["x"] - lm[b]["x"], lm[a]["y"] - lm[b]["y"])

    @staticmethod
    def _palm_width(lm) -> float:
        return max(math.hypot(lm[5]["x"] - lm[17]["x"], lm[5]["y"] - lm[17]["y"]), 0.01)

    def _finger_extended(self, lm, name: str) -> bool:
        mcp, pip, dip, tip = _JOINTS[name]
        pip_a = self._angle(lm, mcp, pip, dip)
        dip_a = self._angle(lm, pip, dip, tip)
        if pip_a > 158 and dip_a > 152:
            return True
        if pip_a < 115 and dip_a < 125:
            return False
        tip_d = self._dist(lm, tip, mcp)
        pip_d = self._dist(lm, pip, mcp)
        if tip_d > pip_d * 1.35 and pip_a > 128:
            return True
        return lm[tip]["y"] < lm[mcp]["y"] - 0.025 and pip_a > 128

    def _finger_closed(self, lm, name: str) -> bool:
        return not self._finger_extended(lm, name)

    def _thumb_extended(self, lm, pw: float) -> bool:
        if self._dist(lm, 4, 5) < pw * 0.32:
            return False
        mcp_a = self._angle(lm, 1, 2, 3)
        ip_a = self._angle(lm, 2, 3, 4)
        if mcp_a < 115 and ip_a < 118:
            return False
        return mcp_a > 145 or ip_a > 140 or abs(lm[4]["x"] - lm[2]["x"]) > pw * 0.42

    def _finger_direction(self, lm, base_idx: int, tip_idx: int, pw: float) -> str:
        dx = lm[tip_idx]["x"] - lm[base_idx]["x"]
        dy = lm[tip_idx]["y"] - lm[base_idx]["y"]
        if abs(dx) > abs(dy) * 1.1:
            return "horizontal"
        if dy < -pw * 0.08:
            return "up"
        if dy > pw * 0.08:
            return "down"
        return "diag_up" if dy < 0 else "diag_down"

    def _gesture_direction(self, lm, idx, mid, rng, pnk, pw) -> str:
        vecs = []
        if idx:
            vecs.append((lm[8]["x"] - lm[5]["x"], lm[8]["y"] - lm[5]["y"]))
        if mid:
            vecs.append((lm[12]["x"] - lm[9]["x"], lm[12]["y"] - lm[9]["y"]))
        if rng:
            vecs.append((lm[16]["x"] - lm[13]["x"], lm[16]["y"] - lm[13]["y"]))
        if pnk:
            vecs.append((lm[20]["x"] - lm[17]["x"], lm[20]["y"] - lm[17]["y"]))
        if not vecs:
            return "up"
        adx = sum(v[0] for v in vecs) / len(vecs)
        ady = sum(v[1] for v in vecs) / len(vecs)
        if abs(adx) > abs(ady) * 1.1:
            return "horizontal"
        if ady > pw * 0.08:
            return "down"
        return "up"

    def _palm_orientation(self, lm, gdir: str) -> str:
        if gdir == "down":
            return "down"
        pw = self._palm_width(lm)
        ph = max(self._dist(lm, 0, 9), 0.01)
        if pw < ph * 0.75:
            return "lateral"
        return "frontal"

    def _two_finger_pose(self, lm, pw: float) -> str:
        i5, i8 = lm[5], lm[8]
        m9, m12 = lm[9], lm[12]
        dx, dy = i8["x"] - m12["x"], i8["y"] - m12["y"]
        dist = math.hypot(dx, dy)
        i_dx, i_dy = i8["x"] - i5["x"], i8["y"] - i5["y"]
        m_dx, m_dy = m12["x"] - m9["x"], m12["y"] - m9["y"]
        if dist < pw * 0.22:
            cross = (i8["x"] - m9["x"]) * (m12["x"] - i5["x"])
            if cross > 0.0003:
                return "crossed"
        if (abs(i_dx) + abs(m_dx)) / 2 > (abs(i_dy) + abs(m_dy)) / 2 * 0.7:
            return "horizontal"
        if dist > pw * 0.38:
            return "apart_up"
        return "together_up"

    def _thumb_cover_count(self, lm, pw: float) -> int:
        t4 = lm[4]
        count = 0
        for pip_i, tip_i in [(6, 8), (10, 12), (14, 16), (18, 20)]:
            tip, pip = lm[tip_i], lm[pip_i]
            if (
                min(pip["x"], tip["x"]) - pw * 0.1 <= t4["x"] <= max(pip["x"], tip["x"]) + pw * 0.1
                and tip["y"] < t4["y"] - pw * 0.01
            ):
                count += 1
        return count

    def _has_inner_gap(self, lm, pw: float, touch: bool) -> bool:
        if not touch:
            return False
        pts = [(lm[4]["x"], lm[4]["y"]), (lm[3]["x"], lm[3]["y"]), (lm[6]["x"], lm[6]["y"]), (lm[8]["x"], lm[8]["y"])]
        area = 0.0
        for i in range(4):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 4]
            area += x1 * y2 - x2 * y1
        return abs(area) * 0.5 > pw * pw * 0.022

    def analyze(self, landmarks: Optional[List]) -> Optional[FingerState]:
        if landmarks is None or len(landmarks) < 21:
            return None

        try:
            if float(landmarks[5]["x"]) > float(landmarks[17]["x"]):
                landmarks = [
                    {"x": 1.0 - float(p["x"]), "y": float(p["y"]), "z": float(p.get("z", 0.0))}
                    for p in landmarks
                ]
        except Exception:
            pass

        pw = self._palm_width(landmarks)
        thumb = self._thumb_extended(landmarks, pw)
        index = self._finger_extended(landmarks, "index")
        middle = self._finger_extended(landmarks, "middle")
        ring = self._finger_extended(landmarks, "ring")
        pinky = self._finger_extended(landmarks, "pinky")

        ti_touch = self._dist(landmarks, 4, 8) < pw * 0.22
        tm_touch = self._dist(landmarks, 4, 12) < pw * 0.28
        cover = self._thumb_cover_count(landmarks, pw)
        gap = self._has_inner_gap(landmarks, pw, ti_touch)

        idx_dir = self._finger_direction(landmarks, 5, 8, pw)
        pnk_dir = self._finger_direction(landmarks, 17, 20, pw)
        gdir = self._gesture_direction(landmarks, index, middle, ring, pinky, pw)
        palm = self._palm_orientation(landmarks, gdir)
        two = self._two_finger_pose(landmarks, pw) if (index and middle) else ""

        pip_angles = [
            self._angle(landmarks, 5, 6, 7),
            self._angle(landmarks, 9, 10, 11),
            self._angle(landmarks, 13, 14, 15),
            self._angle(landmarks, 17, 18, 19),
        ]
        pip_avg = sum(pip_angles) / 4
        thumb_gap = self._dist(landmarks, 4, 8) / pw

        fist = (
            self._finger_closed(landmarks, "index")
            and self._finger_closed(landmarks, "middle")
            and self._finger_closed(landmarks, "ring")
            and self._finger_closed(landmarks, "pinky")
        )

        t4, i5 = landmarks[4], landmarks[5]
        avg_tip_y = (landmarks[8]["y"] + landmarks[12]["y"] + landmarks[16]["y"] + landmarks[20]["y"]) / 4
        thumb_over = t4["y"] < avg_tip_y - pw * 0.06
        thumb_side = (
            not thumb_over
            and not tm_touch
            and abs(t4["x"] - i5["x"]) > pw * 0.45
            and t4["y"] >= avg_tip_y - pw * 0.08
        )
        thumb_between = (
            tm_touch
            or (min(i5["x"], landmarks[9]["x"]) - pw * 0.12 <= t4["x"] <= max(i5["x"], landmarks[9]["x"]) + pw * 0.12
                and t4["y"] > avg_tip_y)
        )

        tips_near = (
            self._dist(landmarks, 8, 12) < pw * 0.2
            and self._dist(landmarks, 12, 16) < pw * 0.2
            and self._dist(landmarks, 16, 20) < pw * 0.2
        )
        circle_closed = ti_touch and fist and tips_near and thumb_gap < pw * 0.35

        others_closed = sum(
            1 for ext in (middle, ring, pinky) if not ext
        )
        circle_small = (
            index
            and idx_dir in ("up", "diag_up")
            and (tm_touch or self._dist(landmarks, 4, 9) < pw * 0.35)
            and others_closed >= 1
            and not (middle and ring and pinky)
        )

        open_curve = (
            0.3 < thumb_gap < 1.0
            and 115 < pip_avg < 168
            and not ti_touch
            and (index or middle or ring)
        )

        compact = max(self._dist(landmarks, 8, 12), self._dist(landmarks, 12, 16), self._dist(landmarks, 16, 20)) < pw * 0.65

        thumb_pos = "unknown"
        if ti_touch:
            thumb_pos = "touch_index"
        elif thumb_between:
            thumb_pos = "between"
        elif thumb_over:
            thumb_pos = "inside_front"
        elif cover >= 3:
            thumb_pos = "inside_over3"
        elif cover == 2:
            thumb_pos = "inside_over2"
        elif thumb_side:
            thumb_pos = "side"
        elif thumb:
            thumb_pos = "extended_side" if idx_dir == "horizontal" else "extended_up"

        curve = "fist" if fist and thumb_gap < pw * 0.5 else "mixed"
        if circle_closed:
            curve = "closed_circle"
        elif open_curve:
            curve = "open_curve"
        elif pip_avg > 160:
            curve = "flat"

        idx_bent = self._angle(landmarks, 5, 6, 7) < 142

        return FingerState(
            thumb=thumb,
            index=index,
            middle=middle,
            ring=ring,
            pinky=pinky,
            thumb_position=thumb_pos,
            index_bent=idx_bent,
            two_finger_pose=two,
            palm_orientation=palm,
            gesture_direction=gdir,
            hand_curve=curve,
            thumb_index_touch=ti_touch,
            thumb_middle_touch=tm_touch,
            thumb_cover_count=cover,
            thumb_over_fingers=thumb_over,
            has_inner_gap=gap,
            finger_compact=compact,
            index_direction=idx_dir,
            pinky_direction=pnk_dir,
            palm_width=pw,
            index_tip=(float(landmarks[8]["x"]), float(landmarks[8]["y"])),
            pinky_tip=(float(landmarks[20]["x"]), float(landmarks[20]["y"])),
            fist_closed=fist,
            thumb_side=thumb_side,
            thumb_between=thumb_between,
            thumb_over=thumb_over,
            circle_closed=circle_closed,
            circle_small=circle_small,
            open_curve=open_curve,
            index_up=idx_dir in ("up", "diag_up"),
            index_horizontal=idx_dir == "horizontal",
            index_down=idx_dir in ("down", "diag_down"),
            palm_frontal=palm == "frontal",
            palm_down=palm == "down",
            four_fingers_up=index and middle and ring and pinky,
        )
