from __future__ import annotations

import enum
import threading
import typing as t

T = t.TypeVar("T")


class _Sentinels(enum.Enum):
    """Enum used to store sentinels used by the module, members should be aliased to constants with the same name."""

    UNINITIALIZED = enum.auto()

    def __str__(self):
        return self._name_

    __repr__ = __str__


UNINITIALIZED = _Sentinels.UNINITIALIZED


class ResultEvent(threading.Event, t.Generic[T]):
    """A threading event that's set with a result."""

    def __init__(self):
        super().__init__()
        self.result: t.Literal[UNINITIALIZED] | T = UNINITIALIZED

    def set_result(self, result: T) -> None:
        """Set the event's result to `result`, and mark it as set."""
        self.result = result
        super().set()

    @t.overload
    def get_result(self) -> T:  # noqa: D102
        ...

    @t.overload
    def get_result(self, timeout: float) -> t.Literal[UNINITIALIZED] | T:  # noqa: D102
        ...

    def get_result(self, timeout: float | None = None) -> t.Literal[UNINITIALIZED] | T:
        """
        Wait until a result is available and return the result.

        If timeout is not None only wait up to `timeout` seconds.
        """
        super().wait(timeout)
        return self.result

    def set(self) -> t.NoReturn:
        """Set can't be called without a result."""
        raise RuntimeError(
            f"set of {self.__class__} should not be used directly, use set_result instead."
        )
