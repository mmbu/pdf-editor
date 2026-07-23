from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.shell.tool_registry import ToolDefinition, get_tools


class ToolButton(QFrame):
    clicked = Signal(str)

    def __init__(self, tool: ToolDefinition, parent=None) -> None:
        super().__init__(parent)
        self.tool_id = tool.tool_id
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            """
            ToolButton {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 12px;
            }
            ToolButton:hover {
                background: #e8f0fe;
                border-color: #4285f4;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel(tool.icon)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 36px; border: none; background: transparent;")

        title = QLabel(tool.title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 14px; font-weight: 600; border: none; background: transparent;")

        desc = QLabel(tool.description)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11px; color: #666; border: none; background: transparent;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.tool_id)
        super().mousePressEvent(event)


class HomeScreen(QWidget):
    tool_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)

        header = QLabel("PDF Editor")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: 700; margin-bottom: 8px;")

        hint = QLabel("Выберите инструмент или перетащите PDF / изображение в окно")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 13px; color: #666; margin-bottom: 24px;")

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setSpacing(16)

        tools = get_tools()
        columns = 3
        for index, tool in enumerate(tools):
            button = ToolButton(tool)
            button.clicked.connect(self.tool_selected.emit)
            row, col = divmod(index, columns)
            grid.addWidget(button, row, col)

        for col in range(columns):
            grid.setColumnStretch(col, 1)

        root.addWidget(header)
        root.addWidget(hint)
        root.addStretch()
        root.addWidget(grid_host)
        root.addStretch()
