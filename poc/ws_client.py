"""
Client Websocket Management

TODO: Add Exception Handling for websocket disconnect
"""

import asyncio
import threading
from typing import Awaitable

import asgiref.sync
from gui import ChatClientGUI
from websockets import connect


class ExampleClient:
    """Example Client that illustrates how to use the ClientConnection API"""

    @asgiref.sync.sync_to_async
    def producer(self):
        """
        An example producer

         - Producers should be awaitable/async
         - Producers are functions that return data after calculations/processing has taken place
         - They should return data at intervals
        """
        # Reading stdin is a blocking call
        txt = input("")
        return txt

    async def consumer(self, msg):
        """
        An example consumer

         - Consumers should be awaitable/async
         - Consumers handle/process received data
        Args:
            msg (Any): Any type of data. Data is transmitted over websockets as bytes or strings
        """
        # Do something with the received msg
        print(msg, end="\n>>>")


class ClientConnection:
    """Websocket Client Connection"""

    def __init__(
        self, ws_connection, producer: Awaitable, consumer: Awaitable, *args, **kwargs
    ):
        """Create a new connection to a websocket

        Args:
            ws_connection (websockets.WebSocketProtocol): Has .send and .recv for communicating over the websocket
            producer (Awaitable): An async function that generates output/text to send over the websocket
            consumer (Awaitable): An async function that handles data received over the websocket
        """
        self.ws_connection = ws_connection
        self.producer = producer
        self.consumer = consumer

    @classmethod
    async def start_connection(cls, uri: str, *args, **kwargs):
        """Entrypoint method for the Client Connection

        Args:
            uri (str): A websocket URI to connect to

        Returns:
            ClientConnection: A new instance of a client connection
        """
        try:
            connection = await connect(uri)
            return cls(connection, *args, **kwargs)
        except ConnectionError:
            # Failed to connect to the server
            print("Connection failed")

    async def producer_handler(self, websocket):
        """Waits for new data from client and sends it over the websocket connection

        Args:
            websocket (websockets.WebSocketProtocol): websocket connection
        """
        while True:
            message = await self.producer()
            await websocket.send(message)

    async def consumer_handler(self, websocket):
        """Looks for data from the websocket server, and forwards it to the consumer

        Args:
            websocket (websockets.WebSocketProtocol): websocket protocol
        """
        while True:
            data = await websocket.recv()
            print("From Consumer Handler", data)
            await self.consumer(data)

    async def handler(self):
        """
        Handles websocket interactions at a high level

            - A good place for error catching and creating other async tasks
        """
        print("Running handler")

        while True:
            await asyncio.gather(
                self.consumer_handler(self.ws_connection),
                self.producer_handler(self.ws_connection),
            )


URI = "wss://demo.piesocket.com/v3/channel_1?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self"
URI2 = "ws://localhost:8000/ws/20"


async def start_simple_async_client():
    """A simple CLI Chat Client"""
    ex_client = ExampleClient()
    client_connection = await ClientConnection.start_connection(
        URI2, producer=ex_client.producer, consumer=ex_client.consumer
    )

    # listen for blocking input in the background
    await client_connection.handler()


def _asyncio_thread(loop, task, task_args=[], task_kwargs={}):
    loop.create_task(task(*task_args, **task_kwargs))
    loop.run_forever()


def start_gui_client():
    """
    Complex Chat Client

        - Tkinter eventloop
        - asyncio eventloop running in a background thread
    """
    async_loop = asyncio.get_event_loop()
    client_gui = ChatClientGUI(async_loop)
    client_connection = async_loop.run_until_complete(
        ClientConnection.start_connection(
            URI2, producer=client_gui.send_message, consumer=client_gui.receive_message
        )
    )

    # Start Websocket Thread
    threading.Thread(
        target=_asyncio_thread,
        args=(
            async_loop,
            client_connection.handler,
        ),
        daemon=True,
    ).start()
    client_gui.start_mainloop()


"""
SIMPLE CLIENT
"""
# asyncio.run(start_simple_async_client())

"""
COMPLEX GUI CLIENT
"""
start_gui_client()
