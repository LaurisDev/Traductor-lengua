# register_screen.py
# Pantalla de registro de usuarios.
# Responsabilidad unica: capturar datos y notificar al controlador.

import tkinter as tk
from typing import Callable

import ttkbootstrap as ttk


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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=40)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        card = ttk.Frame(container, padding=30, bootstyle="light")
        card.grid(row=0, column=0, sticky="n", padx=10, pady=10)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Crear cuenta", font=("", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(card, text="Regístrate para usar el traductor", font=("", 11)).grid(row=1, column=0, sticky="w", pady=(4, 18))

        ttk.Label(card, text="Usuario").grid(row=2, column=0, sticky="w")
        self._username_var = tk.StringVar()
        ttk.Entry(card, textvariable=self._username_var, width=34).grid(row=3, column=0, sticky="ew", pady=(4, 14))

        ttk.Label(card, text="Contraseña").grid(row=4, column=0, sticky="w")
        self._password_var = tk.StringVar()
        ttk.Entry(card, textvariable=self._password_var, show="*", width=34).grid(row=5, column=0, sticky="ew", pady=(4, 14))

        ttk.Label(card, text="Confirmar contraseña").grid(row=6, column=0, sticky="w")
        self._confirm_var = tk.StringVar()
        ttk.Entry(card, textvariable=self._confirm_var, show="*", width=34).grid(row=7, column=0, sticky="ew", pady=(4, 18))

        btn_frame = ttk.Frame(card)
        btn_frame.grid(row=8, column=0, sticky="ew")
        ttk.Button(btn_frame, text="Registrarse", command=self._do_register, bootstyle="success").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Volver al login", command=self._on_go_login, bootstyle="secondary").pack(side=tk.LEFT)

        self._lbl_error = ttk.Label(card, text="", bootstyle="danger")
        self._lbl_error.grid(row=9, column=0, sticky="w", pady=(14, 0))

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
