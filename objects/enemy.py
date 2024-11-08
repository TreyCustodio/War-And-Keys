import pygame
from abc import abstractmethod
from typing import Any, override
from . import Animated
from utils import RESOLUTION, FLOOR, vec
from UI import SoundManager, SpriteManager, WordManager

class Enemy(Animated):
    """
    An Abstract Enemy Class.
    Specifies an enemy's states,
    how to draw them, and how to update them.
    """
    def __init__(self, position, fileName="", offset = (0,0), velocity = vec(-50,0), nFrames = 1, fps = 16, color = (255,255,255), string=""):
        """
        Initialize all of the enemy's variables.
        """
        super().__init__(position, fileName, offset, nFrames, fps)
        
        #   Attributes
        self.vel    = velocity
        self.type = None
        self.color = color

        #   Text Vars
        self.textRow = 0
        self.textTimer = 0.0
        self.string = string
        self.textSurf = None
        self.text_length = 0

        #   States
        self.attacking = False   # Attacking the player
        self.dead   = False # Ready to disappear
        self.dying  = False # Death animation
        
        self.buildString()

    def getLength(self):
        """
        Returns the width of
        the enemy's text surface.
        """
        return self.text_length
    
    def stop(self):
        """
        Stop moving and attack.
        """
        self.vel = vec(0,0)
        self.attacking = True

    @abstractmethod
    def kill(self):
        """
        Defines the enemy's
        death routine.
        """
        return
    
    @abstractmethod
    def getDamage(self):
        """
        Return the enemy's damage.
        """
        return
    
    def buildString(self):
        """
        Build the enemy's text surface.
        """
        self.textSurf, self.text_length = WordManager.buildText(self.string, self.textRow)


    def draw(self, drawSurface, drawHitbox=False, use_camera=True):
        """
        Blit the enemy onto
        the drawSurface.
        """
        if self.dead or self.dying:
            return
        else:
            super().draw(drawSurface, drawHitbox, use_camera)
            drawSurface.blit(self.textSurf, vec(self.position[0] + 8 - self.text_length//2, self.position[1] - 24))
    
    def handleKey(self, key):
        #   Typing damage
        if key == self.string[0]:
            self.string.pop(0)
            if len(self.string) == 0:
                self.dead = True
                SoundManager.getInstance().playSFX("death.wav")
                
    def update(self, seconds, key = None):
        #   Death States
        if self.dead:
            return
        
        elif self.dying:
            return
        
        #   Update TextRow
        self.textTimer += seconds
        if self.textTimer >= 0.2:
            self.textRow += 1
            self.textRow %= 4
            self.textTimer = 0.0
            self.buildString()

        #   Typing Damage
        if key != None:
            self.handleKey(key)

        #   Update Position
        self.position += self.vel * seconds

        #   Animate
        super().update(seconds)

        #   Out of bounds safety
        if self.position[0] <= 0:
            self.dead = True

class Walker(Enemy):
    def __init__(self, string = "a", color = (255,255,255)):
        super().__init__(vec(RESOLUTION[0], RESOLUTION[1] - FLOOR - 16), "walker.png", (0,0), velocity=vec(-50,0), color=color, string=string)

    @override
    def kill(self):
        """
        Begin death animation.
        """
        self.dead = True
    
    @override
    def getDamage(self):
        return 5


class Flyer(Enemy):
    def __init__(self, string = "a", color=(255, 255, 255), speed = 50):
        super().__init__(vec(RESOLUTION[0], 20), "flyer.png", (0,0), color=color)
        self.velocity = vec(speed, speed)
        self.speed = speed
    
    def setVelocity(self):
        self.velocity = vec(self.speed, self.speed)

    @override
    def kill(self):
        """
        Begin death animation.
        """
        self.dead = True
    
    @override
    def getDamage(self):
        return 8
    
    
class Sniper(Walker):
    """
    Type this word to receive an upgrade
    that shortens every enemy's word to 1 char
    for 10 seconds.
    """
    def __init__(self, string="Snipealicious"):
        super().__init__(string, color=(255,255,70))
        self.type = "snipe"

    @override
    def buildString(self):
        self.textSurf, self.text_length = WordManager.buildText(self.string, self.textRow+8)

class Builder():
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass