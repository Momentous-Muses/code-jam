from __future__ import annotations

import logging.handlers
import typing as t

from client import websocket_client

from ._main_window_gui import MainSelectionWindowGui

if t.TYPE_CHECKING:
    from client.error_handler import AppErrorHandler

log = logging.getLogger(__name__)


class MainSelectionWindow(MainSelectionWindowGui):
    """Main window that allows rooms to be joined."""

    def __init__(self, error_handler: AppErrorHandler):
        super().__init__()
        self.websocket_client: None | websocket_client.WebsocketMessageDispatcher = None
        self.error_handler = error_handler
