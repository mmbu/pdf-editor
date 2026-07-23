from __future__ import annotations

from pathlib import Path

from app.core.pdf_errors import PdfUserError, format_pdf_error

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.pdf.page_ops import split_document
from app.shell.tool_registry import register_tool
from app.ui.base_tool_view import BaseToolView


@register_tool(
    tool_id="split",
    title="Разъединить",
    description="Split: каждая страница — отдельный файл",
    icon="✂️",
)
class SplitView(BaseToolView):
    def __init__(self, parent=None) -> None:
        super().__init__("Разъединить PDF", parent)

        self.source_path = QLineEdit()
        self.source_path.setPlaceholderText("PDF-файл…")
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Папка для сохранения…")

        pick_file = QPushButton("Выбрать PDF…")
        pick_dir = QPushButton("Папка…")
        split_btn = QPushButton("Разъединить")
        pick_file.clicked.connect(self.pick_source)
        pick_dir.clicked.connect(self.pick_output)
        split_btn.clicked.connect(self.split)

        form = QVBoxLayout()
        form.addWidget(QLabel("Исходный PDF:"))
        row1 = QHBoxLayout()
        row1.addWidget(self.source_path)
        row1.addWidget(pick_file)
        form.addLayout(row1)

        form.addWidget(QLabel("Папка назначения:"))
        row2 = QHBoxLayout()
        row2.addWidget(self.output_dir)
        row2.addWidget(pick_dir)
        form.addLayout(row2)

        form.addWidget(split_btn)
        self.content.addLayout(form)
        self.content.addStretch()
        self.setAcceptDrops(True)

    def pick_source(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF для разъединения",
            "",
            "PDF файлы (*.pdf)",
        )
        if file_path:
            self.source_path.setText(file_path)

    def pick_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Папка для страниц")
        if directory:
            self.output_dir.setText(directory)

    def split(self) -> None:
        source = Path(self.source_path.text().strip())
        output = Path(self.output_dir.text().strip())

        if not source.exists():
            QMessageBox.warning(self, "Разъединение", "Укажите существующий PDF-файл.")
            return
        if not output.exists():
            QMessageBox.warning(self, "Разъединение", "Укажите существующую папку.")
            return

        try:
            files = split_document(source, output)
            self.set_status(f"Создано файлов: {len(files)}")
            QMessageBox.information(
                self,
                "Готово",
                f"Создано {len(files)} PDF-файлов в:\n{output}",
            )
        except PdfUserError as exc:
            QMessageBox.warning(self, "PDF", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось разъединить PDF:\n{format_pdf_error(exc)}")

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
                self.source_path.setText(str(path))
                if not self.output_dir.text():
                    self.output_dir.setText(str(path.parent / f"{path.stem}_pages"))
                event.acceptProposedAction()
                return
