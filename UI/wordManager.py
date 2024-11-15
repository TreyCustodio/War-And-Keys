from pygame import Surface, transform
from os.path import join
from random import randint
from UI import SpriteManager
from utils import RESOLUTION, vec

"""
Manages words for the game.
"""

class WordManager:

    DIFFICULTY = None

    def setDifficulty(diff = None):
        if WordManager.DIFFICULTY == None:
            WordManager.DIFFICULTY = diff

    def getCommon(sniping = False):
        """
        Return a common word from
        1000-most-common-words.txt
        """
        rand = randint(1,998)
        words = open("words\\common.txt")
        lines = words.readlines()
        line = lines[rand]

        if WordManager.DIFFICULTY == "easy":
            if "'" in line:
                line = lines[rand+1]
        
        if sniping:
            return line[0].upper()
        
        else:
            string = line[0].upper() + line[1:line.index("\n")]
            return string
    
    def getSeven(hard = False):
        """
        Return a seven letter word.
        If hard: get it from word-list-7-letters.txt
        else:    get it from common-7-letter-words.txt
        """
        rand = randint(1,40092)
        words = open("words\\hard7.txt")
        lines = words.readlines()
        line = lines[rand]
        string = line[0].upper() + line[1:line.index("\n")]
        return string

    def buildText(text, row, scale = False, getLen = True, title = False):
        """
        Create a surface containing
        some text.
        """

        #   Initialize the surface and positional vars
        surf = Surface(vec(*RESOLUTION))
        surf.set_colorkey((0,0,0)) # Make black transparent

        x = 0   # x coordinate of the letter
        dx = 8  # difference in x for each char

        for char in text:
            #  Adjust the spacing. About 2 Pixels between each char.
            if char == "I":
                x -= 1
                dx -= 1
            elif char == "M" or char == "W" or char == "Q" or char == "S":
                x += 1
                dx += 1
            elif char == "g":
                x += 1
                dx += 1
            elif char == "i" or char == "l" :
                x -= 2
                dx -= 1
            elif char == " ":
                x += dx
                continue
            
            #   Blit the letter to the surface, update the position
            image = SpriteManager.getInstance().getSprite("chars.png", (ord(char)-33, row))
            surf.blit(image, vec(x, 0))
            x += dx
            dx = 8
        

        ##  Return the scaled surface
        if scale:
            if getLen:
                if title:
                    return transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4)), x
                else:
                    return transform.scale2x(surf), x
            else:
                return transform.scale2x(surf)
        
        ##  Return the unscaled surface
        else:
            if getLen:
                return surf,x
            else:
                return surf
    
