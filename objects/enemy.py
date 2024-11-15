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
        self.sniped = False

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

    def snipe(self):
        self.string = self.string[0]
        self.sniped = True
        self.buildString()

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
        if self.sniped:
            self.textSurf, self.text_length = WordManager.buildText(self.string, self.textRow + 8)
        
        else:
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
    def __init__(self, string = "a", color=(255, 255, 255), speed = 75):
        super().__init__(vec(RESOLUTION[0], 32), "flyer.png", (0,0), color=color, string=string)
        self.speed = speed
        self.frame_counter = 0  #   Change vel every few frames
        self.dive_tick = 0
        self.vel = vec(-self.speed, self.speed)

        self.diving = False

    def setVelocity(self):
        if self.vel[1] > 0:
            self.vel = vec(-self.speed, -self.speed)
        else:
            self.vel = vec(-self.speed, self.speed)

    @override
    def kill(self):
        """
        Begin death animation.
        """
        self.dead = True
    
    @override
    def getDamage(self):
        return 8

    @override
    def update(self, seconds, key=None):

        #   Flyers move in a V shape and then dive for the player
        if not self.diving:
            self.frame_counter += 1
            if self.frame_counter == 20:

                ##  Reset the frame counter
                ##  Increment the dive tick
                self.frame_counter = 0
                
                if self.position[0] <= 250:

                    ##   Dive
                    self.diving = True
                    d_x = self.position[0] - 16*3
                    d_y = self.position[1] - (RESOLUTION[1] - (FLOOR + 16))
                    
                    
                    self.vel = vec(-d_x, -d_y)
                    #self.vel = vec(-self.speed, self.speed)
                
                else:

                    ##  Change the velocity
                    self.setVelocity()
        
        ##  Proceed with regular update routine
        super().update(seconds, key)
    
    
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