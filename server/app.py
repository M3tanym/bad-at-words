from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket


VERSION = 0.1

app = FastAPI()

app.mount("/client", StaticFiles(directory="../client"), name="client")

@app.get("/")
async def get():
    return {"Welcome" : "The Game by Timothy Ford and Ben Gillett"}

@app.get("/version")
async def version():
    return {"Version" : VERSION}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
