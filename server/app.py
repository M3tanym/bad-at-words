from random import sample # random samples
from fastapi import FastAPI # fastAPI
from starlette.responses import RedirectResponse # for redirecting root
from starlette.staticfiles import StaticFiles # serve static files
from starlette.websockets import WebSocket # host websockets

import json

from player import Player
from logic import handleTouch


VERSION = 0.1

app = FastAPI()

app.mount("/client", StaticFiles(directory="../client"), name="client")

words = []
roundWords = []
players = []

playerIdCount = 0

def get_sample():
    return sample(words, 25)

@app.on_event("startup")
async def startup_event():
    global words
    with open("words.txt") as word_file:
        words = word_file.read().splitlines()

    global roundWords 
    roundWords = get_sample()

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

    # new player gets created on new websocket
    global playerIdCount, players
    players.append(Player("name", playerIdCount, "red"))
    playerIdCount += 1

    # send random sample of words on startup
    global roundWords
    wordDict = roundWords
    response = {
        "type" : "update",
        "words" : wordDict
    }
    r = json.dumps(response)
    await websocket.send_text(str(r))

    # Loop to handle all subsequent requets
    while True:
        # receive json message from client
        data = await websocket.receive_text()

        r = handleMessage(data)

        # if reponse generated, send response
        if r is not None:
            await websocket.send_text(r)


def handleMessage(data):
    """
    handles different json messages from websocket
    
    Arguments:
        data {json} -- json message from client
    """
    r = json.loads(data)
    rType = r["type"]

    if rType == "touch":
        """
        {
            type : "touch",
            word : word,
            player : id,
        }
        """
        rWord = str(r["word"])
        # player id
        rPlayer = int(r["player"])

        # HANDLE THE LOGIC HERE
        # handleTouch(rWord, rPlayer)

        # return reponse to client?
        return None
    else:
        print("Case may not be handled yet")
