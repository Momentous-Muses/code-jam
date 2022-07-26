# Parts of this file are under 3rd party licenses; see LICENSE_THIRD_PARTY for more details.

import asyncio
import collections.abc
import contextlib
import logging
import typing
from functools import partial

TASK_RETURN = typing.TypeVar("TASK_RETURN")


def create_task(
    coro: collections.abc.Coroutine[typing.Any, typing.Any, TASK_RETURN],
    *,
    suppressed_exceptions: tuple[type[Exception], ...] = (),
    event_loop: typing.Optional[asyncio.AbstractEventLoop] = None,
    **kwargs,
) -> asyncio.Task[TASK_RETURN]:
    """
    Wrapper for creating an asyncio.Task which logs exceptions raised in the task.

    If the `event_loop` kwarg is provided, the task is created from that event loop,
    otherwise the running loop is used.
    Args:
        coro: The function to call.
        suppressed_exceptions: Exceptions to be handled by the task.
        event_loop: The loop to create the task from.
        kwargs: Passed to asyncio.create_task.
    Returns:
        asyncio.Task: The wrapped task.
    """
    if event_loop is not None:
        task = event_loop.create_task(coro, **kwargs)
    else:
        task = asyncio.create_task(coro, **kwargs)
    task.add_done_callback(
        partial(_log_task_exception, suppressed_exceptions=suppressed_exceptions)
    )
    return task


def _log_task_exception(
    task: asyncio.Task, *, suppressed_exceptions: tuple[type[Exception]]
) -> None:
    """Retrieve and log the exception raised in `task` if one exists."""
    with contextlib.suppress(asyncio.CancelledError):
        exception = task.exception()
        # Log the exception if one exists.
        if exception and not isinstance(exception, suppressed_exceptions):
            log = logging.getLogger(__name__)
            log.error(
                f"Error in task {task.get_name()} {id(task)}!", exc_info=exception
            )
