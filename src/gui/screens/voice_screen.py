

import tkinter as tk
from tkinter import scrolledtext
from typing import Callable

import ttkbootstrap as ttk


class VoiceScreen(ttk.Frame):
    """
    Graba audio del microfono hasta Detener; luego transcribe en un hilo del controlador.
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_start_capture: Callable[[], None],
        on_stop_capture: Callable[[], None],
        on_back: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_start_capture = on_start_capture
        self._on_stop_capture = on_stop_capture
        self._on_back = on_back
        self._capturing = False
        self._transcribing = False
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Button(header, text="← Volver", command=self._on_back_if_idle, bootstyle="secondary").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text="Voz a texto", font=("", 14, "bold")).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )

        body = ttk.Frame(self, padding=(24, 8, 24, 16))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)

        ttk.Label(
            body,
            text="Graba un fragmento de audio.",
            font=("", 10),
            wraplength=640,
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        controls = ttk.Frame(body)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self._btn_record = ttk.Button(
            controls,
            text="Grabar",
            command=self._on_start_clicked,
            bootstyle="primary",
        )
        self._btn_record.pack(side=tk.LEFT)

        self._lbl_status = ttk.Label(body, text="", bootstyle="secondary")
        self._lbl_status.grid(row=2, column=0, sticky="w", pady=(0, 8))

        self._txt = scrolledtext.ScrolledText(
            body,
            height=12,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=8,
            pady=8,
        )
        self._txt.grid(row=3, column=0, sticky="nsew")
        body.rowconfigure(3, weight=1)

        self._lbl_error = ttk.Label(body, text="", bootstyle="danger", wraplength=640)
        self._lbl_error.grid(row=4, column=0, sticky="w", pady=(8, 0))

    def _on_back_if_idle(self) -> None:
        if self._capturing or self._transcribing:
            return
        self._on_back()

    def _on_start_clicked(self) -> None:
        if self._capturing or self._transcribing:
            return
        self._lbl_error.config(text="")
        self._capturing = True
        self._btn_record.config(text="Detener y transcribir", command=self._on_stop_clicked)
        self._lbl_status.config(text="Grabando… hable cerca del micrófono.")
        self._on_start_capture()

    def _on_stop_clicked(self) -> None:
        if not self._capturing:
            return
        self._on_stop_capture()

    def set_transcribing(self, active: bool) -> None:
        """Tras pulsar detener: deshabilita boton mientras transcribe."""
        self._transcribing = active
        if active:
            self._lbl_status.config(text="Transcribiendo…")
            self._btn_record.config(state=tk.DISABLED)
        else:
            self._btn_record.config(state=tk.NORMAL)

    def reset_after_session(self) -> None:
        """Vuelve al estado listo para otra grabacion."""
        self._capturing = False
        self._transcribing = False
        self._btn_record.config(text="Grabar", command=self._on_start_clicked, state=tk.NORMAL)

    def set_result(self, text: str) -> None:
        self._lbl_error.config(text="")
        self._lbl_status.config(text="Transcripción lista.")
        line = text if text else "(No se detectó habla clara.)"
        self._txt.insert(tk.END, line + "\n\n")
        self._txt.see(tk.END)

    def show_error(self, msg: str) -> None:
        self._lbl_status.config(text="")
        self._lbl_error.config(text=msg)
