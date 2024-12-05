from typing import Any
from utils import SCALE, RESOLUTION, vec, rectAdd
from UI import SpriteManager
import pygame

"""
This file contains Drawable Objects, 
including HUD-related objects and text-related objects.
"""

        
class Drawable(object):
    """
    Drawable object class originally written by Dr. Liz Matthews
    """
    
    CAMERA_OFFSET = vec(0,0)
    
    @classmethod
    def updateOffset(cls, trackingObject, worldSize):
        
        objSize = trackingObject.getSize()
        objPos = trackingObject.position
        
        offset = objPos + (objSize // 2) - (RESOLUTION // 2)
        
        for i in range(2):
            offset[i] = int(max(0,
                                min(offset[i],
                                    worldSize[i] - RESOLUTION[i])))
        
        cls.CAMERA_OFFSET = offset

    @classmethod
    def resetOffset(cls):
        cls.CAMERA_OFFSET = vec(0,0)

    @classmethod    
    def translateMousePosition(cls, mousePos):
        newPos = vec(*mousePos)
        newPos /= SCALE
        newPos += cls.CAMERA_OFFSET
        
        return newPos
    
    def __init__(self, position=vec(0,0), fileName="", offset=None, scale = False):
        
        if fileName != "":
            if scale:
                self.image = SpriteManager.getInstance().getSprite(fileName, offset, scale=True)
            else:
                self.image = SpriteManager.getInstance().getSprite(fileName, offset)
        
        self.position  = vec(*position)
        self.imageName = fileName
        self.block = False

    def draw(self, drawSurface, drawHitbox = False, use_camera = False, offset = vec(0,0)):
        """
        Blit's the object's image to the drawSurface.

        Params:
        drawHitbox -> draws the collisionRect if True
        use_camera -> draws the object according to the camera offset if True
        offset     -> draws the object according to a specific offset
        """
        if use_camera:
            drawSurface.blit(self.image, list(map(int, self.position - Drawable.CAMERA_OFFSET)))
        else:
            drawSurface.blit(self.image, list(map(int, self.position - offset)) )
            
        if drawHitbox:
            collision = rectAdd(-Drawable.CAMERA_OFFSET, self.getCollisionRect())
            pygame.draw.rect(drawSurface, (255,255,255), collision, 1)

    def getSize(self):
        return vec(*self.image.get_size())
    
    def getCenterX(self):
        """
        Outdated...
        Returns the x coordinate on the screen
        representing the center point.
        """
        size = self.getSize()
        x = size[0] // 2
        return self.position[0] + x
    
    def handleEvent(self, event):
        pass
    
    def update(self, seconds):
        pass
    
    
    def getCollisionRect(self):
        newRect = self.image.get_rect()
        newRect.left = int(self.position[0])
        newRect.top = int(self.position[1])
        return newRect
    
    def doesCollide(self, other):
        return self.getCollisionRect().colliderect(other.getCollisionRect())   
    
    def doesCollideList(self, others):
        rects = [r.getCollisionRect() for r in others]
        return self.getCollisionRect().collidelist(rects)     