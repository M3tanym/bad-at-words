"""
Functions to handle game logic
"""

from board import Board

def handleTouch(b: Board, word: str, player: int):
    # Set space visible
    b.setVisibleFlag(word)
