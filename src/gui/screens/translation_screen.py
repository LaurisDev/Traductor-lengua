# translation_screen.py
# Pantalla de traduccion en tiempo real: video de la camara y letra detectada.
# Responsabilidad: mostrar frame y resultado, delegar captura/clasificacion al controlador.

import tkinter as tk
from typing import Callable, Optional

import ttkbootstrap as ttk

# PIL para convertir frame OpenCV a ImageTk
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class TranslationScreen(ttk.Frame):
    """
    Muestra el video de la camara y la letra detectada.
    El controlador actualiza el frame y la letra mediante metodos publicos.
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_back: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_back = on_back
        self._photo: Optional[any] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Button(header, text="← Volver", command=self._on_back, bootstyle="secondary").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Traducción en tiempo real", font=("", 14, "bold")).grid(row=0, column=1, sticky="w", padx=(12, 0))

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self._lbl_video = ttk.Label(
            body,
            text="Iniciando cámara...",
            anchor=tk.CENTER,
            bootstyle="light",
        )
        self._lbl_video.grid(row=0, column=0, sticky="nsew", pady=(12, 12))

        # Letra grande y centrada debajo del video
        self._lbl_letter = ttk.Label(
            body,
            text="Letra: -",
            font=("", 28, "bold"),
            bootstyle="inverse-primary",
            anchor=tk.CENTER,
        )
        self._lbl_letter.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self._lbl_instruction = ttk.Label(
            body,
            text="Coloca una mano frente a la cámara con buena luz. Mantén el gesto estable unos segundos.",
            font=("", 10),
        )
        self._lbl_instruction.grid(row=2, column=0, sticky="w")

    # Tamano fijo para mostrar el video (evita problemas de dimension o refresco en Tkinter)
    _DISPLAY_WIDTH = 640
    _DISPLAY_HEIGHT = 480

    def update_frame(self, image_bgr: any) -> None:
        """
        Actualiza la imagen mostrada. image_bgr es un frame BGR (numpy array) de OpenCV.
        Se redimensiona a tamano fijo para que la vista se actualice bien en todos los sistemas.
        """
        if image_bgr is None:
            return
        if Image is None or ImageTk is None:
            self._lbl_video.config(text="Instale Pillow para ver el video: pip install Pillow")
            return
        try:
            import cv2
            h, w = image_bgr.shape[:2]
            if w != self._DISPLAY_WIDTH or h != self._DISPLAY_HEIGHT:
                image_bgr = cv2.resize(
                    image_bgr, (self._DISPLAY_WIDTH, self._DISPLAY_HEIGHT),
                    interpolation=cv2.INTER_LINEAR
                )
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self._photo = ImageTk.PhotoImage(image=img)
            self._lbl_video.config(image=self._photo, text="")
            self._lbl_video.update_idletasks()
        except Exception as e:
            self._lbl_video.config(text="Error al mostrar el frame: {}".format(e))

    def update_letter(self, letter: Optional[str]) -> None:
        """Actualiza la letra mostrada."""
        if letter:
            self._lbl_letter.config(text=f"Letra: {letter}")
        else:
            self._lbl_letter.config(text="Letra: -")

    def show_camera_error(self) -> None:
        """Muestra mensaje de error de camara."""
        self._lbl_video.config(
            text="No se pudo abrir la camara. Compruebe que este conectada, "
                 "que Windows tenga permiso de camara (Configuracion > Privacidad) y que no la use otro programa."
        )

    def show_no_frames_error(self) -> None:
        """Muestra que la camara no esta enviando imagenes."""
        self._lbl_video.config(
            text="La camara no envia imagenes. Cierre Chrome, Zoom, Teams o cualquier app que use la camara y vuelva a intentar."
        )
