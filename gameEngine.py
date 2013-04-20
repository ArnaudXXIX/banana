# coding=utf-8
import pyglet
import game
import menu

class GameEngine(pyglet.window.Window):
    # Constantes de la fenetre
    W_WIDTH = 1024
    W_HEIGHT = 640
    
    def __init__(self):
        super(GameEngine, self).__init__(width=self.W_WIDTH, height=self.W_HEIGHT,resizable=False)
        
        #   =======
        # ~ OPTIONS ~
        #   =======
        
        # - Options generales -
        self.set_vsync(False)
        self.set_caption("Blarg")
        self.set_mouse_cursor(pyglet.window.ImageMouseCursor(pyglet.image.load('sprites/vis.png'), 8, 8)) # Curseur
        
        # - Couleur de fond -
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glClearColor(0.5,0.75,1,1)
        
        # - Physique -
        pyglet.clock.schedule_interval(lambda x:x, 1/100000000.0) # Debridage complet des FPS
        pyglet.clock.schedule_interval(self.physicEngine, 1/100.0)     
        
        
        #   =========
        # ~ VARIABLES ~
        #   =========
        
        # - Input handler -      
        self.keysHandler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keysHandler)
        
        # - Batch -
        self.mainDrawingBatch = pyglet.graphics.Batch()
        
        # - Etat -
        self._state = "menu"
        
        # - Objets -
        self._menu = menu.MainMenu()
        self._game = game.Game()
        self.fpsText = pyglet.text.Label("", x=4, y=self.height, anchor_y="top", batch=self.mainDrawingBatch, color=(0,0,0,255))

    def physicEngine(self, dt):
        if self._state == "playing" and self._game:
            self._game.simulate(dt, self.keysHandler)
    
    def on_draw(self):
        self.clear()
        self.fpsText.text = str( round(pyglet.clock.get_fps(), 2) )
        
        # ----------------------------
        
        if self._state == "playing":
            self._game.render()
        elif self._state == "menu":
            self._state = self._menu.render()
        elif self._state == "quit":
            self.close()
        # -----------------------------

        self.mainDrawingBatch.draw()
        
    def on_mouse_press(self,x, y, button, modifiers):
        # - Passage des evenements aux autres objets
        if self._state == "playing":
            self._game.on_mouse_press(x,y,button,modifiers)
        elif self._state == "menu":
            self._menu.on_mouse_press(x,y,button,modifiers)


    def on_mouse_release(self,x, y, button, modifiers):
        # - Passage des evenements aux autres objets
        if self._state == "playing":
            self._game.on_mouse_release(x, y, button, modifiers)
        
        
    def on_mouse_drag(self,x, y, dx, dy, buttons, modifiers):
        # - Passage des evenements aux autres objets
        if self._state == "playing":
            self._game.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            
    def on_mouse_motion(self,x, y, dx, dy):
        # - Passage des evenements aux autres objets
        if self._state == "menu":
            self._menu.on_mouse_motion(x, y, dx, dy)
        
    def start(self):
        pyglet.app.run()
