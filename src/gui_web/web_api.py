# web_api.py
# API llamada desde JS (pywebview.api.*)

import base64
from typing import Any, Dict, List, Optional


class WebAPI:
    def __init__(self, controller: Any) -> None:
        self._c = controller
        self._last_msg_idx = 0

    # ===== Auth =====
    def login(self, username: str, password: str) -> Dict[str, Any]:
        ok, msg = self._c.web_login(username, password)
        return {"ok": ok, "msg": msg}

    def register(self, username: str, password: str, confirm_password: str) -> Dict[str, Any]:
        ok, msg = self._c.web_register(username, password, confirm_password)
        return {"ok": ok, "msg": msg}

    def logout(self) -> Dict[str, Any]:
        self._c.web_logout()
        self._last_msg_idx = 0
        return {"ok": True}

    # ===== Voice =====
    def voice_start(self) -> Dict[str, Any]:
        self._c.on_voice_start_capture()
        return {"ok": True}

    def voice_stop(self) -> Dict[str, Any]:
        self._c.on_voice_stop_capture()
        return {"ok": True}

    # ===== Signs buffer =====
    def sign_space(self) -> Dict[str, Any]:
        self._c.on_sign_space()
        return {"ok": True}

    def sign_backspace(self) -> Dict[str, Any]:
        self._c.on_sign_backspace()
        return {"ok": True}

    def sign_clear(self) -> Dict[str, Any]:
        self._c.on_sign_clear()
        return {"ok": True}

    def sign_accept(self) -> Dict[str, Any]:
        self._c.on_sign_accept()
        return {"ok": True}

    def sign_send(self) -> Dict[str, Any]:
        self._c.on_sign_send()
        return {"ok": True}

    # ===== Reto: deletrear nombre =====
    def challenge_start(self) -> Dict[str, Any]:
        self._c.on_challenge_start()
        return {"ok": True}

    def challenge_stop(self) -> Dict[str, Any]:
        self._c.on_challenge_stop()
        return {"ok": True}

    # ===== Desempeno de aprendizaje =====
    def learning_attempt(self, target_letter: str, detected_letter: str) -> Dict[str, Any]:
        return self._c.web_learning_attempt(target_letter, detected_letter)

    def review_attempt(self, target_letter: str, detected_letter: str) -> Dict[str, Any]:
        return self._c.web_review_attempt(target_letter, detected_letter)

    def reset_review_attempts(self) -> Dict[str, Any]:
        return self._c.web_reset_review_attempts()

    def learning_performance(self, letter: str) -> Dict[str, Any]:
        return self._c.web_learning_performance(letter)

    def get_favorite_letters(self) -> Dict[str, Any]:
        return self._c.web_get_favorite_letters()

    def set_favorite_letter(self, letter: str, is_favorite: bool) -> Dict[str, Any]:
        return self._c.web_set_favorite_letter(letter, is_favorite)

    # ===== Poll =====
    def get_state(self) -> Dict[str, Any]:
        st = self._c.get_web_state()
        msgs = st.get("messages", [])
        new_msgs = msgs[self._last_msg_idx :]
        self._last_msg_idx = len(msgs)
        st = dict(st)
        st["new_messages"] = new_msgs
        return st

