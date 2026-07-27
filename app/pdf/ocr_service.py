from __future__ import annotations

import io
import os
import re
import sys
from pathlib import Path

import fitz

from app.pdf.models import TextWord

try:
    import pytesseract
    from PIL import Image
    _HAS_TESSERACT = True
except ImportError:
    _HAS_TESSERACT = False

DEFAULT_LANGS = ("rus", "eng", "heb")
HEBREW_RE = re.compile(r"[\u0590-\u05FF]")


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


TESSDATA_DIR = _project_root() / "resources" / "tessdata"


def _configure_tesseract() -> None:
    if os.environ.get("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
    else:
        candidates = [
            _project_root() / "tesseract" / "tesseract.exe",
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
        ]
        for path in candidates:
            if path.exists():
                pytesseract.pytesseract.tesseract_cmd = str(path)
                break

    if TESSDATA_DIR.exists():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA_DIR)


def _tesseract_config() -> str:
    if TESSDATA_DIR.exists():
        return f'--tessdata-dir "{TESSDATA_DIR}" --psm 6'
    return "--psm 6"


def is_tesseract_available() -> bool:
    if not _HAS_TESSERACT:
        return False
    try:
        _configure_tesseract()
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _available_langs() -> set[str]:
    if TESSDATA_DIR.exists():
        return {path.stem for path in TESSDATA_DIR.glob("*.traineddata") if path.stem != "osd"}

    try:
        _configure_tesseract()
        raw = pytesseract.get_languages(config="")
        return set(raw)
    except Exception:
        return {"eng"}


def _lang_string() -> str:
    installed = _available_langs()
    selected = [lang for lang in DEFAULT_LANGS if lang in installed]
    if not selected:
        selected = ["eng"] if "eng" in installed else sorted(installed)[:1]
    return "+".join(selected)


def detect_rtl(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    hebrew_count = sum(1 for char in letters if HEBREW_RE.match(char))
    return hebrew_count / len(letters) >= 0.4


def ocr_page_words(page: fitz.Page, page_index: int, dpi: int = 200) -> list[TextWord]:
    try:
        if not is_tesseract_available():
            return []

        _configure_tesseract()
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))

        scale_x = page.rect.width / pix.width
        scale_y = page.rect.height / pix.height
        lang = _lang_string()

        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            config=_tesseract_config(),
        )

        words: list[TextWord] = []
        count = len(data["text"])
        for index in range(count):
            text = (data["text"][index] or "").strip()
            conf = int(float(data["conf"][index])) if str(data["conf"][index]).isdigit() else -1
            if not text or conf < 40:
                continue

            x = float(data["left"][index]) * scale_x
            y = float(data["top"][index]) * scale_y
            w = float(data["width"][index]) * scale_x
            h = float(data["height"][index]) * scale_y
            bbox = fitz.Rect(x, y, x + w, y + h)

            words.append(
                TextWord(
                    page_index=page_index,
                    text=text,
                    bbox=bbox,
                    font_name="helv",
                    font_size=max(h * 0.85, 8.0),
                    color=0,
                    flags=0,
                    origin=(bbox.x0, bbox.y1),
                )
            )
        return words
    except Exception:
        return []
