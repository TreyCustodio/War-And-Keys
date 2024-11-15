from pygame import Rect, Surface, transform
from pygame.draw import rect
from utils import vec, RESOLUTION
from UI import SpriteManager
from . import WordManager

class HudBuilder:

    def getHud(hp, maxHp, killed):
        #   Initialize surface
        surf = Surface(vec(*RESOLUTION))
        surf.set_colorkey((0,0,0))
        
        #   Create Hp bar
        hpBar = Rect(1,1, hp, 16)
        hpOutline = Rect(0,0, maxHp+2, 16+2)
        heartOutline = Rect(maxHp+3, 0, 18,18)

        #   Blit hp bar to the surface
        rect(surf, (255,255,255), hpOutline, 1)
        rect(surf, (0,255,0), hpBar)
        

        #   Blit the heart image
        heart = SpriteManager.getInstance().getSprite("heart.png", (0,1))
        surf.blit(heart, (maxHp+4, 1))
        rect(surf, (0,0,0), heartOutline, 1)

        #   Blit kill count to the surface
        count = str(killed)
        text, length = WordManager.buildText("Slain: "+count, 3)
        surf.blit(text, (0,18))




        return transform.scale2x(surf)
