from random import sample # random samples
from fastapi import FastAPI # fastAPI
from starlette.responses import RedirectResponse # for redirecting root
from starlette.staticfiles import StaticFiles # serve static files
from starlette.websockets import WebSocket # host websockets

import json
from pprint import pprint

from player import Player
from logic import handleTouch, handleTeamChange, handleRoleChange
from settings import VERSION, RED, BLACK, BLUE, WHITE, GUESSPLAYER, CMPLAYER
from board import Board

app = FastAPI()

# mounts the static index.html file
app.mount("/client", StaticFiles(directory="../client"), name="client")

# Globals:
words = []
roundWords = []
players = []
sockets = [] # store sockets for broadcasting message

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

    # Add to list of sockets
    global sockets
    sockets.append(websocket)

    # new player gets created on new websocket
    global playerIdCount, players
    players.append(Player("name", playerIdCount, RED, GUESSPLAYER))

    r = {
        "type" : "playerid",
        "value" : playerIdCount
    }

    await websocket.send_text(json.dumps(r))
    playerIdCount += 1
    

    # Loop to handle all subsequent requests
    while True:
        # receive json message from client
        data = await websocket.receive_text()

        r = await handleMessage(data)

        # if reponse generated, send response
        if r is not None:
            await websocket.send_text(r)

async def handleMessage(data):
    """
    handles different json messages from websocket connection

    Arguments:
        data {json} -- json message from client
    """
    r = json.loads(data)
    rType = r["type"]

    global b
    global players
    global sockets


    #  Handles a word being touched
    if rType is "touch":
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
        msg = b.toJson()
        await broadcast(sockets, msg)

        # return reponse to client?
        return None
    # Start game message
    elif rType is "start":
        """
        {
            type : "start"
            player : "id"
        }
        """

        # send the board to everyone on start
        msg = b.toJson()
        await broadcast(sockets, msg)
        return None
    elif rType is "set":
        rWhich = str(r["which"])
        rID = int(r["player"])
        rValue = str(r["value"])

        # change the team
        if rWhich is "team":
            handleTeamChange(players, rID, rValue)
        # change the role
        elif rWhich is "role":
            handleRoleChange(players, rID, rValue)
        else:
            print("ERROR - set with incorrect `which` value")

    else:
        print("ERROR - Case may not be handled yet")


def get_sample():
    """
    Gets 25 random words from words file

    Returns:
        [List: [str]] -- list of 25 words
    """
    return sample(words, 25)


async def broadcast(socketList: WebSocket, message: str):
    """
    Broadcasts the same message across all sockets

    Arguments:
        socketList {List: [websockets]} -- list of all active websockets
        message {str} -- json message to send
    """
    for i in range(len(socketList) - 1, -1, -1):
        try:
            await socketList[i].send_text(message)
        except:
            socketList.pop(i)
