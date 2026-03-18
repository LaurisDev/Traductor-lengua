# main.py
# Control principal: coordina autenticacion, navegacion y modulo de traduccion.
# Paradigma: orquestador, inyeccion de dependencias, bajo acoplamiento.

import sys
import os

# Asegurar que el directorio raiz del proyecto esta en el path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.database import DatabaseManager
from src.auth import AuthService
from src.gui import App
from src.camera import CameraCapture
from src.image_processing import HandDetector
from src.sign_language import FingerAnalyzer, GestureClassifier


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

        # Modulo de traduccion (creado al abrir la pantalla)
        self._camera: CameraCapture = None
        self._hand_detector: HandDetector = None
        self._finger_analyzer: FingerAnalyzer = None
        self._gesture_classifier: GestureClassifier = None
        self._translation_running = False
        self._after_id = None
        self._read_fail_count = 0
        self._MAX_READ_FAILS_BEFORE_MESSAGE = 45
        self._read_fail_count = 0

    def set_current_login_screen(self, screen) -> None:
        self._login_screen = screen

    def set_current_register_screen(self, screen) -> None:
        self._register_screen = screen

    def set_translation_screen(self, screen) -> None:
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
        self._app.show_login()

    def on_open_translation(self) -> None:
        self._app.show_translation()

    def on_translation_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        self._app.show_main_menu(self._current_user.username)

    def _start_translation_loop(self) -> None:
        """Inicializa camara, detectores y arranca el bucle de actualizacion."""
        self._camera = CameraCapture()
        if not self._camera.open():
            if self._translation_screen:
                self._translation_screen.show_camera_error()
            return
        for _ in range(15):
            self._camera.read()
        self._hand_detector = HandDetector()
        self._finger_analyzer = FingerAnalyzer()
        self._gesture_classifier = GestureClassifier()
        self._translation_running = True
        self._read_fail_count = 0
        self._update_translation()

    def _update_translation(self) -> None:
        """Un ciclo: leer frame, detectar mano, clasificar letra, actualizar GUI."""
        if not self._translation_running or not self._translation_screen:
            return
        if not self._camera or not self._camera.is_opened():
            return
        ret, frame = self._camera.read()
        if not ret or frame is None:
            self._read_fail_count += 1
            if self._translation_screen and self._read_fail_count >= self._MAX_READ_FAILS_BEFORE_MESSAGE:
                self._translation_screen.show_no_frames_error()
            self._schedule_next()
            return
        self._read_fail_count = 0
        landmarks, frame_out = self._hand_detector.process(frame)
        if landmarks is not None:
            self._hand_detector.draw_landmarks(frame_out, landmarks)
        finger_state = self._finger_analyzer.analyze(landmarks)
        letter = self._gesture_classifier.classify_with_stability(finger_state)
        self._translation_screen.update_frame(frame_out)
        self._translation_screen.update_letter(letter)
        self._schedule_next()

    def _schedule_next(self) -> None:
        """Programa el siguiente frame (aprox. 30 fps)."""
        if self._translation_running and self._app:
            self._after_id = self._app.get_root().after(33, self._update_translation)

    def _stop_translation_loop(self) -> None:
        self._translation_running = False
        if self._app and self._after_id is not None:
            self._app.get_root().after_cancel(self._after_id)
            self._after_id = None

    def _release_translation_resources(self) -> None:
        if self._camera:
            self._camera.release()
            self._camera = None
        if self._hand_detector:
            self._hand_detector.close()
            self._hand_detector = None
        self._translation_screen = None

    def run(self) -> None:
        """Punto de entrada: crea la GUI y arranca."""
        self._app = App(self)
        self._app.run()


def main() -> None:
    controller = MainController()
    controller.run()


if __name__ == "__main__":
    main()
