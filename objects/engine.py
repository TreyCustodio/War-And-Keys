from pygame import Rect, Surface, draw, transform
from pygame.font import SysFont
from random import randint

from . import Drawable, Animated, Walker, Sniper, Flyer
from UI import SoundManager, SpriteManager, WordManager, EventManager, HudBuilder
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
        self.starting = False
        self.paused = False

        self.dead = False
        self.hurting = False

        self.sniping = False
        self.upgradeReady = False
        
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
        self.title_row = 0

        ##  Spawning
        self.spawnTimer = 0.0
        self.snipeTimer = 10.0
        
        ##  Overlay
        self.fade_alpha = 255
        self.flashTimer = 0.0
        self.flash_alpha = 100

        ##  Sound
        self.sound_int = 0

        #   ------------------- #
        #     Drawable Objects  #

        ##  Title Screen
        self.title_text = SysFont("Garamond", 36).render("War And Keys", False, (200,0,0))
        self.title = SysFont("Garamond", 16).render("Press any button", False, (255,255,255))
        
        ##  Background and Floor
        self.background = Surface(vec(*RESOLUTION))
        self.background.fill((0,50,0))

        self.floor = Surface((RESOLUTION[0], FLOOR))
        self.floor.fill((255,255,255))
        self.floor.fill((0,0,0), Rect(1,1,RESOLUTION[0]-2,FLOOR - 2))
        

        ##  Logo
        self.logo = SpriteManager.getInstance().getSprite("trey_logo.png")
        ##  Pause Screen
        self.flash = Surface(vec(*RESOLUTION))
        self.flash.set_alpha(100)
        self.pauseImage = Animated((RESOLUTION[0]//2 - 60//2, RESOLUTION[1]//2 - 16//2), "pause.png", nFrames=1)

        ##  Player
        self.player = Animated((16*3, RESOLUTION[1] - (FLOOR + 16)), "player.png", nFrames=6)
        
        ##  Fade
        self.fade = Surface(vec(*RESOLUTION))

        ##  Read / Go
        self.ready = Animated()
        self.go = Animated()


        #   ------------------- #
        #      Hp and Damage    #

        ##  HP
        self.hp = 50
        self.maxHp = 50
        
        ##  Damage
        self.damage = 0
        self.damageY = self.player.position[1] - 24

        ##  Kill Count
        self.killed = 0


        #   ------------------- #
        #     Data Structures   #

        self.enemies = [] # List containing the enemies
        self.keyBuffer = [] # List containing the player's current string
        self.text = [] # List containing text obtained from the enemy


##  ----------------------------------------------- ##
            ##  Auxillaury Routines   ##

    def getReady(self):
        return (not self.fade_off) and (not self.fade_on) and (not self.starting)
    
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
        self.flash_alpha = 100
        self.flash.set_alpha(100)
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
        rand = randint(0,4)
        
        if rand == 0:
            e = Walker(WordManager.getCommon())
        elif rand == 1:
            e = Flyer(WordManager.getCommon())
        else:
            e = Walker(WordManager.getCommon())

        if self.sniping:
            e.snipe()

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
        self.fade_on = True
        self.starting = True
        self.frameCounter = 0
    
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
                    self.playSFX("death.wav")
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
            e.snipe()
            

        

    ##  ----------------------------------------------- ##
                    ##  Drawing   ##

    def draw(self, drawSurf):
        """
        Blit all the drawable objects
        to the drawSurf.
        """
        if self.inTitle:
            row = self.title_row

            #   Name of the game
            title, title_len = WordManager.buildText("War and Keys", row, scale=True, title=True)
            drawSurf.blit(title, (RESOLUTION[0] // 2 - title_len * 2, 64))
            
            #   Press any button
            press, press_len = WordManager.buildText("Press any Button", row + 8, scale=True )
            drawSurf.blit(press, (RESOLUTION[0] // 2 - press_len, 144))
            
            

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
            drawSurf.blit(text, (8, self.player.position[1] - 24))

            #   Damage
            if self.hurting:
                self.drawDamage(drawSurf)

            #   HUD
            drawSurf.blit(HudBuilder.getHud(self.hp, self.maxHp, self.killed), (8,16))
            
            if self.sniping:
                snipe_time, snipe_len = WordManager.buildText(str(int(self.snipeTimer)), 8)
                
                drawSurf.blit(snipe_time, vec(32, 256))

            #   Ready / Go
            if self.starting:
                if self.spawnTimer == 0.0:
                    return
                
                elif self.spawnTimer > 0.0 and self.spawnTimer < 0.5:
                    if self.sound_int == 0:
                        self.playSFX("Ready.wav")
                        self.sound_int += 1

                    surf, x = WordManager.buildText("Ready?", 2, scale = True)
                    drawSurf.blit(surf, vec(RESOLUTION[0] // 2 - x // 2, RESOLUTION[1] // 2 - 8))

                elif self.spawnTimer > 0.5 and self.spawnTimer < 0.55:
                    return
                
                else:
                    if self.sound_int == 1:
                        self.playSFX("Go.wav")
                        self.sound_int = 0
                    surf, x = WordManager.buildText("GO!", 6, scale = True)
                    drawSurf.blit(surf, vec(RESOLUTION[0] // 2 - x // 2, RESOLUTION[1] // 2 - 8))
                    pass

            #   Pause
            if self.paused:
                drawSurf.blit(self.flash, (0,0))
                self.pauseImage.draw(drawSurf)
                full, x = WordManager.buildText("Toggle Fullscreen", 2, scale=True)
                drawSurf.blit(full, (RESOLUTION[0] // 2 - x//2, RESOLUTION[1]//2 - 8))

    def drawLogo(self, drawSurf):
        drawSurf.blit(self.logo, (RESOLUTION[0] // 2 - self.logo.get_width() // 2, RESOLUTION[1] // 2 - self.logo.get_height() // 2))

    def drawBackground(self, drawSurf):
        """
        Draw the background image.
        """
        drawSurf.blit(self.background, (0,0))

    def drawFloor(self, drawSurf):
        """
        Draw the floor image.
        """
        drawSurf.blit(self.floor, (0, RESOLUTION[1] - FLOOR))

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
                self.fade_alpha = 255
                self.fade.set_alpha(255)
                self.fade_on = False
            else:
                self.fade.set_alpha(self.fade_alpha)
        
        #   Fading Off
        elif self.fade_off:
            self.fade_alpha -= 5
            if self.fade_alpha <= 0:
                self.fade.set_alpha(0)
                self.fade_alpha = 0
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
        if not self.sniping and self.upgradeReady and self.frameCounter == 5:
            self.spawnSniper()
            self.frameCounter = 0
        else:
            self.frameCounter += 1
      

            
        #   Update Snipe Timer
        if self.sniping:
            self.snipeTimer -= seconds

            if self.snipeTimer <= 0.0:

                ##  Stop Sniping
                self.snipeTimer = 10.0
                self.sniping = False
                self.upgradeReady = True
    
    def update(self, seconds):
        print(self.keyBuffer)

        #   Update the fade
        self.update_fade(seconds)

        #   Update Death
        if self.dead:
            return
        
        #   Update Title Text
        if self.inTitle:
            self.frameCounter += 1

            if self.frameCounter == 15:
                self.frameCounter = 0
                self.title_row += 1
                self.title_row %= 4

        #   Update in-game
        if self.inGame:
            
            #   Ready / Go!
            if self.starting:
                if self.fade_off == False:
                    self.spawnTimer += seconds
                    if self.spawnTimer >= 1.0:
                        self.spawnTimer = 0.0
                        self.starting = False
                return

            #   Paused Game
            if self.paused:
                self.pauseImage.update(seconds)

                ##  Flash
                self.flashTimer += seconds
                if self.flashTimer >= 0.5:
                    self.flashTimer = 0.0
                    if self.flash_alpha == 100:
                        self.flash_alpha = 150
                        self.flash.set_alpha(self.flash_alpha)
                    else:
                        self.flash_alpha = 100
                        self.flash.set_alpha(self.flash_alpha)
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
        

        #   Change state once the title screen 
        #   is completely faded to black
        elif self.starting:

            if self.fade_on == False:
                self.inGame = True
                self.fade_off = True

            return



        