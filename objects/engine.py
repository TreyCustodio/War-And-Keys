from pygame import Rect, Surface, draw, transform
from pygame.font import SysFont

from . import Drawable, Animated, Walker, Sniper
from UI import SoundManager, WordManager, EventManager, HudBuilder
from utils import RESOLUTION, FLOOR, vec

class Engine:
    """
    The Engine drives the game.
    Each frame, it draws the game in its current state,
    handles input from the user,
    and updates the objects in the game.
    """


##  ----------------------------------------------- ##
                ##  Initialization   ##

    def __init__(self, spawnRate=1.0):
        """
        Initialize the engine's relevant
        variables and objects.
        """

        #   ------------------- #
        #         States        #

        self.inTitle = True
        self.inGame = False
        self.starting = True
        self.paused = False

        self.dead = False
        self.hurting = False

        self.sniping = False
        self.upgradeReady = True
        
        self.fade_on = False
        self.fade_off = True


        #   ------------------- #
        #   Timers and Counters #

        ##  Spawn Rate / Max Enemies
        self.spawnRate = spawnRate
        self.maxEnemies = 20

        ##  Text
        self.textRow = 0
        self.textTimer = 0.0
        
        ##  Frames
        self.iFrames = 0
        self.frameCounter = 0

        ##  Spawning
        self.spawnTimer = 0.0
        self.snipeTimer = 10.0
        
        ##  Overlay
        self.fade_alpha = 255
        self.flashTimer = 0.0
        self.flash_alpha = 200
    

        #   ------------------- #
        #     Drawable Objects  #

        ##  Title Screen
        self.title_text = SysFont("Garamond", 36).render("War And Keys", False, (200,0,0))
        self.title = SysFont("Garamond", 16).render("Press any button", False, (255,255,255))
        
        ##  Background and Floor
        self.background = Rect((0,0), (RESOLUTION[0], RESOLUTION[1]))
        self.floor = Rect((0,RESOLUTION[1] - FLOOR), (RESOLUTION[0], 1))
        
        ##  Pause Screen
        self.flash = Drawable((0,0), "black.png")
        self.flash.image = transform.scale(self.flash.image, RESOLUTION).set_alpha(self.flash_alpha)
        self.pauseImage = Animated((RESOLUTION[0]//2 - 60//2, RESOLUTION[1]//2 - 16//2), "pause.png", nFrames=1)

        ##  Player
        self.player = Animated((0, RESOLUTION[1] - (FLOOR + 16)), "player.png", nFrames=6)
        
        ##  Fade
        self.fade = Surface(vec(*RESOLUTION))

        ##  Read / Go
        self.ready = Animated()
        self.go = Animated()


        #   ------------------- #
        #      Hp and Damage    #

        ##  HP
        self.hp = 100
        self.maxHp = 100
        
        ##  Damage
        self.damage = 0
        self.damageY = self.player.position[1] - 24

        ##  Kill Count
        self.killed = 0


        #   ------------------- #
        #     Data Structures   #

        self.enemies = [] # List containing the enemies
        self.keyBuffer = [] # List containing the player's current string



##  ----------------------------------------------- ##
            ##  Auxillaury Routines   ##

    def pause(self):
        """
        Pause the game.
        """
        self.playSFX("pause.wav")
        self.paused = True
    
    def resume(self):
        """
        Resume the game.
        """
        self.playSFX("pause.wav")
        self.paused = False
        self.flash_alpha = 200
        self.flash.image.set_alpha(200)
        self.flashTImer = 0.0
    
    def backSpace(self):
        """
        Delete the last character
        in the player's current string.
        """
        if len(self.keyBuffer) > 0:
            del self.keyBuffer[-1]

    def spawn(self, force = False):
        """
        Spawn an enemy.
        """
        if self.sniping:
            e = Walker(WordManager.getCommon(True), (255,255,70))
        else:
            e = Walker(WordManager.getCommon())
        self.enemies.append(e)
    
    def spawnSniper(self):
        """
        Spawn a sniper upgrade.
        """
        e = Sniper()
        self.enemies.append(e)
        self.upgradeReady = False

    def playSFX(self, fileName):
        """
        Play a sound effect.
        """
        SoundManager.getInstance().playSFX(fileName)

    def startGame(self):
        """
        Start the game.
        """
        self.playSFX("pause.wav")
        #SoundManager.getInstance().playBGM("01_Relax-my-eyes.mp3")
        self.inTitle = False
        self.inGame = True
        self.fade_on = True
    
    def hurt(self, damage):
        """
        Hurt the player.
        """
        if not self.hurting:
            self.damageY = self.player.position[1] - 24
            self.hp -= damage
            self.hurting = True



    ##  ----------------------------------------------- ##
                    ##  Event Handling   ##

    def handleKey(self):
        """
        Handles key presses obtained
        from the user.
        """
        if self.paused:
            return
        
        elif self.inGame:
            if WordManager.DIFFICULTY == None:
                WordManager.setDifficulty("easy")

            if EventManager.backspace_ready:
                self.backSpace()
                EventManager.buffBackspace()

            for key in EventManager.queue:
                if len(self.keyBuffer) == 0:
                        self.playSFX("text_1.wav")
                        self.keyBuffer.append(chr(key).upper())
                else:
                    self.playSFX("text_1.wav")
                    self.keyBuffer.append(chr(key))

                del EventManager.queue[0]

    
    def submitString(self):
        """
        Try to damage an enemy
        using the player's current string.
        """
        for e in self.enemies:
            if e.string == ''.join(self.keyBuffer):
                if e.type == "snipe":
                    self.playSFX("text_2.wav")
                    self.snipe()
                    e.kill()
                else:
                    self.playSFX("text_2.wav")
                    self.killed += 1
                    e.kill()
                self.keyBuffer = []
                return
        self.playSFX("text_3.wav")

    def snipe(self):
        """
        Initiate the sniper powerup.
        All enemies can now be
        killed with 1 key press.
        """
        self.sniping = True
        for e in self.enemies:
            e.string = e.string[0]
            e.color = (255,255,70)

        

    ##  ----------------------------------------------- ##
                    ##  Drawing   ##

    def draw(self, drawSurf):
        """
        Blit all the drawable objects
        to the drawSurf.
        """
        if self.inTitle:
            #   Name of the game
            drawSurf.blit(self.title_text, (RESOLUTION[0] // 2 - self.title_text.get_width() // 2, RESOLUTION[1] // 2 - self.title_text.get_height() * 1.5))
            
            #   Press any button
            drawSurf.blit(self.title, (RESOLUTION[0] // 2 - self.title.get_width() // 2, RESOLUTION[1] // 2 - self.title.get_height() // 2))

        elif self.inGame:
            #   Background - First
            self.drawBackground(drawSurf)
            
            #   Floor
            self.drawFloor(drawSurf)
            
            #   Enemies
            for e in self.enemies:
                e.draw(drawSurf)

            #   Player
            self.player.draw(drawSurf)

            #   Current Text Buffer
            text, length = WordManager.buildText(''.join(self.keyBuffer), self.textRow + 4)
            drawSurf.blit(text, (self.player.position[0] + 8, self.player.position[1] - 24))

            #   Damage
            if self.hurting:
                self.drawDamage(drawSurf)

            #   HUD
            drawSurf.blit(HudBuilder.getHud(self.hp, self.maxHp, self.killed), (0,1))
            
            #   Ready / Go
            if self.starting:
                if self.spawnTimer < 0.5:
                    pass
                    #self.ready.draw(drawSurf)
                else:
                    pass
                    #self.go.draw(drawSurf)

            #   Pause
            if self.paused:
                self.flash.draw(drawSurf)
                self.pauseImage.draw(drawSurf)

    def drawBackground(self, drawSurf):
        """
        Draw the background image.
        """
        draw.rect(drawSurf, (0,0,0), self.background)

    def drawFloor(self, drawSurf):
        """
        Draw the floor image.
        """
        draw.rect(drawSurf, (255,255,255), self.floor)

    def drawDamage(self, drawSurf):
        """
        Draw red damage numbers.
        """
        text = SysFont("Garamond", 24).render("-"+str(self.damage), False, (255,50,50))
        drawSurf.blit(text, (self.player.position[0] + 8, self.damageY))

    def drawFade(self, drawSurf):
        """
        Draw black over the entire screen.
        Used for smooth fadeouts.
        """
        drawSurf.blit(self.fade, (0,0))


    ##  ----------------------------------------------- ##
                    ##  Updating    ##

    def update_fade(self, seconds = 0):
        """
        Updates the transparency of
        the fade surface.
        """

        #   Fading On
        if self.fade_on:
            self.fade_alpha += 5
            if self.fade_alpha >= 255:
                self.fade.set_alpha(255)
                self.fade_on = False
            else:
                self.fade.set_alpha(self.fade_alpha)
        
        #   Fading Off
        elif self.fade_off:
            self.fade_alpha -= 5
            if self.fade_alpha <= 0:
                self.fade.set_alpha(0)
                self.fade_off = False
            else:
                self.fade.set_alpha(self.fade_alpha)

    def update_spawn(self, seconds):
        #   Spawn an enemy if the text won't overlap
        spawn = True
        for e in self.enemies:
            if e.position[0] >= RESOLUTION[0] - e.getLength():
                spawn = False
                break
        
        if spawn:
            self.spawnTimer += seconds
            if self.spawnTimer >= self.spawnRate:
                self.spawnTimer = 0.0
                self.spawn()

        #   Spawn a sniper upgrade
        self.frameCounter += 1
        if not self.sniping and self.upgradeReady and self.frameCounter == 5:
            self.spawnSniper()
            self.frameCounter = 0
            
        #   Update Snipe Timer
        if self.sniping:
            self.snipeTimer -= seconds
            if self.snipeTimer <= 0.0:
                self.snipeTimer = 10.0
                self.sniping = False
    
    def update(self, seconds):

        self.update_fade(seconds)

        #   Update Death
        if self.dead:
            return
        
        if self.inGame:

            if self.starting:
                if self.fade_off == False:
                    self.spawnTimer += seconds
                    if self.spawnTimer >= 2.0:
                        self.spawnTimer = 0.0
                        self.starting = False
                return
            elif self.paused:
                self.pauseImage.update(seconds)
                self.flashTimer += seconds
                if self.flashTimer >= 0.5:
                    self.flashTimer = 0.0
                    if self.flash_alpha == 150:
                        self.flash_alpha = 200
                        self.flash.image.set_alpha(self.flash_alpha)
                    else:
                        self.flash_alpha = 150
                        self.flash.image.set_alpha(self.flash_alpha)
                return

            elif self.starting:
                self.update_fade()
                return
            
            #   Update Player
            self.player.update(seconds)
            self.textTimer += seconds
            if self.textTimer >= 0.2:
                self.textRow += 1
                self.textRow %= 4
                self.textTimer = 0.0

            #   Update I-frames
            if self.hurting:
                self.iFrames += 1
                self.damageY -= 1
                if self.iFrames == 30:
                    self.iFrames = 0
                    self.hurting = False
                    self.damage = 0
                    self.damageY = 0
            
            #   Update Enemies
            damage = 0
            if self.enemies:
                for e in self.enemies:
                    if e.dead:
                        del self.enemies[self.enemies.index(e)]
                    else:
                       e.update(seconds)
                       #    Check if enemy is attacking the player
                       if e.position[0] <= self.player.position[0] + self.player.getSize()[0]:
                           e.kill()
                           damage = e.getDamage()
                           self.hurt(damage)
                           self.damage = damage

            #   Spawn Enemies
            self.update_spawn(seconds)


        