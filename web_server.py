"""Browser-hosted version of the Enseñando interface."""

import os
import secrets
import threading
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, abort, jsonify, request, send_from_directory, session

from src.gui_web.web_api import WebAPI
from src.main import MainController


WEB_ROOT = Path(__file__).resolve().parent / "src" / "gui_web" / "web"
app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("WEB_DEPLOYMENT", "").lower() in {"1", "true", "yes"}

_controllers = {}
_controllers_lock = threading.Lock()


def _controller() -> MainController:
    session_id = session.get("web_session_id")
    if not session_id:
        session_id = secrets.token_urlsafe(24)
        session["web_session_id"] = session_id
        session.permanent = True
    with _controllers_lock:
        controller = _controllers.get(session_id)
        if controller is None:
            controller = MainController()
            _controllers[session_id] = controller
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
    return jsonify(getattr(_controller().get_web_api(), method_name)(*args))


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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
