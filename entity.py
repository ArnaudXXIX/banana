#-*- encoding: utf-8 -*-
import math
import time
import os
import pyglet
import gameEngine
import random
import IA
import item
import vector
import animation
import xml.etree.ElementTree as xml
# ---------------------------------------------------


class Entity(object):
    """
    Classe generale d'une entitée
    """
    def __init__(self, x=0, y=0, xVel=0, yVel=0):
        self.x = int(x)
        self.y = int(y)
        self.xVel = xVel
        self.yVel = yVel


    def move(self, x, y, gameMap, dt):
        if not gameMap.collide(self.x - self.width/2 + x * dt * self.speed, self.y - self.height/2 + y * dt * self.speed, self.width, self.height):
            self.x += int(x * dt * self.speed)
            self.y += int(y * dt * self.speed)

# ---------------------------------------------------


class Enemy(Entity):
    """
    Ennemie pour tester l'IA, il essaie juste de toucher le joueur
    """
    def __init__(self, x, y, fileName, gameMap):
        # - Objets -
        Entity.__init__(self, x, y)

        # - Constantes -
        self.type = "enemy"
        self.name = fileName

        # - Mouvements -
        self.blocked = False
        self.x = int(x)
        self.y = int(y)
        self.canMove = True
        self.vector = []
        self.fireRate = 10

        # - IA -
        self.IA = IA.IA(self.x, self.y, gameMap)
        self.caseX = self.x / 64
        self.caseY = self.y / 64

        self.load(fileName)

    def load(self, fileName):
        
        if os.path.isfile("data/ennemies/"+fileName+".xml"):
            xmlTree = xml.parse("data/ennemies/"+fileName+".xml")
            root = xmlTree.getroot()
            for child in root:
                if child.tag == "width":
                    self.width = int(child.text)
                elif child.tag == "height":
                    self.height = int(child.text)
                elif child.tag == "speed":
                    self.speed = float(child.text)
                elif child.tag == "sprite":
                    # - Chargement animations
                    self.animation = animation.AnimationGroup()
                    self.animation.createFromImage(pyglet.image.load(child.text), self.width, self.height)
                elif child.tag == "itemList":
                    self.itemList = []
                    for e in child:
                        self.itemList.append([e.tag, float(e.attrib["value"])])
                elif child.tag == "hp":
                    self.hp = float(child.text)
                elif child.tag == "fireRate":
                    self.fireRate = float(child.text)
                elif child.tag == "bulletSpeed":
                    self.bulletSpeed = float(child.text)
                elif child.tag == "attack":
                    self.attack = float(child.text)
        else:
            print "couldn't load the enemy ["+fileName+"]. No such file."

    def render(self):
        try:
            self.animation.setFrameRate(4/(self.speed/10))
            # Selection de l'animation en fonction de l'orientation de la vidée.
           
            if self.IA.path[-2][1] - self.caseY < 0:
                # bottom:
                if self.IA.path[-2][0] - self.caseX <= 0:
                    # left
                    self.animation.selectAnimation(3)
                elif self.IA.path[-2][0] - self.caseX > 0:
                    # right
                    self.animation.selectAnimation(2)
                    
            elif  self.IA.path[-2][1] - self.caseY > 0:
                # top
                if self.IA.path[-2][0] - self.caseX < 0:
                    # left
                    self.animation.selectAnimation(1)
                elif self.IA.path[-2][0] - self.caseX >= 0:
                    # right
                    self.animation.selectAnimation(0)
                    
            self.animation.render(self.x - self.width/2, self.y - self.height/2)
        except:
            pass

    def move(self, x, y, gameMap, dt, target):
        if self.canMove:
                self.vector = [x, y]
                self.canMove = False
        if not gameMap.collide(self.x - self.width/2 + x * dt * self.speed, self.y - self.height/2 + y * dt * self.speed, self.width, self.height) and sum(self.vector)**2 == 1:
            # Si il ne collisione pas, il se déplace normalement
            self.x += int(self.vector[0] * dt * self.speed)
            self.y += int(self.vector[1] * dt * self.speed)
            if ((self.x + self.width / 2 + 1) / 64) == (self.x / 64) == ((self.x - self.width / 2 - 1) / 64) and ((self.y + self.height / 2 + 1) / 64) == ((self.y) / 64) == ((self.y - self.height / 2 - 1) / 64):  # Pour verifier si on est completement dans une case
                self.canMove = True  # Si on a changé de case, on change de vecteur deplacement
                self.vector = []
                self.caseX = int((self.x) / 64)
                self.caseY = int((self.y) / 64)
        else:
            self.canMove = True

    def hit(self):
        self.hp -= 10

    def shoot(self, x, y, bulletList):
        if random.random() < self.fireRate/200:
            aimDirection = vector.Vector2(x - self.x, y - self.y).getUnitary()
            bulletList.append(Bullet(self.x, self.y, aimDirection.x * self.bulletSpeed, aimDirection.y * self.bulletSpeed, self))

    def loot(self):
        objet = random.randint(0, len(self.itemList) - 1)
        itemToReturn = item.Item(self.x, self.y, self.itemList[objet][0], self.itemList[objet][1])
        return itemToReturn

# ---------------------------------------------------


