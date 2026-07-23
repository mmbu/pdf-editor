"""Тесты обработки ошибок PDF."""
from pathlib import Path

from app.core.pdf_errors import PdfUserError, open_pdf_safe

samples = Path("samples")
samples.mkdir(exist_ok=True)


def expect_error(path: Path, fragment: str) -> None:
    try:
        open_pdf_safe(path)
    except PdfUserError as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
        return
    raise AssertionError(f"Expected PdfUserError for {path}")


expect_error(samples / "missing.pdf", "не найден")

empty = samples / "empty.pdf"
empty.write_bytes(b"")
expect_error(empty, "пуст")

bad = samples / "not_a_pdf.pdf"
bad.write_text("this is not pdf content", encoding="utf-8")
try:
    open_pdf_safe(bad)
except PdfUserError:
    pass
else:
    raise AssertionError("Expected PdfUserError for invalid pdf")

print("OK: PDF error handling")
