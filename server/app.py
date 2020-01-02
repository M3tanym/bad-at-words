from random import sample # random samples
from fastapi import FastAPI # fastAPI
from starlette.responses import RedirectResponse # for redirecting root
from starlette.staticfiles import StaticFiles # serve static files
from starlette.websockets import WebSocket # host websockets

import json
from pprint import pprint

from player import Player
from logic import handleTouch, handleTeamChange, handleRoleChange, handleNameChange
from settings import VERSION, RED, BLACK, BLUE, WHITE, GUESSPLAYER, CMPLAYER, AGENT_VICTORY, ASSASIN_VICTORY
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
turn = False # false is red, true is blue
defaultNumTouches = 2
numTouches = defaultNumTouches # TODO: sad, default for number of touches

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

    # initialize turn
    global turn
    global numTouches
    teamVal = RED if turn is False else BLUE

    redCount, blueCount = b.getScore()

    r = {
        "type" : "turn",
        "team" : teamVal,
        "touches" : numTouches,
        "red" : redCount,
        "blue" : blueCount
    }

    msg = json.dumps(r)
    await broadcast(sockets, msg)

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

    print("INFO - received request of type [{t}]".format(t = rType))

    global b
    global players
    global sockets
    global numTouches
    global turn


    #  Handles a word being touched
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
        teamTurn = RED if turn is False else BLUE

        for p in players:
            if p.id == rPlayer:
                if p.color != teamTurn:
                    print("WARNING - player from wrong team touched")
                    return
                if p.role != GUESSPLAYER:
                    print("WARNING - codemaster tried to touch")
                    return

        numTouches = numTouches - 1

        print("INFO - handling a touch event for '{w}'".format(w = rWord))
        print("INFO - team {c} has {n} touches left".format(c = RED if turn is False else BLUE, n = numTouches))

        # the logic for a touch
        handleTouch(b, rWord, rPlayer)

        r = {
            "type" : "visible",
            "word" : rWord
        }

        msg = json.dumps(r)
        await broadcast(sockets, msg)

        # check win condition
        winVal = b.checkWin()
        teamVal = BLUE if turn else RED # thanks ben

        if winVal != 0:
            winTeam = BLUE
            victoryType = AGENT_VICTORY

            if winVal == 3:
                # blue won
                print("INFO - Blue team has won this match")
                winTeam = BLUE
                victoryType = AGENT_VICTORY
            elif winVal == 2:
                # red won
                print("INFO - Red team has won this match")
                winTeam = RED
                victoryType = AGENT_VICTORY
            elif winVal == -1:
                # Assasin
                teamValInv = RED if turn else BLUE # invert the team
                winTeam = teamValInv
                victoryType = ASSASIN_VICTORY
                print("INFO - {t} team has won this match by the assasin".format(t = teamValInv))
            else:
                print("ERROR - Invalid win value")


            r = {
                "type" : "win",
                "team" : winTeam,
                "method" : victoryType
            }

            msg = json.dumps(r)
            await broadcast(sockets, msg)

        else:
            # Check if incorrect guess switches teams
            space = b.getSpaceInfo(rWord)

            if space.color != teamTurn:
                await turnLogic(True)
            else:
                await turnLogic()

        # return reponse to client?
        return None
    # Start game message
    elif rType == "start":
        """
        {
            type : "start"
            player : "id"
        }
        """

        print("INFO - starting the game with {n} players".format(n = len(players)))

        # send the board to everyone on start
        msg = b.toJson()
        await broadcast(sockets, msg)
        return None
    elif rType == "set":
        rWhich = str(r["which"])
        rID = int(r["player"])
        rValue = str(r["value"])

        print("INFO - setting {w} for player {p} as {v}".format(w = rWhich, p = rID, v = rValue))

        if rWhich == "team":
            handleTeamChange(players, rID, rValue)
        elif rWhich == "role":
            handleRoleChange(players, rID, rValue)
        elif rWhich == "name":
            handleNameChange(players, rID, rValue)
        else:
            print("ERROR - set with incorrect `which` value ({w})".format(w = rWhich))
    elif rType == "pass":
        # end the turn
        rID = int(r["player"])
        teamTurn = RED if turn is False else BLUE

        for p in players:
            if p.id == rID:
                if p.color != teamTurn:
                    print("WARNING - player from wrong team tried to pass")
                    return

        for p in players:
            if p.role == GUESSPLAYER and p.color == teamTurn:
                print("INFO - team {c} has elected to pass".format(c = RED if turn is False else BLUE))

                # force team change
                await turnLogic(True)
                return None

        print("WARNING - player from wrong team requested pass")
    elif rType == "submit":
        rTouchCount = int(r["value"])
        print("INFO - changing the number of touches")


        defaultNumTouches = rTouchCount + 1
        numTouches = defaultNumTouches

        print("INFO - {x} and {y}".format(x = defaultNumTouches, y = numTouches))

        teamVal = RED if turn is False else BLUE

        redCount, blueCount = b.getScore()

        r = {
            "type" : "turn",
            "team" : teamVal,
            "touches" : numTouches,
            "red" : redCount,
            "blue" : blueCount
        }

        # broadcast turn change to everyone
        msg = json.dumps(r)
        await broadcast(sockets, msg)
    else:
        print("ERROR - Case may not be handled yet")


async def turnLogic(forceTurnChange = False):
    """
    Function that handles turn changing and touches
    """

    global numTouches
    global defaultNumTouches
    global turn
    global sockets

    if forceTurnChange:
        print("INFO - the teams have been FORCED to change")

    if numTouches < 1 or forceTurnChange:
            numTouches = defaultNumTouches
            turn = not turn
            print("INFO - it's {c} teams turn".format(c = RED if turn is False else BLUE))

    teamVal = RED if turn is False else BLUE

    redCount, blueCount = b.getScore()

    r = {
        "type" : "turn",
        "team" : teamVal,
        "touches" : numTouches,
        "red" : redCount,
        "blue" : blueCount
    }

    # broadcast turn change to everyone
    msg = json.dumps(r)
    await broadcast(sockets, msg)


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
