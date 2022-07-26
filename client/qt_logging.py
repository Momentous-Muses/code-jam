import logging

from PySide6 import QtCore

from __feature__ import snake_case, true_property  # noqa: F401

qt_logger = logging.getLogger("<Qt>")

QT_LOG_LEVELS = {
    0: logging.DEBUG,
    4: logging.INFO,
    1: logging.WARNING,
    2: logging.ERROR,
    3: logging.CRITICAL,
}


def init_qt_logging() -> None:
    """Redirect QDebug calls to `logger`."""

    def handler(level: int, _context: QtCore.QMessageLogContext, message: str) -> None:
        qt_logger.log(QT_LOG_LEVELS[level], message)

    QtCore.qInstallMessageHandler(handler)
