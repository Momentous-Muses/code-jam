from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse

from starlette.staticfiles import StaticFiles


"""Run FastAPI server from both web and websocket"""
app = FastAPI()

@app.get("/", response_class=RedirectResponse)
def root():
    return "/index.html"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    data = await websocket.receive_json()

app.mount("/", StaticFiles(directory='web'), name="web")
