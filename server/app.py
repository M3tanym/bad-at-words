from random import sample # random samples
from fastapi import FastAPI # fastAPI
from starlette.responses import RedirectResponse # for redirecting root
from starlette.staticfiles import StaticFiles # serve static files
from starlette.websockets import WebSocket # host websockets

import json


VERSION = 0.1

app = FastAPI()

app.mount("/client", StaticFiles(directory="../client"), name="client")

words = []

def get_sample():
    return sample(words, 25)

@app.on_event("startup")
async def startup_event():
    global words
    with open("words.txt") as word_file:
        words = word_file.read().splitlines()

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

    wordDict = Convert(get_sample())

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
