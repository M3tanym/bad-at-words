from random import sample # random samples
from fastapi import FastAPI # fastAPI
from starlette.responses import RedirectResponse # for redirecting root
from starlette.staticfiles import StaticFiles # serve static files
from starlette.websockets import WebSocket # host websockets

import json

from player import Player
from logic import handleTouch
from settings import VERSION
from board import Board

app = FastAPI()

# mounts the static index.html file
app.mount("/client", StaticFiles(directory="../client"), name="client")

# Globals:
words = []
roundWords = []
players = []

playerIdCount = 0

b = None

@app.on_event("startup")
async def startup_event():
    global words
    with open("words.txt") as word_file:
        words = word_file.read().splitlines()

    global roundWords 
    roundWords = get_sample()

    global b
    b = Board(roundWords)

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

    # send board json on start
    global b
    await websocket.send_text(b.toJson)

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
    handles different json messages from websocket connection
    
    Arguments:
        data {json} -- json message from client
    """
    r = json.loads(data)
    rType = r["type"]

    global b

    # Handles a word being touched
    if rType == "touch":
        """
        {
            type : "touch",
            word : word,
            player : id
        }
        """
        rWord = str(r["word"])
        # player id
        rPlayer = int(r["player"])

        # the logic for a touch
        handleTouch(b, rWord, rPlayer)

        # return reponse to client?
        return None
    else:
        print("Case may not be handled yet")


def get_sample():
    """
    Gets 25 random words from words file
    
    Returns:
        [List: [str]] -- list of 25 words
    """
    return sample(words, 25)