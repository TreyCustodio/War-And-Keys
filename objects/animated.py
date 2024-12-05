from . import Drawable
from utils import vec
from UI import SpriteManager
import numpy as np

class Animated(Drawable):
    def __init__(self, position: tuple = vec(0,0), fileName: str ="", offset: tuple =(0,0), nFrames: int = 1, fps: int = 16, scale=False):
        if scale:
            super().__init__(position, fileName, offset, scale=True)
        else:
            super().__init__(position, fileName, offset)
        self.fileName = fileName
        self.nFrames = nFrames
        self.fps = fps
        self.frameCount = 0
        self.row = offset[0]
        self.column = offset[1]
        self.timer = 0.0

        self.states = {"base":[fileName, nFrames, fps, vec(0,0)]} #  Maps states to their nFrames and fps
        self.state = "base"
        self.playing = False
        self.previous = "base"

    
    def addState(self, name : str, fileName: str, nFrames: int, fps: int, offset: tuple = vec(0,0)):
        """
        Adds a new animation for a given state.
        Indices for each state in self.states:
        0 -> fileName, 1 -> nFrames, 2 -> fps
        """
        self.states[name] = [fileName, nFrames, fps, offset]
    
    def change_state(self, state : str):
        if state in self.states:
            ##  Change states
            self.state = state

            ##  Reset Animation
            self.row = 0
            self.column = 0

            ##  Update the image
            self.image = (SpriteManager.getInstance().getSprite(self.states[self.state][0], (self.row, self.column)))

    def play_animation(self, state="base", loop = False):
        """
        Plays the specified animation.

        Params:
        state -> tells Animated which animation to play
        loop  -> if True, continues playing the same animation after one loop. Else, return to the base animation
        """
        if state in self.states:
            self.previous = self.state #Store previous state
            self.playing = True
            self.looping = loop
            self.change_state(state)

    def draw(self, drawSurface, drawHitbox=False, use_camera=True):
        super().draw(drawSurface, offset=self.states[self.state][3])

    def update(self, seconds, scale = False):
        super().update(seconds)

        self.timer += seconds
        if self.timer >= 1 / self.states[self.state][2]:
            self.timer = 0.0
            self.row += 1
            self.row %= self.states[self.state][1]
            
            ##  Stop playing Animation
            if self.playing and self.row == 0:
                self.playing = False
                if not self.looping:
                    self.change_state(self.previous)
                    self.image = SpriteManager.getInstance().getSprite(self.states[self.state][0], (0, 0))
                    self.looping = False
                return
            
            self.image = SpriteManager.getInstance().getSprite(self.states[self.state][0], (self.row, self.column))


        
class Bullet(Animated):
    def __init__(self, position: tuple = vec(0, 0), enemy = None):
        super().__init__(position, "bullet.png", (0,0), 3, 16)

        ##  Keeps track of the enemy for homing properties
        self.enemy = enemy

        ##  Speed Attributes
        self.speed = 50
        self.max_speed = 300

        ##  Set Velocity
        self.set_velocity()


    def set_velocity(self):
        """
        A homing function.
        Steers the bullet and keeps the velocity
        below the maximum speed
        """

        ##  Calculate the slope of the line pointing from the bullet to the enemy
        self.vel = (self.enemy.position - self.position) * self.speed
        
        ##  Adjust the velocity according to the maximum speed
        if self.vel[0] < 0:
            self.vel[0] = -self.max_speed if self.vel[0] < -self.max_speed else self.vel[0]

        elif self.vel[0] > 0:
            self.vel[0] = self.max_speed if self.vel[0] > self.max_speed else self.vel[0]

        if self.vel[1] < 0:
            self.vel[1] = -self.max_speed if self.vel[1] < -self.max_speed else self.vel[1]

        elif self.vel[1] > 0:
            self.vel[1] = self.max_speed if self.vel[1] > self.max_speed else self.vel[1]

        

    def update(self, seconds):
        super().update(seconds)
        self.set_velocity()
        self.position += self.vel * seconds