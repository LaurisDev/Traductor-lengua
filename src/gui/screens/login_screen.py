# login_screen.py
# Pantalla de inicio de sesion.
# Responsabilidad unica: capturar credenciales y notificar resultado.

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional


class LoginScreen(ttk.Frame):
    """
    Formulario de login: usuario, contrasena, boton Entrar y enlace a Registro.
    Comunicacion mediante callbacks (bajo acoplamiento).
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_login: Callable[[str, str], None],
        on_go_register: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_login = on_login
        self._on_go_register = on_go_register
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill=tk.BOTH)

        ttk.Label(container, text="Inicio de sesion", font=("", 16)).pack(pady=(0, 20))

        ttk.Label(container, text="Usuario:").pack(anchor=tk.W)
        self._username_var = tk.StringVar()
        self._entry_user = ttk.Entry(container, textvariable=self._username_var, width=30)
        self._entry_user.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(container, text="Contrasena:").pack(anchor=tk.W)
        self._password_var = tk.StringVar()
        self._entry_pass = ttk.Entry(container, textvariable=self._password_var, show="*", width=30)
        self._entry_pass.pack(fill=tk.X, pady=(0, 20))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Entrar", command=self._do_login).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Registrarse", command=self._on_go_register).pack(side=tk.LEFT)

        self._lbl_error = ttk.Label(container, text="", foreground="red")
        self._lbl_error.pack(pady=10)

    def _do_login(self) -> None:
        user = self._username_var.get().strip()
        pwd = self._password_var.get()
        if not user:
            self._show_error("Ingrese su usuario")
            return
        if not pwd:
            self._show_error("Ingrese su contrasena")
            return
        self._lbl_error.config(text="")
        self._on_login(user, pwd)

    def _show_error(self, msg: str) -> None:
        self._lbl_error.config(text=msg)

    def show_error(self, msg: str) -> None:
        """Permite al controlador mostrar errores de autenticacion."""
        self._show_error(msg)

    def clear_error(self) -> None:
        self._lbl_error.config(text="")
