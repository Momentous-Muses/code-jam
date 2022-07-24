from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class ConnectionManager:
    """
    Connection Manager for multiple Clients

        - Handles rooms and client-pairing
        - TODO: Emit events to the message bus and event handler
    """

    def __init__(self):
        # self.active_connections: Dict[WebSocket, Any] = defaultdict(dict)
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept a new websocket connection

            - Add them to a general room

        Args:
            websocket (WebSocket): New websocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Handle client disconnects

            - Remove them from the general room
        Args:
            websocket (WebSocket): Disconneted websocket connection
        """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a single websocket client

        Args:
            message (str): Message to send
            websocket (WebSocket): Websocket connection
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Senda  message to all websocket clients connected to the server

        Args:
            message (str): Message to send
        """
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int | None):
    """General websocket/chat room endpoint"""
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} has joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
