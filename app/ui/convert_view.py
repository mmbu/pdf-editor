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
)

from app.pdf.image_converter import IMAGE_EXTENSIONS, images_to_pdf, is_image_path
from app.shell.tool_registry import register_tool
from app.ui.base_tool_view import BaseToolView


@register_tool(
    tool_id="convert",
    title="Конвертировать в PDF",
    description="Изображение → PDF-страница",
    icon="🖼️",
)
class ConvertView(BaseToolView):
    def __init__(self, parent=None) -> None:
        super().__init__("Конвертировать в PDF", parent)

        self.image_list = QListWidget()
        self.image_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.content.addWidget(QLabel("Изображения (каждое станет отдельной страницей):"))
        self.content.addWidget(self.image_list)

        buttons = QHBoxLayout()
        add_btn = QPushButton("Добавить изображения…")
        remove_btn = QPushButton("Убрать")
        convert_btn = QPushButton("Создать PDF…")
        add_btn.clicked.connect(self.add_images)
        remove_btn.clicked.connect(self.remove_selected)
        convert_btn.clicked.connect(self.convert)
        buttons.addWidget(add_btn)
        buttons.addWidget(remove_btn)
        buttons.addStretch()
        buttons.addWidget(convert_btn)
        self.content.addLayout(buttons)

        self.setAcceptDrops(True)

    def add_images(self, paths: list[Path] | None = None) -> None:
        if paths is None:
            patterns = " ".join(f"*{ext}" for ext in sorted(IMAGE_EXTENSIONS))
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Выберите изображения",
                "",
                f"Изображения ({patterns})",
            )
            paths = [Path(f) for f in files]

        for path in paths:
            if is_image_path(path) and not self._contains(path):
                self.image_list.addItem(str(path))

    def _contains(self, path: Path) -> bool:
        for row in range(self.image_list.count()):
            if Path(self.image_list.item(row).text()) == path:
                return True
        return False

    def remove_selected(self) -> None:
        for item in self.image_list.selectedItems():
            self.image_list.takeItem(self.image_list.row(item))

    def convert(self) -> None:
        if self.image_list.count() == 0:
            QMessageBox.information(self, "Конвертация", "Добавьте хотя бы одно изображение.")
            return

        paths = [Path(self.image_list.item(i).text()) for i in range(self.image_list.count())]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF",
            "converted.pdf",
            "PDF файлы (*.pdf)",
        )
        if not file_path:
            return

        try:
            images_to_pdf(paths, Path(file_path))
            self.set_status(f"PDF создан: {file_path}")
            QMessageBox.information(self, "Готово", f"Сохранено:\n{file_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF:\n{exc}")

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if is_image_path(Path(url.toLocalFile())):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        self.add_images([p for p in paths if is_image_path(p)])
        event.acceptProposedAction()
