from __future__ import annotations

from dataclasses import dataclass

import fitz


@dataclass(frozen=True)
class TextSpan:
    page_index: int
    text: str
    bbox: fitz.Rect
    font_name: str
    font_size: float
    color: int
    flags: int
    origin: tuple[float, float]

    @property
    def is_bold(self) -> bool:
        return bool(self.flags & 2**4)

    @property
    def is_italic(self) -> bool:
        return bool(self.flags & 2**1)

    def contains_point(self, x: float, y: float) -> bool:
        return self.bbox.contains((x, y))
