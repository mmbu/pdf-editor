from __future__ import annotations

import fitz

from app.pdf.font_resolver import resolve_font
from app.pdf.models import TextSpan, TextWord


def _color_to_rgb(color: int) -> tuple[float, float, float]:
    r = ((color >> 16) & 255) / 255
    g = ((color >> 8) & 255) / 255
    b = (color & 255) / 255
    return (r, g, b)


def replace_text_span(page: fitz.Page, span: TextSpan | TextWord, new_text: str) -> str | None:
    target = span.to_span() if hasattr(span, "to_span") else span
    if new_text == target.text:
        return None

    page.add_redact_annot(target.bbox, fill=(1, 1, 1))
    page.apply_redactions()

    font, font_file, font_warning = resolve_font(target.font_name, target.is_bold, target.is_italic)
    rgb = _color_to_rgb(target.color)

    if font_file:
        page.insert_font(fontname="editfont", fontfile=font_file)

    writer = fitz.TextWriter(page.rect)
    writer.append(
        target.origin,
        new_text,
        font=font,
        fontsize=target.font_size,
    )
    writer.write_text(page, color=rgb)
    return font_warning
