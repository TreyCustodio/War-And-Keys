import pygame

class EventManager(object):

    #   Dictionary of actions corresponding to each key
    actions = {(i + 97): False for i in range(26)}

    #   Priority queue of keys
    queue = []

    #   Backspace
    backspace = False
    backspace_timer = 0.0
    backspace_ready = False

    #   Startup
    startup = False
    timer = 0.0
    transitioning = False

    #   Ready
    ready = True

    def __init__(self):
        pass
    
    def buffBackspace():
        EventManager.backspace_ready = False

    """
    Affect the engine
    based on input from the user.
    """
    def handleEvents(engine):

        for event in pygame.event.get():

            if not engine.getReady():
                return
            
            if event.type == pygame.WINDOWMOVED or event.type == pygame.WINDOWLEAVE or not pygame.mouse.get_focused():
                if not EventManager.startup:
                    EventManager.ready = False
                return
            
            elif not EventManager.ready:
                EventManager.ready = True

            if event.type == pygame.KEYDOWN:
                
                #  High priority events

                
                ##  Escape - Quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                
                ##  Startup - Logo
                if EventManager.startup:
                    return
                
                ##  Any - Start Game
                if engine.inTitle:
                    engine.startGame()
                
                ##  Enter - Pause Game
                elif event.key == pygame.K_RETURN:
                    if engine.paused:
                        engine.resume()
                    else:
                        engine.pause()

                #  Core game controls
                elif not engine.paused:
                    if event.key == pygame.K_SPACE:
                        engine.submitString()

                    elif event.key == pygame.K_BACKSPACE:
                        EventManager.backspace = True
                        EventManager.backspace_ready = True
                    else:
                        if event.key in EventManager.actions:
                            EventManager.queue.append(event.key)
                            #engine.handleKey(event)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    EventManager.backspace = False
                    EventManager.backspace_ready = False
                    EventManager.backspace_timer = 0.0
                
        engine.handleKey()

    def readyToUpdate():
        return True
    
    def updateTimer(seconds, engine):
        """
        Update the event manager's timer
        """
        EventManager.timer += seconds
        if EventManager.timer >= 2.0:
            EventManager.timer = 0.0
            EventManager.transitioning = True
            engine.fade_on = True

    def updateBuffer(seconds):
        if EventManager.backspace and not EventManager.backspace_ready:
            EventManager.backspace_timer += seconds
            if EventManager.backspace_timer >= 0.1:
                EventManager.backspace_timer = 0.0
                EventManager.backspace_ready = True
                