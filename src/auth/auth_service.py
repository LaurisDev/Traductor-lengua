# auth_service.py
# Servicio de autenticacion: registro e inicio de sesion.
# Responsabilidad unica: validar credenciales y delegar en la base de datos.
# Paradigma: capa de logica de negocio, bajo acoplamiento con GUI y DB.

from typing import Optional, Tuple

from src.database import DatabaseManager, User


class AuthService:
    """
    Gestiona registro e inicio de sesion.
    Valida reglas de negocio antes de llamar al DatabaseManager.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def register(self, username: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Registra un usuario tras validar formato y coincidencia de contrasenas.
        Retorna (exito, mensaje).
        """
        msg = self._validate_credentials(username, password)
        if msg:
            return False, msg
        if password != confirm_password:
            return False, "Las contrasenas no coinciden"
        return self._db.register_user(username, password)

    def _validate_credentials(self, username: str, password: str) -> str:
        """Valida longitud y caracteres. Retorna mensaje de error o cadena vacia."""
        from src.config import MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
        username = username.strip()
        if len(username) < MIN_USERNAME_LENGTH:
            return f"El usuario debe tener al menos {MIN_USERNAME_LENGTH} caracteres"
        if len(username) > MAX_USERNAME_LENGTH:
            return f"El usuario no puede superar {MAX_USERNAME_LENGTH} caracteres"
        if len(password) < MIN_PASSWORD_LENGTH:
            return f"La contrasena debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
        if len(password) > MAX_PASSWORD_LENGTH:
            return f"La contrasena no puede superar {MAX_PASSWORD_LENGTH} caracteres"
        return ""

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Valida credenciales y retorna el User si el login es correcto.
        """
        if not username or not password:
            return None
        return self._db.authenticate(username.strip(), password)
