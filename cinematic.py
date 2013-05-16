# coding=utf-8
import pyglet
import gameEngine
import xml.etree.ElementTree as ET
import time
import animation


class Cinematic(object):
    def __init__(self, filename=None):
        """
        Créé une cinématique a partir du fichier XML filename

        :param filename: Chemin du fichier

        :type filename: str
        """

        #   =========
        # ~ VARIABLES ~

        # - Gestion du temps -
        self.lastOnDrawTime = None
        self.dt = 0
        self.time = 0
        self.endTime = 1000

        # - Objets -
        self.mainDrawingBatch = pyglet.graphics.Batch()  # Batch que l'on va draw

        # - Divers -
        self.elements = []  # Elements de la cinématique

        # - Construction -
        self.constructFromFile(filename)

    def constructFromFile(self, fileName=None):
        """
        Construction d'une cinematique a partir d'un fichier xml

        :param filename: Chemin du fichier XML

        :type filename: str
        """

        # On parse le XML
        tree = ET.parse(fileName)
        root = tree.getroot()
        for child in root:
            if(child.tag == "border"):  # Si on veut une bordure
                self.elements.append(Border(self.mainDrawingBatch, ch=[childs for childs in child], **child.attrib))
            if(child.tag == "image"):  # Si c'est une image
                self.elements.append(Image(self.mainDrawingBatch, ch=[childs for childs in child], **child.attrib))
            if(child.tag == "end"):
                if(child.attrib['time']):
                    self.endTime = int(child.attrib["time"])

    def run(self):  # Fonction pour afficher notre cinematique a l'écran
        # - Calcul de dt -
        if self.lastOnDrawTime is not None:
            self.dt = time.time() - self.lastOnDrawTime
            self.time += self.dt

        # - Render/Animation -
        for elmt in self.elements:
            elmt.animate(self.dt)  # On anime tous les elements
        self.mainDrawingBatch.draw()
        self.lastOnDrawTime = time.time()
        if(float(self.time) > self.endTime):  # Fin de la cinematique
            return False


# -----------------------------------------------------------

class Border(pyglet.sprite.Sprite):

    def __init__(self, batch, ch=None, text="", textSize="24", pos="bot", height=None, width=None, velY=80, maxY=None):
        """
        Dessine une bordure noire a l'écran a la position pos
        Si il y a une balise <textChange>Text</textChange>, "Text" sera placé au milieu de la bordure

        :param textSize: Taille de la police
        :param height: Hauteur de la bordure
        :param width: Largeur
        :param velY: Vitesse en Y
        :param maxY: Y maximum de la bordure (coté bas de la bordure)

        :type textSize: int
        :type height: int
        :type width: int
        :type velY: int|float
        :type maxY: int
        """

        # - Constantes -
        self.W_HEIGHT = gameEngine.GameEngine.W_HEIGHT
        self.W_WIDTH = gameEngine.GameEngine.W_WIDTH

        # - Objets -
        self._batch = batch

        # - Temps -
        self.time = 0

        # - Vitesse -
        self.velY = int(velY)

        # - Taille -
        if(height is None):
            height = self.W_HEIGHT/4
        if(width is None):
            width = self.W_WIDTH

        # - Image -
        super(Border, self).__init__(pyglet.image.create(width, height, pyglet.image.SolidColorImagePattern((0, 0, 0, 255))))

        # - Position -
        self.pos = pos
        if(pos == "bot"):
            self.y = -self.height
            if(maxY is None):
                self.maxY = 0
            else:
                self.maxY = int(maxY)
        elif(pos == "top"):
            if(maxY is None):
                self.maxY = self.W_HEIGHT - self.height + 2
            else:
                self.maxY = int(maxY)
            self.y = self.W_HEIGHT

        # - Texte -
        if(text is not None):
            # - Contenu -
            self.textContent = text

            # - Size -
            self.textSize = int(textSize)
            self.text = pyglet.text.Label(self.textContent, font_size=self.textSize, batch=self._batch, anchor_x="center", anchor_y="center", x=self.width/2, y=self.height/2, color=(255, 255, 255, 255))

        else:
            self.text = None

        # Parsage des childs avec des petits oignons
        self.toDoChangeText = {}
        for elmt in ch:
            if elmt.tag == "textChange":
                self.toDoChangeText[elmt.attrib['time']] = elmt.text

    def animate(self, dt):
        """
        Anime le tout selon les parametres definis auparavant
        """
        self.time += dt

        if(self.pos == "bot"):  # Bordure en bas
            if(int(self.y) < self.maxY):
                self.y += self.velY * dt
        elif(self.pos == "top"):  # En haut
            if(int(self.y) > self.maxY):
                self.y -= self.velY * dt

        if(self.text is not None):  # Si il y a du texte
            for elmt in self.toDoChangeText:
                if(int(self.time) >= int(elmt)):
                    self.text.text = self.toDoChangeText[elmt]  # On le change
                    self.text.y = self.y + self.height / 2  # Et on le place au centre
                    self.text.x = self.x + self.width / 2


# -----------------------------------------------------------

class Image():

    def __init__(self, batch, ch=None, path=None, x=250, y=250, w=48, h=48):
        """
        Dessine une image "path" a la position (x,y)
        Si il y a une balise <move x="350" y="325" timeStart="2" timeStop="3"/>
        l'image bouge jusqu'en (x,y) a partir du temps timeStart jusqu'au temps timeStop

        :param batch: Batch dans lequel inserer notre sprite
        :param ch: Enfants, pour avoir les transitions
        :param path: Chemin vers l'image
        :param x: x initial
        :param y: y initial

        :type batch: Batch
        :type ch: XML
        :type path: str
        :type x: str | int
        :type y: str | int
        """
        self.animation = animation.AnimationGroup()
        self.animation.createFromImage(pyglet.image.load(path), int(w), int(h))
        self.animation.setFrameRate(4.0/50.0)
        self.animation.selectAnimation(0)
        self.animation.setIdleState()

        # - Position -
        self.x = int(x)
        self.y = int(y)
        self.width = int(w)
        self.height = int(h)
        # Pour garder une vitesse constante
        self.startX = self.x
        self.startY = self.y
        # - Temps -
        self.time = 0

        # - Animation -
        self.moveNb = 0
        self.mvtDone = False
        self.elmt = ""

        # - Parsage des enfants avec des petits pois -
        self.toDoMovement = {}
        for elmt in ch:
            if elmt.tag == "move":  # Si on demande de move
                attrib = {}
                for i in elmt.attrib:
                    attrib[i] = elmt.attrib[i]
                self.toDoMovement[elmt.attrib['timeStart']] = attrib  # Alors on le mets dans le todo
        self.keylist = self.toDoMovement.keys()
        self.keylist.sort()

    def animate(self, dt):
        """
        Anime le tout selon les parametres definis auparavant
        """

        self.time += dt
        try:
            self.elmt = self.toDoMovement[self.keylist[self.moveNb]]

            if(float(self.elmt['timeStop']) >= float(self.time) >= float(self.elmt['timeStart'])):
                self.animation.unsetIdleState()
                self.mvtDone = True
                self.x += dt * ((int(self.elmt['x']) - self.startX)) / (int(self.elmt['timeStop']) - int(self.elmt['timeStart']))
                self.y += dt * ((int(self.elmt['y']) - self.startY)) / (int(self.elmt['timeStop']) - int(self.elmt['timeStart']))
            else:
                if self.mvtDone:
                    self.startX = self.x
                    self.startY = self.y
                    self.animation.setIdleState()
                    self.moveNb += 1
                    self.mvtDone = False

            self.animation.render(self.x, self.y)
        except:
            pass
