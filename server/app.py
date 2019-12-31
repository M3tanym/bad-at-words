from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket


app = FastAPI()

app.mount("/", StaticFiles(directory="../client"), name="index.html")


VERSION = 0.1


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/")
def root():
    return {"Welcome" : "The Game by Timothy Ford and Ben Gillett"}

@app.get("/version")
def version():
    return {"Version" : VERSION}
