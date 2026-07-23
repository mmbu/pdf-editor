from __future__ import annotations

import fitz


def is_page_scanned(page: fitz.Page) -> bool:
    text = page.get_text().strip()
    if len(text) >= 30:
        return False

    images = page.get_images(full=True)
    if not images:
        return len(text) == 0

    text_blocks = page.get_text("blocks")
    text_area = 0.0
    for block in text_blocks:
        if block[6] != 0:
            continue
        x0, y0, x1, y1 = block[:4]
        text_area += max(0.0, (x1 - x0) * (y1 - y0))

    page_area = page.rect.width * page.rect.height
    if page_area <= 0:
        return bool(images)

    ratio = text_area / page_area
    return ratio < 0.02 or len(text) < 10
