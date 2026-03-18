# register_screen.py
# Pantalla de registro de usuarios.
# Responsabilidad unica: capturar datos y notificar al controlador.

import tkinter as tk
from tkinter import ttk
from typing import Callable


class RegisterScreen(ttk.Frame):
    """
    Formulario de registro: usuario, contrasena, confirmacion, boton Registrar.
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_register: Callable[[str, str, str], None],
        on_go_login: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_register = on_register
        self._on_go_login = on_go_login
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill=tk.BOTH)

        ttk.Label(container, text="Registro de usuario", font=("", 16)).pack(pady=(0, 20))

        ttk.Label(container, text="Usuario:").pack(anchor=tk.W)
        self._username_var = tk.StringVar()
        ttk.Entry(container, textvariable=self._username_var, width=30).pack(fill=tk.X, pady=(0, 15))

        ttk.Label(container, text="Contrasena:").pack(anchor=tk.W)
        self._password_var = tk.StringVar()
        ttk.Entry(container, textvariable=self._password_var, show="*", width=30).pack(fill=tk.X, pady=(0, 15))

        ttk.Label(container, text="Confirmar contrasena:").pack(anchor=tk.W)
        self._confirm_var = tk.StringVar()
        ttk.Entry(container, textvariable=self._confirm_var, show="*", width=30).pack(fill=tk.X, pady=(0, 20))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Registrarse", command=self._do_register).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Volver al login", command=self._on_go_login).pack(side=tk.LEFT)

        self._lbl_error = ttk.Label(container, text="", foreground="red")
        self._lbl_error.pack(pady=10)

    def _do_register(self) -> None:
        user = self._username_var.get().strip()
        pwd = self._password_var.get()
        confirm = self._confirm_var.get()
        if not user:
            self._show_error("Ingrese un usuario")
            return
        if not pwd:
            self._show_error("Ingrese una contrasena")
            return
        if pwd != confirm:
            self._show_error("Las contrasenas no coinciden")
            return
        self._lbl_error.config(text="")
        self._on_register(user, pwd, confirm)

    def _show_error(self, msg: str) -> None:
        self._lbl_error.config(text=msg)

    def show_error(self, msg: str) -> None:
        self._lbl_error.config(text=msg)

    def clear_error(self) -> None:
        self._lbl_error.config(text="")
