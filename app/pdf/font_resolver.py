from __future__ import annotations

import os
from pathlib import Path

import fitz

BASE14_ALIASES = {
    "helvetica": "helv",
    "helvetica-bold": "helvB",
    "helvetica-oblique": "helvO",
    "helvetica-boldoblique": "helvBO",
    "times-roman": "times",
    "times-bold": "timesB",
    "times-italic": "timesI",
    "times-bolditalic": "timesBI",
    "courier": "cour",
    "courier-bold": "courB",
    "courier-oblique": "courO",
    "courier-boldoblique": "courBO",
}


def _normalize_font_name(name: str) -> str:
    return name.lower().replace(" ", "").replace(",", "").replace("-", "")


def _windows_fonts_dir() -> Path:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    return Path(windir) / "Fonts"


def _find_system_font_file(font_name: str) -> Path | None:
    fonts_dir = _windows_fonts_dir()
    if not fonts_dir.exists():
        return None

    normalized = _normalize_font_name(font_name)
    candidates = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))
    for path in candidates:
        stem = _normalize_font_name(path.stem)
        if normalized in stem or stem in normalized:
            return path
    return None


def resolve_font(font_name: str, bold: bool = False, italic: bool = False) -> tuple[fitz.Font, str | None]:
    alias_key = font_name.lower().replace(" ", "")
    if alias_key in BASE14_ALIASES:
        base_name = BASE14_ALIASES[alias_key]
        return fitz.Font(base_name), None

    font_file = _find_system_font_file(font_name)
    if font_file is not None:
        return fitz.Font(fontfile=str(font_file)), str(font_file)

    fallback = "helvB" if bold else "helv"
    return fitz.Font(fallback), None
