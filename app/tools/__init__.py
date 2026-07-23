"""Импорт представлений регистрирует инструменты в tool_registry."""

from app.ui import convert_view, editor_view, merge_view, page_manager_view, split_view

__all__ = [
    "convert_view",
    "editor_view",
    "merge_view",
    "page_manager_view",
    "split_view",
]
