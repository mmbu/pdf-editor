from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.pdf.page_ops import merge_documents
from app.shell.tool_registry import register_tool
from app.ui.base_tool_view import BaseToolView


@register_tool(
    tool_id="merge",
    title="Объединить несколько в один",
    description="Merge PDF-файлов",
    icon="📎",
)
class MergeView(BaseToolView):
    def __init__(self, parent=None) -> None:
        super().__init__("Объединить PDF", parent)

        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.content.addWidget(QLabel("Файлы будут объединены сверху вниз:"))
        self.content.addWidget(self.file_list)

        buttons = QHBoxLayout()
        add_btn = QPushButton("Добавить PDF…")
        remove_btn = QPushButton("Убрать")
        merge_btn = QPushButton("Объединить и сохранить…")
        add_btn.clicked.connect(self.add_files)
        remove_btn.clicked.connect(self.remove_selected)
        merge_btn.clicked.connect(self.merge_and_save)
        buttons.addWidget(add_btn)
        buttons.addWidget(remove_btn)
        buttons.addStretch()
        buttons.addWidget(merge_btn)
        self.content.addLayout(buttons)

        self.setAcceptDrops(True)

    def add_files(self, paths: list[Path] | None = None) -> None:
        if paths is None:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Выберите PDF",
                "",
                "PDF файлы (*.pdf)",
            )
            paths = [Path(f) for f in files]
        for path in paths:
            if path.suffix.lower() == ".pdf" and not self._contains(path):
                self.file_list.addItem(str(path))

    def _contains(self, path: Path) -> bool:
        for row in range(self.file_list.count()):
            if Path(self.file_list.item(row).text()) == path:
                return True
        return False

    def remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def merge_and_save(self) -> None:
        if self.file_list.count() < 2:
            QMessageBox.information(self, "Объединение", "Добавьте минимум два PDF-файла.")
            return

        paths = [Path(self.file_list.item(i).text()) for i in range(self.file_list.count())]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить объединённый PDF",
            "merged.pdf",
            "PDF файлы (*.pdf)",
        )
        if not file_path:
            return

        try:
            merged = merge_documents(paths)
            merged.save(str(file_path), garbage=4, deflate=True)
            merged.close()
            self.set_status(f"Объединено {len(paths)} файлов → {file_path}")
            QMessageBox.information(self, "Готово", f"Сохранено:\n{file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось объединить PDF:\n{exc}")

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        self.add_files([p for p in paths if p.suffix.lower() == ".pdf"])
        event.acceptProposedAction()
