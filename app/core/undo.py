from __future__ import annotations

from collections import deque


class UndoStack:
    def __init__(self, max_size: int = 30) -> None:
        self._undo: deque[bytes] = deque(maxlen=max_size)
        self._redo: deque[bytes] = deque(maxlen=max_size)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def push(self, snapshot: bytes) -> None:
        self._undo.append(snapshot)
        self._redo.clear()

    def can_undo(self) -> bool:
        return len(self._undo) > 1

    def can_redo(self) -> bool:
        return len(self._redo) > 0

    def undo(self) -> bytes | None:
        if not self.can_undo():
            return None
        current = self._undo.pop()
        self._redo.appendleft(current)
        return self._undo[-1]

    def redo(self) -> bytes | None:
        if not self.can_redo():
            return None
        snapshot = self._redo.popleft()
        self._undo.append(snapshot)
        return snapshot

    def seed(self, snapshot: bytes) -> None:
        self.clear()
        self._undo.append(snapshot)
