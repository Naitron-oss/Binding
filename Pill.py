from pygame import *
from random import *
from const import *
from func import *
from Item import *
# from PHD import *

class Pill(Item):
	def __init__(self, xy, texture):
		self.x, self.y = xy
		# self.positive = PHD in character.items
		self.texture = texture.subsurface(randint(0,2)*64, randint(0,2)*64, 64, 64)
		self.bounds = Rect(GRIDX+GRATIO*self.x,GRIDY+GRATIO*self.y, 32, 64)
		self.stats = [0]*6
		self.stats[randint(0,5)] = 1