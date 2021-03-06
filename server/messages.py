"""
Contains functinos to build custom reponse messages for websockets
"""

import json
from player import Player
from settings import VERSION, RED, BLACK, BLUE, WHITE, GUESSPLAYER, CMPLAYER, AGENT_VICTORY, ASSASIN_VICTORY

def room_msg(players: list):
    """
    A message to list player data in a room
    
    Arguments:
        players {list} -- list of players
    """

    msgType = "room"

    p = [p.toDict() for p in players]

    r = {
        "type" : msgType,
        "players" : p
    }

    return json.dumps(r)


async def playerid_msg(playerIdCount: int):
    """
    Message to send player when they first join the game with their ID
    
    Arguments:
        playerIdCount {int} -- The unique player ID
    """

    msgType = "playerid"
    
    r = {
        "type" : msgType,
        "value" : playerIdCount
    }

    return json.dumps(r)



if __name__ == "__main__":
    players = []
    players.append(Player("bob", 0, RED, GUESSPLAYER))
    players.append(Player("jerry", 1, RED, CMPLAYER))
    players.append(Player("joe", 2, BLUE, GUESSPLAYER))
    players.append(Player("boop", 3, BLUE, CMPLAYER))

    print(room_msg(players))