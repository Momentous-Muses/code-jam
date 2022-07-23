from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles

"""
uvicorn server.__main__:app --reload

Run FastAPI server from both web and websocket"""
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Websocket example"""
    # data = await websocket.receive_json()
    ...


app.mount("/", StaticFiles(directory="web"), name="web")
