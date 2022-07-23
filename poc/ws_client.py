#TODO: Add Exception Handling for websocket disconnect
from dataclasses import dataclass
import typing
from websockets import connect 
from datetime import datetime 
import asgiref.sync
import asyncio


class Event:
    pass 

@dataclass
class NewMessage(Event):
    """ 
    Event that gets emitted whenever a new message is created
    Should be handled my the EventHandler
    """
    client_id: str 
    room_id: str
    data: typing.Any
    
    type: str = "new-message"
    

    @classmethod
    def from_json(cls, data):
        return cls(**data)

msg_data = {
    "timestamp": datetime.now().isoformat(),# ISO format time
    "content": "Message content",
}
msg = NewMessage.from_json({"client_id":"client_Peter0912", "room_id":"room_9023as", "data":msg_data})
print(msg)


class ClientConnection:
    def __init__(self, ws_connection, *args, **kwargs):
        self.ws_connection = ws_connection
    
    @classmethod
    async def start_connection(cls, uri, *args, **kwargs):
        connection = await connect(uri)
        return cls(connection, *args, **kwargs)

    @asgiref.sync.sync_to_async
    def producer(self):
        # Reading stdin is blocking
        txt = input(">>> ")
        return txt
    
    async def consumer(self, msg):
        # Do something with the received msg
        print(msg)

    async def producer_handler(self, websocket):
        while True:
            message = await self.producer()
            await websocket.send(message)

    async def consumer_handler(self, websocket):
        while True:
            data = await websocket.recv()
            await self.consumer(data)

    async def handler(self):
        await asyncio.gather(
            self.consumer_handler(self.ws_connection),
            self.producer_handler(self.ws_connection),
        )
    
    
URI = "wss://demo.piesocket.com/v3/channel_1?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self"
URI2 = "ws://localhost:8000/ws/20"

async def main():
    client = await ClientConnection.start_connection(URI2)
    
    # listen for blocking input in the background
    asyncio.create_task(client.producer())
    await client.handler()
    
asyncio.run(main())


