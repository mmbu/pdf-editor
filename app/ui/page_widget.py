from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.pdf.document import PdfDocument
from app.pdf.extractor import find_span_at_point
from app.pdf.models import TextSpan


class PageWidget(QWidget):
    span_clicked = Signal(int, object)

    def __init__(self, pdf: PdfDocument, page_index: int, zoom: float, parent=None) -> None:
        super().__init__(parent)
        self.pdf = pdf
        self.page_index = page_index
        self.zoom = zoom
        self.spans: list[TextSpan] = []

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.addWidget(self.image_label)

        self.refresh()

    def refresh(self) -> None:
        pixmap = QPixmap()
        pix = self.pdf.render_page(self.page_index, self.zoom)
        pixmap.loadFromData(pix.tobytes("png"))
        self.image_label.setPixmap(pixmap)
        self.spans = self.pdf.get_spans(self.page_index)
        self.setFixedSize(pixmap.size())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)

        label_pos = self.image_label.mapFrom(self, event.position().toPoint())
        if not self.image_label.rect().contains(label_pos):
            return super().mousePressEvent(event)

        pdf_x = label_pos.x() / self.zoom
        pdf_y = label_pos.y() / self.zoom
        span = find_span_at_point(self.spans, pdf_x, pdf_y)
        if span is not None:
            self.span_clicked.emit(self.page_index, span)
        super().mousePressEvent(event)
