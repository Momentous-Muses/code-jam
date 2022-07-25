from __future__ import annotations

import asyncio
import collections.abc
import json
import logging
import queue
import typing as t
from contextlib import suppress

import websockets.client

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


class WebsocketMessageDispatcher:
    """
    Dispatch messages received from the websocket to subscribed consumers and allow sending back to the server.

    This class is designed to be threadsafe and to work from a thread.

    All messages that are sent or dispatched will be of the Message type.

    To run, use the `run` method instead of managing the object yourself or the websocket won't be managed properly.
    Example usage:

    import asyncio
    import threading

    import websockets.client

    from websocket_client import ResultEvent, WebsocketMessageDispatcher

    def main():
        result_event = ResultEvent[WebsocketMessageDispatcher]()
        connect_factory = WebsocketMessageDispatcher.run(result_event, partial(websockets.client.connect, "URI"))

        thread = threading.Thread(target=asyncio.run, args=(connect_factory,))
        thread.start()
        dispatcher = result_event.get_result()  # get the created WebsocketMessageDispatcher object

        subscribe_id, message_queue = dispatcher.subscribe("domain")  # subscribe_id allows unsubscribe later on
        message = message_queue.get()  # receive message
        dispatcher.queue_send(YourMessage())  # queue message to be sent
    """

    def __init__(self, *, websocket: websockets.client.WebSocketClientProtocol):
        self._websocket = websocket
        self._receive_queues: dict[
            str, dict[collections.abc.Hashable, queue.SimpleQueue[Message]]
        ] = {}
        self._send_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._loop = asyncio.get_running_loop()

    def queue_send(self, message: Message) -> None:
        """Queue `message` to be sent."""
        self._loop.call_soon_threadsafe(self._send_queue.put_nowait, message)

    def subscribe(self, domain: str) -> SubscribeResult:
        """Subscribe to events from `domain`"""
        queue_dict = self._receive_queues.setdefault(domain, {})
        queue_: queue.SimpleQueue[Message] = queue.SimpleQueue()
        id_ = id(queue_)
        queue_dict[id_] = queue_
        return SubscribeResult(id_, queue_)

    def unsubscribe(self, identifier: collections.abc.Hashable, domain: str) -> None:
        """Unsubscribe from the `domain` with the `identifier` received from the subscribe method."""
        with suppress(KeyError):
            del self._receive_queues[domain][identifier]

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
            send_task = asyncio.create_task(inst._sender())
            await inst._handler()
            await send_task

    async def _sender(self) -> None:
        while True:
            message = await self._send_queue.get()
            message_json = message.to_json()
            log.debug("Sending %s json through websocket.", message_json)
            await self._websocket.send(message_json)

    async def _handler(self) -> None:
        async for message in self._websocket:
            try:
                message_payload = json.loads(message)
                if "domain" not in message_payload or "type" not in message_payload:
                    raise ValueError
            except ValueError:
                log.warning("Received invalid json message payload.")
                continue

            try:
                message = messages.message_from_dict(message_payload)
            except messages.UnknownMessageTypeError:
                log.warning(
                    f"Received unknown message type {message_payload['type']} for domain {message_payload['domain']}"
                )
                continue

            log.debug(
                "Dispatching message of %s type to %s domain queues.",
                message.type_,
                message.domain,
            )
            if (queues := self._receive_queues.get(message.domain)) is not None:
                for queue_ in queues.values():
                    queue_.put(message)
