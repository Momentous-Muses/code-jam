import logging.handlers
import sys

from PySide6 import QtWidgets

from __feature__ import snake_case, true_property  # noqa: F401
from client.error_handler import AppErrorHandler
from client.main_window.main_window import MainSelectionWindow
from client.qt_utils import init_qt_logging, interrupt_timer

app = QtWidgets.QApplication()
app.set_style("Fusion")

root_logger = logging.getLogger()

log_format = logging.Formatter(
    "{asctime} | {name:>40} | {levelname:>7} | {message}",
    datefmt="%H:%M:%S",
    style="{",
)

if __debug__:
    root_logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(log_format)
    root_logger.addHandler(stream_handler)

file_handler = logging.handlers.RotatingFileHandler(
    "log.log", maxBytes=1024 * 1024, backupCount=2, encoding="utf8"
)
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)

init_qt_logging()

interrupter = interrupt_timer(app)

error_handler = AppErrorHandler(app)
sys.excepthook = error_handler.handler

main_window = MainSelectionWindow(error_handler)
main_window.show()

app.exec()
