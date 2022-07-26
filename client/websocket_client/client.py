from __future__ import annotations

import asyncio
import collections.abc
import itertools
import json
import logging
import queue  # noqa: F401 used in annotation
import typing as t
import uuid
from weakref import WeakValueDictionary

import websockets.client
from PySide6 import QtCore

from __feature__ import snake_case, true_property  # noqa: F401
from client import utils

from . import messages

if t.TYPE_CHECKING:
    import typing_extensions as te

    from . import ResultEvent
    from .messages import Message

T = t.TypeVar("T")

log = logging.getLogger(__name__)


class SubscribeResult(t.NamedTuple):
    """Result of ClientManager's subscribe method."""

    id: collections.abc.Hashable
    queue: queue.SimpleQueue[Message]


class ScheduledMessage(t.NamedTuple):
    """A message to send and the channel to send it through."""

    message: Message
    channel: str


class Connection(QtCore.QObject):
    """
    A connection to the server through a channel.

    When created the connection is unprepared while the channel is negotiated with the remote server,
    and must have its channel set through `set_channel`.
    """

    connection_established = QtCore.Signal()
    """Emitted when the connection is bound to a channel and ready to send/receive messages."""
    connection_refused = QtCore.Signal()
    """Emitted when the server refuses the creation of a new channel."""
    connection_closed = QtCore.Signal()
    """Emitted when the connection is closed."""
    message_received = QtCore.Signal(messages.Message)
    """Emitted with the message when a new message is received on the channel this is bound to."""

    def __init__(
        self,
        *,
        message_schedule_func: collections.abc.Callable[[ScheduledMessage], object],
    ):
        super().__init__()
        self._channel = None
        self._schedule_func = message_schedule_func
        self._closed = False

    def set_channel(self, channel: str) -> None:
        """Set the connection's channel, and emit the `connection_established` signal with it."""
        self._channel = channel
        self.connection_established.emit()

    def receive_message(self, message: Message):
        """Receive the `message` and send it through the `message_received` signal."""
        if isinstance(message, messages.ConnectionEndRequest):
            self.close_connection()
        else:
            self.message_received.emit(message)

    def schedule_send(self, message: Message):
        """Schedule `message` to be sent to the server."""
        if self._channel is None:
            raise RuntimeError("The connection is not yet ready.")
        if self._closed:
            raise RuntimeError("Connection's channel has already been closed.")

        self._schedule_func(ScheduledMessage(message, self._channel))

    def disconnect_channel(self):
        """Schedule this connection to be closed."""
        self.schedule_send(messages.ConnectionEndRequest())
        self.close_connection()
        self._closed = True

    def close_connection(self):
        """
        Mark this connection as closed and emit the `connection_closed` signal.

        Should be called when the channel is closed at the remote server instead of from this client.
        """
        self.connection_closed.emit()
        self._closed = True


class WebsocketMessageDispatcher:
    """
    Dispatch messages received from the websocket to subscribed consumers and allow sending back to the server.

    This class is designed to be threadsafe and to work from a thread.

    All messages that are sent or dispatched will be of the Message type.

    To run, use the `run` method instead of managing the object yourself or the websocket won't be managed properly.
    Example usage:

    import asyncio
    import threading
    from functools import partial

    import websockets.client

    from websocket_client import ResultEvent, WebsocketMessageDispatcher

    def main():
        result_event = ResultEvent[WebsocketMessageDispatcher]()
        connect_factory = WebsocketMessageDispatcher.run(result_event, partial(websockets.client.connect, "URI"))

        thread = threading.Thread(target=asyncio.run, args=(connect_factory,))
        thread.start()
        dispatcher = result_event.get_result()  # get the created WebsocketMessageDispatcher object

        connection = dispatcher.subscribe("domain")  # subscribe_id allows unsubscribe later on
        connection.connection_established.connect(connection_established_callback)
        connection.message_received.connect(message_received_callback)
        connection.schedule_send(YourMessage())
    """

    def __init__(self, *, websocket: websockets.client.WebSocketClientProtocol):
        self._websocket = websocket
        self._loop = asyncio.get_running_loop()
        self._client_id = uuid.uuid4().hex

        # connections waiting for channel uuid, keys are request ids
        self._unprepared_connections: WeakValueDictionary[
            str, Connection
        ] = WeakValueDictionary()
        # uuid to connection with channel using that uuid
        self._connections: WeakValueDictionary[str, Connection] = WeakValueDictionary()
        self._send_queue: asyncio.Queue[ScheduledMessage] = asyncio.Queue()

        self._connection_request_id_iterator = map(str, itertools.count())

    def connect_channel(self, domain: str) -> Connection:
        """Create a communication channel of the `domain` type."""
        connection_request_id = next(self._connection_request_id_iterator)
        connection = Connection(message_schedule_func=self._queue_send)
        self._unprepared_connections[connection_request_id] = connection
        log.info("Requesting channel with request id %r.", connection_request_id)
        # Connection start negotiations have a static channel.
        self._queue_send(
            ScheduledMessage(
                messages.ConnectionStartRequest(connection_request_id, domain),
                "channel_communication_negotiation",
            )
        )
        return connection

    @classmethod
    async def run(
        cls,
        result_event: ResultEvent[te.Self],
        connect_factory: collections.abc.Callable[[], websockets.client.connect],
    ) -> None:
        """Run a websocket and create a dispatcher for it, the dispatcher is set as the result of `result_event`."""
        async with connect_factory() as websocket:
            inst = cls(websocket=websocket)
            result_event.set_result(inst)
            send_task = utils.create_task(inst._sender())
            await inst._handler()
            await send_task

    async def _sender(self) -> None:
        while True:
            message, channel = await self._send_queue.get()
            message_dict = message.to_json_dict()
            message_dict["channel"] = channel
            message_dict["client_id"] = self._client_id
            log.debug("Sending %s json through websocket.", message_dict)
            await self._websocket.send(json.dumps(message_dict))

    async def _handler(self) -> None:
        async for message in self._websocket:
            try:
                message_payload = json.loads(message)
            except ValueError:
                log.warning("Received invalid json message payload. Body: %r", message)
                continue

            match message_payload:
                case {"channel": channel, "type": _, "domain": _}:
                    pass
                case _:
                    log.warning(
                        "Received JSON is missing required keys. Body: %r",
                        message_payload,
                    )
                    continue

            try:
                message = messages.message_from_dict(message_payload)
            except messages.UnknownMessageTypeError:
                log.warning(
                    "Received unknown message type %r for domain %r",
                    message_payload["type"],
                    message_payload["domain"],
                )
                continue

            if isinstance(message, messages.ConnectionStartResponse):
                self._handle_connection_start_response(message)
                continue

            log.debug(
                "Dispatching message of %s type to %s domain queues.",
                message.type_,
                message.domain,
            )
            connection = self._connections.get(channel)
            if connection is not None:
                connection.receive_message(message)
            else:
                log.warning("Received message on unknown channel.")

    def _handle_connection_start_response(
        self,
        message: messages.ConnectionStartResponse,
    ):
        connection = self._unprepared_connections.get(message.request_id)
        if connection is None:
            log.warning(
                "Received unexpected connection start response with id %r.",
                message.request_id,
            )
            return
        connection.set_channel(message.generated_uuid)
        del self._unprepared_connections[message.request_id]
        self._connections[message.generated_uuid] = connection
        log.info("Got channel for request %r.", message.request_id)

    def _queue_send(self, to_schedule: ScheduledMessage) -> None:
        """Queue `message` to be sent."""
        self._loop.call_soon_threadsafe(self._send_queue.put_nowait, to_schedule)
