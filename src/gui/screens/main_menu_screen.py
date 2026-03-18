# main_menu_screen.py
# Menu principal tras iniciar sesion.
# Opciones: Traduccion, Cerrar sesion.

import tkinter as tk
from tkinter import ttk
from typing import Callable


class MainMenuScreen(ttk.Frame):
    """
    Menu principal: muestra nombre de usuario y botones
    para ir a Traduccion o Cerrar sesion.
    """

    def __init__(
        self,
        parent: tk.Misc,
        username: str,
        on_translation: Callable[[], None],
        on_logout: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_translation = on_translation
        self._on_logout = on_logout
        self._username = username
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=40)
        container.pack(expand=True, fill=tk.BOTH)

        ttk.Label(container, text="Menu principal", font=("", 18)).pack(pady=(0, 10))
        ttk.Label(container, text=f"Bienvenido, {self._username}", font=("", 12)).pack(pady=(0, 30))

        ttk.Button(
            container,
            text="Abrir modulo de traduccion",
            command=self._on_translation
        ).pack(fill=tk.X, pady=10)

        ttk.Button(container, text="Cerrar sesion", command=self._on_logout).pack(fill=tk.X, pady=10)
