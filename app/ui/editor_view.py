from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QScrollArea,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.core.session import DocumentSession
from app.pdf.editor import replace_text_span
from app.pdf.scan_detector import is_page_scanned
from app.shell.tool_registry import register_tool
from app.ui.base_tool_view import BaseToolView
from app.ui.page_widget import PageWidget


@register_tool(
    tool_id="edit",
    title="Редактировать PDF",
    description="Клик по тексту для правки",
    icon="📝",
)
class EditorView(BaseToolView):
    ZOOM = 1.5

    def __init__(self, parent=None) -> None:
        super().__init__("Редактировать PDF", parent)
        self.session = DocumentSession()
        self.page_widgets: list[PageWidget] = []

        toolbar = QToolBar("Редактор")
        self.content.addWidget(toolbar)

        open_action = QAction("Открыть", self)
        open_action.triggered.connect(lambda: self.open_file())
        toolbar.addAction(open_action)

        save_action = QAction("Сохранить как", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        toolbar.addAction(self.undo_action)

        self.redo_action = QAction("Повторить", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo)
        toolbar.addAction(self.redo_action)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.pages_container = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_container)
        self.pages_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.scroll_area.setWidget(self.pages_container)

        self.content.addWidget(self.scroll_area)
        self._show_placeholder()
        self.setAcceptDrops(True)

    def _show_placeholder(self) -> None:
        self._clear_pages()
        label = QLabel("Откройте PDF или перетащите файл сюда.\nКликните по слову — редактирование прямо на странице.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 16px; padding: 48px;")
        self.pages_layout.addWidget(label)

    def _clear_pages(self) -> None:
        while self.pages_layout.count():
            item = self.pages_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.page_widgets.clear()

    def open_file(self, path: Path | None = None) -> None:
        if path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Открыть PDF",
                "",
                "PDF файлы (*.pdf)",
            )
            if not file_path:
                return
            path = Path(file_path)

        try:
            self.session.open(path)
            self._render_all_pages()
            scanned_pages = sum(
                1
                for index in range(self.session.pdf.page_count)
                if is_page_scanned(self.session.pdf.page(index))
            )
            if scanned_pages:
                self.set_status(
                    f"Открыт: {path.name}. OCR-страниц: {scanned_pages}"
                )
            else:
                self.set_status(f"Открыт: {path.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF:\n{exc}")

    def _render_all_pages(self) -> None:
        self._clear_pages()
        for index in range(self.session.pdf.page_count):
            widget = PageWidget(self.session.pdf, index, self.ZOOM, self)
            widget.word_edit_committed.connect(self._on_word_edit_committed)
            self.page_widgets.append(widget)
            self.pages_layout.addWidget(widget)
        self._update_undo_actions()

    def _on_word_edit_committed(self, page_index: int, word: TextWord, new_text: str) -> None:
        if new_text == word.text:
            return

        try:
            page = self.session.pdf.page(page_index)
            warning = replace_text_span(page, word, new_text)
            self.session.record_change()
            self.page_widgets[page_index].refresh()
            message = "Текст изменён"
            if warning:
                message += f". {warning}"
            self.set_status(message)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить текст:\n{exc}")
        finally:
            self._update_undo_actions()

    def save_file(self) -> None:
        if not self.session.is_open:
            QMessageBox.information(self, "Сохранение", "Сначала откройте PDF-файл.")
            return

        default_name = "edited.pdf"
        if self.session.current_path is not None:
            default_name = f"{self.session.current_path.stem}_edited.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF",
            default_name,
            "PDF файлы (*.pdf)",
        )
        if not file_path:
            return

        try:
            self.session.save_as(Path(file_path))
            self.set_status(f"Сохранено: {file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить PDF:\n{exc}")

    def undo(self) -> None:
        if not self.session.undo():
            return
        self._refresh_after_history()
        self.set_status("Отменено")

    def redo(self) -> None:
        if not self.session.redo():
            return
        self._refresh_after_history()
        self.set_status("Повторено")

    def _refresh_after_history(self) -> None:
        for widget in self.page_widgets:
            widget.pdf = self.session.pdf
            widget.refresh()
        self._update_undo_actions()

    def _update_undo_actions(self) -> None:
        self.undo_action.setEnabled(self.session.can_undo())
        self.redo_action.setEnabled(self.session.can_redo())

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() == ".pdf":
                self.open_file(path)
                event.acceptProposedAction()
                return
