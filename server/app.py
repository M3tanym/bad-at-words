from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

import json


VERSION = 0.1

app = FastAPI()

app.mount("/client", StaticFiles(directory="../client"), name="client")

@app.get("/")
async def get():
    response = RedirectResponse(url='/client/index.html')
    return response

@app.get("/version")
async def version():
    return {"Version" : VERSION}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    words = ["barry", "juice", "nuts"]
    wordDict = Convert(words)

    response = { 
        "type" : "update", 
        "words" : wordDict
    }

    r = json.dumps(response)
    await websocket.send_text(str(r))


    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")



def Convert(lst): 
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)} 
    return res_dct 