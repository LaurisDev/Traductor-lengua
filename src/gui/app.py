# app.py
# Ventana principal y navegacion entre pantallas.
# Responsabilidad: ensamblar GUI y coordinar con logica (controlador inyectado).

import tkinter as tk
from tkinter import ttk

from src.config import APP_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from .screens import LoginScreen, RegisterScreen, MainMenuScreen, TranslationScreen


class App:
    """
    Aplicacion Tkinter: ventana principal y cambio de pantallas.
    No contiene logica de negocio; recibe callbacks del controlador.
    """

    def __init__(self, controller: any) -> None:
        self._controller = controller
        self._root = tk.Tk()
        self._root.title(APP_TITLE)
        self._root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._current_frame: ttk.Frame = None

    def run(self) -> None:
        """Inicia el bucle principal de la GUI."""
        self._show_login()
        self._root.mainloop()

    def _clear_screen(self) -> None:
        """Destruye el frame actual."""
        if self._current_frame is not None:
            self._current_frame.destroy()
            self._current_frame = None

    def _show_screen(self, frame: ttk.Frame) -> None:
        self._clear_screen()
        self._current_frame = frame
        self._current_frame.pack(expand=True, fill=tk.BOTH)

    def _show_login(self) -> None:
        screen = LoginScreen(
            self._root,
            on_login=self._controller.on_login,
            on_go_register=self._controller.on_go_register
        )
        self._show_screen(screen)
        self._controller.set_current_login_screen(screen)

    def show_login(self) -> None:
        """Llamado por el controlador para volver al login."""
        self._show_login()

    def show_register(self) -> None:
        screen = RegisterScreen(
            self._root,
            on_register=self._controller.on_register,
            on_go_login=lambda: self._controller.on_go_login()
        )
        self._show_screen(screen)
        self._controller.set_current_register_screen(screen)

    def show_main_menu(self, username: str) -> None:
        screen = MainMenuScreen(
            self._root,
            username=username,
            on_translation=self._controller.on_open_translation,
            on_logout=self._controller.on_logout
        )
        self._show_screen(screen)

    def show_translation(self) -> None:
        screen = TranslationScreen(
            self._root,
            on_back=self._controller.on_translation_back
        )
        self._show_screen(screen)
        self._controller.set_translation_screen(screen)

    def get_root(self) -> tk.Tk:
        return self._root

    def quit(self) -> None:
        self._root.quit()
        self._root.destroy()
