from __future__ import annotations

from pathlib import Path

import fitz

from app.pdf.extractor import extract_text_spans
from app.pdf.models import TextSpan


class PdfDocument:
    def __init__(self, path: Path | None = None) -> None:
        self.path: Path | None = path
        self.doc: fitz.Document | None = None
        if path is not None:
            self.open(path)

    def open(self, path: Path) -> None:
        self.close()
        self.path = path
        self.doc = fitz.open(str(path))

    def close(self) -> None:
        if self.doc is not None:
            self.doc.close()
            self.doc = None

    @property
    def page_count(self) -> int:
        return len(self.doc) if self.doc else 0

    def page(self, index: int) -> fitz.Page:
        if self.doc is None:
            raise RuntimeError("Документ не открыт")
        return self.doc[index]

    def render_page(self, index: int, zoom: float = 1.5) -> fitz.Pixmap:
        page = self.page(index)
        matrix = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=matrix, alpha=False)

    def get_spans(self, page_index: int) -> list[TextSpan]:
        return extract_text_spans(self.page(page_index), page_index)

    def save_as(self, path: Path) -> None:
        if self.doc is None:
            raise RuntimeError("Документ не открыт")
        self.doc.save(str(path), garbage=4, deflate=True)
        self.path = path

    def snapshot(self) -> bytes:
        if self.doc is None:
            raise RuntimeError("Документ не открыт")
        return self.doc.tobytes()

    def restore(self, data: bytes) -> None:
        self.close()
        self.doc = fitz.open(stream=data, filetype="pdf")
