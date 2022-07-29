"""FastAPI server with websockets."""

from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Websocket example"""
    # data = await websocket.receive_json()
    ...


# Uncomment for StaticFiles

# from starlette.staticfiles import StaticFiles
# app.mount("/", StaticFiles(directory="web"), name="web")
