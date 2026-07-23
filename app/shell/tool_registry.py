from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    title: str
    description: str
    icon: str
    factory: Callable[[], QWidget]


_REGISTRY: list[ToolDefinition] = []


def register_tool(
    tool_id: str,
    title: str,
    description: str,
    icon: str,
) -> Callable[[Callable[[], QWidget]], Callable[[], QWidget]]:
    def decorator(factory: Callable[[], QWidget]) -> Callable[[], QWidget]:
        _REGISTRY.append(
            ToolDefinition(
                tool_id=tool_id,
                title=title,
                description=description,
                icon=icon,
                factory=factory,
            )
        )
        return factory

    return decorator


def get_tools() -> list[ToolDefinition]:
    return list(_REGISTRY)