class Player(Entity):
    """
    Joueur
    """
    def __init__(self, x, y):
        # - Objets -
        Entity.__init__(self, x, y)

        # - Constantes -
        self.width = 48
        self.height = 48
        self.aimVector = vector.Vector2(0, 0)
        self.mouthOffset = 7
        self.type = "player"

        # - Tir -
        self.isFiring = False
        self.lastShoot = time.time()

        # - Caractéristiques -
        self.maxHp = 100.0
        self.hp = 100.0
        self.speed = 30.0
        self.shieldCapacity = 50.0
        self.shield = 50.0
        self.fireRate = 10.0
        self.resistance = 100
        self.attack = 10
        self.isMoving = False
        self.mucus = 100
        self.mucusMax = 100
        self.regenMucus = 0.01

        self.increasedMucus = 0

        # - Chargement animations
        self.animation = animation.AnimationGroup()
        self.animation.createFromImage(pyglet.image.load("data/sprites/blarg.png"), self.width, self.height)

    def increaseMucus(self):
        self.increasedMucus += self.regenMucus
        if self.increasedMucus >= 1:
            if self.mucus < self.mucusMax:
                self.mucus += 1
            self.increasedMucus = 0

    def aim(self, x, y):
        """
        Détermine le vecteur directeur de la droite passant par
        le centre de l'écran et le pointeur de la souris.
        On le détermine en divisant le vecteur définit
        par le centre de l'écran et le cursor par sa norme.
        """
        width, height = gameEngine.getDinamicWindowSize()
        
        centerX = width/2
        centerY = height/2 + self.mouthOffset

        self.aimVector.set(x-centerX, y-centerY)
        self.aimVector = self.aimVector.getUnitary()

    def shoot(self, bullets):
        if self.isFiring and time.time() - self.lastShoot > 1/self.fireRate and self.mucus > 0:
            self.lastShoot = time.time()
            bullets.append(Bullet(self.x, self.y + self.mouthOffset, self.aimVector.x * 1000, self.aimVector.y * 1000, self))
            self.mucus -= 1

    def hit(self, attack):
        if self.shield - attack > 0:
            self.shield -= attack
        elif self.hp - (attack - self.shield) / (1 + math.log(1 + self.resistance / 25)) > 0:
            self.shield = 0
            self.hp -= (attack - self.shield) / (1 + math.log(1 + self.resistance / 25))
        else:
            self.hp = 0
            self.shield = 0

    def render(self):
        # update du framerate de l'animation
        self.animation.setFrameRate(4/self.speed)

        # Selection de l'animation en fonction de l'orientation de la vidée.
        if self.aimVector.x < 0 and self.aimVector.y < 0:
            # Bottom Left
            self.animation.selectAnimation(3)
        elif self.aimVector.x > 0 and self.aimVector.y < 0:
            # Bottom Right
            self.animation.selectAnimation(2)

        elif self.aimVector.x < 0 and self.aimVector.y > 0:
            # Top left
            self.animation.selectAnimation(1)

        elif self.aimVector.x > 0 and self.aimVector.y > 0:
            # Top right
            self.animation.selectAnimation(0)

        self.animation.render(self.x - self.width/2, self.y - self.height/2)

# ---------------------------------------------------


class Bullet(Entity):
    SIZE = 10

    def __init__(self, x, y, xVel, yVel, owner):
        # - Objet -
        super(Bullet, self).__init__(x, y, xVel, yVel)

        # - Constantes -
        self.width = 10
        self.height = 10
        self.speed = 1
        self.range = 1000
        self.initX = x
        self.initY = y
        self.owner = owner

    def simulate(self, gameMap, player, ennemies, dt=0.1):
        norm = math.sqrt((self.initX - self.x)**2 + (self.initY - self.y)**2)
        if not gameMap.collide(self.x - self.width/2 + self.xVel * dt * self.speed, self.y - self.height/2 + self.yVel * dt * self.speed, self.width, self.height) and norm < self.range:
            self.x += int(self.xVel * dt * self.speed)
            self.y += int(self.yVel * dt * self.speed)
        else:
            return False
        for en in ennemies:
            if self.collide(en):
                en.hit()
                return False
        if self.collide(player):
            player.hit(self.owner.attack)
            return False

    def collide(self, ent):
        """
                              == COLLIDE ==

        Voir gameMap.collide() pour les explications

        :param ent: ennemi avec lequel check les collisions
        :type ent: Ennemy
        """
        if ent.type != self.owner.type:
            # One does not simply understand what's written there
            if self.x <= ent.x <= self.x + self.width or self.x <= ent.x+ent.width <= self.x + self.width:
                if self.y <= ent.y <= self.y + self.height or self.y <= ent.y+ent.height <= self.y + self.height:
                    return True
                elif ent.y <= self.y <= ent.y+ent.height or ent.y <= self.y + self.height <= ent.y+ent.height:
                    return True

            elif ent.x <= self.x <= ent.x+ent.width or ent.x <= self.x + self.width <= ent.x+ent.width:
                if (self.y <= ent.y <= self.y + self.height) or (self.y <= ent.y+ent.height <= self.y + self.height):
                    return True
                elif ent.y <= self.y <= ent.y+ent.height or ent.y <= self.y + self.height <= ent.y+ent.height:
                    return True

        return False
