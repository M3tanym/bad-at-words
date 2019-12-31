"""
Functions to handle game logic
"""

from board import Board
from player import Player

def handleTouch(b: Board, word: str, player: int):
    # Set space visible
    b.setVisibleFlag(word)

    
def handleTeamChange(players, rID: int, rValue: str):
    for p in players:
        if p.id == rID:
            print("INFO - changing player {p} to team {c}".format(p = str(p), c = rValue))
            p.color = rValue


def handleRoleChange(players, rID: int, rValue: str):
    for p in players:
        if p.id == rID:
            print("INFO - changing player {p} to role {c}".format(p = str(p), c = rValue))
            p.role = rValue


def handleNameChange(players, rID: int, rValue: str):
    for p in players:
        if p.id == rID:
            print("INFO - changing player {p} to name {c}".format(p = str(p), c = rValue))
            p.name = rValue
