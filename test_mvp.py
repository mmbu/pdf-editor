"""Создаёт тестовый PDF и проверяет извлечение/редактирование текста."""
from pathlib import Path

import fitz

from app.pdf.document import PdfDocument
from app.pdf.editor import replace_text_span
from app.pdf.extractor import extract_text_spans, find_span_at_point

sample_path = Path("samples/test.pdf")
sample_path.parent.mkdir(exist_ok=True)

doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 100), "Привет, PDF Editor!", fontsize=18, fontname="helv")
page.insert_text((72, 140), "Click to edit this text.", fontsize=12, fontname="helv")
doc.save(sample_path)
doc.close()

pdf = PdfDocument(sample_path)
spans = pdf.get_spans(0)
assert len(spans) >= 2, f"Expected spans, got {len(spans)}"

target = find_span_at_point(spans, 80, 95)
assert target is not None, "Span not found at click point"
assert "PDF Editor" in target.text

page = pdf.page(0)
replace_text_span(page, target, "Hello, PDF Editor!")
pdf.save_as(Path("samples/test_edited.pdf"))

edited = PdfDocument(Path("samples/test_edited.pdf"))
edited_spans = edited.get_spans(0)
assert any("Hello" in span.text for span in edited_spans), "Edit not persisted"
print("OK: PDF open, extract, edit, save")
