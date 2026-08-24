# main.py
# Control principal: coordina autenticacion, navegacion y modulo de traduccion.
# Paradigma: orquestador, inyeccion de dependencias, bajo acoplamiento.

import sys
import os
import threading
import queue
import traceback
from typing import Optional
import base64
import copy
import time

# Asegurar que el directorio raiz del proyecto esta en el path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.database import DatabaseManager
from src.auth import AuthService
from src.gui import App
from src.camera import CameraCapture
from src.image_processing import HandDetector
from src.sign_language import (
    FingerAnalyzer,
    LearningPerformanceAnalyzer,
    MotionDetector,
    ReviewAI,
    SignClassifier,
    letters_for_challenge,
)
from src.config import USE_WEB_UI


class MainController:
    """
    Controlador principal: enlaza GUI, autenticacion, base de datos
    y modulo de traduccion (camara + deteccion + clasificacion).
    """

    def __init__(self) -> None:
        self._db = DatabaseManager()
        self._auth = AuthService(self._db)
        self._db.init_database()

        self._app: App = None
        self._current_user = None
        self._login_screen = None
        self._register_screen = None
        self._translation_screen = None
        self._interaction_screen = None
        self._aprendizaje_screen = None
        self._voice_screen = None
        self._voice_recording = False
        self._voice_stop_event: Optional[threading.Event] = None
        self._voice_thread: Optional[threading.Thread] = None
        self._sign_buffer = ""
        self._last_appended_letter: Optional[str] = None
        self._lm_smooth: Optional[list] = None

        # Modulo de traduccion (creado al abrir la pantalla)
        self._camera: CameraCapture = None
        self._hand_detector: HandDetector = None
        self._sign_classifier: SignClassifier = None
        # Deteccion de movimiento para J y Z (el modelo ML solo ve una postura estatica).
        self._finger_analyzer: FingerAnalyzer = None
        self._motion_detector: MotionDetector = None
        self._translation_running = False
        self._after_id = None
        self._read_fail_count = 0
        self._MAX_READ_FAILS_BEFORE_MESSAGE = 45
        self._camera_error: Optional[str] = None

        # Threading para que la GUI no se congele
        self._translation_thread: Optional[threading.Thread] = None
        self._stop_translation_event: Optional[threading.Event] = None
        self._translation_queue: Optional["queue.Queue[tuple]"] = None

        # ===== Estado UI Web (PyWebView) =====
        self._web_api = None
        self._web_messages = []  # {"who": str, "text": str}
        self._web_frame_b64: Optional[str] = None
        self._web_letter: Optional[str] = None
        self._web_finger_state= None
        self._web_confidence:float = 0.0
        self._web_landmarks= None
        self._web_features = None
        self._web_last_frame_ts = 0.0
        self._voice_status = "Listo"
        self._voice_error = ""
        self._learning_performance = LearningPerformanceAnalyzer()
        self._review_ai = ReviewAI()
        # Historial efimero: solo conserva los intentos confirmados de la
        # letra actual en Repaso; nunca se persiste en MongoDB.
        self._review_attempts: list[dict] = []
        
        # ===== Reto: deletrear el nombre de usuario =====
        self._challenge_letters: list = []
        self._challenge_index: int = 0
        self._challenge_done: bool = False
        self._challenge_active: bool = False
        self._challenge_match_count: int = 0
        self._challenge_hold_frames: int = 10  # frames consecutivos para confirmar cada letra

    def set_current_login_screen(self, screen) -> None:
        self._login_screen = screen

    def set_current_register_screen(self, screen) -> None:
        self._register_screen = screen

    def set_translation_screen(self, screen) -> None:
        self._translation_screen = screen
        self._start_translation_loop()

    def set_interaction_screen(self, screen) -> None:
        self._interaction_screen = screen
        self._translation_screen = screen
        self._start_translation_loop()
        self._sync_sign_buffer()

    def set_aprendizaje_screen(self, screen) -> None:
        self._aprendizaje_screen = screen
        self._translation_screen = screen
        self._start_translation_loop()

    def on_login(self, username: str, password: str) -> None:
        user = self._auth.login(username, password)
        if user is None:
            if self._login_screen:
                self._login_screen.show_error("Usuario o contrasena incorrectos")
            return
        self._current_user = user
        self._app.show_main_menu(user.username)

    def on_go_register(self) -> None:
        if self._login_screen:
            self._login_screen.clear_error()
        self._app.show_register()

    def on_go_login(self) -> None:
        if self._register_screen:
            self._register_screen.clear_error()
        self._app.show_login()

    def on_register(self, username: str, password: str, confirm_password: str) -> None:
        ok, msg = self._auth.register(username, password, confirm_password)
        if not ok:
            if self._register_screen:
                self._register_screen.show_error(msg)
            return
        if self._register_screen:
            self._register_screen.clear_error()
        self._app.show_login()

    def on_logout(self) -> None:
        self._current_user = None
        self._review_attempts.clear()
        if not USE_WEB_UI:
            self._app.show_login()

    def on_open_translation(self) -> None:
        self._app.show_translation()

    def on_open_voice(self) -> None:
        self._app.show_voice()

    def on_open_interaction(self) -> None:
        if USE_WEB_UI:
            self._ensure_translation_running()
        else:
            self._app.show_interaction()

    def on_open_aprendizaje(self) -> None:
        if not USE_WEB_UI:
            self._app.show_aprendizaje()

    def on_interaction_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        self._interaction_screen = None
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def on_aprendizaje_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        self._aprendizaje_screen = None
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def on_app_close(self) -> None:
        """Cierre limpio de la app (evita crash de MediaPipe en background)."""
        try:
            self._voice_stop_event.set() if self._voice_stop_event is not None else None
        except Exception:
            pass
        try:
            self._stop_translation_loop()
            self._release_translation_resources()
        except Exception:
            pass
        try:
            if self._app:
                self._app.quit()
        except Exception:
            pass

    # ====== Helpers para ejecutar "en UI" ======
    def _post_to_ui(self, fn) -> None:
        if USE_WEB_UI:
            fn()
            return
        try:
            if self._app and self._app.get_root():
                self._app.get_root().after(0, fn)
            else:
                fn()
        except Exception:
            fn()

    # ====== Web API ======
    def get_web_api(self):
        if self._web_api is None:
            from src.gui_web.web_api import WebAPI
            self._web_api = WebAPI(self)
        return self._web_api

    def web_login(self, username: str, password: str):
        user = self._auth.login(username, password)
        if user is None:
            return False, "Usuario o contraseña incorrectos"
        self._current_user = user
        self._ensure_translation_running()
        return True, "OK"

    def web_register(self, username: str, password: str, confirm_password: str):
        return self._auth.register(username, password, confirm_password)

    def web_logout(self) -> None:
        self._current_user = None
        self._review_attempts.clear()
        self._stop_translation_loop()
        self._release_translation_resources()
        self._web_messages.clear()
        self._sign_buffer = ""
        self._web_frame_b64 = None
        self._web_letter = None                             # <-- LÍNEA NUEVA
        self._web_landmarks = None 
        self._web_features = None
        self._web_last_frame_ts = 0.0
        self._voice_status = "Listo"
        self._voice_error = ""
        self._challenge_letters = []
        self._challenge_index = 0
        self._challenge_done = False
        self._challenge_active = False
        self._challenge_match_count = 0
        self._camera_error = None

    def web_learning_attempt(self, target_letter: str, detected_letter: str) -> dict:
        """Registra un intento confirmado de APRENDIZAJE del usuario autenticado."""
        if self._current_user is None:
            return {"ok": False, "msg": "Debes iniciar sesión"}

        target = (target_letter or "").strip().upper()
        detected = (detected_letter or "").strip().upper()
        if not target or not detected:
            return {"ok": False, "msg": "El intento no tiene una letra válida"}

        stats = self._db.record_learning_attempt(
            self._current_user.username,
            target,
            detected == target,
        )
        analysis = self._learning_performance.analyze(stats, target)
        return {"ok": True, "letter": target, "analysis": analysis.as_dict()}

    def web_review_attempt(self, target_letter: str, detected_letter: str) -> dict:
        """Registra un intento del modo REPASO y devuelve retroalimentación de la IA."""
        if self._current_user is None:
            return {"ok": False, "msg": "Debes iniciar sesión"}

        target = (target_letter or "").strip().upper()
        detected = (detected_letter or "").strip().upper()
        if not target or not detected:
            return {"ok": False, "msg": "El intento no tiene una letra válida"}

        # Reutiliza el mismo contador de 5 intentos que ya usa Aprendizaje.
        stats = self._db.record_learning_attempt(
            self._current_user.username,
            target,
            detected == target,
        )
        analysis = self._learning_performance.analyze(stats, target)

        # Un cambio de letra inicia una nueva sesion de Repaso. Las copias
        # profundas evitan que los datos del frame siguiente alteren intentos
        # ya confirmados. Solo se guardan como maximo los cinco intentos.
        if self._review_attempts and self._review_attempts[0]["target_letter"] != target:
            self._review_attempts.clear()
        if len(self._review_attempts) < 5:
            self._review_attempts.append(
                {
                    "target_letter": target,
                    "detected_letter": detected,
                    "confidence": float(self._web_confidence or 0.0),
                    "finger_state": copy.deepcopy(self._web_finger_state),
                    "features": copy.deepcopy(self._web_features),
                    "landmarks": copy.deepcopy(self._web_landmarks),
                }
            )

        # Un acierto siempre debe reemplazar una correccion previa, incluso
        # si ya se completo el analisis de cinco intentos.
        if detected == target:
            feedback = self._review_ai.analyze(
                target_letter=target,
                detected_letter=detected,
                confidence=self._web_confidence,
                finger_state=self._web_finger_state,
                features=self._web_features,
                landmarks=self._web_landmarks,
            )
        elif len(self._review_attempts) == 5:
            feedback = self._review_ai.analyze_attempts(self._review_attempts)
        else:
            feedback = self._review_ai.analyze(
                target_letter=target,
                detected_letter=detected,
                confidence=self._web_confidence,
                finger_state=self._web_finger_state,
                features=self._web_features,
                landmarks=self._web_landmarks,
            )

        return {
            "ok": True,
            "letter": target,
            "analysis": analysis.as_dict(),
            "feedback": feedback.as_dict(),
            "review_attempt": len(self._review_attempts),
            "review_attempt_limit": 5,
            "review_analysis_ready": len(self._review_attempts) == 5,
        }

    def web_reset_review_attempts(self) -> dict:
        """Descarta el historial temporal al salir o reiniciar Repaso."""
        self._review_attempts.clear()
        return {"ok": True}

    def web_learning_performance(self, letter: str) -> dict:
        """Devuelve el analisis actual de una letra para el asistente de APRENDIZAJE."""
        if self._current_user is None:
            return {"ok": False, "msg": "Debes iniciar sesión"}
        target = (letter or "").strip().upper()
        if not target:
            return {"ok": False, "msg": "La letra no es válida"}
        stats = self._db.get_learning_performance(self._current_user.username, target)
        analysis = self._learning_performance.analyze(stats, target)
        return {"ok": True, "letter": target, "analysis": analysis.as_dict()}

    def web_get_favorite_letters(self) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": "Debes iniciar sesión", "letters": []}
        return {
            "ok": True,
            "letters": self._db.get_favorite_letters(self._current_user.username),
        }

    def web_set_favorite_letter(self, letter: str, is_favorite: bool) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": "Debes iniciar sesión", "letters": []}
        target = (letter or "").strip().upper()
        if not target:
            return {"ok": False, "msg": "La letra no es válida", "letters": []}
        if is_favorite:
            letters = self._db.add_favorite_letter(self._current_user.username, target)
        else:
            letters = self._db.remove_favorite_letter(self._current_user.username, target)
        return {"ok": True, "letters": letters}

    def get_web_state(self):
        challenge_progress = 0.0
        if self._challenge_letters and not self._challenge_done:
            challenge_progress = self._challenge_match_count / float(self._challenge_hold_frames)
        return {
            "logged_in": self._current_user is not None,
            "username": self._current_user.username if self._current_user else None,
            "frame_jpeg_b64": self._web_frame_b64,
            "letter": self._web_letter,
            "sign_text": self._sign_buffer,
            "messages": list(self._web_messages),
            "voice_status": self._voice_status,
            "voice_error": self._voice_error,
            "camera_error": self._camera_error,
            "challenge_letters": list(self._challenge_letters),
            "challenge_index": self._challenge_index,
            "challenge_done": self._challenge_done,
            "challenge_progress": min(1.0, challenge_progress),
        }

    # ====== Reto: deletrear el nombre de usuario ======
    def on_challenge_start(self) -> None:
        """Arranca (o reinicia) el reto de deletrear el nombre del usuario."""
        username = self._current_user.username if self._current_user else ""
        self._challenge_letters = letters_for_challenge(username)
        self._challenge_index = 0
        self._challenge_done = False
        self._challenge_match_count = 0
        self._challenge_active = True

    def on_challenge_stop(self) -> None:
        """El usuario salio de la pantalla de reto (no hace falta seguir comparando letras)."""
        self._challenge_active = False

    def _advance_challenge(self, letter: Optional[str]) -> None:
        """
        Compara la letra detectada con la letra objetivo actual del reto.
        Requiere sostener la seña correcta varios frames seguidos antes de avanzar,
        para evitar que una deteccion aislada cuente como acierto.
        """
        if not self._challenge_letters or self._challenge_done:
            return
        target = self._challenge_letters[self._challenge_index]
        if letter != target:
            self._challenge_match_count = 0
            return
        self._challenge_match_count += 1
        if self._challenge_match_count < self._challenge_hold_frames:
            return
        self._challenge_match_count = 0
        self._challenge_index += 1
        if self._challenge_index >= len(self._challenge_letters):
            self._challenge_done = True

    # ====== Buffer de señas ======
    def _sync_sign_buffer(self) -> None:
        if self._interaction_screen is not None:
            self._interaction_screen.set_sign_text(self._sign_buffer)

    def on_sign_clear(self) -> None:
        self._sign_buffer = ""
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_space(self) -> None:
        self._sign_buffer += " "
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_backspace(self) -> None:
        if self._sign_buffer:
            self._sign_buffer = self._sign_buffer[:-1]
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_accept(self) -> None:
        """Agrega la letra actualmente detectada al buffer (confirmacion manual)."""
        letter = self._web_letter
        if letter:
            self._sign_buffer += letter
            self._sync_sign_buffer()

    def on_sign_send(self) -> None:
        """Envia el texto armado por senas al chat y limpia el buffer."""
        text = (self._sign_buffer or "").strip()
        if not text:
            return
        if self._interaction_screen is not None:
            self._interaction_screen.append_chat("Persona (señas)", text)
        self._web_messages.append({"who": "Persona (señas)", "text": text})
        self.on_sign_clear()

    def set_voice_screen(self, screen) -> None:
        self._voice_screen = screen

    def on_voice_back(self) -> None:
        self._voice_screen = None
        self._app.show_main_menu(self._current_user.username)

    def on_voice_start_capture(self) -> None:
        if self._voice_recording:
            return
        if self._voice_thread is not None and self._voice_thread.is_alive():
            self._voice_error = "El micrófono aún se está liberando. Espera 1 segundo y vuelve a intentar."
            return
        self._voice_recording = True
        self._voice_status = "Grabando…"
        self._voice_error = ""
        self._voice_stop_event = threading.Event()
        thread = threading.Thread(
            target=self._voice_stream_worker,
            name="voice-stream-worker",
            daemon=True,
        )
        self._voice_thread = thread
        thread.start()

    def on_voice_stop_capture(self) -> None:
        if self._voice_stop_event is not None:
            self._voice_stop_event.set()
        self._voice_status = "Transcribiendo…"
        if self._voice_screen is not None:
            self._voice_screen.set_transcribing(True)

    def _voice_stream_worker(self) -> None:
        err_msg = None
        text = None
        try:
            from src.speech.voice_transcriber import record_until_stop, transcribe_spanish
            ev = self._voice_stop_event
            if ev is None:
                raise RuntimeError("Estado de grabacion invalido")
            audio = record_until_stop(ev)
            text = transcribe_spanish(audio) if audio.size > 0 else ""
        except Exception as e:
            print(traceback.format_exc())
            err_msg = str(e) if str(e).strip() else "No se pudo usar el micrófono. Revisa el micrófono predeterminado de Windows."

        def finish() -> None:
            self._voice_recording = False
            self._voice_stop_event = None
            self._voice_thread = None
            if self._voice_screen is not None:
                self._voice_screen.set_transcribing(False)
                self._voice_screen.reset_after_session()
                if err_msg:
                    self._voice_screen.show_error(err_msg)
                else:
                    self._voice_screen.set_result(text or "")
            if self._interaction_screen is not None:
                self._interaction_screen.voice_done()
                if err_msg:
                    self._interaction_screen.voice_error(err_msg)
                else:
                    if text and text.strip():
                        self._interaction_screen.append_chat("Yo (voz)", text)
                    else:
                        self._interaction_screen.voice_error("Repite nuevamente.")
            self._voice_status = "Listo"
            if err_msg:
                self._voice_error = err_msg
            else:
                self._voice_error = ""
                if text and text.strip():
                    self._web_messages.append({"who": "Yo (voz)", "text": text.strip()})
                else:
                    self._voice_error = "Repite nuevamente."

        self._post_to_ui(finish)

    def _ensure_translation_running(self) -> None:
        if self._translation_running:
            return
        self._start_translation_loop()

    def on_translation_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def _start_translation_loop(self) -> None:
        """Inicializa camara, detectores y arranca el bucle de traduccion."""
        self._camera_error = None
        self._camera = CameraCapture()
        if not self._camera.open():
            self._camera_error = (
                "No se pudo abrir la camara. Verifique permisos y que no la use otra app "
                "(Chrome, Zoom, Teams, etc.)."
            )
            if self._translation_screen:
                self._translation_screen.show_camera_error()
            return
        for _ in range(15):
            self._camera.read()
        self._hand_detector = HandDetector()
        self._sign_classifier = SignClassifier()
        self._finger_analyzer = FingerAnalyzer()
        self._motion_detector = MotionDetector()
        if not self._sign_classifier.is_trained():
            print(
                "[Senas] Modelo no entrenado. Ejecute: python collect_sign_samples.py"
            )
        self._translation_running = True
        self._read_fail_count = 0
        self._stop_translation_event = threading.Event()
        self._translation_queue = queue.Queue(maxsize=1)
        self._translation_thread = threading.Thread(
            target=self._translation_worker,
            name="translation-worker",
            daemon=True,
        )
        self._translation_thread.start()
        if not USE_WEB_UI:
            self._poll_translation_queue()

    def _translation_worker(self) -> None:
        assert self._translation_queue is not None
        assert self._stop_translation_event is not None
        while self._translation_running and not self._stop_translation_event.is_set():
            if not self._camera or not self._camera.is_opened():
                break
            ret, frame = self._camera.read()
            if not ret or frame is None:
                self._read_fail_count += 1
                if self._read_fail_count >= self._MAX_READ_FAILS_BEFORE_MESSAGE:
                    self._put_latest((None, None, "no_frames"))
                    self._camera_error = (
                        "La camara no envia imagenes. Cierre Chrome/Zoom/Teams y reintente."
                    )
                continue

            self._read_fail_count = 0
            self._camera_error = None
            try:
                landmarks, frame_out = self._hand_detector.process(frame)
            except RuntimeError:
                break
            landmarks_classify = landmarks
            try:
                if landmarks is not None:
                    try:
                        from src.config import LANDMARK_SMOOTH_ALPHA, LANDMARK_SMOOTH_FOR_CLASSIFY
                        a = float(LANDMARK_SMOOTH_ALPHA)
                        smooth_classify = bool(LANDMARK_SMOOTH_FOR_CLASSIFY)
                    except Exception:
                        a = 0.65
                        smooth_classify = False
                    if self._lm_smooth is None or len(self._lm_smooth) != len(landmarks):
                        self._lm_smooth = [dict(lm) for lm in landmarks]
                    else:
                        for i in range(len(landmarks)):
                            cur = landmarks[i]
                            prev = self._lm_smooth[i]
                            prev["x"] = a * float(prev.get("x", 0.0)) + (1.0 - a) * float(cur.get("x", 0.0))
                            prev["y"] = a * float(prev.get("y", 0.0)) + (1.0 - a) * float(cur.get("y", 0.0))
                            prev["z"] = a * float(prev.get("z", 0.0)) + (1.0 - a) * float(cur.get("z", 0.0))
                    landmarks_draw = self._lm_smooth if a > 0 else landmarks
                    landmarks_classify = self._lm_smooth if smooth_classify else landmarks
                    self._hand_detector.draw_landmarks(frame_out, landmarks_draw)
                else:
                    self._lm_smooth = None

                letter, _conf = self._sign_classifier.letter_for_display(landmarks_classify)

                # J y Z son senas de MOVIMIENTO: el modelo ML solo ve una postura estatica
                # por frame y no puede distinguirlas de I / D en una sola imagen. Se rastrea
                # la trayectoria de la punta del dedo entre frames y, si calza con el gancho
                # de J o el zigzag de Z, se prioriza sobre la prediccion estatica del modelo.
                finger_state = self._finger_analyzer.analyze(landmarks_classify) if self._finger_analyzer else None
                self._web_finger_state = finger_state
                self._web_confidence= float(_conf or 0.0)
                self._web_landmarks=landmarks_classify
                self._web_features = self._sign_classifier.latest_features() if self._sign_classifier else None
                j_motion, z_motion = (
                    self._motion_detector.update(finger_state) if self._motion_detector else (False, False)
                )
                if finger_state is not None:
                    if j_motion and finger_state.pinky and not finger_state.index and not finger_state.middle:
                        letter = "J"
                    elif (
                        z_motion
                        and finger_state.index
                        and finger_state.index_up
                        and not finger_state.middle
                        and not finger_state.ring
                        and not finger_state.pinky
                    ):
                        letter = "Z"

                self._put_latest((frame_out, letter, "ok"))

                # Solo mostrar la letra detectada; el usuario confirma con "Aceptar".
                self._web_letter = letter

                if self._challenge_active:
                    self._advance_challenge(letter)
            except Exception:
                # Nunca dejar que un frame problematico mate el hilo de camara completo.
                print(traceback.format_exc())
                continue

            # Enviar frame a la UI web
            now = time.monotonic()
            try:
                from src.config import WEB_VIDEO_INTERVAL_MS, WEB_VIDEO_TARGET_WIDTH, WEB_VIDEO_JPEG_QUALITY
                interval_s = float(WEB_VIDEO_INTERVAL_MS) / 1000.0
                target_w = int(WEB_VIDEO_TARGET_WIDTH)
                jpeg_q = int(WEB_VIDEO_JPEG_QUALITY)
            except Exception:
                interval_s = 0.045
                target_w = 800
                jpeg_q = 55

            if now - self._web_last_frame_ts >= interval_s:
                self._web_last_frame_ts = now
                try:
                    import cv2
                    h, w = frame_out.shape[:2]
                    if w > target_w:
                        scale = float(target_w) / float(w)
                        frame_small = cv2.resize(frame_out, (int(w * scale), int(h * scale)))
                    else:
                        frame_small = frame_out
                    ok, buf = cv2.imencode(".jpg", frame_small, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_q])
                    if ok:
                        self._web_frame_b64 = base64.b64encode(buf.tobytes()).decode("ascii")
                except Exception:
                    pass

    def _put_latest(self, item: tuple) -> None:
        if not self._translation_queue:
            return
        try:
            if self._translation_queue.full():
                try:
                    self._translation_queue.get_nowait()
                except queue.Empty:
                    pass
            self._translation_queue.put_nowait(item)
        except Exception:
            pass

    def _poll_translation_queue(self) -> None:
        if not self._translation_running or not self._translation_screen:
            return
        try:
            frame_out, letter, status = self._translation_queue.get_nowait() if self._translation_queue else (None, None, None)
            if status == "no_frames":
                self._translation_screen.show_no_frames_error()
            elif status == "ok":
                if frame_out is not None:
                    self._translation_screen.update_frame(frame_out)
                self._translation_screen.update_letter(letter)
                if self._interaction_screen is not None and letter:
                    if letter != self._last_appended_letter:
                        self._sign_buffer += letter
                        self._last_appended_letter = letter
                        self._sync_sign_buffer()
                self._web_letter = letter
                try:
                    import cv2
                    ok, buf = cv2.imencode(".jpg", frame_out, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if ok:
                        self._web_frame_b64 = base64.b64encode(buf.tobytes()).decode("ascii")
                except Exception:
                    pass
        except queue.Empty:
            pass
        self._schedule_next()

    def _schedule_next(self) -> None:
        if USE_WEB_UI:
            return
        if self._translation_running and self._app:
            self._after_id = self._app.get_root().after(33, self._poll_translation_queue)

    def _stop_translation_loop(self) -> None:
        self._translation_running = False
        if self._stop_translation_event is not None:
            self._stop_translation_event.set()
        if not USE_WEB_UI:
            if self._app and self._after_id is not None:
                self._app.get_root().after_cancel(self._after_id)
                self._after_id = None
        if self._translation_thread is not None and self._translation_thread.is_alive():
            self._translation_thread.join(timeout=2.0)

    def _release_translation_resources(self) -> None:
        if self._camera:
            self._camera.release()
            self._camera = None
        if self._hand_detector:
            self._hand_detector.close()
            self._hand_detector = None
        self._translation_thread = None
        self._stop_translation_event = None
        self._translation_queue = None
        self._translation_screen = None
        self._aprendizaje_screen = None

    def run(self) -> None:
        """Punto de entrada: crea la GUI y arranca."""
        if USE_WEB_UI:
            from src.gui_web import WebApp
            self._app = WebApp(self)
            self._app.run()
        else:
            self._app = App(self)
            self._app.run()


def main() -> None:
    try:
        controller = MainController()
        controller.run()
    except RuntimeError as e:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error de base de datos", str(e))
            root.destroy()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
