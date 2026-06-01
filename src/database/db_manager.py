# db_manager.py
# Gestion de base de datos MongoDB (local).
# Responsabilidad unica: operaciones CRUD y conexion.
# Paradigma: encapsulamiento, bajo acoplamiento.

import hashlib
import os
from typing import Optional, Tuple

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.config import MONGO_DB_NAME, MONGO_URI, MONGO_USERS_COLLECTION
from .models import User


class DatabaseManager:
    """
    Gestiona la conexion y operaciones sobre la base de datos.
    Implementa patron de responsabilidad unica para acceso a datos.
    """

    def __init__(self, mongo_uri: Optional[str] = None) -> None:
        # Permite override por variable de entorno, util para demos o laboratorios.
        env_uri = os.getenv("MONGO_URI")
        self._mongo_uri = (mongo_uri or env_uri or MONGO_URI).strip()
        self._client: Optional[MongoClient] = None

    def _get_client(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(self._mongo_uri)
        return self._client

    def _users_collection(self):
        client = self._get_client()
        db = client[MONGO_DB_NAME]
        return db[MONGO_USERS_COLLECTION]

    def init_database(self) -> None:
        """
        Inicializa la coleccion e indices necesarios.
        En MongoDB la base se crea automaticamente al insertar el primer documento.
        """
        try:
            users = self._users_collection()
            # Username unico para evitar duplicados.
            users.create_index("username", unique=True)
        except Exception as e:
            raise RuntimeError(
                "No se pudo conectar a MongoDB. Verifique que el servicio de MongoDB este ejecutandose "
                "y que pueda conectarse a 'mongodb://localhost:27017' (o configure MONGO_URI)."
            ) from e

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
        try:
            password_hash = self.hash_password(password)
            users = self._users_collection()
            users.insert_one(
                {
                    "username": username_clean,
                    "password_hash": password_hash,
                }
            )
            return True, "Registro exitoso"
        except DuplicateKeyError:
            return False, "El nombre de usuario ya existe"
        except PyMongoError as e:
            return False, f"Error al registrar: {str(e)}"

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Valida credenciales y retorna el User si son correctas.
        """
        if not username or not password:
            return None
        password_hash = self.hash_password(password)
        users = self._users_collection()
        doc = users.find_one(
            {"username": username.strip(), "password_hash": password_hash},
            {"username": 1, "password_hash": 1},
        )
        if not doc:
            return None
        return User(id=str(doc.get("_id")), username=doc["username"], password_hash=doc["password_hash"])

    def user_exists(self, username: str) -> bool:
        """Comprueba si existe un usuario con el nombre dado."""
        users = self._users_collection()
        return users.count_documents({"username": username.strip()}, limit=1) > 0
