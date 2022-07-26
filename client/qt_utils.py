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


def interrupt_timer(app: QtCore.QCoreApplication) -> QtCore.QTimer:
    """Interrupt the Qt event loop regularly to let python process keyboard interrupts."""
    timer = QtCore.QTimer(app)
    timer.interval = 200
    timer.timeout.connect(lambda: None)
    timer.start()
    return timer
