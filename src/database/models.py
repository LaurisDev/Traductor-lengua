# models.py
# Modelos de datos del sistema (abstraccion de entidades).
# Paradigma: POO - encapsulamiento de datos de usuario.

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Representa un usuario del sistema.
    Encapsula id, nombre de usuario y contrasena (hash).
    """
    id: Optional[int]
    username: str
    password_hash: str

    def __post_init__(self) -> None:
        if self.id is not None and self.id < 0:
            raise ValueError("El id de usuario debe ser no negativo")
