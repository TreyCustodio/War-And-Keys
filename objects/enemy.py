import pygame
from abc import abstractmethod
from typing import Any, override
from . import Animated
from utils import RESOLUTION, FLOOR, vec
from UI import SoundManager, SpriteManager, WordManager

from random import randint

class Enemy(Animated):
    """
    An Abstract Enemy Class.
    Specifies an enemy's states,
    how to draw them, and how to update them.
    """
    def __init__(self, position, fileName="", offset = (0,0), velocity = vec(-50,0), nFrames = 1, fps = 16, color = (255,255,255), string="", attack_frame = 0, deaths = 0):
        """
        Initialize all of the enemy's variables.
        """
        super().__init__(position, fileName, offset, nFrames, fps)
        
        #   Attributes
        self.vel    = velocity
        self.type = None
        self.color = color
        self.attack_frame = attack_frame
        self.death_tick = 0
        self.max_tick = deaths

        #   Text Vars
        self.textRow = 0
        self.textTimer = 0.0
        self.string = string
        self.textSurf = None
        self.text_length = 0

        #   States
        self.attacking = False   # Attacking the player
        self.attack_done = False # Ready to deal damage to the player
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
    def attack(self):
        """
        Defines the enemy's
        routine for damaging the Player.
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


    def draw(self, drawSurface, drawHitbox=False, use_camera=False):
        """
        Blit the enemy onto
        the drawSurface.
        """
        if self.dead:
            return
        else:
            super().draw(drawSurface, drawHitbox, use_camera)
            if not self.dying:
                drawSurface.blit(self.textSurf, vec(self.position[0] + 8 - self.text_length//2, self.position[1] - 24))

                
    def update(self, seconds, key = None):
        #   Death States
        if self.dead:
            return
        
        elif self.dying or self.attacking:
            if self.playing == False: ## At the end of the death animation
                self.dead = True
                return
            
            else:
                super().update(seconds)
                if self.attacking and not self.attack_done and self.row == self.attack_frame:
                    self.attack_done = True
                return
        
        #   Update TextRow
        self.textTimer += seconds
        if self.textTimer >= 0.2:
            self.textRow += 1
            self.textRow %= 4
            self.textTimer = 0.0
            self.buildString()


        #   Update Position
        self.position += self.vel * seconds

        #   Animate
        super().update(seconds)

        #   Out of bounds safety
        if self.position[0] <= 0:
            self.dead = True

class Walker(Enemy):
    def __init__(self, string = "a", color = (255,255,255)):
        super().__init__(vec(RESOLUTION[0], RESOLUTION[1] - FLOOR - 16), "ground_1.png", (0,0), velocity=vec(-100,0), nFrames=14, fps=32, color=color, string=string, attack_frame=18, deaths=3)
        
        ##  Animations
        self.addState("attack", "ground_2.png", 27, 16, vec(57, 142))
        self.addState("death_1", "ground_3.png", 26, 32, vec(57, 142))
        self.addState("death_2", "ground_4.png", 10, 32, vec(57, 142))
        self.addState("death_3", "ground_5.png", 17, 32, vec(57, 142))


    @override
    def attack(self):
        """
        Begin attack animation
        """
        if not self.dying:
            self.attacking = True
            self.vel = vec(0,0)
            self.play_animation("attack", loop=True)

    @override
    def kill(self):
        """
        Begin death animation.
        """

        ##  Set death state
        self.dying = True

        ##  Play the death animation
        rand = randint(0,2)
        if rand == 0:
            self.play_animation("death_1", loop=True)
        elif rand == 1:
            self.play_animation("death_2", loop=True)
        elif rand == 2:
            self.play_animation("death_3", loop=True)
        
    

    @override
    def getDamage(self):
        return 5


class Flyer(Enemy):
    def __init__(self, string = "a", color=(255, 255, 255), speed = 75):
        super().__init__(vec(RESOLUTION[0], 64), "flyer_1.png", (0,0), color=color, string=string, attack_frame=12)

        ##  Attributes and Counters
        self.diving = False
        self.speed = speed

        self.frame_counter = 0  #   Change vel every few frames
        self.dive_tick = 0

        self.vel = vec(-self.speed, self.speed)
        
        
        ##  Animations
        self.addState("dive", "flyer_2.png", 22, 16, vec(0, 0))
        self.addState("explode", "flyer_4.png", 17, 64, vec(23, 21))

        self.addState("death_1", "flyer_3.png", 19, 32, vec(115, 54))

        self.addState("death_2", "flyer_5.png", 17, 32, vec(51, 30))
        self.addState("death_3", "flyer_6.png", 25, 32, vec(74, 30))

    def setVelocity(self):
        if self.vel[1] > 0:
            self.vel = vec(-self.speed, -self.speed)
        else:
            self.vel = vec(-self.speed, self.speed)

    @override
    def attack(self):
        """
        Begin damage animation
        """
        if not self.dying:
            self.attacking = True

            self.vel = vec(0,-75)
            self.play_animation("explode", loop=True)

    @override
    def kill(self):
        """
        Begin death animation.
        """

        ##  Set death state
        self.dying = True
        ##  Play the death animation
        rand = randint(0,2)
        if rand == 0:
            self.play_animation("death_1", loop=True)
        elif rand == 1:
            self.play_animation("death_2", loop=True)
        elif rand == 2:
            self.play_animation("death_3", loop=True)
    
    @override
    def getDamage(self):
        return 8

    @override
    def update(self, seconds, key=None):

        #   Flyers move in a V shape and then dive for the player
        if not self.diving and not self.dying:
            self.frame_counter += 1
            if self.frame_counter == 20:

                ##  Reset the frame counter
                ##  Increment the dive tick
                self.frame_counter = 0
                
                if self.position[0] <= 250:

                    ##   Dive
                    self.diving = True
                    self.change_state("dive")

                    d_x = self.position[0] - 16*3
                    d_y = self.position[1] - (RESOLUTION[1] - (FLOOR + 16))
                    
                    
                    self.vel = vec(-d_x, -d_y)
                    #self.vel = vec(-self.speed, self.speed)
                
                else:

                    ##  Change the velocity
                    self.setVelocity()
        
        ##  Proceed with regular update routine
        super().update(seconds)
    
    
class Sniper(Walker):
    """
    Type this word to receive an upgrade
    that shortens every enemy's word to 1 char
    for 10 seconds.
    """
    def __init__(self, string="Snipealicious"):
        super().__init__(string, color=(255,255,70))
        self.type = "snipe"
        self.image.set_alpha(0)

    @override
    def buildString(self):
        self.textSurf, self.text_length = WordManager.buildText(self.string, self.textRow+8)

class Builder():
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass