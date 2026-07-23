"""Тест inline-редактирования на уровне слов."""
from pathlib import Path

import fitz

from app.pdf.document import PdfDocument
from app.pdf.editor import replace_text_span
from app.pdf.extractor import extract_text_words, find_word_at_point

samples = Path("samples")
samples.mkdir(exist_ok=True)

sample_path = samples / "inline_test.pdf"
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 100), "Hello PDF Editor", fontsize=18, fontname="helv")
doc.save(sample_path)
doc.close()

pdf = PdfDocument(sample_path)
words = pdf.get_words(0)
assert len(words) >= 3, f"Expected words, got {len(words)}"

target = find_word_at_point(words, 80, 95)
assert target is not None, "Word not found at click point"
assert target.text == "Hello"

page = pdf.page(0)
replace_text_span(page, target, "Hi")
pdf.save_as(samples / "inline_test_edited.pdf")

edited = PdfDocument(samples / "inline_test_edited.pdf")
edited_words = edited.get_words(0)
assert any(w.text == "Hi" for w in edited_words), "Word edit not persisted"
print("OK: inline word extract and edit")
