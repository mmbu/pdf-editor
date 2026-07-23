"""Тесты OCR и определения скана."""
from pathlib import Path

import fitz

from app.pdf.document import PdfDocument
from app.pdf.ocr_service import detect_rtl, is_tesseract_available, ocr_page_words
from app.pdf.scan_detector import is_page_scanned

samples = Path("samples")
samples.mkdir(exist_ok=True)

# Текстовый PDF — не скан
text_pdf = samples / "ocr_text.pdf"
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "Native PDF text", fontsize=14)
doc.save(text_pdf)
doc.close()

native = fitz.open(str(text_pdf))
assert not is_page_scanned(native[0])
native.close()

# «Скан»: картинка без текстового слоя
scan_pdf = samples / "ocr_scan.pdf"
doc = fitz.open()
page = doc.new_page()
pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 400, 120), 1)
pix.clear_with(255)
page.insert_image(page.rect, pixmap=pix)
doc.save(scan_pdf)
doc.close()

scan = fitz.open(str(scan_pdf))
assert is_page_scanned(scan[0])
scan.close()

assert detect_rtl("שלום") is True
assert detect_rtl("Hello") is False

if is_tesseract_available():
    pdf = PdfDocument(text_pdf)
    words = pdf.get_words(0)
    assert len(words) >= 2
    print("OK: OCR service available, scan detection, RTL")
else:
    print("SKIP OCR runtime: tesseract not available")
