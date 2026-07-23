from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.pdf.document import PdfDocument
from app.pdf.extractor import find_word_at_point
from app.pdf.models import TextWord
from app.ui.inline_text_editor import InlineTextEditor


class PageWidget(QWidget):
    word_edit_committed = Signal(int, object, str)
    word_edit_cancelled = Signal()

    def __init__(self, pdf: PdfDocument, page_index: int, zoom: float, parent=None) -> None:
        super().__init__(parent)
        self.pdf = pdf
        self.page_index = page_index
        self.zoom = zoom
        self.words: list[TextWord] = []
        self._hover_word: TextWord | None = None
        self._active_word: TextWord | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMouseTracking(True)
        layout.addWidget(self.image_label)

        self.highlight = QLabel(self.image_label)
        self.highlight.setStyleSheet("background: rgba(66, 133, 244, 60); border: 1px solid #4285f4;")
        self.highlight.hide()

        self.inline_editor = InlineTextEditor(self.image_label)
        self.inline_editor.hide()
        self.inline_editor.committed.connect(self._on_editor_committed)
        self.inline_editor.cancelled.connect(self._on_editor_cancelled)

        self.setMouseTracking(True)
        self.refresh()

    def refresh(self) -> None:
        if self.inline_editor.isVisible():
            self.inline_editor.commit_and_close()
        pixmap = QPixmap()
        pix = self.pdf.render_page(self.page_index, self.zoom)
        pixmap.loadFromData(pix.tobytes("png"))
        self.image_label.setPixmap(pixmap)
        self.words = self.pdf.get_words(self.page_index)
        self.setFixedSize(pixmap.size())
        self._hover_word = None
        self.highlight.hide()

    def _pdf_point_from_event(self, event: QMouseEvent) -> tuple[float, float] | None:
        label_pos = self.image_label.mapFrom(self, event.position().toPoint())
        if not self.image_label.rect().contains(label_pos):
            return None
        return label_pos.x() / self.zoom, label_pos.y() / self.zoom

    def _show_hover(self, word: TextWord | None) -> None:
        if word is None:
            self.highlight.hide()
            self._hover_word = None
            return
        if self._active_word is not None:
            return
        self._hover_word = word
        x = int(word.bbox.x0 * self.zoom)
        y = int(word.bbox.y0 * self.zoom)
        w = int(word.bbox.width * self.zoom)
        h = int(word.bbox.height * self.zoom)
        self.highlight.setGeometry(x, y, w, h)
        self.highlight.show()
        self.highlight.raise_()

    def _open_editor(self, word: TextWord) -> None:
        self._active_word = word
        self.highlight.hide()
        self.inline_editor.open_for_word(word, self.zoom)
        self.inline_editor.raise_()

    def _on_editor_committed(self, new_text: str) -> None:
        if self._active_word is None:
            return
        if new_text != self._active_word.text:
            self.word_edit_committed.emit(self.page_index, self._active_word, new_text)
        self.inline_editor.hide()
        self._active_word = None

    def _on_editor_cancelled(self) -> None:
        self.inline_editor.hide()
        self._active_word = None
        self.word_edit_cancelled.emit()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._active_word is not None:
            return super().mouseMoveEvent(event)
        point = self._pdf_point_from_event(event)
        if point is None:
            self._show_hover(None)
        else:
            self._show_hover(find_word_at_point(self.words, point[0], point[1]))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)

        point = self._pdf_point_from_event(event)
        if point is None:
            if self.inline_editor.isVisible():
                self.inline_editor.commit_and_close()
            return super().mousePressEvent(event)

        word = find_word_at_point(self.words, point[0], point[1])
        if word is None:
            if self.inline_editor.isVisible():
                self.inline_editor.commit_and_close()
            return super().mousePressEvent(event)

        if self.inline_editor.isVisible() and self._active_word != word:
            self.inline_editor.commit_and_close()

        if not self.inline_editor.isVisible():
            self._open_editor(word)

        super().mousePressEvent(event)

    def leaveEvent(self, event) -> None:
        if self._active_word is None:
            self._show_hover(None)
        super().leaveEvent(event)
