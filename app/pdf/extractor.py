from __future__ import annotations

import fitz

from app.pdf.models import TextSpan


def extract_text_spans(page: fitz.Page, page_index: int) -> list[TextSpan]:
    spans: list[TextSpan] = []
    data = page.get_text("dict")

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text.strip():
                    continue
                spans.append(
                    TextSpan(
                        page_index=page_index,
                        text=text,
                        bbox=fitz.Rect(span["bbox"]),
                        font_name=span.get("font", "helv"),
                        font_size=float(span.get("size", 12)),
                        color=int(span.get("color", 0)),
                        flags=int(span.get("flags", 0)),
                        origin=tuple(span.get("origin", (span["bbox"][0], span["bbox"][3]))),
                    )
                )
    return spans


def find_span_at_point(spans: list[TextSpan], x: float, y: float) -> TextSpan | None:
    hits = [span for span in spans if span.contains_point(x, y)]
    if not hits:
        return None
    return min(hits, key=lambda span: span.bbox.width * span.bbox.height)
