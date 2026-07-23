from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent
from PySide6.QtWidgets import QLineEdit

from app.pdf.models import TextWord
from app.pdf.ocr_service import detect_rtl


class InlineTextEditor(QLineEdit):
    committed = Signal(str)
    cancelled = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._word: TextWord | None = None
        self._closing = False
        self.setFrame(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def open_for_word(self, word: TextWord, zoom: float) -> None:
        self._word = word
        self._closing = False
        self.setText(word.text)
        self.selectAll()

        font = QFont()
        font.setPointSizeF(max(word.font_size * zoom * 0.72, 8))
        font.setBold(word.is_bold)
        font.setItalic(word.is_italic)
        self.setFont(font)

        color = QColor(
            (word.color >> 16) & 255,
            (word.color >> 8) & 255,
            word.color & 255,
        )
        self.setStyleSheet(
            f"""
            InlineTextEditor {{
                background: rgba(255, 255, 255, 245);
                border: 2px solid #4285f4;
                border-radius: 2px;
                padding: 0 2px;
                color: {color.name()};
            }}
            """
        )

        if detect_rtl(word.text):
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.setAlignment(Qt.AlignmentFlag.AlignLeft)

        screen_rect = self._word_screen_rect(word, zoom)
        self.setGeometry(screen_rect)
        self.show()
        self.raise_()
        self.setFocus()

    def _word_screen_rect(self, word: TextWord, zoom: float) -> object:
        from PySide6.QtCore import QRect

        padding = 4
        x = int(word.bbox.x0 * zoom) - padding
        y = int(word.bbox.y0 * zoom) - padding
        w = int(word.bbox.width * zoom) + padding * 2 + 40
        h = int(word.bbox.height * zoom) + padding * 2
        return QRect(max(x, 0), max(y, 0), max(w, 80), max(h, 20))

    def _finish(self, commit: bool) -> None:
        if self._closing or self._word is None:
            return
        self._closing = True
        if commit:
            self.committed.emit(self.text())
        else:
            self.cancelled.emit()
        self.hide()
        self._word = None
        self._closing = False

    def commit_and_close(self) -> None:
        self._finish(commit=True)

    def cancel_and_close(self) -> None:
        self._finish(commit=False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._finish(commit=False)
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._finish(commit=True)
            event.accept()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event) -> None:
        if self.isVisible() and not self._closing:
            self._finish(commit=True)
        super().focusOutEvent(event)
