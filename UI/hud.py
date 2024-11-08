from pygame import Rect, Surface
from pygame.draw import rect
from utils import vec, RESOLUTION
from . import WordManager

class HudBuilder:

    def getHud(hp, maxHp, killed):
        #   Initialize surface
        surf = Surface(vec(*RESOLUTION))
        surf.set_colorkey((0,0,0))
        
        #   Create Hp bar
        hpBar = Rect(1,1, hp, 16)
        hpOutline = Rect(0,0, maxHp+2, 16+2)

        #   Blit hp bar to the surface
        rect(surf, (255,255,255), hpOutline, 1)
        rect(surf, (0,255,0), hpBar)

        #   Blit kill count to the surface
        count = str(killed)
        text, length = WordManager.buildText("Slain: "+count, 3)
        surf.blit(text, (2,18))




        return surf