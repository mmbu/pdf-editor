"""Тесты этапов 2–3: страницы, merge, split, конвертация."""
from pathlib import Path

import fitz

from app.pdf.document import PdfDocument
from app.pdf.image_converter import images_to_pdf
from app.pdf.page_ops import merge_documents, reorder_pages, split_document

samples = Path("samples")
samples.mkdir(exist_ok=True)

# Тестовый PDF на 3 страницы
src = samples / "multi.pdf"
doc = fitz.open()
for i in range(3):
    page = doc.new_page()
    page.insert_text((72, 72), f"Page {i + 1}", fontsize=16)
doc.save(src)
doc.close()

pdf = fitz.open(str(src))
reorder_pages(pdf, [2, 0, 1])
reordered_path = samples / "reordered.pdf"
pdf.save(str(reordered_path))
pdf.close()

check = PdfDocument(reordered_path)
assert "Page 3" in check.get_spans(0)[0].text
assert "Page 1" in check.get_spans(1)[0].text

merged = merge_documents([src, reordered_path])
merged_path = samples / "merged.pdf"
merged.save(str(merged_path))
merged.close()
assert fitz.open(str(merged_path)).page_count == 6

split_dir = samples / "split_out"
if split_dir.exists():
    for f in split_dir.glob("*.pdf"):
        f.unlink()
files = split_document(src, split_dir)
assert len(files) == 3

# PNG → PDF
png_path = samples / "test.png"
img_doc = fitz.open()
img_page = img_doc.new_page(width=200, height=100)
img_page.insert_text((20, 50), "Image page", fontsize=12)
img_doc.save(str(png_path))
img_doc.close()

# create real png via pixmap
pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 200, 100), 1)
pix.save(str(samples / "photo.png"))

out_pdf = samples / "from_image.pdf"
images_to_pdf([samples / "photo.png"], out_pdf)
assert fitz.open(str(out_pdf)).page_count == 1

print("OK: reorder, merge, split, image->pdf")
