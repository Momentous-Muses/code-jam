import logging
from types import TracebackType

from PySide6 import QtCore

from __feature__ import snake_case, true_property  # noqa: F401

log = logging.getLogger(__name__)


class AppErrorHandler(QtCore.QObject):
    """Provides error handler that exits the passed app on keyboard interrupts, and logs and notifies on errors."""

    uncaught_error_raised = QtCore.Signal()

    def __init__(self, app: QtCore.QCoreApplication):
        super().__init__(app)
        self.app = app

    def handler(
        self,
        exctype: type[BaseException],
        value: BaseException,
        tb: TracebackType | None,
    ) -> None:
        """
        Log the exception and raise the `uncaught_error_raised` signal.

        If the error is a `KeyboardInterrupt`, exit the app.
        """
        if exctype is KeyboardInterrupt:
            self.app.exit()
            return

        log.critical("Uncaught exception:", exc_info=(exctype, value, tb))

        self.uncaught_error_raised.emit()
