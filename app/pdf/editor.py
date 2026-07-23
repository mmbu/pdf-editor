from __future__ import annotations

import fitz

from app.pdf.font_resolver import resolve_font
from app.pdf.models import TextSpan


def _color_to_rgb(color: int) -> tuple[float, float, float]:
    r = ((color >> 16) & 255) / 255
    g = ((color >> 8) & 255) / 255
    b = (color & 255) / 255
    return (r, g, b)


def replace_text_span(page: fitz.Page, span: TextSpan, new_text: str) -> str | None:
    if new_text == span.text:
        return None

    page.add_redact_annot(span.bbox, fill=(1, 1, 1))
    page.apply_redactions()

    font, font_file = resolve_font(span.font_name, span.is_bold, span.is_italic)
    rgb = _color_to_rgb(span.color)

    if font_file:
        page.insert_font(fontname="editfont", fontfile=font_file)

    writer = fitz.TextWriter(page.rect)
    writer.append(
        span.origin,
        new_text,
        font=font,
        fontsize=span.font_size,
    )
    writer.write_text(page, color=rgb)
    return "Использован системный или базовый шрифт-заменитель." if font_file is None else None
