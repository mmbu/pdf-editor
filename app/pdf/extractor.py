from __future__ import annotations

import fitz

from app.pdf.models import TextSpan, TextWord


def _find_span_for_bbox(spans: list[TextSpan], bbox: fitz.Rect) -> TextSpan | None:
    center_x = (bbox.x0 + bbox.x1) / 2
    center_y = (bbox.y0 + bbox.y1) / 2
    hit = find_span_at_point(spans, center_x, center_y)
    if hit is not None:
        return hit

    best: TextSpan | None = None
    best_area = 0.0
    for span in spans:
        intersection = span.bbox & bbox
        if intersection.is_empty:
            continue
        area = intersection.width * intersection.height
        if area > best_area:
            best_area = area
            best = span
    return best


def extract_text_words(page: fitz.Page, page_index: int) -> list[TextWord]:
    spans = extract_text_spans(page, page_index)
    words: list[TextWord] = []

    for x0, y0, x1, y1, text, *_rest in page.get_text("words"):
        if not text.strip():
            continue
        bbox = fitz.Rect(x0, y0, x1, y1)
        parent = _find_span_for_bbox(spans, bbox)
        if parent is None:
            continue
        words.append(
            TextWord(
                page_index=page_index,
                text=text,
                bbox=bbox,
                font_name=parent.font_name,
                font_size=parent.font_size,
                color=parent.color,
                flags=parent.flags,
                origin=(bbox.x0, bbox.y1),
            )
        )
    return words


def find_word_at_point(words: list[TextWord], x: float, y: float) -> TextWord | None:
    hits = [word for word in words if word.contains_point(x, y)]
    if not hits:
        return None
    return min(hits, key=lambda word: word.bbox.width * word.bbox.height)


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
