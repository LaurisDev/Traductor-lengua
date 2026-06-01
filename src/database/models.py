from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Representa un usuario del sistema.
    Encapsula id, nombre de usuario y contrasena (hash).
    """
    # En MongoDB el id real es ObjectId; se expone como str para la app.
    id: Optional[str]
    username: str
    password_hash: str

    def __post_init__(self) -> None:
        if self.id is not None and not str(self.id).strip():
            raise ValueError("El id de usuario no puede ser vacio")
