#-*- encoding: utf-8 -*-
import math
import pyglet
import gameEngine

class Entity(object):
    def __init__(self, x=0, y=0, xVel=0, yVel=0):
        self.x = x
        self.y = y
        self.xVel = xVel
        self.yVel = yVel

    def simulate(self, dt=1):
        if self.xVel != 0:
            self.x += self.xVel * dt
        if self.yVel != 0:
            self.y += self.yVel * dt
            
class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x=0, y=0, xVel=0, yVel=0)
        self.hp = 100
        self.width = 48
        self.height = 48
        self.speed = 30
        self.aimVector = [0,0]
        self.mouseOffset = 7
        
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load("sprites/blarg.png").get_texture())
        self.sprite.x = gameEngine.GameEngine.W_WIDTH/2 - self.sprite.width/2
        self.sprite.y = gameEngine.GameEngine.W_HEIGHT/2 - self.sprite.height/2
    
    def aim(self, x, y):
        """
        Détermine le vecteur directeur de la droite passant par 
        le centre de l'écran et le pointeur de la souris.
        On le détermine en divisant le vecteur définit
        par le centre de l'écran et le cursor par sa norme.
        """
        centerX = gameEngine.GameEngine.W_WIDTH/2
        centerY = gameEngine.GameEngine.W_HEIGHT/2 + self.mouseOffset
        
        norm = math.sqrt( (x - centerX)**2 + (y - centerY)**2 )
        
        self.aimVector[0] = (x - centerX) / norm
        self.aimVector[1] = (y - centerY) / norm
        
    def move(self, x,y, gameMap ,dt):
        
        if not gameMap.colide( self.x - self.width/2 + x * dt * self.speed, self.y - self.height/2 + y * dt * self.speed, self.width, self.height):
            self.x += int(x * dt * self.speed)
            self.y += int(y * dt * self.speed)
                    
    def render(self):
        self.sprite.draw()
        
        centerX = gameEngine.GameEngine.W_WIDTH/2
        centerY = gameEngine.GameEngine.W_HEIGHT/2 + self.mouseOffset
        
        # DEBUG: On trace la la droite qui porte le
        # veceur aimVector
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        pyglet.gl.glVertex2i( centerX, centerY)
        pyglet.gl.glVertex2i( int(centerX + 2000 * self.aimVector[0]), int(centerY + 2000 * self.aimVector[1]))
        pyglet.gl.glEnd()
        
class Npc(object):
    def __init__(self,x,y):
        super(Npc, self).__init__(x,y)
        
        
    def move(self, map):
        pass
    
    def render(self):
        pass
    
    def kill(self):
        pass
    
        
