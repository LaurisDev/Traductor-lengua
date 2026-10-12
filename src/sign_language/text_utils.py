# text_utils.py
# Utilidades de texto para el modulo de senas (reto "deletrea tu nombre").

from __future__ import annotations

import unicodedata
from typing import List


def letters_for_challenge(text: str, language: str = "es") -> List[str]:
    """
    Convierte un texto (p.ej. el nombre de usuario) en la secuencia de letras
    deletreables con el abecedario dactilologico entrenado (A-Z).

    - Quita tildes (MARIA -> MARIA, JOSÉ -> JOSE).
    - La Ñ se reduce a N (el clasificador no tiene clase para Ñ).
    - En portugues (LIBRAS) la Ç se conserva: tiene su propia seña.
    - Descarta espacios, numeros y simbolos.

    Ejemplo: "María José" -> ["M", "A", "R", "I", "A", "J", "O", "S", "E"]
    """
    if not text:
        return []
    letters: List[str] = []
    for ch in text.strip().upper():
        if language == "pt" and ch == "Ç":
            letters.append(ch)
            continue
        letters.extend(c for c in unicodedata.normalize("NFKD", ch) if "A" <= c <= "Z")
    return letters
