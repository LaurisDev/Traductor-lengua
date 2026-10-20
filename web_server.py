"""Version web de Enseñando para compartirla con un enlace.

Corre en este mismo computador con el MongoDB local; un tunel (por ejemplo
Cloudflare) publica el enlace HTTPS. La camara y la voz de cada participante
se usan desde su navegador y los frames se procesan aqui.
"""

import os

# Activa el modo web antes de importar la configuracion del proyecto.
os.environ.setdefault("WEB_DEPLOYMENT", "1")
import secrets
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, abort, jsonify, request, send_from_directory, session
from pymongo.errors import PyMongoError

from src.gui_web.web_api import WebAPI
from src.main import MainController


WEB_ROOT = Path(__file__).resolve().parent / "src" / "gui_web" / "web"
app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

_controllers = {}
_last_seen = {}
_controllers_lock = threading.Lock()

# Una pestaña abierta consulta el estado varias veces por segundo. Si una sesion
# pasa este tiempo sin actividad (pestaña cerrada sin cerrar sesion), se libera
# su detector de manos y su hilo para no agotar la memoria del servidor.
SESSION_IDLE_SECONDS = int(os.getenv("SESSION_IDLE_SECONDS", "600"))


def _release_idle_sessions(now: float) -> None:
    """Debe llamarse con _controllers_lock tomado."""
    for session_id in [sid for sid, seen in _last_seen.items() if now - seen > SESSION_IDLE_SECONDS]:
        controller = _controllers.pop(session_id, None)
        _last_seen.pop(session_id, None)
        if controller is not None:
            try:
                controller.web_logout()
            except Exception:
                app.logger.exception("Could not release idle web session")


def _controller() -> MainController:
    session_id = session.get("web_session_id")
    if not session_id:
        session_id = secrets.token_urlsafe(24)
        session["web_session_id"] = session_id
        session.permanent = True
    now = time.monotonic()
    with _controllers_lock:
        _release_idle_sessions(now)
        controller = _controllers.get(session_id)
        if controller is None:
            controller = MainController()
            _controllers[session_id] = controller
        _last_seen[session_id] = now
        return controller


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return send_from_directory(WEB_ROOT, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    candidate = (WEB_ROOT / filename).resolve()
    if WEB_ROOT not in candidate.parents and candidate != WEB_ROOT:
        abort(404)
    return send_from_directory(WEB_ROOT, filename)


@app.post("/api/<method_name>")
def call_web_api(method_name: str):
    args = request.get_json()
    if not isinstance(args, list):
        return jsonify({"error": "Se esperaba una lista de argumentos."}), 400
    if method_name.startswith("_") or method_name not in {
        name for name, value in vars(WebAPI).items() if callable(value)
    }:
        abort(404)
    try:
        controller = _controller()
    except RuntimeError:
        app.logger.exception("Could not initialize the database for web session")
        return jsonify({"error": "database_unavailable"}), 503
    try:
        return jsonify(getattr(controller.get_web_api(), method_name)(*args))
    except PyMongoError:
        app.logger.exception("MongoDB request failed for web API method %s", method_name)
        return jsonify({"error": "database_unavailable"}), 503


@app.post("/api/camera/frame")
def camera_frame():
    raw_frame = request.get_data(cache=False)
    if not raw_frame or len(raw_frame) > app.config["MAX_CONTENT_LENGTH"]:
        return jsonify({"error": "El frame está vacío o excede el tamaño permitido."}), 400
    encoded = np.frombuffer(raw_frame, dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "No se pudo interpretar el frame de cámara."}), 400
    if frame.shape[1] > 1280 or frame.shape[0] > 720:
        return jsonify({"error": "La resolución del frame excede el máximo permitido."}), 400
    if not _controller().submit_browser_frame(frame):
        return jsonify({"error": "La sesión de traducción no está activa."}), 409
    return jsonify({"ok": True})


@app.post("/api/camera/error")
def camera_error():
    _controller().set_browser_camera_error()
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Solo escucha en este equipo; el tunel es quien lo publica en internet.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), threaded=True)
