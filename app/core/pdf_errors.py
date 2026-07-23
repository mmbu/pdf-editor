from __future__ import annotations

from pathlib import Path

import fitz


class PdfUserError(Exception):
    """Понятная пользователю ошибка работы с PDF."""


def format_pdf_error(error: Exception) -> str:
    message = str(error).strip()
    lowered = message.lower()

    if "password" in lowered or "encrypted" in lowered or "authentication" in lowered:
        return "PDF защищён паролем. Сначала снимите защиту в другой программе."
    if "format error" in lowered or "corrupt" in lowered or "invalid" in lowered:
        return "Файл повреждён или это не PDF. Проверьте файл и попробуйте снова."
    if "memory" in lowered:
        return "Файл слишком большой для обработки. Закройте другие программы и повторите."
    if message:
        return f"Не удалось обработать PDF: {message}"
    return "Не удалось обработать PDF из-за неизвестной ошибки."


def open_pdf_safe(path: Path) -> fitz.Document:
    if not path.exists():
        raise PdfUserError(f"Файл не найден: {path.name}")

    if path.stat().st_size == 0:
        raise PdfUserError("Файл пуст.")

    if path.suffix.lower() != ".pdf":
        raise PdfUserError("Ожидался PDF-файл с расширением .pdf")

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise PdfUserError(format_pdf_error(exc)) from exc

    if doc.is_encrypted and not doc.authenticate(""):
        doc.close()
        raise PdfUserError("PDF защищён паролем. Откройте его без пароля или снимите защиту.")

    if doc.page_count == 0:
        doc.close()
        raise PdfUserError("PDF не содержит страниц.")

    return doc
