"""
File for game board related details
"""

import json
import random
from pprint import pprint

from settings import RED, BLUE, BLACK, WHITE, ASSASIN_VICTORY, AGENT_VICTORY

class Space:
    """
    A space has a color and a word and a visibility flag
    """
    color: str = None
    word: str = None
    visible: bool = False

    def __init__(self, inColor: str, inWord: str):
        """
        Default constructor for space

        Arguments:
            inColor {str} -- color to set space to
            inWord {str} -- word for that space
        """
        self.color = inColor
        self.word = inWord

    def __str__(self):
        """
        String overload for Space
        """
        return "{w} -- ({c}) -- ({v})".format(w = self.word, c = self.color, v = self.visible)

    def toDict(self):
        """
        Makes a dictionary of space
        """
        r = {
            "word" : self.word,
            "color" : self.color,
            "visible" : self.visible
        }

        return r


class Board:
    spaces = []

    def __init__(self, wordList):
        """
        Constructor for a board

        Arguments:
            wordList {List: [str]} -- randomly sampled list of 25 words
        """
        random.shuffle(wordList)

        # make spaces out of words
        # RED team
        # TODO: red team always starts lol
        for word in wordList[0:9]:
            self.spaces.append(Space(RED, word))
        # BLUE team
        for word in wordList[9:17]:
            self.spaces.append(Space(BLUE, word))
        # NOBODYS team
        for word in wordList[17:24]:
            self.spaces.append(Space(WHITE, word))
        self.spaces.append(Space(BLACK, wordList[24]))

        # shuffle the board for final representation
        random.shuffle(self.spaces)

    def __str__(self):
        """
        String overload for Board
        """

        print(len(self.spaces))

        r = ""

        start: int = 0
        end: int = 5
        step: int = 5
        while end is not 30:
            for s in self.spaces[start:end]:
                r += str(s).ljust(30)
            r += "\n"
            end += step
            start += step

        return r

    def toJson(self):
        """
        Serialize board to json
        """
        spaceDicts = [s.toDict() for s in self.spaces]

        r = {
            "type" : "board",
            "spaces" : spaceDicts
        }

        return json.dumps(r)

    def setVisibleFlag(self, word: str):
        """
        Given a word, change that spaces visible flag to True

        Arguments:
            word {str} -- the word
        """

        # TODO: I know this isn't optimal but I don't know what is
        for s in self.spaces:
            if s.word == word:
                s.visible = True
    
    def removeVisibleFlag(self, word: str):
        """
        Given a word, change that spaces visible flag to False

        Arguments:
            word {str} -- the word
        """

        # TODO: I know this isn't optimal but I don't know what is
        for s in self.spaces:
            if s.word == word:
                s.visible = False

    def getSpaceInfo(self, word: str):
        """
        Returns the representation for the given word space
        
        Arguments:
            word {str} -- the word to look for
        """

        for s in self.spaces:
            if s.word == word:
                return s

    def getScore(self):
        """
        Finds the count of red and blue agents currently visible
        """
        redCount = 0
        blueCount = 0

        for s in self.spaces:
            if s.visible == True:
                if s.color == RED:
                    redCount += 1
                elif s.color == BLUE:
                    blueCount += 1

        return redCount, blueCount


    def checkWin(self):
        redCount = 0
        blueCount = 0
        assasin = False

        for s in self.spaces:
            if s.visible == True:
                if s.color == RED:
                    redCount += 1
                elif s.color == BLUE:
                    blueCount += 1
                elif s.color == BLACK:
                    assasin = True
        
        # check if assasin is toggled
        # -1 signifies the current team loses
        if assasin:
            return -1
        
        # all red agents found
        # 2 signifies Red team victory
        if redCount >= 9:
            return 2
        # all blue agents found
        # 3 signifies the Blue team victory
        if blueCount >= 8:
            return 3
        
        # return 0 on no winning condition
        return 0 





if __name__ == "__main__":
    # Test word sample
    test = ["night", "purple", "income", "police", "mix", "committee", "bus", "buyer", "hit", "valuable", "pressure", "food", "stay", "shake", "wind", "white", "insect", "shine", "formal", "birthday", "presence", "review", "opportunity", "fee", "agency"]

    # Make a board, give it words
    b = Board(test)

    # Serialize the board to a json message
    # pprint(b.toJson())

    print("____TEST ASSASIN LOSS____")
    # set the visible flag for assasin
    for s in b.spaces:
        if s.color == BLACK:
            b.setVisibleFlag(s.word)
    
    winVal = b.checkWin()
    print("ASSERT {v} == -1".format(v = winVal))
    for s in b.spaces:
        if s.color == BLACK:
            b.removeVisibleFlag(s.word)


    print("____TEST RED WIN____")
    for s in b.spaces:
        if s.color == RED:
            b.setVisibleFlag(s.word)
    
    winVal = b.checkWin()
    print("ASSERT {v} == 2".format(v = winVal))
    for s in b.spaces:
        if s.color == RED:
            b.removeVisibleFlag(s.word)

    
    print("____TEST BLUE WIN____")
    for s in b.spaces:
        if s.color == BLUE:
            b.setVisibleFlag(s.word)
    
    winVal = b.checkWin()
    print("ASSERT {v} == 3".format(v = winVal))
    for s in b.spaces:
        if s.color == BLUE:
            b.removeVisibleFlag(s.word)

    
    print("____TEST NO WIN____")
    count = 0
    cap = 5
    for s in b.spaces:
        if s.color == RED and count < cap:
            b.setVisibleFlag(s.word)
            count += 1
        if s.color == BLUE and count < cap:
            b.setVisibleFlag(s.word)
            count += 1
    
    winVal = b.checkWin()
    print("ASSERT {v} == 0".format(v = winVal))
    for s in b.spaces:
        if s.color == RED:
            b.removeVisibleFlag(s.word)
        if s.color == BLUE:
            b.removeVisibleFlag(s.word)
