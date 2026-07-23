from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class BaseToolView(QWidget):
    back_requested = Signal()

    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self._title = title

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(8, 8, 8, 8)

        header = QHBoxLayout()
        self.back_button = QPushButton("← На главную")
        self.back_button.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_button)
        header.addStretch()
        self.root.addLayout(header)

        self.content = QVBoxLayout()
        self.root.addLayout(self.content, stretch=1)

    def set_status(self, message: str) -> None:
        window = self.window()
        if hasattr(window, "statusBar"):
            window.statusBar().showMessage(message)
