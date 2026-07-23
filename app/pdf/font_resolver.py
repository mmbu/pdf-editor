from __future__ import annotations

import json
import os
import tempfile
import urllib.parse
import urllib.request
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

_CACHE_DIR = Path(tempfile.gettempdir()) / "pdf-editor-fonts"


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


def _download_google_font(font_name: str) -> Path | None:
    try:
        query = urllib.parse.quote(font_name)
        url = f"https://fonts.google.com/download/list?family={query}"
        with urllib.request.urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload:
            return None

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        for item in payload:
            file_url = item.get("file")
            if not file_url:
                continue
            filename = Path(urllib.parse.urlparse(file_url).path).name
            target = _CACHE_DIR / filename
            if not target.exists():
                with urllib.request.urlopen(file_url, timeout=15) as font_response:
                    target.write_bytes(font_response.read())
            return target
    except Exception:
        return None
    return None


def resolve_font(
    font_name: str,
    bold: bool = False,
    italic: bool = False,
) -> tuple[fitz.Font, str | None, str | None]:
    alias_key = font_name.lower().replace(" ", "")
    if alias_key in BASE14_ALIASES:
        base_name = BASE14_ALIASES[alias_key]
        return fitz.Font(base_name), None, None

    font_file = _find_system_font_file(font_name)
    if font_file is not None:
        return fitz.Font(fontfile=str(font_file)), str(font_file), None

    web_font = _download_google_font(font_name)
    if web_font is not None:
        return fitz.Font(fontfile=str(web_font)), str(web_font), None

    fallback = "helvB" if bold else "helv"
    warning = (
        f"Шрифт «{font_name}» не найден. "
        f"Использован заменитель ({fallback})."
    )
    return fitz.Font(fallback), None, warning
