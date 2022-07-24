# Proof-of-Concept for Jam Project

`events.py` : Sample Event base class and Event types

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

Uncomment as appropriate to run the CLI or GUI chat client

# TODO

 - Ready to go 🚀
