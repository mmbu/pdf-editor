from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QStatusBar

from app.pdf.image_converter import is_image_path
from app.shell.home_screen import HomeScreen
from app.shell.tool_registry import get_tools
from app.ui.convert_view import ConvertView
from app.ui.styles import SHORTCUTS_HELP
import app.tools  # noqa: F401 — регистрация инструментов


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Editor")
        self.resize(1200, 820)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setStatusBar(QStatusBar())

        self.home = HomeScreen()
        self.home.tool_selected.connect(self.open_tool)
        self.stack.addWidget(self.home)

        self._tools: dict[str, object] = {}
        for tool in get_tools():
            widget = tool.factory()
            if hasattr(widget, "back_requested"):
                widget.back_requested.connect(self.show_home)
            self._tools[tool.tool_id] = widget
            self.stack.addWidget(widget)

        self.stack.setCurrentWidget(self.home)
        self.setAcceptDrops(True)
        self._build_menu()

    def _build_menu(self) -> None:
        nav_menu = self.menuBar().addMenu("Навигация")
        home_action = QAction("На главную", self)
        home_action.setShortcut(QKeySequence("Ctrl+H"))
        home_action.triggered.connect(self.show_home)
        nav_menu.addAction(home_action)

        help_menu = self.menuBar().addMenu("Справка")
        shortcuts_action = QAction("Горячие клавиши", self)
        shortcuts_action.setShortcut(QKeySequence("F1"))
        shortcuts_action.triggered.connect(self._show_shortcuts_help)
        help_menu.addAction(shortcuts_action)

    def _show_shortcuts_help(self) -> None:
        QMessageBox.information(self, "Горячие клавиши", SHORTCUTS_HELP.strip())

    def show_home(self) -> None:
        self.stack.setCurrentWidget(self.home)
        self.setWindowTitle("PDF Editor")
        self.statusBar().showMessage("Готово")

    def open_tool(self, tool_id: str, path: Path | None = None) -> None:
        widget = self._tools.get(tool_id)
        if widget is None:
            return
        self.stack.setCurrentWidget(widget)
        tool = next(t for t in get_tools() if t.tool_id == tool_id)
        self.setWindowTitle(f"PDF Editor — {tool.title}")

        if path is not None and hasattr(widget, "open_file"):
            widget.open_file(path)
        elif path is not None and hasattr(widget, "add_files") and path.suffix.lower() == ".pdf":
            widget.add_files([path])
        elif path is not None and hasattr(widget, "add_images") and is_image_path(path):
            widget.add_images([path])
        elif path is not None and hasattr(widget, "source_path"):
            widget.source_path.setText(str(path))

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape and self.stack.currentWidget() is not self.home:
            self.show_home()
            event.accept()
            return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event) -> None:
        if not event.mimeData().hasUrls():
            return
        for url in event.mimeData().urls():
            local = Path(url.toLocalFile())
            if local.suffix.lower() == ".pdf" or is_image_path(local):
                event.acceptProposedAction()
                return

    def dropEvent(self, event) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        pdfs = [p for p in paths if p.suffix.lower() == ".pdf"]
        images = [p for p in paths if is_image_path(p)]

        if pdfs:
            current = self.stack.currentWidget()
            if current is not self.home and hasattr(current, "open_file"):
                current.open_file(pdfs[0])
            elif current is not self.home and hasattr(current, "add_files"):
                current.add_files(pdfs)
            elif current is not self.home and hasattr(current, "source_path"):
                current.source_path.setText(str(pdfs[0]))
            else:
                self.open_tool("edit", pdfs[0])
        elif images:
            current = self.stack.currentWidget()
            if current is not self.home and hasattr(current, "add_images"):
                current.add_images(images)
            else:
                self.open_tool("convert")
                convert = self._tools.get("convert")
                if isinstance(convert, ConvertView):
                    convert.add_images(images)

        event.acceptProposedAction()
