from PySide6 import QtWidgets

from __feature__ import snake_case, true_property  # noqa: F401


class MainSelectionWindowGui(QtWidgets.QMainWindow):
    """Main window base."""

    def __init__(self):
        super().__init__()
