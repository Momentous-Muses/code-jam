# Proof-of-Concept for Jam Project

`server.py` : WebSockets Server implemented with FastAPI

`gui.py` : Tkinter Chat Client GUI

`ws_client.py` : An implementation of websocket client with *`websockets`* library. Supports calls to a blocking "producer".

# To Run
Start Server
```bash
> poetry run uvicorn poc.server:app
```

Start Client
```bash
> poetry run python poc/ws_client.py
```

# TODO
 - Tkinter GUI has not been connected to    `ws_client`
async callbacks should be started with `async.ensure_future`

 - The Prompt for new text in the `ws_client.py` does not align properly.
