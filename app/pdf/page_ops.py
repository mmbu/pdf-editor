from __future__ import annotations

from pathlib import Path

import fitz

from app.core.pdf_errors import open_pdf_safe


def delete_page(doc: fitz.Document, index: int) -> None:
    if index < 0 or index >= len(doc):
        raise IndexError(f"Страница {index} не существует")
    doc.delete_page(index)


def reorder_pages(doc: fitz.Document, order: list[int]) -> None:
    if len(order) != len(doc):
        raise ValueError("Порядок страниц не совпадает с документом")
    doc.select(order)


def insert_pages(
    doc: fitz.Document,
    at_index: int,
    source_path: Path,
    page_numbers: list[int] | None = None,
) -> None:
    source = open_pdf_safe(source_path)
    try:
        if page_numbers is None:
            doc.insert_pdf(source, start_at=at_index)
            return
        for offset, page_num in enumerate(page_numbers):
            doc.insert_pdf(
                source,
                from_page=page_num,
                to_page=page_num,
                start_at=at_index + offset,
            )
    finally:
        source.close()


def merge_documents(paths: list[Path]) -> fitz.Document:
    if not paths:
        raise ValueError("Нужен хотя бы один PDF-файл")

    result = fitz.open()
    for path in paths:
        source = open_pdf_safe(path)
        try:
            result.insert_pdf(source)
        finally:
            source.close()
    return result


def split_document(source_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = open_pdf_safe(source_path)
    outputs: list[Path] = []

    try:
        for index in range(len(doc)):
            single = fitz.open()
            single.insert_pdf(doc, from_page=index, to_page=index)
            out_path = output_dir / f"{source_path.stem}_стр_{index + 1:03d}.pdf"
            single.save(str(out_path), garbage=4, deflate=True)
            single.close()
            outputs.append(out_path)
    finally:
        doc.close()

    return outputs
