from __future__ import annotations

from pathlib import Path

import fitz

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def images_to_pdf(image_paths: list[Path], output_path: Path) -> None:
    if not image_paths:
        raise ValueError("Нужно хотя бы одно изображение")

    doc = fitz.open()
    try:
        for image_path in image_paths:
            img_doc = fitz.open(str(image_path))
            try:
                pdf_bytes = img_doc.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdf_bytes)
                try:
                    doc.insert_pdf(img_pdf)
                finally:
                    img_pdf.close()
            finally:
                img_doc.close()
        doc.save(str(output_path), garbage=4, deflate=True)
    finally:
        doc.close()
