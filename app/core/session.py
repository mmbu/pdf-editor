from __future__ import annotations

from pathlib import Path

from app.core.undo import UndoStack
from app.pdf.document import PdfDocument


class DocumentSession:
    def __init__(self) -> None:
        self.pdf = PdfDocument()
        self.undo = UndoStack()
        self.current_path: Path | None = None

    @property
    def is_open(self) -> bool:
        return self.pdf.doc is not None

    def open(self, path: Path) -> None:
        self.pdf.open(path)
        self.current_path = path
        self.undo.seed(self.pdf.snapshot())

    def close(self) -> None:
        self.pdf.close()
        self.current_path = None
        self.undo.clear()

    def save_as(self, path: Path) -> None:
        self.pdf.save_as(path)
        self.current_path = path

    def record_change(self) -> None:
        self.undo.push(self.pdf.snapshot())

    def undo(self) -> bool:
        snapshot = self.undo.undo()
        if snapshot is None:
            return False
        self.pdf.restore(snapshot)
        return True

    def redo(self) -> bool:
        snapshot = self.undo.redo()
        if snapshot is None:
            return False
        self.pdf.restore(snapshot)
        return True

    def can_undo(self) -> bool:
        return self.undo.can_undo()

    def can_redo(self) -> bool:
        return self.undo.can_redo()
