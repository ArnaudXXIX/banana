# coding=utf-8
import pyglet
import cinematic 
import game
class GameEngine(pyglet.window.Window):
    W_WIDTH = 1024
    W_HEIGHT = 640
    def __init__(self):
        super(GameEngine, self).__init__(width=self.W_WIDTH, height=self.W_HEIGHT,resizable=False)
        
        self.set_vsync(False)
        self.set_caption("Banana")
        pyglet.clock.schedule_interval(lambda x:x, 1/1000000.0) # Debridage complet des FPS
        pyglet.clock.schedule_interval(self.physicEngine, 1/100.0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

        # Input handler        
        self.keysHandler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keysHandler)
        
        # ===================================== #
        # =              VARIABLES            = #

        self.mainDrawingBatch = pyglet.graphics.Batch()
        self.state = "cin"
        self.cin = cinematic.Cinematic()
        self.game = game.Game()
        self.fpsText = pyglet.text.Label("", x=4, y=self.height, anchor_y="top", batch=self.mainDrawingBatch, color=(0,0,0,255))
        self.background = pyglet.image.create(self.width, self.height, pyglet.image.SolidColorImagePattern((255,255,0,255))) # Background

    def physicEngine(self, dt):
        if self.state == "playing" and self.game:
            self.game.simulate(dt, self.keysHandler)
         
    
    def on_draw(self):
        
        self.clear()
        self.background.blit(0,0)
        self.fpsText.text = str( round(pyglet.clock.get_fps(), 2) )
        
        if self.state == "playing" and self.game:
            self.game.render()
        
        self.fps =  round(pyglet.clock.get_fps(), 2) +0.1
        if(self.state == "cin"):
            self.cin.run()

        self.mainDrawingBatch.draw()
        
    def on_mouse_motion(self,x, y, dx, dy):
        if(self.state == "playing"):
            self.game.on_mouse_motion(x,y,dx,dy)
        
    def start(self):
        pyglet.app.run()
