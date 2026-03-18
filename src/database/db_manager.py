# db_manager.py
# Gestion de base de datos SQLite.
# Responsabilidad unica: operaciones CRUD y conexion.
# Paradigma: encapsulamiento, bajo acoplamiento.

import os
import sqlite3
import hashlib
from typing import Optional, Tuple

from .models import User

# Ruta por defecto: carpeta database junto al directorio del proyecto (raiz de src)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "database", "senas.db")


class DatabaseManager:
    """
    Gestiona la conexion y operaciones sobre la base de datos.
    Implementa patron de responsabilidad unica para acceso a datos.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = DEFAULT_DB_PATH
        self._db_path = db_path
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Crea el directorio de la base de datos si no existe."""
        directory = os.path.dirname(self._db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexion a la base de datos."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Crea las tablas necesarias si no existen."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash SHA-256 de la contrasena."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario.
        Retorna (exito, mensaje).
        """
        if not username or not password:
            return False, "Usuario y contrasena son obligatorios"
        username_clean = username.strip()
        conn = self._get_connection()
        try:
            password_hash = self.hash_password(password)
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username_clean, password_hash)
            )
            conn.commit()
            return True, "Registro exitoso"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"
        finally:
            conn.close()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Valida credenciales y retorna el User si son correctas.
        """
        if not username or not password:
            return None
        password_hash = self.hash_password(password)
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ? AND password_hash = ?",
                (username.strip(), password_hash)
            ).fetchone()
            if row is None:
                return None
            return User(id=row["id"], username=row["username"], password_hash=row["password_hash"])
        finally:
            conn.close()

    def user_exists(self, username: str) -> bool:
        """Comprueba si existe un usuario con el nombre dado."""
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username.strip(),)
            ).fetchone()
            return row is not None
        finally:
            conn.close()
