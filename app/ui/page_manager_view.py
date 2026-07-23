from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from app.core.session import DocumentSession
from app.pdf.page_ops import delete_page, insert_pages, reorder_pages
from app.shell.tool_registry import register_tool
from app.ui.base_tool_view import BaseToolView


THUMB_ZOOM = 0.35


@register_tool(
    tool_id="reorder",
    title="Изменить порядок страниц",
    description="Сортировка, удаление, вставка",
    icon="↕️",
)
class PageManagerView(BaseToolView):
    def __init__(self, parent=None) -> None:
        super().__init__("Страницы PDF", parent)
        self.session = DocumentSession()

        toolbar = QToolBar("Страницы")
        self.content.addWidget(toolbar)
        toolbar.addAction("Открыть", lambda: self.open_file())
        toolbar.addAction("Сохранить как", self.save_file)
        toolbar.addAction("Отменить", self.undo)
        toolbar.addAction("Повторить", self.redo)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Миниатюры страниц (перетащите для сортировки)"))

        self.page_list = QListWidget()
        self.page_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.page_list.setMovement(QListWidget.Movement.Snap)
        self.page_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.page_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.page_list.setSpacing(12)
        self.page_list.setMinimumWidth(280)
        self.page_list.currentRowChanged.connect(self._update_buttons)
        self.page_list.model().rowsMoved.connect(self._on_rows_moved)
        left_layout.addWidget(self.page_list)

        buttons = QHBoxLayout()
        self.up_btn = QPushButton("↑ Вверх")
        self.down_btn = QPushButton("↓ Вниз")
        self.delete_btn = QPushButton("Удалить")
        self.insert_btn = QPushButton("Вставить из PDF…")
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        self.delete_btn.clicked.connect(self.delete_current)
        self.insert_btn.clicked.connect(self.insert_from_pdf)
        for btn in (self.up_btn, self.down_btn, self.delete_btn, self.insert_btn):
            buttons.addWidget(btn)
        left_layout.addLayout(buttons)

        self.preview = QLabel("Откройте PDF для управления страницами")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(400, 500)
        self.preview.setStyleSheet("background: #fafafa; border: 1px solid #ddd;")

        splitter.addWidget(left)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(1, 1)
        self.content.addWidget(splitter)

        self.page_list.currentRowChanged.connect(self._update_preview)
        self.setAcceptDrops(True)
        self._update_buttons()

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
            self._reload_thumbnails()
            self.set_status(f"Открыт: {path.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF:\n{exc}")

    def _reload_thumbnails(self) -> None:
        self.page_list.blockSignals(True)
        self.page_list.clear()
        if not self.session.is_open:
            self.page_list.blockSignals(False)
            return

        for index in range(self.session.pdf.page_count):
            pix = self.session.pdf.render_page(index, THUMB_ZOOM)
            pixmap = QPixmap()
            pixmap.loadFromData(pix.tobytes("png"))
            item = QListWidgetItem(QIcon(pixmap), f"Стр. {index + 1}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.page_list.addItem(item)

        self.page_list.blockSignals(False)
        if self.page_list.count():
            self.page_list.setCurrentRow(0)
        self._update_buttons()

    def _update_preview(self, row: int) -> None:
        if row < 0 or not self.session.is_open:
            return
        pix = self.session.pdf.render_page(row, 1.2)
        pixmap = QPixmap()
        pixmap.loadFromData(pix.tobytes("png"))
        self.preview.setPixmap(pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _update_buttons(self, _row: int = -1) -> None:
        row = self.page_list.currentRow()
        count = self.page_list.count()
        enabled = count > 0 and self.session.is_open
        self.up_btn.setEnabled(enabled and row > 0)
        self.down_btn.setEnabled(enabled and 0 <= row < count - 1)
        self.delete_btn.setEnabled(enabled and count > 1)
        self.insert_btn.setEnabled(enabled)

    def _on_rows_moved(self, *args) -> None:
        if not self.session.is_open:
            return
        order = self._current_visual_order()
        if order == list(range(len(order))):
            return
        self._apply_order(order)

    def _current_visual_order(self) -> list[int]:
        order: list[int] = []
        for row in range(self.page_list.count()):
            item = self.page_list.item(row)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        return order

    def _apply_order(self, target_order: list[int]) -> None:
        doc = self.session.pdf.doc
        if doc is None:
            return

        try:
            reorder_pages(doc, target_order)
            self.session.record_change()
            self._reload_thumbnails()
            self.set_status("Порядок страниц изменён")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def move_up(self) -> None:
        row = self.page_list.currentRow()
        if row <= 0:
            return
        order = self._current_visual_order()
        order[row - 1], order[row] = order[row], order[row - 1]
        self._apply_order(order)
        self.page_list.setCurrentRow(row - 1)

    def move_down(self) -> None:
        row = self.page_list.currentRow()
        if row < 0 or row >= self.page_list.count() - 1:
            return
        order = self._current_visual_order()
        order[row + 1], order[row] = order[row], order[row + 1]
        self._apply_order(order)
        self.page_list.setCurrentRow(row + 1)

    def delete_current(self) -> None:
        row = self.page_list.currentRow()
        if row < 0 or self.session.pdf.doc is None:
            return
        if self.session.pdf.page_count <= 1:
            QMessageBox.warning(self, "Удаление", "Нельзя удалить единственную страницу.")
            return

        reply = QMessageBox.question(
            self,
            "Удалить страницу",
            f"Удалить страницу {row + 1}?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_page(self.session.pdf.doc, row)
            self.session.record_change()
            self._reload_thumbnails()
            self.set_status(f"Страница {row + 1} удалена")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def insert_from_pdf(self) -> None:
        row = self.page_list.currentRow()
        if row < 0:
            row = self.page_list.count()
        if self.session.pdf.doc is None:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF для вставки",
            "",
            "PDF файлы (*.pdf)",
        )
        if not file_path:
            return

        try:
            insert_pages(self.session.pdf.doc, row + 1, Path(file_path))
            self.session.record_change()
            self._reload_thumbnails()
            self.set_status("Страницы вставлены")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось вставить страницы:\n{exc}")

    def save_file(self) -> None:
        if not self.session.is_open:
            QMessageBox.information(self, "Сохранение", "Сначала откройте PDF.")
            return

        default = "pages_edited.pdf"
        if self.session.current_path:
            default = f"{self.session.current_path.stem}_pages.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF",
            default,
            "PDF файлы (*.pdf)",
        )
        if not file_path:
            return

        try:
            self.session.save_as(Path(file_path))
            self.set_status(f"Сохранено: {file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def undo(self) -> None:
        if not self.session.undo():
            return
        self._reload_thumbnails()
        self.set_status("Отменено")

    def redo(self) -> None:
        if not self.session.redo():
            return
        self._reload_thumbnails()
        self.set_status("Повторено")

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
