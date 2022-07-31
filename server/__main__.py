import uvicorn

HOST = "127.0.0.1"
PORT = 5000
RELOAD = True

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=RELOAD, log_level="info")
